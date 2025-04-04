from flask import Blueprint, jsonify, request
import time
import threading
from flask_cors import CORS

api_bp = Blueprint("api", __name__)
CORS(api_bp)  # Enable CORS for frontend access

# 🔹 In-memory storage for devices & logs
devices = {}  # Stores connected devices
logs = []  # Stores motion detection logs

# 🔹 Time before a device is marked as disconnected (in seconds)
DISCONNECT_THRESHOLD = 30  #
MAX_LOGS = 50  # Limit log storage to avoid memory overflow

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
        return jsonify({"status": "Device already registered", "device_id": device_id, "name": devices[device_id]["name"]}), 200

    # Register new device
    devices[device_id] = {
        "name": device_name,
        "status": "connected",
        "last_motion_distance": None,
        "last_motion_time": None,
        "last_seen": time.time()
    }

    print(f"✅ New device registered: {device_id} ({device_name})")
    return jsonify({"status": "Device registered", "device_id": device_id, "name": device_name}), 201

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
            "status": "connected"  # Reactivate if previously disconnected
        })

    # Store motion log
    logs.append({
        "timestamp": timestamp,
        "device_id": device_id,
        "distance": distance,
        "message": f"Motion detected ({distance:.2f} cm)"
    })
    
    print(f"🚨 [{timestamp}] Motion detected from {device_id}: {distance:.2f} cm")
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