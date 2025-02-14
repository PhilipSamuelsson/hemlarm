import firebase_admin
from firebase_admin import credentials, db
import json
import os

# 🔹 Load Firebase credentials from ENV
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials:
    raise FileNotFoundError("❌ Firebase Service Account not found in environment variables")

# 🔹 Parse JSON from ENV
cred = credentials.Certificate(json.loads(firebase_credentials))

# 🔹 Initialize Firebase with database URL
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://home-alarm-c3d76-default-rtdb.europe-west1.firebasedatabase.app/"
})

ref = db.reference("/")
print("✅ Firebase connected successfully!")