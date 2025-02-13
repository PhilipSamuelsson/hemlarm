import firebase_admin
from firebase_admin import credentials, db
import requests
import time

# 🔹 Ladda in Firebase Service Account
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://home-alarm-c3d76-default-rtdb.europe-west1.firebasedatabase.app/"
})

motion_ref = db.reference("motion")

# 🔹 Flask API URL (Backend)
FLASK_URL = "http://YOUR_BACKEND_IP:5000/motion_data"

# 🔹 Funktion för att skicka data till Flask API
def send_to_backend(data):
    try:
        response = requests.post(FLASK_URL, json=data)
        print(f"✅ Data skickad till Flask API: {response.text}")
    except Exception as e:
        print(f"❌ Fel vid skickning till Flask: {e}")

# 🔹 Main loop för att hämta data från Firebase
while True:
    logs = motion_ref.get()
    if logs:
        for key, log in logs.items():
            send_to_backend(log)  # Skicka varje logg till Flask
            motion_ref.child(key).delete()  # Ta bort loggen från Firebase efter skickning

    time.sleep(5)  # Hämta ny data var 5:e sekund