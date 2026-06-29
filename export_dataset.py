import sqlite3
import csv
import json

# 1. Export Market Prices from SQLite
try:
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM market_prices')
    rows = cursor.fetchall()
    
    if rows:
        headers = [description[0] for description in cursor.description]
        with open('market_prices_dataset.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print("Success: market_prices_dataset.csv created.")
    else:
        print("Info: No market data found.")
    conn.close()
except Exception as e:
    print(f"Error exporting market data: {e}")

# 2. Export Disease Data (Manually replicated from app.py)
diseases = [
    {"disease": "Leaf Blight", "treatment": "Use Fungicide X (Copper-based)"},
    {"disease": "Rust", "treatment": "Remove infected leaves immediately. Apply Sulfur dust."},
    {"disease": "Healthy", "treatment": "Keep monitoring, water regularly."},
    {"disease": "Powdery Mildew", "treatment": "Spray Neem Oil or Sulfur based fungicide."},
    {"disease": "Bacterial Spot", "treatment": "Apply copper bactericides. Avoid overhead watering."},
    {"disease": "Aphids", "treatment": "Spray soapy water or Neem oil."},
    {"disease": "Spider Mites", "treatment": "Increase humidity, use miticide."},
    {"disease": "Yellow Leaf Curl", "treatment": "Control whiteflies, remove infected plants."},
    {"disease": "Root Rot", "treatment": "Improve drainage, avoid overwatering."},
    {"disease": "Downy Mildew", "treatment": "Improve air circulation, use specific fungicides."},
    {"disease": "Early Blight", "treatment": "Mulch soil, use tomato-safe fungicide."},
    {"disease": "Mosaic Virus", "treatment": "Remove plant to prevent spread (No cure)."},
    {"disease": "Scale Insects", "treatment": "Prune infested branches, use horticultural oil."},
    {"disease": "Anthracnose", "treatment": "Remove dead wood, use fungicidal sprays."},
    {"disease": "Mealybugs", "treatment": "Dab with alcohol, spray insecticidal soap."},
    {"disease": "Cashew anthracnose", "treatment": "Prune infected parts, use copper-based fungicides."},
    {"disease": "Cashew gumosis", "treatment": "Improve drainage, apply Bordeaux paste to stems."},
    {"disease": "Cashew healthy", "treatment": "Keep monitoring, maintain proper spacing."},
    {"disease": "Cashew leaf miner", "treatment": "Use Neem oil or systemic insecticides."},
    {"disease": "Cashew red rust", "treatment": "Improve air circulation, use sulfur fungicides."},
    {"disease": "Cassava bacterial blight", "treatment": "Use healthy planting material, rotate crops."},
    {"disease": "Cassava brown spot", "treatment": "Plant resistant varieties, remove infected leaves."},
    {"disease": "Cassava green mite", "treatment": "Use predatory mites or biological controls."},
    {"disease": "Cassava healthy", "treatment": "Keep monitoring, water regularly."},
    {"disease": "Cassava mosaic", "treatment": "Use disease-free stems, control whiteflies."},
    {"disease": "Maize fall armyworm", "treatment": "Apply Neem-based pesticides or biological controls."},
    {"disease": "Maize grasshoper", "treatment": "Maintain field sanitation, use bird-friendly habitats."},
    {"disease": "Maize healthy", "treatment": "Keep monitoring, ensure proper fertilization."},
    {"disease": "Maize leaf beetle", "treatment": "Spray soapy water or use recommended insecticides."},
    {"disease": "Maize leaf blight", "treatment": "Use host-resistant hybrids, rotate crops."},
    {"disease": "Maize leaf spot", "treatment": "Avoid overhead irrigation, use fungicides if severe."},
    {"disease": "Maize streak virus", "treatment": "Control leafhoppers, plant resistant varieties."},
    {"disease": "Tomato healthy", "treatment": "Keep monitoring, water regularly."},
    {"disease": "Tomato leaf blight", "treatment": "Apply copper-based fungicides, improve spacing."},
    {"disease": "Tomato leaf curl", "treatment": "Control whiteflies, use reflective mulches."},
    {"disease": "Tomato septoria leaf spot", "treatment": "Remove lower leaves, avoid overhead watering."},
    {"disease": "Tomato verticulium wilt", "treatment": "Improve soil drainage, plant resistant varieties."},
    {"disease": "American Bollworm on Cotton", "treatment": "Use pheromone traps and recommended insecticides like NPV."},
    {"disease": "Anthracnose on Cotton", "treatment": "Remove infected leaves, use copper-based fungicides."},
    {"disease": "Army worm", "treatment": "Spray Bacillus thuringiensis (Bt) or use deep plowing."},
    {"disease": "Bacterial Blight in Rice", "treatment": "Avoid excess nitrogen, use resistant varieties and copper fungicides."},
    {"disease": "Brownspot", "treatment": "Ensure proper nutrition, apply Mancozeb or Edifenphos."},
    {"disease": "Common Rust", "treatment": "Apply fungicides containing chlorothalonil or mancozeb."},
    {"disease": "Cotton Aphid", "treatment": "Use insecticidal soaps, neem oil, or promote natural predators like ladybugs."},
    {"disease": "Flag Smut", "treatment": "Treat seeds with fungicides like carboxin before sowing."},
    {"disease": "Gray Leaf Spot", "treatment": "Rotate crops and use foliar fungicides if severe."},
    {"disease": "Healthy Maize", "treatment": "Keep monitoring, maintain proper soil health."},
    {"disease": "Healthy Wheat", "treatment": "Keep monitoring, ensure adequate watering."},
    {"disease": "Healthy cotton", "treatment": "Keep monitoring, maintain proper spacing."},
    {"disease": "Leaf Curl", "treatment": "Control whiteflies using sticky traps and insecticidal soaps."},
    {"disease": "Leaf smut", "treatment": "Use disease-free seeds and apply seed treatment fungicides."},
    {"disease": "Mosaic sugarcane", "treatment": "Use virus-free cutting materials, control aphid vectors."},
    {"disease": "RedRot sugarcane", "treatment": "Remove infected plants, avoid waterlogging, use healthy setts."},
    {"disease": "RedRust sugarcane", "treatment": "Apply sulfur-based fungicides and improve drainage."},
    {"disease": "Rice Blast", "treatment": "Avoid excess nitrogen, use Tricyclazole or validamycin."},
    {"disease": "Sugarcane Healthy", "treatment": "Keep monitoring, ensure timely irrigation."},
    {"disease": "Tungro", "treatment": "Control green leafhoppers, use resistant varieties."},
    {"disease": "Wheat Brown leaf Rust", "treatment": "Use resistant varieties, apply foliar fungicides like tebuconazole."},
    {"disease": "Wheat Stem fly", "treatment": "Adjust sowing dates, use systemic insecticides."},
    {"disease": "Wheat aphid", "treatment": "Use botanical extracts like neem oil or systemic insecticides."},
    {"disease": "Wheat black rust", "treatment": "Use resistant varieties, apply fungicides promptly."},
    {"disease": "Wheat leaf blight", "treatment": "Use disease-free seeds, practice crop rotation."},
    {"disease": "Wheat mite", "treatment": "Apply specific miticides or wettable sulfur."},
    {"disease": "Wheat powdery mildew", "treatment": "Apply sulfur dust or systemic fungicides."},
    {"disease": "Wheat scab", "treatment": "Avoid excessive irrigation during flowering, apply fungicides."},
    {"disease": "Wheat Yellow Rust", "treatment": "Use resistant seeds, spray propiconazole."},
    {"disease": "Wilt", "treatment": "Improve soil drainage, practice long crop rotations."},
    {"disease": "Yellow Rust Sugarcane", "treatment": "Apply fungicides and use resistant varieties."},
    {"disease": "bacterial blight in Cotton", "treatment": "Use acid-delinted seeds, spray copper bactericides."},
    {"disease": "bollrot on Cotton", "treatment": "Ensure proper spacing for sunlight, avoid excessive nitrogen."},
    {"disease": "bollworm on Cotton", "treatment": "Use Bt cotton varieties, apply recommended insecticides."},
    {"disease": "cotton mealy bug", "treatment": "Prune infested parts, spray neem oil or systemic insecticides."},
    {"disease": "cotton whitefly", "treatment": "Use yellow sticky traps, spray neem oil or insecticidal soap."},
    {"disease": "maize ear rot", "treatment": "Store grains properly at low moisture, deep plow residues."},
    {"disease": "maize fall armyworm", "treatment": "Apply Bacillus thuringiensis (Bt) or recommended bio-pesticides."},
    {"disease": "maize stem borer", "treatment": "Use light traps, apply granular insecticides in leaf whorls."},
    {"disease": "pink bollworm in cotton", "treatment": "Plow fields deeply after harvest, use pheromone traps."},
    {"disease": "red cotton bug", "treatment": "Maintain field sanitation, use appropriate chemical sprays."},
    {"disease": "thirps on cotton", "treatment": "Spray dimethoate or neem seed kernel extract."}
]

try:
    with open('disease_symptoms_dataset.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Disease Name", "Recommended Treatment"])
        for d in diseases:
            writer.writerow([d['disease'], d['treatment']])
    print("Success: disease_symptoms_dataset.csv created.")
except Exception as e:
    print(f"Error exporting disease data: {e}")

print("Data export complete.")
