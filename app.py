import os
import random
import json
import requests
from datetime import timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from werkzeug.utils import secure_filename

# =========================================
# 1. DYNAMIC PATH LOGIC
# =========================================
basedir = os.path.abspath(os.path.dirname(__file__))
# We look for the frontend folder one level up
frontend_dir = os.path.abspath(os.path.join(basedir, '..', 'frontend'))

# LOG FOR DEBUGGING (View this in Render Logs)
print(f"DEBUG: Looking for frontend files in: {frontend_dir}")
print(f"DEBUG: Does index.html exist there? {os.path.exists(os.path.join(frontend_dir, 'index.html'))}")

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

# Settings
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'smarthire_secret_2026')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt_secret_9988')
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database
db_url = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'smarthire.db'))
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# AI Config
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "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")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

# ... (Include your User, Profile, Resume, InterviewSession, Job models here) ...

# =========================================
# 2. STATIC FILE SERVING (FIXED CATCH-ALL)
# =========================================

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Check if the file requested actually exists in the frontend folder
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # If not, return index.html (Standard for Single Page Apps)
    return send_from_directory(app.static_folder, 'index.html')

# ... (Include all your API @app.route endpoints here) ...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
