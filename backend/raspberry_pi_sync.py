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

logs_ref = db.reference("logs")
devices_ref = db.reference("devices")

def is_recent(timestamp, threshold=30):
    """ Kontrollera om en logg är nyare än threshold sekunder. """
    try:
        return (time.time() - float(timestamp)) < threshold  # Konvertera timestamp till float
    except (ValueError, TypeError):
        print(f"⚠️ Ogiltigt timestamp-format: {timestamp}")
        return False  # Om konvertering misslyckas, behandla loggen som gammal

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

# 🔹 Uppdatera enheters status till "disconnected" om de inte har uppdaterats nyligen
def check_device_status():
    current_time = time.time()
    devices = devices_ref.get()
    
    if devices:
        for device_id, device_info in devices.items():
            last_seen = device_info.get("last_seen", 0)
            try:
                last_seen = float(last_seen)  # Konvertera last_seen till float
            except (ValueError, TypeError):
                print(f"⚠️ Ogiltigt last_seen-format för enhet {device_id}: {last_seen}")
                continue
            
            if (current_time - last_seen) > 30:  # Ingen uppdatering på 30 sek
                devices_ref.child(device_id).update({"status": "disconnected"})
                print(f"🔴 Enhet {device_id} markerad som offline")

# 🔹 Main loop för att hämta data från Firebase
while True:
    logs = logs_ref.get()
    
    if logs:
        for key, log in logs.items():
            if "timestamp" in log and is_recent(log["timestamp"]):
                send_to_backend(log)  # Skicka loggen utan att radera den
            else:
                print(f"⚠️ Ignorerar gammal eller ogiltig logg: {key}")
    
    check_device_status()  # Kontrollera enheters status
    time.sleep(5)  # Vänta 5 sekunder innan vi hämtar ny data
