from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__)

# Dummy API routes
@api_bp.route("/devices", methods=["GET"])
def get_devices():
    return jsonify([
        {"id": 1, "name": "Household 1", "isActive": True},
        {"id": 2, "name": "Household 2", "isActive": False}
    ])

@api_bp.route("/logs", methods=["GET"])
def get_logs():
    return jsonify([
        {"timestamp": "2025-01-31 10:00", "message": "Household 1 alarm activated"},
        {"timestamp": "2025-01-31 10:05", "message": "Household 2 alarm deactivated"}
    ])