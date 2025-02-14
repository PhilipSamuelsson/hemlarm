import firebase_admin
from firebase_admin import credentials, db
import json
import os

# 🔹 Läs Firebase credentials från ENV
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials:
    raise FileNotFoundError("❌ Firebase Service Account not found in environment variables")

# 🔹 Konvertera JSON-sträng till Python-dictionary
try:
    cred_data = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_data)
except json.JSONDecodeError:
    raise ValueError("❌ Invalid JSON format in FIREBASE_CREDENTIALS environment variable")

# 🔹 Initiera Firebase
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://home-alarm-c3d76-default-rtdb.europe-west1.firebasedatabase.app/"
})

ref = db.reference("/")
print("✅ Firebase connected successfully!")