"""
AgriVistara Server Diagnostic Script
Run this to find out exactly why the server won't start.
Usage: python diagnose_server.py
"""
import sys
import os

# Make sure we can import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("  AgriVistara Server Diagnostic")
print("=" * 60)
print(f"Python: {sys.version}")
print(f"Working Dir: {os.getcwd()}")
print()

errors = []

# 1. Check all required packages
print("[1/8] Checking required packages...")
packages = {
    'flask': 'flask',
    'flask_cors': 'flask-cors',
    'flask_jwt_extended': 'flask-jwt-extended',
    'marshmallow': 'marshmallow',
    'diskcache': 'diskcache',
    'google.generativeai': 'google-generativeai',
    'pandas': 'pandas',
    'openpyxl': 'openpyxl',
    'requests': 'requests',
    'deep_translator': 'deep-translator',
    'dotenv': 'python-dotenv',
    'bcrypt': 'bcrypt',
    'google.oauth2': 'google-auth',
    'google.auth.transport': 'google-auth',
}

for module_name, pip_name in packages.items():
    try:
        __import__(module_name)
        print(f"  [OK] {module_name}")
    except ImportError as e:
        print(f"  [MISSING] {module_name} --> pip install {pip_name}")
        errors.append(f"Missing package: {pip_name}")
    except Exception as e:
        print(f"  [ERROR] {module_name} --> {e}")
        errors.append(f"Error importing {module_name}: {e}")

# 2. Check firebase-admin (optional, not used by app.py directly)
print("\n[2/8] Checking firebase-admin (optional)...")
try:
    import firebase_admin
    print(f"  [OK] firebase-admin")
except ImportError:
    print(f"  [WARN] firebase-admin not installed (optional, not blocking)")
except Exception as e:
    print(f"  [WARN] firebase-admin error: {e} (optional, not blocking)")

# 3. Check .env file
print("\n[3/8] Checking .env file...")
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print(f"  [OK] .env found at {env_path}")
    from dotenv import load_dotenv
    load_dotenv(env_path)
    for key in ['GEMINI_API_KEY', 'WEATHER_API_KEY', 'GOOGLE_CLIENT_ID']:
        val = os.environ.get(key, '')
        if val:
            print(f"  [OK] {key} = {val[:10]}...")
        else:
            print(f"  [WARN] {key} not set (some features may not work)")
else:
    print(f"  [WARN] .env not found at {env_path}")

# 4. Check database
print("\n[4/8] Checking database...")
db_path = os.path.join(os.path.dirname(__file__), 'backend', 'database.sqlite')
if os.path.exists(db_path):
    print(f"  [OK] database.sqlite exists ({os.path.getsize(db_path)} bytes)")
else:
    print(f"  [INFO] database.sqlite not found (will be auto-created)")

# 5. Check db_helper import
print("\n[5/8] Checking db_helper module...")
try:
    import db_helper
    print(f"  [OK] db_helper imported successfully")
except Exception as e:
    print(f"  [ERROR] db_helper import failed: {e}")
    errors.append(f"db_helper import error: {e}")

# 6. Check ai_prompt import
print("\n[6/8] Checking ai_prompt module...")
try:
    import ai_prompt
    print(f"  [OK] ai_prompt imported successfully")
except Exception as e:
    print(f"  [ERROR] ai_prompt import failed: {e}")
    errors.append(f"ai_prompt import error: {e}")

# 7. Check if port 8000 is already in use
print("\n[7/8] Checking if port 8000 is available...")
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 8000))
sock.close()
if result == 0:
    print(f"  [WARN] Port 8000 is ALREADY IN USE! Close the other server first.")
    errors.append("Port 8000 is already in use by another process")
else:
    print(f"  [OK] Port 8000 is available")

# 8. Try to actually import app.py
print("\n[8/8] Attempting to import the Flask app...")
try:
    # Change to backend dir so relative imports work
    original_dir = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
    
    from app import app
    print(f"  [OK] Flask app imported successfully!")
    print(f"  [OK] App has {len([rule.rule for rule in app.url_map.iter_rules()])} routes registered")
    
    os.chdir(original_dir)
except Exception as e:
    print(f"  [ERROR] Flask app import FAILED: {e}")
    import traceback
    traceback.print_exc()
    errors.append(f"App import error: {e}")

# Summary
print("\n" + "=" * 60)
if errors:
    print(f"  FOUND {len(errors)} ERROR(S):")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
    print("\nFix the errors above, then run: python backend/app.py")
else:
    print("  ALL CHECKS PASSED! Server should start fine.")
    print("  Run: python backend/app.py")
print("=" * 60)
