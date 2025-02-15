from flask import Blueprint, jsonify, request
import time
from firebase_config import ref  # Import Firebase reference
from flask_cors import CORS  # Om du behöver CORS

api_bp = Blueprint("api", __name__)
CORS(api_bp)  # Aktivera CORS på alla endpoints om frontend ska nå backend

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

    # Check if device is already registered
    existing_device = ref.child("devices").child(device_id).get()
    if existing_device:
        return jsonify({"status": "Device already registered", "device_id": device_id, "name": existing_device.get("name", device_id)}), 200

    # Store new device in Firebase
    ref.child("devices").child(device_id).set({
        "name": device_name,
        "status": "connected",
        "last_motion_distance": None,
        "last_motion_time": None
    })

    print(f"✅ New device registered: {device_id} ({device_name})")
    return jsonify({"status": "Device registered", "device_id": device_id, "name": device_name}), 201

# 🔹 Get all connected devices
@api_bp.route("/devices", methods=["GET"])
def get_devices():
    devices = ref.child("devices").get() or {}  # Fallback till tom dictionary om inget finns

    device_list = [
        {
            "id": device_id,
            "name": details.get("name", device_id),
            "status": details.get("status", "unknown"),
            "last_motion_distance": details.get("last_motion_distance"),
            "last_motion_time": details.get("last_motion_time")
        }
        for device_id, details in devices.items()
    ]
    
    return jsonify(device_list), 200

# 🔹 Get motion detection logs (returns the last 50 logs)
@api_bp.route("/logs", methods=["GET"])
def get_logs():
    logs = ref.child("logs").order_by_child("timestamp").limit_to_last(50).get() or {}

    logs_list = [{"id": key, **log} for key, log in logs.items()]
    logs_list.sort(key=lambda x: x["timestamp"], reverse=True)

    return jsonify(logs_list), 200

# 🔹 Receive motion detection from a Pico W
@api_bp.route("/motion_detected", methods=["POST"])
def motion_detected():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid request. Must send JSON data."}), 400

    required_keys = ["device_id", "distance"]
    if not all(key in data for key in required_keys):
        return jsonify({"error": f"Missing required keys. Expected {required_keys}"}), 400

    device_id = data["device_id"]
    distance = data["distance"]
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # Check if device exists before logging data
    device_ref = ref.child("devices").child(device_id)
    if not device_ref.get():
        return jsonify({"error": f"Device '{device_id}' not registered."}), 404

    # Update last motion data for the device
    device_ref.update({
        "last_motion_distance": distance,
        "last_motion_time": timestamp
    })

    # Add log entry to Firebase
    log_entry = {
        "timestamp": timestamp,
        "device_id": device_id,
        "distance": distance,
        "message": f"Motion detected ({distance:.2f} cm)"
    }
    ref.child("logs").push(log_entry)

    print(f"🚨 [{timestamp}] Motion detected from {device_id}: {distance:.2f} cm")
    return jsonify({"status": "Motion recorded", "device_id": device_id, "distance": distance}), 201