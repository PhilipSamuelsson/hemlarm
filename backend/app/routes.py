from flask import Blueprint, jsonify, request
import time
import threading
import requests
from flask_cors import CORS

api_bp = Blueprint("api", __name__)
CORS(api_bp)

# 🔹 In-memory storage for devices & logs
devices = {}
logs = []

# 🔹 Settings
DISCONNECT_THRESHOLD = 30
MAX_LOGS = 50

# 🔹 Pushover settings
PUSHOVER_TOKEN = "ae65hr6iroswx6j1srwgqhm3qncs77"  # Application token
PUSHOVER_USERS = [
    "uiku12gm15jk5namtmv5td1vnttuiv",
    # Lägg till fler användarnycklar här
]

# 🔹 Health check
@api_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "Backend is running"}), 200

# 🔹 Register device
@api_bp.route("/register_device", methods=["POST"])
def register_device():
    data = request.get_json()
    if not data or "device_id" not in data:
        return jsonify({"error": "Missing 'device_id'."}), 400

    device_id = data["device_id"]
    device_name = data.get("name", device_id)

    if device_id in devices:
        return jsonify({
            "status": "Device already registered",
            "device_id": device_id,
            "name": devices[device_id]["name"]
        }), 200

    devices[device_id] = {
        "name": device_name,
        "status": "connected",
        "last_motion_distance": None,
        "last_motion_time": None,
        "last_seen": time.time()
    }

    print(f"✅ New device registered: {device_id} ({device_name})")
    return jsonify({
        "status": "Device registered",
        "device_id": device_id,
        "name": device_name
    }), 201

# 🔹 Get devices
@api_bp.route("/devices", methods=["GET"])
def get_devices():
    return jsonify([
        {
            "id": device_id,
            "name": details["name"],
            "status": details["status"],
            "last_motion_distance": details["last_motion_distance"],
            "last_motion_time": details["last_motion_time"],
            "last_seen": details["last_seen"]
        }
        for device_id, details in devices.items()
    ]), 200

# 🔹 Get logs
@api_bp.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(logs[-MAX_LOGS:]), 200

# 🔹 Motion detected
@api_bp.route("/motion_detected", methods=["POST"])
def motion_detected():
    data = request.get_json()
    if not data or "device_id" not in data or "distance" not in data:
        return jsonify({"error": "Missing required fields."}), 400

    device_id = data["device_id"]
    distance = data["distance"]
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if device_id not in devices:
        print(f"⚠️ Auto-registering device {device_id}")
        devices[device_id] = {
            "name": device_id,
            "status": "connected",
            "last_motion_distance": distance,
            "last_motion_time": timestamp,
            "last_seen": time.time()
        }
    else:
        devices[device_id].update({
            "last_motion_distance": distance,
            "last_motion_time": timestamp,
            "last_seen": time.time(),
            "status": "connected"
        })

    log_entry = {
        "timestamp": timestamp,
        "device_id": device_id,
        "distance": distance,
        "message": f"Motion detected ({distance:.2f} cm)"
    }
    logs.append(log_entry)
    print(f"🚨 [{timestamp}] Motion from {device_id}: {distance:.2f} cm")

    # 🔔 Pushover notifications
    for user_key in PUSHOVER_USERS:
        try:
            r = requests.post("https://api.pushover.net/1/messages.json", data={
                "token": PUSHOVER_TOKEN,
                "user": user_key,
                "title": f"Larm från {device_id}",
                "message": f"Rörelse upptäckt: {distance:.2f} cm vid {timestamp}"
            })
            if r.status_code == 200:
                print(f"📲 Notis skickad till {user_key}")
            else:
                print(f"❌ Misslyckades för {user_key}: {r.text}")
        except Exception as e:
            print(f"❌ Fel vid notis för {user_key}: {e}")

    return jsonify({"status": "Motion recorded", "device_id": device_id, "distance": distance}), 201

# 🔹 Background task: Mark inactive devices
def check_inactive_devices():
    while True:
        current_time = time.time()
        for device_id, details in devices.items():
            if current_time - details.get("last_seen", 0) > DISCONNECT_THRESHOLD and details["status"] == "connected":
                devices[device_id]["status"] = "disconnected"
                print(f"⚠️ Device {device_id} marked as disconnected.")
        time.sleep(30)

# 🔹 Start background thread
threading.Thread(target=check_inactive_devices, daemon=True).start()