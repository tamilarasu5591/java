import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Define constants
CROPS = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Tomato', 'Potato', 'Sugarcane', 'Soybean', 'Barley', 'Millet']
REGIONS = ['North', 'South', 'East', 'West', 'Central', 'North-East']
SEASONS = ['Kharif (Monsoon)', 'Rabi (Winter)', 'Zaid (Summer)']
SOIL_TYPES = ['Alluvial', 'Black', 'Red', 'Laterite', 'Arid', 'Mountain']

# Helper to generate dates
def generate_dates(start_date, num_days):
    return [start_date + timedelta(days=i) for i in range(num_days)]

# 1. Crop Disease Dataset
def generate_crop_disease(n=1000):
    diseases = {
        'Rice': [('Blast', 'Leaves', 'Fungicide A', 'Neem Oil'), ('Brown Spot', 'Leaves', 'Fungicide B', 'Cow Urine Extract')],
        'Wheat': [('Rust', 'Stem', 'Fungicide C', 'Garlic Extract'), ('Smut', 'Grain', 'Fungicide D', 'Seed Treatment')],
        'Tomato': [('Late Blight', 'Leaves/Fruit', 'Fungicide E', 'Copper Spray'), ('Leaf Curl', 'Leaves', 'Insecticide A', 'Neem Oil')],
        'Potato': [('Early Blight', 'Leaves', 'Fungicide F', 'Baking Soda Spray'), ('Scab', 'Tuber', 'Soil Fungicide', 'Crop Rotation')],
        'Cotton': [('Boll Rot', 'Boll', 'Fungicide G', 'Proper Spacing'), ('Wilt', 'Roots/Stem', 'Fungicide H', 'Trichoderma')],
        # Fallbacks:
        'Maize': [('Leaf Blight', 'Leaves', 'Fungicide I', 'Neem Extract')],
        'Sugarcane': [('Red Rot', 'Stem', 'Fungicide J', 'Hot Water Treatment')],
        'Soybean': [('Rust', 'Leaves', 'Fungicide K', 'Organic Fungicide')],
        'Barley': [('Powdery Mildew', 'Leaves', 'Fungicide L', 'Sulfur Spray')],
        'Millet': [('Downy Mildew', 'Leaves', 'Fungicide M', 'Neem Array')]
    }
    
    data = []
    for _ in range(n):
        crop = random.choice(CROPS)
        disease_info = random.choice(diseases.get(crop, diseases['Rice']))
        
        data.append({
            'Crop Name': crop,
            'Disease Name': disease_info[0],
            'Symptoms': f"Yellowing or spotting on {disease_info[1].lower()}",
            'Affected Plant Part': disease_info[1],
            'Severity Level': random.choice(['Low', 'Medium', 'High', 'Severe']),
            'Recommended Treatment': disease_info[2],
            'Pesticide Name': f"{disease_info[2]} Brand",
            'Organic Treatment': disease_info[3],
            'Region': random.choice(REGIONS),
            'Season': random.choice(SEASONS)
        })
    return pd.DataFrame(data)

# 2. Soil Health Dataset
def generate_soil_health(n=1000):
    data = []
    for _ in range(n):
        soil = random.choice(SOIL_TYPES)
        N = np.random.uniform(10, 150)
        P = np.random.uniform(5, 80)
        K = np.random.uniform(10, 200)
        pH = np.random.uniform(4.5, 8.5)
        
        data.append({
            'Soil Type': soil,
            'Nitrogen (N)': round(N, 2),
            'Phosphorus (P)': round(P, 2),
            'Potassium (K)': round(K, 2),
            'pH Level': round(pH, 2),
            'Moisture Level': round(np.random.uniform(10, 60), 2),
            'Organic Matter': round(np.random.uniform(0.5, 5.0), 2),
            'Suitable Crops': ", ".join(random.sample(CROPS, k=random.randint(1, 4))),
            'Fertilizer Recommendation': 'Urea' if N < 50 else ('DAP' if P < 30 else 'MOP'),
            'Region': random.choice(REGIONS)
        })
    return pd.DataFrame(data)

# 3. Weather Dataset
def generate_weather(n=1000):
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=random.randint(0, 365*2)) for _ in range(n)]
    
    data = []
    for date in dates:
        month = date.month
        season = 'Rabi (Winter)' if month in [11, 12, 1, 2] else ('Zaid (Summer)' if month in [3, 4, 5, 6] else 'Kharif (Monsoon)')
        
        # Adjust temp based on season
        if season == 'Rabi (Winter)':
            temp = np.random.uniform(5, 25)
        elif season == 'Zaid (Summer)':
            temp = np.random.uniform(25, 45)
        else:
            temp = np.random.uniform(20, 35)
            
        rain = np.random.uniform(0, 50) if season == 'Kharif (Monsoon)' else np.random.uniform(0, 10)
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Temperature (°C)': round(temp, 2),
            'Humidity (%)': round(np.random.uniform(30, 90), 2),
            'Rainfall (mm)': round(rain, 2),
            'Wind Speed': round(np.random.uniform(0, 20), 2),
            'Solar Radiation': round(np.random.uniform(100, 300), 2),
            'Region': random.choice(REGIONS),
            'Season': season
        })
    return pd.DataFrame(data)

# 4. Crop Recommendation Dataset
def generate_crop_recommendation(n=1000):
    data = []
    for _ in range(n):
        crop = random.choice(CROPS)
        
        # Create some reasonable correlations between crop and env
        if crop in ['Rice', 'Sugarcane']:
            rain = np.random.uniform(100, 300)
            hum = np.random.uniform(70, 90)
            temp = np.random.uniform(20, 30)
        elif crop in ['Wheat', 'Barley']:
            rain = np.random.uniform(30, 80)
            hum = np.random.uniform(40, 60)
            temp = np.random.uniform(10, 25)
        elif crop in ['Cotton']:
            rain = np.random.uniform(50, 100)
            hum = np.random.uniform(50, 70)
            temp = np.random.uniform(25, 35)
        else:
            rain = np.random.uniform(50, 150)
            hum = np.random.uniform(50, 80)
            temp = np.random.uniform(15, 30)
            
        data.append({
            'Soil Type': random.choice(SOIL_TYPES),
            'Temperature': round(temp, 2),
            'Humidity': round(hum, 2),
            'Rainfall': round(rain, 2),
            'pH Level': round(np.random.uniform(5.5, 7.5), 2),
            'Recommended Crop': crop,
            'Season': random.choice(SEASONS),
            'Expected Yield': f"{round(np.random.uniform(2, 6), 2)} tons/ha"
        })
    return pd.DataFrame(data)

# 5. Fertilizer Recommendation Dataset
def generate_fertilizer_recommendation(n=1000):
    data = []
    for _ in range(n):
        crop = random.choice(CROPS)
        N = np.random.uniform(0, 150)
        P = np.random.uniform(0, 80)
        K = np.random.uniform(0, 200)
        
        if N < 50:
            rec_fert = 'Urea'
        elif P < 20:
            rec_fert = 'DAP'
        elif K < 40:
            rec_fert = 'MOP'
        else:
            rec_fert = 'NPK Complex'
            
        data.append({
            'Crop Name': crop,
            'Soil Nitrogen': round(N, 2),
            'Soil Phosphorus': round(P, 2),
            'Soil Potassium': round(K, 2),
            'Recommended Fertilizer': rec_fert,
            'Application Amount': f"{random.randint(50, 200)} kg/ha",
            'Application Stage': random.choice(['Basal (At sowing)', 'Top Dressing (Vegetative stage)', 'Pre-flowering'])
        })
    return pd.DataFrame(data)

def main():
    print("Generating datasets...")
    df_disease = generate_crop_disease(1005)
    df_soil = generate_soil_health(1010)
    df_weather = generate_weather(1015)
    df_crop_rec = generate_crop_recommendation(1020)
    df_fert_rec = generate_fertilizer_recommendation(1025)
    
    output_file = 'd:/tamilarasu/project/agricultural_datasets.xlsx'
    
    print("Saving to Excel...")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_disease.to_excel(writer, sheet_name='Crop_Disease', index=False)
        df_soil.to_excel(writer, sheet_name='Soil_Health', index=False)
        df_weather.to_excel(writer, sheet_name='Weather', index=False)
        df_crop_rec.to_excel(writer, sheet_name='Crop_Recommendation', index=False)
        df_fert_rec.to_excel(writer, sheet_name='Fert_Recommendation', index=False)
        
    print(f"Successfully saved all datasets to {output_file}")

if __name__ == '__main__':
    main()
