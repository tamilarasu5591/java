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
    {"disease": "Mealybugs", "treatment": "Dab with alcohol, spray insecticidal soap."}
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
