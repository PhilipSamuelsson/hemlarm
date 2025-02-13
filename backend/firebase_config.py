import os
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Firebase credentials and database URL
SERVICE_ACCOUNT_FILE = os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "https://home-alarm-c3d76-default-rtdb.europe-west1.firebasedatabase.app/")

# Ensure the service account file exists
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise FileNotFoundError(f"❌ Service account file not found: {SERVICE_ACCOUNT_FILE}")

try:
    # Initialize Firebase only if it's not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})

    # Get reference to Firebase Realtime Database
    ref = db.reference("/")
    print("✅ Successfully connected to Firebase Realtime Database!")

except Exception as e:
    print(f"❌ Firebase connection failed: {e}")
    ref = None  # Set ref to None if Firebase fails