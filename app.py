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
import pdfplumber
from docx import Document

# =========================================
# PATH CONFIGURATION
# =========================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
UPLOADS_DIR = os.path.join(PROJECT_ROOT, 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

print(f"--- DEPLOYMENT DEBUG ---")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Frontend Dir: {FRONTEND_DIR}")
print(f"Index exists: {os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))}")
print(f"------------------------")

# =========================================
# FLASK APP
# =========================================
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# ✅ FIXED CORS - Allow all origins for now
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'smarthire_secret_2026')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt_secret_9988')
app.config['UPLOAD_FOLDER'] = UPLOADS_DIR
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# ✅ FIXED DATABASE - Works with PostgreSQL or SQLite
db_url = os.getenv('DATABASE_URL')
if not db_url:
    # Local development
    db_path = os.path.join(PROJECT_ROOT, 'smarthire.db')
    db_url = f'sqlite:///{db_path}'
    print(f"Using SQLite: {db_path}")
else:
    # Production - handle PostgreSQL URL format
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    print(f"Using PostgreSQL")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# AI Config
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "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")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

# =========================================
# DATABASE MODELS (keep as is)
# =========================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)  # ✅ Increased length
    role = db.Column(db.String(20), nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email, 'role': self.role}

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    role_title = db.Column(db.String(100))
    education = db.Column(db.String(200))
    skills = db.Column(db.Text)
    projects = db.Column(db.Text)
    def to_dict(self):
        return {
            'role': self.role_title,
            'education': self.education,
            'skills': self.skills,
            'projects': self.projects
        }

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200))
    ats_score = db.Column(db.Integer)
    def to_dict(self):
        return {'filename': self.filename, 'ats_score': self.ats_score}

class InterviewSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50))
    language = db.Column(db.String(50))
    score = db.Column(db.Integer)
    details_json = db.Column(db.Text)
    date = db.Column(db.String(20))
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'language': self.language,
            'score': self.score,
            'date': self.date,
            'results': json.loads(self.details_json) if self.details_json else []
        }

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(100))
    location = db.Column(db.String(100))
    skills = db.Column(db.Text)
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'department': self.department,
            'location': self.location,
            'skills': self.skills,
            'description': self.description
        }

# ✅ CREATE TABLES IMMEDIATELY (before any requests)
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Test database connection
        user_count = User.query.count()
        print(f"✅ Database working - {user_count} users exist")
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        import traceback
        traceback.print_exc()

# =========================================
# AUTHENTICATION (with better error handling)
# =========================================
@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"Registration attempt: {data.get('email')}")
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "User already exists"}), 409
        
        hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            name=data['name'],
            email=data['email'],
            password_hash=hashed,
            role=data.get('role', 'candidate')
        )
        db.session.add(new_user)
        db.session.commit()
        
        print(f"✅ User registered: {data['email']}")
        return jsonify({"message": "Registered Successfully"}), 201
    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"Login attempt: {data.get('email')}")
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            print(f"❌ User not found: {data.get('email')}")
            return jsonify({"error": "Invalid email or password"}), 401
        
        if not bcrypt.check_password_hash(user.password_hash, data['password']):
            print(f"❌ Invalid password for: {data.get('email')}")
            return jsonify({"error": "Invalid email or password"}), 401
        
        token = create_access_token(identity=str(user.id))
        print(f"✅ Login successful: {data.get('email')}")
        
        return jsonify({
            "access_token": token,
            "user": user.to_dict()
        }), 200
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ... (keep all other routes as they were in the previous version)

# =========================================
# STATIC SERVING
# =========================================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    try:
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        
        if path and os.path.exists(os.path.join(app.static_folder, path + ".html")):
            return send_from_directory(app.static_folder, path + ".html")
        
        if path.endswith('.html') and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        print(f"Serve error: {e}")
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
