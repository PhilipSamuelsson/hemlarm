import firebase_admin
from firebase_admin import credentials, db
import requests
import time
import os
from dotenv import load_dotenv

# 🔹 Ladda in miljövariabler
load_dotenv()

# 🔹 Firebase Service Account (Se till att din serviceAccountKey.json finns lokalt eller lagras i Render som miljövariabel)
SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"

# 🔹 Flask API URL (ändra till din backend-URL)
FLASK_URL = "https://hemlarm.onrender.com/api/motion_detected"
# 🔹 Initiera Firebase
try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://home-alarm-c3d76-default-rtdb.europe-west1.firebasedatabase.app/"
    })
    print("✅ Ansluten till Firebase!")
except Exception as e:
    print(f"❌ Fel vid anslutning till Firebase: {e}")

motion_ref = db.reference("logs")

# 🔹 Funktion för att skicka data till Flask API
def send_to_backend(data):
    try:
        response = requests.post(FLASK_URL, json=data)
        if response.status_code == 201:
            print(f"✅ Data skickad till Flask: {response.text}")
            return True  # Om data skickades korrekt
        else:
            print(f"⚠️ Flask API svarade med statuskod {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Fel vid skickning till Flask: {e}")
        return False

# 🔹 Main loop för att hämta data från Firebase
while True:
    logs = motion_ref.get()
    
    if logs:
        for key, log in logs.items():
            if send_to_backend(log):  # Om vi lyckas skicka, radera posten i Firebase
                motion_ref.child(key).delete()
                print(f"🗑️ Data raderad från Firebase: {key}")
    
    time.sleep(5)  # Vänta 5 sekunder innan vi hämtar ny data