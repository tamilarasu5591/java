import sys

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith('CROP_RULES = ['):
        start_idx = i
    if start_idx != -1 and line.startswith('    return scored[:3] if scored else '):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_block = '''CROP_RULES = [
    {"name": "Rice (Paddy)", "n": (40,80), "p": (10,40), "k": (10,40), "ph": (5.5,7.0), "target_n": 40, "target_p": 20, "target_k": 20, "season": "Kharif (Jun-Sep)", "tip": "Maintain standing water. Requires high nitrogen input."},
    {"name": "Wheat", "n": (20,80), "p": (15,40), "k": (15,40), "ph": (6.0,7.5), "target_n": 50, "target_p": 25, "target_k": 16, "season": "Rabi (Nov-Mar)", "tip": "Irrigate at crown root initiation (21 days after sowing)."},
    {"name": "Maize", "n": (20,100), "p": (20,60), "k": (20,60), "ph": (5.5,7.5), "target_n": 48, "target_p": 24, "target_k": 16, "season": "Kharif (Jun-Aug)", "tip": "Thin seedlings to 25 cm spacing for best yield."},
    {"name": "Sugarcane", "n": (40,150), "p": (20,60), "k": (30,80), "ph": (6.0,8.0), "target_n": 100, "target_p": 30, "target_k": 30, "season": "Full year", "tip": "Requires 180-200 cm water annually; use drip if possible."},
    {"name": "Cotton", "n": (30,90), "p": (20,50), "k": (20,50), "ph": (6.0,8.0), "target_n": 48, "target_p": 24, "target_k": 24, "season": "Kharif (May-Jun)", "tip": "Apply 30N at sowing, 30N at square formation."},
    {"name": "Groundnut", "n": (10,40), "p": (20,50), "k": (10,40), "ph": (5.5,7.0), "target_n": 10, "target_p": 20, "target_k": 20, "season": "Kharif (Jun-Jul)", "tip": "Inoculate seeds with Rhizobium culture before sowing."},
    {"name": "Tomato", "n": (20,80), "p": (20,60), "k": (20,80), "ph": (5.5,7.0), "target_n": 60, "target_p": 25, "target_k": 25, "season": "Sep-Jan / Feb-May", "tip": "Use stakes or trellis. Mulching reduces diseases significantly."},
    {"name": "Onion", "n": (20,80), "p": (20,50), "k": (20,60), "ph": (6.0,7.5), "target_n": 40, "target_p": 20, "target_k": 24, "season": "Rabi (Oct-Nov)", "tip": "Cease irrigation 2 weeks before harvest for better curing."},
    {"name": "Millet (Bajra)", "n": (10,60), "p": (10,40), "k": (10,40), "ph": (5.5,7.5), "target_n": 24, "target_p": 12, "target_k": 12, "season": "Kharif (Jun-Jul)", "tip": "Highly drought-resistant; suited to sandy soils."}
]

def calculate_stcr_fertilizer(soil_n, soil_p, soil_k, target_n, target_p, target_k, acres):
    """
    Soil Test Crop Response (STCR) based calculation.
    Assumptions (Approx): Urea=46% N, DAP=18% N and 46% P, MOP=60% K
    """
    try:
        soil_n, soil_p, soil_k, acres = float(soil_n), float(soil_p), float(soil_k), float(acres)
        
        # Deficit logic (simplified for demonstration from true STCR formulas)
        def_n = max(0, target_n - (soil_n * 0.2))
        def_p = max(0, target_p - (soil_p * 0.2))
        def_k = max(0, target_k - (soil_k * 0.2))

        # P requirement is fulfilled primarily by DAP
        dap_req = def_p / 0.46
        n_from_dap = dap_req * 0.18
        
        # Remaining N comes from Urea
        remaining_n = max(0, def_n - n_from_dap)
        urea_req = remaining_n / 0.46
        
        # K comes from MOP
        mop_req = def_k / 0.60
        
        return {
            "urea_kg": round(urea_req * acres, 1),
            "dap_kg": round(dap_req * acres, 1),
            "mop_kg": round(mop_req * acres, 1),
            "urea_bags": round((urea_req * acres) / 45.0, 1), # 45kg standard India bag
            "dap_bags": round((dap_req * acres) / 50.0, 1),   # 50kg bag
            "mop_bags": round((mop_req * acres) / 50.0, 1),   # 50kg bag
            "land_acres": acres
        }
    except Exception as e:
        return {"urea_kg": 0, "dap_kg": 0, "mop_kg": 0, "urea_bags": 0, "dap_bags": 0, "mop_bags": 0, "land_acres": acres}

def get_crop_recommendation(n, p, k, ph):
    n, p, k, ph = float(n), float(p), float(k), float(ph)
    scored = []
    for crop in CROP_RULES:
        score = 0
        if crop["n"][0] <= n <= crop["n"][1]: score += 1
        if crop["p"][0] <= p <= crop["p"][1]: score += 1
        if crop["k"][0] <= k <= crop["k"][1]: score += 1
        if crop["ph"][0] <= ph <= crop["ph"][1]: score += 1
        confidence = int((score / 4) * 100)
        
        if confidence > 0:
            scored.append({
                "name": crop["name"],
                "confidence": confidence,
                "season": crop["season"],
                "tip": crop["tip"],
                "target_n": crop["target_n"],
                "target_p": crop["target_p"],
                "target_k": crop["target_k"]
            })
    scored.sort(key=lambda x: x["confidence"], reverse=True)
    return scored[:3] if scored else [{"name": "Millet (Bajra)", "confidence": 50, "season": "Kharif", "tip": "Drought-tolerant.", "target_n": 24, "target_p": 12, "target_k": 12}]
'''
    
    del lines[start_idx:end_idx+1]
    lines.insert(start_idx, new_block + '\n')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print('Updated CROP_RULES and added calculate_stcr_fertilizer successfully')
else:
    print('Could not find CROP_RULES block')
