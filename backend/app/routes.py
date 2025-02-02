from flask import Blueprint, jsonify, request
import time

api_bp = Blueprint("api", __name__)

# Store connected devices
connected_devices = {}

# Store motion detection logs
motion_logs = []

# Register a new device (Pico W)
@api_bp.route("/register_device", methods=["POST"])
def register_device():
    data = request.json
    if not data or "device_id" not in data:
        return jsonify({"error": "Invalid request"}), 400

    device_id = data["device_id"]
    device_name = data.get("name", device_id)  # Get name, or default to id

    # Store device in dictionary
    connected_devices[device_id] = {
        "name": device_name,
        "status": "connected",
        "last_motion_distance": None,
        "last_motion_time": None
    }

    print(f"New device registered: {device_id} ({device_name})")
    return jsonify({"status": "Device registered", "device_id": device_id, "name": device_name}), 200

# Get all connected devices
@api_bp.route("/devices", methods=["GET"])
def get_devices():
    if not connected_devices:
        return jsonify([])  # Return an empty array if no devices exist

    return jsonify([
        {
            "id": device_id,
            "name": details.get("name", device_id),  # If no name, use id
            "status": details["status"],
            "last_motion_distance": details["last_motion_distance"],
            "last_motion_time": details["last_motion_time"]
        }
        for device_id, details in connected_devices.items()
    ])

# Get motion detection logs
@api_bp.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(motion_logs)

# Receive motion detection from a Pico W
@api_bp.route("/motion_detected", methods=["POST"])
def motion_detected():
    data = request.json
    if not data or "device_id" not in data or "distance" not in data:
        return jsonify({"error": "Invalid request"}), 400

    device_id = data["device_id"]
    distance = data["distance"]
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # Store the latest motion detection for this device
    if device_id in connected_devices:
        connected_devices[device_id]["last_motion_distance"] = distance
        connected_devices[device_id]["last_motion_time"] = timestamp

    # Log the motion detection event
    motion_logs.append({
        "timestamp": timestamp,
        "device_id": device_id,
        "distance": distance,
        "message": f"Motion detected ({distance:.2f} cm)"
    })

    print(f"[{timestamp}] Motion detected from {device_id}: {distance:.2f} cm")
    return jsonify({"status": "Motion recorded", "device_id": device_id, "distance": distance}), 200
