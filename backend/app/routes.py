from flask import Blueprint, jsonify, request
import time
import threading
import requests
from flask_cors import CORS

api_bp = Blueprint("api", __name__)
CORS(api_bp)  # Enable CORS for frontend access

# 🔹 In-memory storage for devices & logs
devices = {}  # Stores connected devices
logs = []  # Stores motion detection logs

# 🔹 Time before a device is marked as disconnected (in seconds)
DISCONNECT_THRESHOLD = 30
MAX_LOGS = 50  # Limit log storage to avoid memory overflow

# 🔹 Pushover inställningar (byt ut till dina egna nycklar)
PUSHOVER_USER = "uiku12gm15jk5namtmv5td1vnttuiv"     # Din *user key*
PUSHOVER_TOKEN = "ae65hr6iroswx6j1srwgqhm3qncs77"    # Din *application token*

# 🔹 Health Check Endpoint
@api_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "Backend is running"}), 200

# 🔹 Register a new device (Pico W)
@api_bp.route("/register_device", methods=["POST"])
def register_device():
    data = request.get_json()
    if not data or "device_id" not in data:
        return jsonify({"error": "Invalid request. Missing 'device_id'."}), 400

    device_id = data["device_id"]
    device_name = data.get("name", device_id)  # Default to device_id if no name provided

    # Check if device already exists
    if device_id in devices:
        return jsonify({
            "status": "Device already registered",
            "device_id": device_id,
            "name": devices[device_id]["name"]
        }), 200

    # Register new device
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
#test----------------------------------------------------------------------------------------------------    
# 🔹 Receive device status updates
@api_bp.route("/device_status", methods=["POST"])
def device_status():
    data = request.get_json()
    if not data or "device_id" not in data or "status" not in data:
        return jsonify({"error": "Invalid request. Missing 'device_id' or 'status'."}), 400

    device_id = data["device_id"]
    status = data["status"]
    device_name = data.get("name", device_id)  # update name

    if device_id not in devices:
        print(f"⚠️ Device '{device_id}' not found. Auto-registering with status...")
        devices[device_id] = {
            "name": device_name,
            "status": status,
            "last_motion_distance": None,
            "last_motion_time": None,
            "last_seen": time.time()
        }
    else:
        devices[device_id].update({
            "status": status,
            "last_seen": time.time()
        })
        devices[device_id]["name"] = device_name # update name if sent
#test---------------------------------------------------------------------------------------------------- 
    print(f"🔄 Device {device_id} status updated to: {status}")
    return jsonify({"status": f"Device status updated to {status}", "device_id": device_id}), 200
# 🔹 Get all connected devices
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

# 🔹 Get motion detection logs (returns the last 50 logs)
@api_bp.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(logs[-MAX_LOGS:]), 200  # Return the most recent logs

# 🔹 Receive motion detection from a Pico W
@api_bp.route("/motion_detected", methods=["POST"])
def motion_detected():
    data = request.get_json()
    
    if not data or "device_id" not in data or "distance" not in data:
        return jsonify({"error": "Invalid request. Missing required fields."}), 400

    device_id = data["device_id"]
    distance = data["distance"]
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # Auto-register device if it doesn't exist
    if device_id not in devices:
        print(f"⚠️ Device '{device_id}' not found. Auto-registering...")
        devices[device_id] = {
            "name": device_id,
            "status": "connected",
            "last_motion_distance": distance,
            "last_motion_time": timestamp,
            "last_seen": time.time()
        }
    else:
        # Update device status
        devices[device_id].update({
            "last_motion_distance": distance,
            "last_motion_time": timestamp,
            "last_seen": time.time(),
            "status": "connected"
        })

    # Store motion log
    log_entry = {
        "timestamp": timestamp,
        "device_id": device_id,
        "distance": distance,
        "message": f"Motion detected ({distance:.2f} cm)"
    }
    logs.append(log_entry)
    
    print(f"🚨 [{timestamp}] Motion detected from {device_id}: {distance:.2f} cm")

    # 🔔 Skicka Pushover-notis
    try:
        r = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "title": f"Larm från {device_id}",
            "message": f"Rörelse upptäckt: {distance:.2f} cm vid {timestamp}"
        })
        if r.status_code == 200:
            print("📲 Notis skickad!")
        else:
            print(f"❌ Kunde inte skicka notis: {r.text}")
    except Exception as e:
        print(f"❌ Fel vid försök att skicka notis: {e}")

    return jsonify({"status": "Motion recorded", "device_id": device_id, "distance": distance}), 201

# 🔹 Background Task: Mark Inactive Devices as Disconnected
def check_inactive_devices():
    while True:
        current_time = time.time()
        for device_id, details in devices.items():
            last_seen = details.get("last_seen", 0)
            if current_time - last_seen > DISCONNECT_THRESHOLD and details["status"] == "connected":
                devices[device_id]["status"] = "disconnected"
                print(f"⚠️ Device {device_id} marked as disconnected.")

        time.sleep(30)  # Run every 30 seconds

# 🔹 Start background thread
threading.Thread(target=check_inactive_devices, daemon=True).start()
