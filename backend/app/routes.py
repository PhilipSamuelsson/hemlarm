from flask import Blueprint, jsonify, request
import time
import threading
import requests
from flask_cors import CORS
from datetime import datetime
import pytz
import psycopg2
import os

api_bp = Blueprint("api", __name__)
CORS(api_bp)

# 🔹 In-memory storage for short-term display
devices = {}
logs = []

# 🔹 Settings
DISCONNECT_THRESHOLD = 30
MAX_LOGS = 50

# 🔹 Pushover settings
PUSHOVER_TOKEN = "ae65hr6iroswx6j1srwgqhm3qncs77"
PUSHOVER_USERS = [
    "uiku12gm15jk5namtmv5td1vnttuiv", #Philip
    "u1s3rfg1knys87gtsbom6v6oyjkhx1", #gul
    "usre5z1ad9jghda42rekqza7h2mavt", #Johan
]

# 🔹 Helper to open fresh DB connection
def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode='require')

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

    devices[device_id] = {
        "name": device_name,
        "status": "online",
        "last_motion_distance": None,
        "last_motion_time": None,
        "last_seen": time.time()
    }

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO devices (id, device_name, is_active, last_seen)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT (id) DO UPDATE
                    SET device_name = EXCLUDED.device_name,
                        is_active = EXCLUDED.is_active,
                        last_seen = EXCLUDED.last_seen;
                """, (device_id, device_name, True))
                conn.commit()
    except Exception as e:
        print(f"❌ DB error on register_device: {e}")

    print(f"✅ Registered: {device_id} ({device_name})")
    return jsonify({"status": "Device registered", "device_id": device_id, "name": device_name}), 201

# 🔹 Device status update
@api_bp.route("/device_status", methods=["POST"])
def device_status():
    data = request.get_json()
    if not data or "device_id" not in data or "status" not in data:
        return jsonify({"error": "Missing 'device_id' or 'status'."}), 400

    device_id = data["device_id"]
    status = data["status"]
    device_name = data.get("name", device_id)

    if device_id not in devices:
        print(f"⚠️ Auto-registering {device_id} with status")
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
            "last_seen": time.time(),
            "name": device_name
        })

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO devices (id, device_name, is_active, last_seen)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT (id) DO UPDATE
                    SET device_name = EXCLUDED.device_name,
                        is_active = EXCLUDED.is_active,
                        last_seen = EXCLUDED.last_seen;
                """, (device_id, device_name, status == "connected"))
                conn.commit()
    except Exception as e:
        print(f"❌ DB error on device_status: {e}")

    print(f"🔄 {device_id} status: {status}")
    return jsonify({"status": f"Device status updated to {status}", "device_id": device_id}), 200

# 🔹 Get single device status
@api_bp.route("/device_status/<device_id>", methods=["GET"])
def get_device_status(device_id):
    device = devices.get(device_id)
    if not device:
        return jsonify({"error": f"No device found with ID '{device_id}'"}), 404

    return jsonify({
        "device_id": device_id,
        "name": device["name"],
        "status": device["status"],
        "last_seen": device["last_seen"],
        "last_motion_time": device["last_motion_time"],
        "last_motion_distance": device["last_motion_distance"]
    }), 200

# 🔹 Get all devices
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

# 🔹 Clear all devices
@api_bp.route("/clear_devices", methods=["POST"])
def clear_devices():
    devices.clear()
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM devices;")
                conn.commit()
    except Exception as e:
        print(f"❌ DB error clearing devices: {e}")
    return jsonify({"status": "All devices cleared"}), 200

# 🔹 Get logs
@api_bp.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(logs[-MAX_LOGS:]), 200

# 🔹 Clear logs
@api_bp.route("/clear_logs", methods=["POST"])
def clear_logs():
    logs.clear()
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM alarm_logs;")
                conn.commit()
    except Exception as e:
        print(f"❌ DB error clearing logs: {e}")
    return jsonify({"status": "Logs cleared"}), 200

# 🔹 Motion detected
@api_bp.route("/motion_detected", methods=["POST"])
def motion_detected():
    data = request.get_json()
    if not data or "device_id" not in data or "distance" not in data:
        return jsonify({"error": "Missing required fields."}), 400

    device_id = data["device_id"]
    distance = data["distance"]
    alarm_active = data.get("alarm_active", False)

    cest = pytz.timezone('Europe/Stockholm')
    timestamp_cest = datetime.now(cest).strftime("%Y-%m-%d %H:%M:%S")

    if device_id not in devices:
        devices[device_id] = {
            "name": device_id,
            "status": "online",
            "last_motion_distance": distance,
            "last_motion_time": timestamp_cest,
            "last_seen": time.time()
        }
    else:
        devices[device_id].update({
            "last_motion_distance": distance,
            "last_motion_time": timestamp_cest,
            "last_seen": time.time(),
            "status": "online"
        })

    log_entry = {
        "timestamp": timestamp_cest,
        "device_id": device_id,
        "distance": distance,
        "alarm_active": alarm_active,
        "message": f"Rörelse: {distance:.2f} cm ({'aktivt larm' if alarm_active else 'passivt'})"
    }
    logs.append(log_entry)

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO alarm_logs (device_id, timestamp, distance, alarm_active, message)
                    VALUES (%s, %s, %s, %s, %s);
                """, (device_id, timestamp_cest, distance, alarm_active, log_entry["message"]))
                conn.commit()
    except Exception as e:
        print(f"❌ DB error on motion log: {e}")

    print(f"🚨 [{timestamp_cest}] {device_id}: {distance:.2f} cm (active={alarm_active})")

    if alarm_active:
        try:
            for user in PUSHOVER_USERS:
                r = requests.post("https://api.pushover.net/1/messages.json", data={
                    "token": PUSHOVER_TOKEN,
                    "user": user,
                    "title": f"Larm från {device_id}",
                    "message": f"Rörelse: {distance:.2f} cm vid {timestamp_cest}"
                })
                if r.status_code == 200:
                    print("📲 Notis skickad!")
                else:
                    print(f"❌ Kunde inte skicka notis: {r.text}")
        except Exception as e:
            print(f"❌ Fel vid Pushover: {e}")

    return jsonify({
        "status": "Motion recorded",
        "device_id": device_id,
        "distance": distance
    }), 201

# 🔹 Get all device statuses
@api_bp.route("/device_status_list", methods=["GET"])
def get_all_device_statuses():
    return jsonify([
        {
            "device_id": device_id,
            "name": device["name"],
            "status": device["status"],
            "last_seen": device["last_seen"],
            "last_motion_time": device["last_motion_time"],
            "last_motion_distance": device["last_motion_distance"]
        }
        for device_id, device in devices.items()
    ]), 200

# 🔹 Background thread placeholder (optional)
threading.Thread(daemon=True).start()