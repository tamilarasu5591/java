import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

# Initialize Firebase
# Expects serviceAccountKey.json in the same directory as this file
cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')

if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully.")
else:
    print(f"WARNING: Firebase credentials not found at {cred_path}. Database operations will fail.")
    db = None
