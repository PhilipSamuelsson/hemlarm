from flask import Flask
from flask_cors import CORS
from app.routes import api_bp  # Importera dina routes

def create_app():
    app = Flask(__name__)
    CORS(app)  # Aktivera CORS för frontend-access

    # 🔹 Se till att Blueprinten registreras korrekt
    app.register_blueprint(api_bp, url_prefix="/api")  # 🔥 OBS! Prefix "/api"
    
    return app