from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
import os
import json
import csv
import random
import re
import hashlib
import datetime
from datetime import timedelta
import requests
import bcrypt
from diskcache import Cache
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from google import genai
import db_helper
import ai_prompt

try:
    import torch
    import torch.nn as nn
    from torchvision import transforms, models
    from PIL import Image
    import io
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from ai_prompt import MASTER_PROMPT

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# Google OAuth
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

# Paths for Models and Datasets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'disease_model.pth')
DATASET_PATH = os.path.join(BASE_DIR, '..', 'disease_symptoms_dataset.csv')
CROP_JSON_PATH = os.path.join(BASE_DIR, '..', 'advanced_crop_datasets.json')
GLOBAL_PRICES_PATH = os.path.join(BASE_DIR, '..', 'ProductPriceIndex.csv')

app = Flask(__name__, static_folder='../', static_url_path='/')
# Enable CORS for all routes
CORS(app, supports_credentials=True)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "agrivistara-super-secret-key-123")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
jwt = JWTManager(app)

# Initialize DiskCache for weather and market data
cache = Cache(os.path.join(BASE_DIR, 'agri_cache'))

# Validation Schemas
class LoginSchema(Schema):
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    password = fields.Str(required=True)

class RegisterSchema(Schema):
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    name = fields.Str(required=True, validate=validate.Length(min=2))
    email = fields.Email(required=True)

class ChatSchema(Schema):
    message = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    lang = fields.Str(load_default='en')

class RecommendSchema(Schema):
    N = fields.Float(required=True)
    P = fields.Float(required=True)
    K = fields.Float(required=True)
    ph = fields.Float(required=True, validate=validate.Range(min=0, max=14))
    acres = fields.Float(load_default=1.0)

@app.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    return jsonify({"status": "error", "message": "Input validation failed", "errors": e.messages}), 400

# Load Global Datasets for Chatbot
CROP_DATA = []
DISEASE_DATA = {}
OTP_STORAGE = {} # Temporary storage for OTPs: {phone: otp}

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

# Expanded Crop Recommendation with scoring
CROP_RULES = [
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


# AI Chat Logic
import random

LANG_FULL_NAMES = {
    'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
    'ml': 'Malayalam', 'kn': 'Kannada', 'gu': 'Gujarati', 'mr': 'Marathi',
    'bn': 'Bengali', 'pa': 'Punjabi', 'or': 'Odia', 'as': 'Assamese',
    'ur': 'Urdu', 'sa': 'Sanskrit', 'fr': 'French', 'de': 'German',
    'es': 'Spanish', 'pt': 'Portuguese', 'ar': 'Arabic',
    'zh': 'Chinese', 'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Traditional)',
    'ja': 'Japanese', 'ko': 'Korean', 'ru': 'Russian', 'it': 'Italian',
    'tr': 'Turkish', 'vi': 'Vietnamese', 'th': 'Thai', 'id': 'Indonesian',
    'ms': 'Malay', 'sw': 'Swahili'
}

def get_ai_response(message, target_lang='en'):
    message_lower = message.lower()

    # Normalise compound codes the frontend may send (e.g. 'zh-CN' → keep, verify in map)
    # LANG_FULL_NAMES covers both 'zh' and 'zh-CN' so this lookup is safe.
    lang_name = LANG_FULL_NAMES.get(target_lang, 'English')
    if target_lang != 'en':
        lang_instruction = f"\n\n⚠️ IMPORTANT: You MUST reply entirely in {lang_name}. Do not use English in your response."
    else:
        lang_instruction = ""


    # Removed static greeting logic so Gemini generates natural, unique greetings

    # AI Generation Logic
    openai_api_key = os.getenv('OPENAI_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    context = ""
    
    # 1. High-Efficiency Local Native Dataset Search (RAG)
    try:
        import rag_helper
        rag_context = rag_helper.search_knowledge_base(message_lower)
        if rag_context:
            context += f"\n\n{rag_context}\n"
    except Exception as e:
        print(f"RAG Integration Error: {e}")

    if "price" in message_lower or "market" in message_lower:
        try:
            prices = db_helper.get_market_prices(limit=5)
            if prices:
                context = "\n\nLive Market Data (Reference this if asked for prices):\n"
                for p in prices[:5]:
                    context += f"- {p['crop']}: ₹{p['price']:.2f} at {p['market']}\n"
        except Exception:
            pass
            
    if "weather" in message_lower:
        try:
            import requests as http_requests
            W_API_KEY = os.getenv('WEATHER_API_KEY', '')
            if W_API_KEY:
                city = "Chennai"
                for c in ["chennai", "salem", "coimbatore", "madurai", "bangalore", "delhi", "mumbai"]:
                    if c in message_lower:
                        city = c.title()
                        break
                resp = http_requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={W_API_KEY}&units=metric", timeout=2)
                if resp.status_code == 200:
                    data = resp.json()
                    weather_str = f"\n\nLive Weather Data for {city}: {int(data['main']['temp'])}°C, {data['weather'][0]['main']}, Humidity {data['main']['humidity']}%."
                    context += str(weather_str)
        except Exception:
            pass

    # Build full prompt with language instruction appended
    full_prompt = f"User Query: {message}\n{context}{lang_instruction}"

    if openai_api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": MASTER_PROMPT},
                    {"role": "user", "content": full_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            open_ai_error = str(e)
            print(f"OpenAI API Error: {open_ai_error}")
            if "insufficient_quota" in open_ai_error or "429" in open_ai_error:
                openai_api_key = None # Move on to Gemini

    if gemini_api_key:
        try:
            client = genai.Client(api_key=gemini_api_key)
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=MASTER_PROMPT
                    )
                )
            except Exception as model_err:
                print(f"Gemini 2.5 Flash error: {model_err}. Falling back to Gemini 2.0 Flash...")
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=MASTER_PROMPT
                    )
                )
            result_text = response.text
            return result_text

        except Exception as e:
            err_str = str(e).lower()
            print(f"Gemini API Error: {err_str}")
            if "429" in err_str or "exhausted" in err_str or "quota" in err_str:
                return "⚠️ **API Quota Exceeded**: Your Gemini (and OpenAI) API keys have hit their rate limits or daily free tier limits. Please wait a while or check your billing dashboard."
            if "503" in err_str or "unavailable" in err_str:
                return "⚠️ **Service Overloaded**: Google's Gemini AI is currently experiencing exceptionally high demand globally. Please try again in a few minutes."
            
            return f"⚠️ **AI Error**: Could not generate response. Error: {str(e)[:100]}"
    
    # Fallback if no API key or API completely fails to init
    unknown_variants = [
        "That's interesting! Could you tell me more about your query? I specialize in crops, soil health, and market pricing.",
        "I'm not quite sure about that. Could you rephrase your question? I'm better with farming-related topics.",
        "I'm still learning! Ask me about things like rice cultivation, tomato pests, or current market trends."
    ]
    return random.choice(unknown_variants)

@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    json_data = request.get_json()
    data = ChatSchema().load(json_data)
    
    user_message = data.get('message')
    target_lang = data.get('lang', 'en')
    
    # Pass target_lang so Gemini is instructed to reply in the correct language directly
    ai_response = get_ai_response(user_message, target_lang)
    
    # Determine if this is a fallback response
    unknown_variants = [
        "That's interesting! Could you tell me more about your query?",
        "I'm not quite sure about that.",
        "I'm still learning!"
    ]
    is_fallback = any(v in ai_response for v in unknown_variants)
    suggestions = []
    if is_fallback:
        suggestions = ["🌾 Crop advice", "💰 Market prices", "🐛 Pest control", "☁ Weather", "📋 Govt schemes", "🧪 Soil test"]
    
    # Gemini is already instructed to reply in the target language — no extra translation needed.
            
    # Log Activity
    user_phone = get_jwt_identity()
    db_helper.log_user_activity(user_phone, "Chatbot Query", f"Asked AI: '{user_message[:50]}...' [{target_lang}]")
    
    return jsonify({
        "status": "success",
        "response": ai_response,
        "suggestions": suggestions,
        "lang": target_lang
    })


@app.route('/api/user/profile', methods=['POST'])
@jwt_required()
def update_profile():
    user_phone = get_jwt_identity()
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    
    if not name:
        return jsonify({"error": "Name is required"}), 400
        
    try:
        conn = db_helper.get_db_connection()
        conn.execute('UPDATE users SET name = ?, email = ? WHERE phone = ?', (name, email, user_phone))
        conn.commit()
        conn.close()
        
        db_helper.log_user_activity(user_phone, "Profile Update", "Updated personal profile information")
        return jsonify({"message": "Profile updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/change_password', methods=['POST'])
@jwt_required()
def change_password_route():
    user_phone = get_jwt_identity()
    data = request.get_json()
    
    current_pw = data.get('current_password')
    new_pw = data.get('new_password')
    
    if not current_pw or not new_pw:
        return jsonify({"error": "Current and new passwords required"}), 400
        
    user = db_helper.verify_user(user_phone, current_pw)
    if not user:
        return jsonify({"error": "Incorrect current password"}), 401
    
    try:
        hashed = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = db_helper.get_db_connection()
        conn.execute('UPDATE users SET password = ? WHERE phone = ?', (hashed, user_phone))
        conn.commit()
        conn.close()
        
        db_helper.log_user_activity(user_phone, "Security", "Changed account password")
        return jsonify({"message": "Password updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send_otp', methods=['POST'])
def send_otp():
    data = request.json
    phone = data.get('phone')
    if not phone:
        return jsonify({"error": "Phone number required"}), 400
    
    # Generate a simple 4-digit OTP
    otp = str(random.randint(1000, 9999))
    OTP_STORAGE[phone] = otp
    
    # In a real app, you'd send this via SMS. For now, we print it to console.
    print(f"--- [OTP for {phone}]: {otp} ---")
    
    return jsonify({"message": "OTP sent successfully!", "otp_mock": otp}), 200

@app.route('/api/send_email_otp', methods=['POST'])
def send_email_otp():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))
    OTP_STORAGE[email] = otp
    
    # In a real app we'd send an email here
    print(f"--- [EMAIL OTP for {email}]: {otp} ---")
    
    return jsonify({"message": "OTP sent to email successfully!", "otp_mock": otp}), 200

@app.route('/api/verify_email_otp', methods=['POST'])
def verify_email_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({"error": "Email and OTP required"}), 400
        
    if OTP_STORAGE.get(email) == otp:
        return jsonify({"message": "OTP verified successfully!"}), 200
    
    return jsonify({"error": "Invalid OTP"}), 400

@app.route('/api/recommend', methods=['POST'])
@jwt_required()
def recommend():
    try:
        json_data = request.get_json()
        data = RecommendSchema().load(json_data)
        
        n = data.get('N')
        p = data.get('P')
        k = data.get('K')
        ph = data.get('ph')
        acres = data.get('acres', 1.0)
        
        top_crops = get_crop_recommendation(n, p, k, ph)
        top_crop = top_crops[0] if top_crops else {"name": "Millets", "confidence": 50, "target_n": 24, "target_p": 12, "target_k": 12}
        
        # Calculate Fertilizer Prescription
        fertilizer_plan = calculate_stcr_fertilizer(n, p, k, top_crop.get("target_n", 0), top_crop.get("target_p", 0), top_crop.get("target_k", 0), acres)
        
        # --- Dataset-backed insights (from ingested agricultural_datasets.xlsx) ---
        dataset_insights = []
        try:
            fert_matches = db_helper.get_fertilizer_recommendations_from_dataset(
                crop=top_crop['name'].split('(')[0].strip(), n=n, p=p, k=k, limit=3
            )
            for fm in fert_matches:
                dataset_insights.append({
                    "fertilizer": fm.get('Recommended Fertilizer', ''),
                    "amount": fm.get('Application Amount', ''),
                    "stage": fm.get('Application Stage', '')
                })
        except Exception as ds_err:
            print(f"Dataset insight error: {ds_err}")
        
        # Save to DB (App Data)
        user_phone = get_jwt_identity() # Use identity from JWT
        db_helper.save_soil_test(user_phone, n, p, k, ph, top_crop['name'])
        
        # Log Activity
        db_helper.log_user_activity(user_phone, "Soil Test", f"Received recommendation for {top_crop['name']} ({acres} acres)")
        
        return jsonify({
            "status": "success",
            "recommended_crop": top_crop['name'],
            "confidence": f"{top_crop['confidence']}%",
            "season": top_crop.get('season', ''),
            "tip": top_crop.get('tip', ''),
            "alternatives": top_crops[1:] if len(top_crops) > 1 else [],
            "fertilizer_plan": fertilizer_plan,
            "dataset_insights": dataset_insights
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/recent_soil_test', methods=['GET'])
@jwt_required()
def recent_soil_test():
    user_phone = get_jwt_identity()
    test = db_helper.get_recent_soil_test(user_phone)
    return jsonify(test)

# =============================================
# HYBRID AI DISEASE DETECTION (Gemini + Local PyTorch)
# =============================================

MODEL_WEIGHTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'disease_model.pth')
CLASS_NAMES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'class_names.json')

def get_local_ml_prediction(image_bytes):
    """Runs inference on the local MobileNetV2 model trained on the provided datasets."""
    if not TORCH_AVAILABLE or not os.path.exists(MODEL_WEIGHTS_PATH) or not os.path.exists(CLASS_NAMES_PATH):
        return None
        
    try:
        with open(CLASS_NAMES_PATH, 'r') as f:
            id_to_class = json.load(f)
            
        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = nn.Linear(model.last_channel, len(id_to_class))
        model.load_state_dict(torch.load(MODEL_WEIGHTS_PATH, map_location=torch.device('cpu'), weights_only=True))
        model.eval()
        
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        tensor = transform(img).unsqueeze(0)
        
        with torch.no_grad():
            outputs = model(tensor)
            probabilities = nn.functional.softmax(outputs[0], dim=0)
            confidence, predicted = torch.max(probabilities, 0)
            
            class_id = str(predicted.item())
            disease_name = id_to_class.get(class_id, "Unknown")
            conf_percent = int(round(confidence.item() * 100))
            
            # Use deterministic treatment mapping for local model
            treatment = "Treatment recommendation: Please consult local agricultural guidelines."
            return {
                "disease": disease_name,
                "confidence": conf_percent,
                "treatment": treatment
            }
    except Exception as e:
        print(f"Local ML Inference failed: {e}")
        return None


@app.route('/api/detect_disease', methods=['POST'])
@jwt_required()
def detect_disease():
    """Hybrid AI-powered crop disease detection using both Gemini Vision and PyTorch local dataset model."""
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    file_content = file.read()
    
    # 1. Get Local ML Prediction (Offline Model trained on dataset)
    local_result = get_local_ml_prediction(file_content)

    # 52 EXACT categories from for Option A (Gemini Vision)
    DISEASE_CATEGORIES = [
        "Cashew anthracnose", "Cashew gumosis", "Cashew healthy", "Cashew leaf miner", "Cashew red rust",
        "Cassava bacterial blight", "Cassava brown spot", "Cassava green mite", "Cassava healthy", "Cassava mosaic",
        "Maize fall armyworm", "Maize grasshopper", "Maize healthy", "Maize leaf beetle", "Maize leaf blight", "Maize leaf spot", "Maize streak virus",
        "Tomato healthy", "Tomato leaf blight", "Tomato leaf curl", "Tomato septoria leaf spot", "Tomato verticillium wilt",
        "Rice Bacterial Blight", "Rice Brownspot", "Rice Blast", "Rice Tungro", "Rice Healthy",
        "Sugarcane Mosaic", "Sugarcane RedRot", "Sugarcane RedRust", "Sugarcane Healthy", "Sugarcane Yellow Rust",
        "Wheat Brown Rust", "Wheat Stem fly", "Wheat aphid", "Wheat black rust", "Wheat leaf blight", "Wheat mite", "Wheat powdery mildew", "Wheat scab", "Wheat Yellow Rust", "Wheat Healthy",
        "Cotton American Bollworm", "Cotton Anthracnose", "Cotton Army worm", "Cotton Aphid", "Cotton Healthy", "Cotton Leaf Curl", "Cotton Wilt", "Cotton Mealy bug", "Cotton whitefly", "Cotton thrips"
    ]

    # 2. OPTION A: Combine with Gemini Vision AI (if online)
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            ext = os.path.splitext(file.filename)[1].lower()
            mime_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
                        '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp'}
            mime_type = mime_map.get(ext, 'image/jpeg')
            
            vision_prompt = f"""You are an expert agricultural plant pathologist AI. Analyze this crop/plant leaf image carefully.

Classify the disease into EXACTLY ONE of these categories from our training dataset:
{", ".join(DISEASE_CATEGORIES)}

If the plant looks healthy, pick the matching "Healthy" category for that crop.
If you cannot determine the crop type, pick the closest matching category.

Respond in ONLY this exact JSON format, nothing else:
{{"disease": "<exact category name>", "confidence": <number 70-99>, "treatment": "<2-3 sentence treatment recommendation>"}}"""
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    genai.types.Part.from_bytes(data=file_content, mime_type=mime_type),
                    vision_prompt
                ]
            )
            
            ai_text = response.text.strip()
            if '```json' in ai_text:
                ai_text = ai_text.split('```json')[1].split('```')[0].strip()
            elif '```' in ai_text:
                ai_text = ai_text.split('```')[1].split('```')[0].strip()
            
            gemini_result = json.loads(ai_text)
            gemini_result.setdefault('disease', 'Unknown')
            gemini_result.setdefault('confidence', 85)
            gemini_result.setdefault('treatment', 'Consult an agricultural expert for treatment.')
            
            payload = {
                "ai_powered": True,
                "offline_mode": False,
                "gemini": gemini_result,
                "local_model": local_result  # May be None if local model fails
            }
            
            db_helper.log_user_activity(get_jwt_identity(), "Disease Scan (Hybrid)", f"Gemini: {gemini_result['disease']}")
            return jsonify(payload)
            
        except Exception as e:
            print(f"Gemini Vision Error: {e}")
            # Fall through to offline handling
    
    # 3. OFFLINE HANDLING: Return Local PyTorch Model Prediction
    if local_result:
        payload = {
            "ai_powered": False,
            "offline_mode": True,
            "local_model": local_result
        }
        db_helper.log_user_activity(get_jwt_identity(), "Disease Scan (Offline ML)", f"Local: {local_result['disease']}")
        return jsonify(payload)
    
    # 4. LAST RESORT FALLBACK: If both Gemini AND Local ML fail (e.g., PyTorch isn't installed yet)
    file_hash = int(hashlib.md5(file_content).hexdigest(), 16)
    diseases_fallback = [
        {"disease": "Leaf Blight", "treatment": "Use Fungicide X (Copper-based)"},
        {"disease": "Rust", "treatment": "Remove infected leaves immediately. Apply Sulfur dust."},
        {"disease": "Healthy", "treatment": "Keep monitoring, water regularly."}
    ]
    index = file_hash % len(diseases_fallback)
    result = dict(diseases_fallback[index])
    result["confidence"] = 85 + (file_hash % 15)
    
    payload = {
        "ai_powered": False,
        "offline_mode": True,
        "local_model": result # Wrap in local_model format to keep frontend simple
    }
    return jsonify(payload)


# =============================================
# DATASET STATS ENDPOINT
# =============================================

@app.route('/api/dataset_stats', methods=['GET'])
@jwt_required()
def dataset_stats():
    """Returns counts from all integrated datasets."""
    stats = db_helper.get_dataset_stats()
    stats['disease_categories'] = 62  # Total disease categories from image datasets
    stats['global_price_index_file'] = os.path.exists(GLOBAL_PRICES_PATH)
    stats['disease_symptoms_file'] = os.path.exists(DATASET_PATH)
    return jsonify(stats)


# --- Translate API (Multilingual Support) ---
@app.route('/api/translate', methods=['POST'])
@jwt_required()
def translate_text():
    """Translate a batch of text strings efficiently using caching and batching."""
    data = request.get_json()
    texts = data.get('texts', [])
    target = data.get('lang', 'en')

    if not texts:
        return jsonify({"translations": []}), 200

    if target == 'en':
        return jsonify({"translations": texts})

    try:
        translated_map = {}
        to_translate = []
        original_indices = []

        # 1. Check Cache first
        for i, text in enumerate(texts):
            if not text or not text.strip():
                translated_map[i] = text
                continue
            
            cache_key = f"trans_{target}_{hashlib.md5(text.encode('utf-8')).hexdigest()}"
            cached_val = cache.get(cache_key)
            if cached_val:
                translated_map[i] = cached_val
            else:
                to_translate.append(text)
                original_indices.append(i)

        # 2. Translate missing strings in batch
        if to_translate:
            # Batch size limit for deep-translator common practice
            batch_size = 50 
            all_new_translations = []
            
            translator = GoogleTranslator(source='auto', target=target)
            
            for i in range(0, len(to_translate), batch_size):
                chunk = to_translate[i:i + batch_size]
                try:
                    # translate_batch is much faster than individual translate calls
                    results = translator.translate_batch(chunk)
                    all_new_translations.extend(results)
                except Exception as batch_error:
                    print(f"Batch Translation Error: {batch_error}")
                    # Fallback to individual for this chunk if batch fails
                    for item in chunk:
                        try:
                            all_new_translations.append(translator.translate(item))
                        except:
                            all_new_translations.append(item)

            # 3. Update Cache and Mapping
            for i, result in enumerate(all_new_translations):
                orig_idx = original_indices[i]
                orig_text = to_translate[i]
                translated_map[orig_idx] = result
                
                cache_key = f"trans_{target}_{hashlib.md5(orig_text.encode('utf-8')).hexdigest()}"
                cache.set(cache_key, result, expire=604800) # Cache for 1 week

        # 4. Final collection in original order
        final_translations = [translated_map[i] for i in range(len(texts))]
        return jsonify({"translations": final_translations})

    except Exception as e:
        print(f"Global Translation Error: {e}")
        return jsonify({"translations": texts, "error": str(e)}), 200


@app.route('/api/market_prices', methods=['GET'])
@jwt_required()
def market_prices():
    # Cache market data for 10 minutes
    cached_data = cache.get('market_prices')
    if cached_data:
        return jsonify(cached_data)
        
    data = db_helper.get_market_prices(limit=100)
    cache.set('market_prices', data, expire=600)
    return jsonify(data)

@app.route('/api/download_market_data', methods=['GET'])
@jwt_required()
def download_market_data():
    """Generates a fresh CSV and serves it structured as a market matrix."""
    try:
        matrix = db_helper.get_market_matrix()
        export_file = os.path.join(BASE_DIR, '..', 'Market_Price_Matrix.csv')
        
        markets = matrix.get("markets", [])
        vegetables = matrix.get("vegetables", [])
        data_dict = matrix.get("data", {})
        
        with open(export_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write Header
            header = ["Vegetable"] + markets
            writer.writerow(header)
            
            # Write rows for each vegetable
            for veg in vegetables:
                row = [veg]
                for mkt in markets:
                    cell = data_dict.get(veg, {}).get(mkt)
                    price = cell.get("price", "") if cell else ""
                    row.append(price)
                writer.writerow(row)
                
        return send_file(export_file, as_attachment=True, download_name='Market_Price_Matrix.csv')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sell_crop', methods=['POST'])
@jwt_required()
def sell_crop():
    data = request.json
    # data: {crop, price, market}
    crop = data.get('crop')
    price = data.get('price')
    market = data.get('market')
    phone = get_jwt_identity()
    
    success = db_helper.add_market_item(crop, price, market, phone)
    if success:
        cache.delete('market_matrix')
        # Log Activity
        db_helper.log_user_activity(phone, "Market Listing", f"Listed {crop} for ₹{price} at {market}")
        return jsonify({"message": "Listed for sale!"}), 200
    return jsonify({"error": "Failed to list item"}), 500


# =============================================
# GLOBAL PRICE INDEX ENDPOINT
# =============================================

@app.route('/api/global_prices', methods=['GET'])
@jwt_required()
def get_global_prices():
    """Reads the massive ProductPriceIndex.csv to extract global market trends and average spreads."""
    cached = cache.get('global_price_index')
    if cached:
        return jsonify(cached)
        
    try:
        if not os.path.exists(GLOBAL_PRICES_PATH):
            return jsonify({"error": "Global Price Index dataset missing."}), 404
            
        aggregates = {}
        with open(GLOBAL_PRICES_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prod = row.get('productname')
                if not prod: continue
                
                # Parse numeric values by stripping $ and % symbols
                try:
                    farm = float(row.get('farmprice', '0').replace('$', '').replace(',', ''))
                    ny = float(row.get('newyorkretail', '0').replace('$', '').replace(',', ''))
                    spread = float(row.get('averagespread', '0').replace('%', '').replace(',', ''))
                except ValueError:
                    continue
                    
                if prod not in aggregates:
                    aggregates[prod] = {'count': 0, 'farm_total': 0, 'ny_total': 0, 'spread_total': 0}
                    
                aggregates[prod]['count'] += 1
                aggregates[prod]['farm_total'] += farm
                aggregates[prod]['ny_total'] += ny
                aggregates[prod]['spread_total'] += spread
                
        # Calculate averages for top 10 products
        results = []
        for prod, data in aggregates.items():
            if data['count'] > 0:
                results.append({
                    "product": prod,
                    "avg_farm_price_usd": round(data['farm_total'] / data['count'], 2),
                    "avg_retail_price_usd": round(data['ny_total'] / data['count'], 2),
                    "avg_margin_percent": round(data['spread_total'] / data['count'], 2),
                    "data_points": data['count']
                })
                
        # Sort by most data points to show most reliable commodities first
        results.sort(key=lambda x: x['data_points'], reverse=True)
        top_results = results[:12]
        
        # Cache this heavy calculation for 24 hours
        cache.set('global_price_index', top_results, expire=86400)
        return jsonify(top_results)
        
    except Exception as e:
        print(f"Error reading ProductPriceIndex: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================
# MARKET PRICE MATRIX ENDPOINTS
# =============================================

@app.route('/api/market_matrix', methods=['GET'])
@jwt_required()
def get_market_matrix():
    """Returns the full vegetable × market price matrix."""
    cached = cache.get('market_matrix')
    if cached:
        return jsonify(cached)
    
    data = db_helper.get_market_matrix()
    cache.set('market_matrix', data, expire=300)
    return jsonify(data)


@app.route('/api/market_matrix/vegetables', methods=['GET'])
@jwt_required()
def get_matrix_vegetables():
    """Returns list of all vegetable names for dropdown."""
    vegetables = db_helper.get_all_vegetables()
    return jsonify(vegetables)

@app.route('/api/market_matrix/spreads', methods=['GET'])
@jwt_required()
def get_matrix_spreads():
    return jsonify(db_helper.get_market_spreads())


@app.route('/api/market_matrix/markets', methods=['GET'])
@jwt_required()
def get_matrix_markets():
    """Returns list of all market names for dropdown."""
    markets = db_helper.get_all_markets()
    return jsonify(markets)


@app.route('/api/market_matrix/upsert', methods=['POST'])
@jwt_required()
def upsert_market_price():
    """Upsert a single cell in the vegetable × market matrix."""
    data = request.get_json()
    vegetable = data.get('vegetable', '').strip()
    market = data.get('market', '').strip()
    price = data.get('price')
    
    if not vegetable:
        return jsonify({"error": "Vegetable name is required"}), 400
    if not market:
        return jsonify({"error": "Market name is required"}), 400
    if price is None or price == '':
        return jsonify({"error": "Price is required"}), 400
    
    try:
        price = float(price)
        if price < 0:
            return jsonify({"error": "Price cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid price value"}), 400
    
    phone = get_jwt_identity()
    result = db_helper.upsert_market_price(vegetable, market, price, phone)
    
    if result.get('success'):
        # Clear caches
        cache.delete('market_matrix')
        cache.delete('market_prices')
        
        # Log Activity
        action_msg = {
            'updated': f"Updated {vegetable} price to ₹{price} at {market}",
            'new_vegetable': f"Added new vegetable {vegetable} with ₹{price} at {market}",
            'new_market': f"Added new market {market} with {vegetable} at ₹{price}",
            'new_both': f"Added new entry: {vegetable} at {market} for ₹{price}"
        }
        db_helper.log_user_activity(phone, "Market Price Update", action_msg.get(result['action'], ''))
        
        return jsonify({
            "message": "Price updated successfully!",
            "action": result['action'],
            "vegetable": result['vegetable'],
            "market": result['market'],
            "price": result['price']
        }), 200
    
    return jsonify({"error": result.get('error', 'Failed to update price')}), 500


@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    import datetime
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    notifications = [
        {"id": 1, "title": "PM-KISAN Update", "message": "14th installment of PM-KISAN will be released next week. Ensure KYC is updated.", "date": today, "type": "info"},
        {"id": 2, "title": "Market Alert", "message": "Tomato prices have surged by 15% in your nearby mandis today.", "date": today, "type": "success"},
        {"id": 3, "title": "Advisory", "message": "Apply the second dose of Urea to your Rice crop this week based on your sowing date.", "date": today, "type": "warning"}
    ]
    return jsonify(notifications)

@app.route('/api/weather', methods=['GET'])
@jwt_required(optional=True)
def get_weather():
    API_KEY = os.getenv('WEATHER_API_KEY', '')
    
    city = request.args.get('city', 'Chennai')
    
    CITY_COORDS = {
        "Chennai": (13.0827, 80.2707),
        "Salem": (11.6643, 78.1460),
        "Coimbatore": (11.0168, 76.9558),
        "Madurai": (9.9252, 78.1198),
        "Bangalore": (12.9716, 77.5946),
        "Delhi": (28.7041, 77.1025),
        "Mumbai": (19.0760, 72.8777)
    }
    
    # Cache weather for 15 minutes
    cache_key = f"weather_{city}"
    cached_weather = cache.get(cache_key)
    if cached_weather:
        return jsonify(cached_weather)

    lat, lng = CITY_COORDS.get(city.title(), CITY_COORDS["Chennai"])

    try:
        url = f"https://api.stormglass.io/v2/weather/point?lat={lat}&lng={lng}&params=airTemperature,humidity,windSpeed,cloudCover,precipitation"
        headers = {"Authorization": API_KEY}
        
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            data = response.json()
            hours = data.get('hours', [])
            
            if not hours:
                return get_mock_weather(city)
                
            current = hours[0]
            
            # Extract current data using 'sg' model prioritizing it
            def get_val(item, key):
                return item.get(key, {}).get('sg', 0)
                
            temp = int(get_val(current, 'airTemperature'))
            humidity = int(get_val(current, 'humidity'))
            wind_ms = get_val(current, 'windSpeed')
            wind_kph = round(float(wind_ms * 3.6), 1)
            rain_1h = get_val(current, 'precipitation')
            cloud_cover = get_val(current, 'cloudCover')
            
            condition = "Sunny"
            if rain_1h > 0:
                condition = "Rainy"
            elif cloud_cover > 50:
                condition = "Cloudy"

            # Farming-specific alert logic
            alerts = []
            if rain_1h > 30:
                alerts.append("⚠️ Heavy rain detected — delay field operations and protect harvested crops.")
            elif rain_1h > 10:
                alerts.append("🌧️ Moderate rain — avoid spraying fertilizers or pesticides today.")
            if temp > 42:
                alerts.append("🌡️ Extreme heat — irrigate in evenings to reduce plant stress.")
            elif temp > 38:
                alerts.append("☀️ Hot conditions — ensure adequate irrigation for standing crops.")
            if temp < 5:
                alerts.append("❄️ Frost warning — cover sensitive crops with mulch or plastic sheets.")
            if wind_kph > 50:
                alerts.append("💨 High winds — secure greenhouse covers and avoid aerial spraying.")
            if humidity > 85:
                alerts.append("💧 High humidity — watch for fungal diseases like blight and mildew.")

            # Calculate Forecast (Next 3 Days)
            forecast = []
            days_seen = set()
            
            for h in hours:
                dt_str = h.get('time', '')
                try:
                    dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                except:
                    continue
                    
                day_name = dt.strftime('%a')
                if dt.date() > datetime.datetime.now().date() and day_name not in days_seen:
                    # Look for data around noon (midday temp)
                    if dt.hour >= 11 and dt.hour <= 14:
                        days_seen.add(day_name)
                        f_temp = int(get_val(h, 'airTemperature'))
                        f_rain = get_val(h, 'precipitation')
                        f_cloud = get_val(h, 'cloudCover')
                        
                        f_icon = "fa-sun"
                        if f_rain > 0: f_icon = "fa-cloud-rain"
                        elif f_cloud > 50: f_icon = "fa-cloud"
                        
                        forecast.append({
                            "day": "Tomorrow" if len(forecast) == 0 else ("Day After" if len(forecast) == 1 else day_name),
                            "temp": f"{f_temp}°C",
                            "icon": f_icon
                        })
                        
                if len(forecast) == 3:
                    break

            weather = {
                "city": city,
                "temp": f"{temp}°C",
                "condition": condition,
                "humidity": f"{humidity}%",
                "wind_kph": wind_kph,
                "alerts": alerts,
                "forecast": forecast
            }
            cache.set(cache_key, weather, expire=900)
            return jsonify(weather)
        else:
            return get_mock_weather(city)
    except Exception as e:
        print(f"Weather API Error: {e}")
        return get_mock_weather(city)

def get_mock_weather(city):
    # Realistic mock data for Indian cities in March
    mock_temps = {"Chennai": 31, "Salem": 33, "Coimbatore": 30, "Madurai": 34, "Bangalore": 28, "Delhi": 25, "Mumbai": 29}
    temp = mock_temps.get(city, 30)
    humidity = random.randint(40, 65)
    
    return jsonify({
        "city": city,
        "temp": f"{temp}°C",
        "condition": "Cloudy" if humidity > 60 else "Sunny",
        "humidity": f"{humidity}%",
        "wind_kph": random.randint(5, 15),
        "alerts": ["☀️ Maintaining optimal conditions for local crops."] if temp < 38 else ["🔥 High temperature alert - monitor soil moisture."],
        "forecast": [
            {"day": "Today",     "temp": f"{temp}°C",     "icon": "fa-sun"},
            {"day": "Tomorrow",  "temp": f"{temp + 1}°C", "icon": "fa-sun"},
            {"day": "Day After", "temp": f"{temp - 1}°C", "icon": "fa-cloud"}
        ]
    })


# =============================================
# NEW FEATURE ENDPOINTS
# =============================================

# --- Yield Estimation ---
YIELD_DATA = {
    "Rice": {"yield_per_acre": 2.5, "unit": "tons"},
    "Wheat": {"yield_per_acre": 2.0, "unit": "tons"},
    "Maize": {"yield_per_acre": 3.5, "unit": "tons"},
    "Sugarcane": {"yield_per_acre": 35.0, "unit": "tons"},
    "Cotton": {"yield_per_acre": 0.6, "unit": "tons"},
    "Groundnut": {"yield_per_acre": 1.2, "unit": "tons"},
    "Soybean": {"yield_per_acre": 1.0, "unit": "tons"},
    "Tomato": {"yield_per_acre": 10.0, "unit": "tons"},
    "Potato": {"yield_per_acre": 8.0, "unit": "tons"},
    "Onion": {"yield_per_acre": 6.0, "unit": "tons"},
    "Banana": {"yield_per_acre": 15.0, "unit": "tons"},
    "Turmeric": {"yield_per_acre": 2.5, "unit": "tons"},
    "Chickpea": {"yield_per_acre": 0.8, "unit": "tons"},
    "Mustard": {"yield_per_acre": 0.7, "unit": "tons"},
    "Sunflower": {"yield_per_acre": 0.8, "unit": "tons"},
}

@app.route('/api/yield_estimate', methods=['POST'])
@jwt_required()
def yield_estimate():
    data = request.get_json()
    crop = data.get('crop', '')
    acres = float(data.get('acres', 1))
    
    crop_info = YIELD_DATA.get(crop)
    if not crop_info:
        # Fallback estimate
        crop_info = {"yield_per_acre": 2.0, "unit": "tons"}
    
    # Add some variability based on random factor (simulating weather/soil conditions)
    factor = random.uniform(0.85, 1.15)
    estimated = round(float(crop_info["yield_per_acre"] * acres * factor), 2)
    revenue_per_ton = random.randint(15000, 45000)
    estimated_revenue = round(estimated * revenue_per_ton)
    
    result = {
        "crop": crop,
        "acres": acres,
        "estimated_yield": f"{estimated} {crop_info['unit']}",
        "estimated_revenue": f"₹{estimated_revenue:,}",
        "confidence": f"{random.randint(75, 95)}%",
        "tip": f"Based on average {crop_info['yield_per_acre']} {crop_info['unit']}/acre. Actual yield depends on soil, weather, and management."
    }
    
    user_phone = get_jwt_identity()
    db_helper.save_yield_estimate(user_phone, crop, acres, result["estimated_yield"])
    
    return jsonify(result)

# --- Market Trends ---
@app.route('/api/market_trends', methods=['GET'])
@jwt_required()
def market_trends():
    crop = request.args.get('crop', 'Tomato')
    trends = db_helper.get_market_trends(crop)
    
    # Ensure prices are floats for comparison and round them
    for p in trends:
        p["price"] = round(float(p["price"]), 2)

    # If not enough data, generate synthetic trend data
    if len(trends) < 5:
        base_prices = {"Tomato": 2500, "Potato": 1200, "Onion": 1800, "Rice": 3200, "Wheat": 2600, "Maize": 1900}
        base = base_prices.get(crop, 2000)
        trends = []
        for i in range(30):
            date = (datetime.datetime.now() - datetime.timedelta(days=29-i)).strftime('%Y-%m-%d')
            price = base + random.randint(-300, 300)
            trends.append({"price": price, "timestamp": date})
    
    return jsonify(trends)

# --- Community Forum ---
@app.route('/api/forum', methods=['GET'])
@jwt_required()
def get_forum():
    category = request.args.get('category', 'All')
    posts = db_helper.get_forum_posts(category)
    # Attach comment count
    for post in posts:
        comments = db_helper.get_forum_comments(post['id'])
        post['comment_count'] = len(comments)
    return jsonify(posts)

@app.route('/api/forum', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    user_phone = get_jwt_identity()
    
    # Get user name from DB
    conn = db_helper.get_db_connection()
    user = conn.execute('SELECT name FROM users WHERE phone = ?', (user_phone,)).fetchone()
    conn.close()
    author_name = dict(user)['name'] if user else 'Farmer'
    
    success = db_helper.create_forum_post(
        user_phone, author_name,
        data.get('title', ''), data.get('content', ''),
        data.get('category', 'General')
    )
    if success:
        # Log Activity
        db_helper.log_user_activity(user_phone, "Forum Post", f"Created post: '{data.get('title', '')}'")
        return jsonify({"message": "Post created!"}), 201
    return jsonify({"error": "Failed to create post"}), 500

@app.route('/api/forum/<int:post_id>/comment', methods=['POST'])
@jwt_required()
def comment_on_post(post_id):
    data = request.get_json()
    user_phone = get_jwt_identity()
    
    conn = db_helper.get_db_connection()
    user = conn.execute('SELECT name FROM users WHERE phone = ?', (user_phone,)).fetchone()
    conn.close()
    author_name = dict(user)['name'] if user else 'Farmer'
    
    success = db_helper.add_forum_comment(post_id, user_phone, author_name, data.get('content', ''))
    if success:
        return jsonify({"message": "Comment added!"}), 201
    return jsonify({"error": "Failed to add comment"}), 500

@app.route('/api/forum/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    success = db_helper.like_forum_post(post_id)
    if success:
        return jsonify({"message": "Liked!"}), 200
    return jsonify({"error": "Failed"}), 500

@app.route('/api/forum/<int:post_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(post_id):
    comments = db_helper.get_forum_comments(post_id)
    return jsonify(comments)

@app.route('/api/forum/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_phone = get_jwt_identity()
    success, message = db_helper.delete_forum_post(post_id, user_phone)
    if success:
        db_helper.log_user_activity(user_phone, "Forum Post Deletion", f"Deleted post ID: {post_id}")
        return jsonify({"message": message}), 200
    return jsonify({"error": message}), 403

# --- Government Schemes ---
GOVT_SCHEMES = [
    {"name": "PM-KISAN", "description": "₹6,000/year in 3 installments to small & marginal farmers.", "eligibility": "Land < 5 acres", "max_land": 5, "link": "https://pmkisan.gov.in", "icon": "fa-hand-holding-usd"},
    {"name": "PM Fasal Bima Yojana", "description": "Crop insurance at subsidized premiums (1.5%-5%).", "eligibility": "All farmers with crop loans", "max_land": 999, "link": "https://pmfby.gov.in", "icon": "fa-shield-alt"},
    {"name": "Kisan Credit Card (KCC)", "description": "Short-term credit up to ₹3 lakh at 4% interest.", "eligibility": "All cultivators, tenant farmers", "max_land": 999, "link": "https://www.nabard.org", "icon": "fa-credit-card"},
    {"name": "Soil Health Card Scheme", "description": "Free soil testing and nutrient-based recommendations.", "eligibility": "All farmers", "max_land": 999, "link": "https://soilhealth.dac.gov.in", "icon": "fa-flask"},
    {"name": "Paramparagat Krishi Vikas Yojana", "description": "₹50,000/hectare for organic farming adoption.", "eligibility": "Farmers willing to adopt organic practices", "max_land": 999, "link": "https://pgsindia-ncof.gov.in", "icon": "fa-leaf"},
    {"name": "Micro Irrigation Fund", "description": "Subsidy up to 55% on drip/sprinkler irrigation systems.", "eligibility": "All farmers, priority to small holders", "max_land": 999, "link": "https://pmksy.gov.in", "icon": "fa-tint"},
    {"name": "National Mission on Oilseeds & Oil Palm", "description": "Financial assistance for oilseed crop cultivation.", "eligibility": "Farmers growing oilseeds", "max_land": 999, "crops": ["Groundnut", "Mustard", "Sunflower", "Soybean"], "link": "#", "icon": "fa-seedling"},
    {"name": "e-NAM (National Agriculture Market)", "description": "Online trading platform for transparent pricing.", "eligibility": "All farmers with produce to sell", "max_land": 999, "link": "https://enam.gov.in", "icon": "fa-store"},
]

@app.route('/api/scheme_check', methods=['POST'])
@jwt_required()
def scheme_check():
    data = request.get_json()
    state = data.get('state', '')
    land_acres = float(data.get('land_acres', 0))
    income = float(data.get('income', 0))
    crop = data.get('crop', '')
    
    eligible = []
    for scheme in GOVT_SCHEMES:
        is_eligible = True
        if land_acres > scheme.get('max_land', 999):
            is_eligible = False
        if 'crops' in scheme and crop not in scheme['crops']:
            is_eligible = False
        if is_eligible:
            eligible.append(scheme)
    
    return jsonify({"eligible_schemes": eligible, "total": len(eligible)})

# --- Agri-Store ---
@app.route('/api/store/products', methods=['GET'])
@jwt_required()
def store_products():
    category = request.args.get('category', 'All')
    products = db_helper.get_store_products(category)
    return jsonify(products)

@app.route('/api/store/order', methods=['POST'])
@jwt_required()
def store_order():
    data = request.get_json()
    user_phone = get_jwt_identity()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    success = db_helper.create_order(user_phone, product_id, quantity)
    if success:
        # Log Activity
        db_helper.log_user_activity(user_phone, "Store Order", f"Placed order for Product ID: {product_id} (Qty: {quantity})")
        return jsonify({"message": "Order placed successfully!"}), 201
    return jsonify({"error": "Failed to place order"}), 500

@app.route('/api/store/orders', methods=['GET'])
@jwt_required()
def my_orders():
    user_phone = get_jwt_identity()
    orders = db_helper.get_user_orders(user_phone)
    return jsonify(orders)

# --- Machinery Rental ---
@app.route('/api/machinery', methods=['GET'])
@jwt_required()
def get_machinery():
    type_filter = request.args.get('type', 'All')
    listings = db_helper.get_machinery_listings(type_filter)
    return jsonify(listings)

@app.route('/api/machinery', methods=['POST'])
@jwt_required()
def add_machinery():
    data = request.get_json()
    user_phone = get_jwt_identity()
    
    conn = db_helper.get_db_connection()
    user = conn.execute('SELECT name FROM users WHERE phone = ?', (user_phone,)).fetchone()
    conn.close()
    owner_name = dict(user)['name'] if user else 'Owner'
    
    success = db_helper.create_machinery_listing(
        user_phone, owner_name, data.get('name', ''),
        data.get('type', 'Other'), float(data.get('rate', 0)),
        data.get('location', ''), data.get('description', '')
    )
    if success:
        return jsonify({"message": "Equipment listed!"}), 201
    return jsonify({"error": "Failed to list"}), 500

@app.route('/api/machinery/book', methods=['POST'])
@jwt_required()
def book_equipment():
    data = request.get_json()
    user_phone = get_jwt_identity()
    listing_id = data.get('listing_id')
    hours = int(data.get('hours', 1))
    date = data.get('date', '')
    
    success = db_helper.book_machinery(
        user_phone, listing_id, date, hours
    )
    if success:
        # Log Activity
        db_helper.log_user_activity(user_phone, "Equipment Booking", f"Booked machinery (ID: {listing_id}) for {hours} hours on {date}")
        return jsonify({"message": "Booking confirmed!"}), 201
    return jsonify({"error": "Booking failed"}), 500

# --- Carbon Credit Calculator ---
CARBON_FACTORS = {
    "organic_farming": 2.5,       # tons CO2 saved per acre/year
    "no_till": 1.8,
    "cover_cropping": 1.5,
    "agroforestry": 4.0,
    "drip_irrigation": 1.2,
    "composting": 0.8,
    "crop_rotation": 1.0,
    "mulching": 0.6,
}

@app.route('/api/carbon_calculator', methods=['POST'])
@jwt_required()
def carbon_calculator():
    data = request.get_json()
    land_acres = float(data.get('land_acres', 1))
    practices = data.get('practices', [])  # list of practice keys
    
    total_co2_saved = 0
    breakdown = []
    for practice in practices:
        factor = CARBON_FACTORS.get(practice, 0)
        saved = round(float(factor * land_acres), 2)
        total_co2_saved += saved
        breakdown.append({
            "practice": practice.replace('_', ' ').title(),
            "co2_saved": f"{saved} tons/year"
        })
    
    total_co2_saved = round(float(total_co2_saved), 2)
    # Approximate carbon credit value: ~$15-30 per ton
    credit_value = round(float(total_co2_saved * random.uniform(15, 30)), 2)
    
    return jsonify({
        "total_co2_saved": f"{total_co2_saved} tons/year",
        "estimated_credits": f"${credit_value:.2f}/year",
        "equivalent_trees": int(total_co2_saved * 45),  # ~45 trees per ton
        "breakdown": breakdown
    })


@app.route('/api/login', methods=['POST'])
def login():
    json_data = request.get_json()
    data = LoginSchema().load(json_data)
    phone = data.get('phone')
    password = data.get('password')
    
    user = db_helper.verify_user(phone, password)
    if user:
        access_token = create_access_token(identity=phone)
        
        # Log Activity (Login)
        db_helper.log_user_activity(phone, "Login", "User logged in to the application.")
        
        return jsonify({
            "status": "success", 
            "user": user, 
            "token": access_token
        })
    return jsonify({"status": "error", "message": "Invalid phone or password"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    json_data = request.get_json()
    data = RegisterSchema().load(json_data)
    phone = data.get('phone')
    password = data.get('password')
    name = data.get('name')
    email = data.get('email')
    
    if db_helper.register_user(phone, password, name, email):
        access_token = create_access_token(identity=phone)
        return jsonify({
            "status": "success", 
            "token": access_token
        })
    return jsonify({"status": "error", "message": "User already exists or registration failed"}), 400

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    json_data = request.get_json()
    token = json_data.get('credential')
    if not token:
        return jsonify({"status": "error", "message": "No credential provided"}), 400

    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)

        email = idinfo.get('email')
        name = idinfo.get('name', '')
        google_id = idinfo.get('sub')

        if not email:
            return jsonify({"status": "error", "message": "No email provided by Google"}), 400

        # Attempt to find or register user
        user = db_helper.register_user_google(email, name, google_id)
        
        if user:
            # Create a JWT token seamlessly
            access_token = create_access_token(identity=user['phone'])
            db_helper.log_user_activity(user['phone'], "Login", "User logged in with Google")
            return jsonify({"status": "success", "user": user, "token": access_token})
        
        return jsonify({"status": "error", "message": "Failed to authenticate Google user"}), 500

    except ValueError as e:
        return jsonify({"status": "error", "message": f"Invalid token: {str(e)}"}), 401

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

@app.route('/api/user/activities', methods=['GET'])
@jwt_required()
def get_activities():
    user_phone = get_jwt_identity()
    limit = request.args.get('limit', 50, type=int)
    activities = db_helper.get_user_activities(user_phone, limit)
    return jsonify(activities)

@app.route('/api/user/export', methods=['GET'])
@jwt_required()
def export_user_data():
    user_phone = get_jwt_identity()
    data = db_helper.export_all_user_data(user_phone)
    
    # Log Activity
    db_helper.log_user_activity(user_phone, "Data Export", "Exported all personal data as JSON")
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=False, port=8000, host='0.0.0.0')
