from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import db_helper
import os
import json
import csv

# Paths for Models and Datasets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'disease_model.pth')
DATASET_PATH = os.path.join(BASE_DIR, '..', 'disease_symptoms_dataset.csv')
CROP_JSON_PATH = os.path.join(BASE_DIR, '..', 'advanced_crop_datasets.json')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load Global Datasets for Chatbot
CROP_DATA = []
DISEASE_DATA = {}

def load_datasets():
    global CROP_DATA, DISEASE_DATA
    try:
        # Load Crop JSON
        if os.path.exists(CROP_JSON_PATH):
            with open(CROP_JSON_PATH, 'r') as f:
                CROP_DATA = json.load(f)
        
        # Load Disease CSV
        if os.path.exists(DATASET_PATH):
            with open(DATASET_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    DISEASE_DATA[row['Disease Name'].lower()] = row['Recommended Treatment']
        print("Datasets loaded successfully.")
    except Exception as e:
        print(f"Error loading datasets: {e}")

# Ensure DB exists on startup
db_helper.init_db()
load_datasets()

# Mock Database / Logic for Crop Recommendation
def get_crop_recommendation(n, p, k, ph):
    # Expanded logic for better recommendations
    if ph < 5.0:
        return "Tea" if k > 50 else "Blueberry"
    elif ph > 8.0:
        return "Barley" if n > 80 else "Date Palm"
    elif n > 120:
        return "Cotton" if p > 60 else "Sugar Cane"
    elif n < 40:
        return "Legumes (Beans)" if k > 40 else "Peanuts"
    elif p > 80:
        return "Grapes" if ph > 6.5 else "Apple"
    elif k > 100:
        return "Banana" if n > 100 else "Potato"
    elif k < 30:
        return "Spinach" if n > 60 else "Carrot"
    elif 6.0 <= ph <= 7.0:
        if n > 80: return "Wheat"
        if p > 50: return "Rice"
        return "Maize"
    else:
        return "Millets"

# AI Chat Logic
import random

def get_ai_response(message):
    message = message.lower()
    
    # 1. Check for Disease Knowledge (from CSV)
    for disease, treatment in DISEASE_DATA.items():
        if disease in message:
            return f"I found information on {disease.title()}: {treatment}"
            
    # 2. Check for Crop Knowledge (from JSON)
    for crop in CROP_DATA:
        if crop['name'].lower() in message:
            return f"{crop['name']} is a {crop['type']} grown in the {crop['season']} season. {crop['description']}"

    # Random variants for better interaction
    welcome_variants = [
        "Hello! I am AgriVistara AI. How can I help you today with your farming needs?",
        "Greetings! AgriVistara AI is here. What can I help you with today?",
        "Hi there! Welcome to AgriVistara. Need help with crops, soil, or market prices?"
    ]
    
    unknown_variants = [
        "That's interesting! Could you tell me more about your query? I specialize in crops, soil health, and market prices.",
        "I'm not quite sure about that. Could you rephrase your question? I'm better with farming-related topics.",
        "I'm still learning! Ask me about things like rice cultivation, tomato pests, or current market trends."
    ]

    # Rule-base pattern matching
    if any(word in message for word in ["hello", "hi", "hey"]):
        return random.choice(welcome_variants)
    
    # Modern Techniques
    elif "hydroponics" in message:
        return "Hydroponics allows growing crops without soil using nutrient-rich water. It's great for leafy greens like lettuce and spinach and uses 90% less water!"
    
    elif "drip" in message and "irrigation" in message:
        return "Drip irrigation is highly efficient. It delivers water directly to the plant's roots, reducing waste and weed growth. Highly recommended for orchards and vegetables."

    # General Farming Features
    elif "crop" in message and ("suggest" in message or "recommend" in message):
        return "I can help with crop recommendations! Please use the 'Analyze Soil' feature on your dashboard or tell me your soil N-P-K values."
    
    elif "price" in message or "market" in message:
        return "Market prices are currently active. You can check the 'Market' section for live updates on tomato, wheat, and rice prices."
    
    elif "weather" in message:
        return "Checking the sky... Currently, it's 28°C and sunny in your region. A great day for field work, but stay hydrated!"
    
    elif "help" in message or "support" in message:
        return "For immediate support, you can call us at +91 98765 43210 or email support@agrivistara.com."
    
    else:
        return random.choice(unknown_variants)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    user_message = data.get('message')
    target_lang = data.get('lang', 'en') # Get target language from frontend
    
    ai_response = get_ai_response(user_message)
    
    # Translate if target language is not English
    if target_lang != 'en':
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source='auto', target=target_lang).translate(ai_response)
            ai_response = translated
        except Exception as e:
            print(f"Translation Error: {e}")
            # Fallback to English if translation fails
    
    return jsonify({
        "status": "success",
        "response": ai_response
    })

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Helper function to safely convert to float
        def safe_float(val, default=0.0):
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        n = safe_float(data.get('N'), 0)
        p = safe_float(data.get('P'), 0)
        k = safe_float(data.get('K'), 0)
        ph = safe_float(data.get('ph'), 7)
        
        crop = get_crop_recommendation(n, p, k, ph)
        
        # Save to DB (App Data)
        user_phone = data.get('phone') # Optional, if provided
        db_helper.save_soil_test(user_phone, n, p, k, ph, crop)
        
        return jsonify({
            "status": "success",
            "recommended_crop": crop,
            "confidence": "85%"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/detect_disease', methods=['POST'])
def detect_disease():
    # Mock Detection Logic - Deterministic based on file content
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    # Generate a hash of the file content to pick a result deterministically
    import hashlib
    file_content = file.read()
    file_hash = int(hashlib.md5(file_content).hexdigest(), 16)
    
    # Reset file pointer if we were to save it (not saving here to keep simple)
    # file.seek(0)
    
    # Updated disease list including the 22 new categories
    # In a real scenario, this would be predicted by the .pth model
    diseases = [
        {"disease": "Leaf Blight", "treatment": "Use Fungicide X (Copper-based)"},
        {"disease": "Rust", "treatment": "Remove infected leaves immediately. Apply Sulfur dust."},
        {"disease": "Healthy", "treatment": "Keep monitoring, water regularly."},
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
        {"disease": "Tomato verticulium wilt", "treatment": "Improve soil drainage, plant resistant varieties."}
    ]
    
    # Use hash to pick a specific disease (Mock prediction)
    index = file_hash % len(diseases)
    result = diseases[index]
    result["confidence"] = 85 + (file_hash % 15) # confidence between 85-99
    
    return jsonify(result)

@app.route('/api/market_prices', methods=['GET'])
def market_prices():
    # Limit to latest 100 for performance
    data = db_helper.get_market_prices(limit=100)
    return jsonify(data)

@app.route('/api/download_market_data', methods=['GET'])
def download_market_data():
    """Generates a fresh CSV and serves it for download."""
    try:
        # Get ALL data for download
        import csv
        data = db_helper.get_market_prices()
        export_file = os.path.join(BASE_DIR, '..', 'market_prices_dataset.csv')
        
        if data:
            keys = data[0].keys()
            with open(export_file, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(data)
                
        return send_file(export_file, as_attachment=True, download_name='market_prices_dataset.csv')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sell_crop', methods=['POST'])
def sell_crop():
    data = request.json
    # data: {crop, price, market, phone}
    success = db_helper.add_market_item(data.get('crop'), data.get('price'), data.get('market'), data.get('phone'))
    if success:
        return jsonify({"message": "Listed for sale!"}), 200
    return jsonify({"error": "Failed to list item"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = db_helper.verify_user(data.get('phone'), data.get('password'))
    if user:
        return jsonify({"message": "Login Successful", "user": user}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    success = db_helper.register_user(data.get('phone'), data.get('password'), data.get('name'))
    if success:
        return jsonify({"message": "Registration Successful"}), 200
    return jsonify({"error": "User already exists or error"}), 400

@app.route('/api/weather', methods=['GET'])
def get_weather():
    import requests
    # REPLACE WITH YOUR OPENWEATHERMAP API KEY
    API_KEY = "8f5b804550186105ce3073d745585501" 
    
    city = request.args.get('city', 'Chennai') # Dynamic city support
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather = {
                "city": city,
                "temp": f"{int(data['main']['temp'])}°C",
                "condition": data['weather'][0]['main'],
                "humidity": f"{data['main']['humidity']}%",
                "forecast": [
                    {"day": "Today", "temp": f"{int(data['main']['temp'])}°C", "icon": "fa-sun"},
                    {"day": "Tomorrow", "temp": f"{int(data['main']['temp'])-1}°C", "icon": "fa-cloud-rain"},
                    {"day": "Day After", "temp": f"{int(data['main']['temp'])+1}°C", "icon": "fa-cloud-sun"}
                ]
            }
            return jsonify(weather)
        else:
             # Fallback if API fails
            return jsonify({
                "temp": "28°C", "condition": "Sunny (Mock)", "humidity": "60%",
                "forecast": [{"day": "Today", "temp": "28°C", "icon": "fa-sun"}]
            })
    except Exception as e:
        print(f"Weather API Error: {e}")
        return jsonify({
             "temp": "--°C", "condition": "Error", "humidity": "--%",
             "forecast": []
        })



@app.route('/')
def home():
    return jsonify({"message": "AgriVistara Backend is Running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
