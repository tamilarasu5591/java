import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_synonyms():
    return {
        "paddy": "rice",
        "peanut": "groundnut",
        "corn": "maize",
        "eggplant": "brinjal",
        "bhindi": "okra",
        "jowar": "millets",
        "bajra": "millets",
        "faw": "armyworm",
        "bph": "hopper"
    }

def expand_query_with_synonyms(query_words):
    synonyms = get_synonyms()
    expanded = set(query_words)
    for word in query_words:
        if word in synonyms:
            expanded.add(synonyms[word])
    return expanded

def search_knowledge_base(query):
    """Scored RAG search against knowledge_base.json"""
    kb_path = os.path.join(BASE_DIR, 'knowledge_base.json')
    if not os.path.exists(kb_path):
        return ""
        
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb = json.load(f)
            
        categories = kb.get('categories', {})
        # Tokenize and normalize query
        query_words = set(re.findall(r'\w+', query.lower()))
        query_words = expand_query_with_synonyms(query_words)
        
        matches = [] # list of (score, string_match)
        
        # Helper to calculate score
        def get_score(item, fields, boost_fields=None):
            score = 0
            for field in fields:
                val = item.get(field, "")
                if isinstance(val, list):
                    val = " ".join(val)
                if isinstance(val, str):
                    words = set(re.findall(r'\w+', val.lower()))
                    overlap = len(query_words.intersection(words))
                    score += overlap
            
            if boost_fields:
                for field in boost_fields:
                    val = item.get(field, "")
                    if isinstance(val, list):
                        val = " ".join(val)
                    if isinstance(val, str):
                        words = set(re.findall(r'\w+', val.lower()))
                        overlap = len(query_words.intersection(words))
                        score += overlap * 2 # Double points for exact name/id match
            return score

        # Check local names directly
        def check_local_names(item, query):
            local_vals = list(item.get('local_names', {}).values())
            for lv in local_vals:
                if lv.lower() in query.lower():
                    return 5 # High score for direct local name match
            return 0

        # Search Crops
        for crop in categories.get('crops', []):
            score = get_score(crop, ['soil', 'varieties'], ['name'])
            score += check_local_names(crop, query)
            if score > 0:
                s = f"Crop Info: {crop['name']} | Soil: {crop.get('soil')} | NPK: {crop.get('npk')} | Season: {', '.join(crop.get('seasons', []))} | Tip: {crop.get('sowing_tip')}"
                matches.append((score, s))

        # Search Pests
        for pest in categories.get('pests', []):
            score = get_score(pest, ['affects', 'symptoms'], ['name'])
            score += check_local_names(pest, query)
            if score > 0:
                s = f"Pest/Disease Info: {pest['name']} | Affects: {', '.join(pest.get('affects', []))} | Symptoms: {pest.get('symptoms')} | Organic Control: {pest.get('organic_control')} | Chemical: {pest.get('chemical_control')}"
                matches.append((score, s))
                
        # Search Schemes
        for scheme in categories.get('government_schemes', []):
            score = get_score(scheme, ['benefit', 'eligibility'], ['name', 'id'])
            if score > 0:
                s = f"Scheme Info: {scheme['name']} | Benefit: {scheme.get('benefit')} | Eligibility: {scheme.get('eligibility')} | Apply: {scheme.get('how_to_apply')}"
                matches.append((score, s))
                
        # Search Fertilizers
        for fert in categories.get('fertilizers', []):
            score = get_score(fert, ['type', 'application'], ['name'])
            if score > 0:
                s = f"Fertilizer: {fert['name']} | NPK: {fert.get('npk_content')} | Dose: {fert.get('recommended_dose')} | Application: {fert.get('application')}"
                matches.append((score, s))

        # Search Irrigation
        for irrig in categories.get('irrigation_methods', []):
            score = get_score(irrig, ['benefits', 'best_for'], ['name'])
            if score > 0:
                s = f"Irrigation Method: {irrig['name']} | Best for: {', '.join(irrig.get('best_for', []))} | Water Savings: {irrig.get('water_savings')} | Benefits: {irrig.get('benefits')}"
                matches.append((score, s))

        # Search Soil Health
        for soil in categories.get('soil_health', []):
            score = get_score(soil, ['characteristics', 'regions', 'suitable_crops'], ['name'])
            if score > 0:
                s = f"Soil Info: {soil['name']} | Regions: {', '.join(soil.get('regions', []))} | Characteristics: {soil.get('characteristics')} | Best Crops: {', '.join(soil.get('suitable_crops', []))}"
                matches.append((score, s))


        if matches:
            # Sort by score descending and take top 8
            matches.sort(key=lambda x: x[0], reverse=True)
            top_matches = matches[:8]
            
            # Deduplicate just in case
            unique_texts = []
            seen = set()
            for score, text in top_matches:
                if text not in seen:
                    seen.add(text)
                    unique_texts.append(text)
                    
            return "From Local Agricultural Knowledge Base:\n- " + "\n- ".join(unique_texts)
        return ""
    except Exception as e:
        print(f"RAG Search Error: {e}")
        return ""
