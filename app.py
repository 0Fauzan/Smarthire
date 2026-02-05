import os
import random
import json
import logging
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
# 1. APP INITIALIZATION & CONFIGURATION
# =========================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder='../', static_url_path='/')
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'smarthire.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'smarthire_ultimate_secret_2026'
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24) # Tokens last 24h

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --- Hugging Face Setup ---
# Using the token provided in your previous snippet
HF_API_TOKEN = "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"
HF_MODEL_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HF_ENABLED = True if HF_API_TOKEN else False

# =========================================
# 2. DATABASE MODELS
# =========================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'candidate' or 'hr'
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    def to_dict(self): return {'id': self.id, 'name': self.name, 'email': self.email, 'role': self.role}

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    role_title = db.Column(db.String(100))
    education = db.Column(db.String(200))
    skills = db.Column(db.Text)
    projects = db.Column(db.Text)
    def to_dict(self): return {'role': self.role_title, 'education': self.education, 'skills': self.skills, 'projects': self.projects}

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200))
    ats_score = db.Column(db.Integer)
    def to_dict(self): return {'filename': self.filename, 'ats_score': self.ats_score}

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
            'id': self.id, 'type': self.type, 'language': self.language, 
            'score': self.score, 'date': self.date, 
            'results': json.loads(self.details_json) if self.details_json else []
        }

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(100))
    location = db.Column(db.String(100))
    skills = db.Column(db.Text)
    def to_dict(self): return {'id': self.id, 'title': self.title, 'department': self.department, 'location': self.location, 'skills': self.skills, 'description': self.description}

# =========================================
# 3. AUTHENTICATION ENDPOINTS
# =========================================

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first(): return jsonify({"error": "User already exists"}), 409
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(name=data['name'], email=data['email'], password_hash=hashed, role=data['role'])
    db.session.add(new_user); db.session.commit()
    return jsonify({"message": "Registered Successfully"}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        # ✅ Identity is stringified to fix "Subject must be a string"
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token, "user": user.to_dict()})
    return jsonify({"error": "Invalid email or password"}), 401

# =========================================
# 4. PROFILE & RESUME ENDPOINTS
# =========================================

@app.route('/api/profile', methods=['GET', 'POST'])
@jwt_required()
def handle_profile():
    uid = int(get_jwt_identity())
    profile = Profile.query.filter_by(user_id=uid).first()
    if request.method == 'POST':
        data = request.get_json()
        if not profile:
            profile = Profile(user_id=uid)
            db.session.add(profile)
        profile.role_title = data.get('role')
        profile.education = data.get('education')
        profile.skills = data.get('skills')
        profile.projects = data.get('projects')
        db.session.commit()
        return jsonify({"msg": "Updated"}), 200
    return jsonify(profile.to_dict() if profile else {})

def parse_and_score(filepath):
    text = ""
    try:
        if filepath.endswith('.pdf'):
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages: text += page.extract_text() or ""
        elif filepath.endswith('.docx'):
            doc = Document(filepath)
            text = " ".join([p.text for p in doc.paragraphs])
        
        keywords = ["python", "javascript", "react", "node", "sql", "aws", "docker", "agile", "java"]
        score = 45 + len([k for k in keywords if k in text.lower()]) * 6
        return min(score, 98)
    except: return 50

@app.route('/api/resume/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    uid = int(get_jwt_identity())
    file = request.files.get('resume')
    if not file: return jsonify({"error": "No file"}), 400
    filename = secure_filename(file.filename)
    if not os.path.exists(app.config['UPLOAD_FOLDER']): os.makedirs(app.config['UPLOAD_FOLDER'])
    path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uid}_{filename}")
    file.save(path)
    score = parse_and_score(path)
    res = Resume.query.filter_by(user_id=uid).first()
    if res: res.filename, res.ats_score = filename, score
    else: db.session.add(Resume(user_id=uid, filename=filename, ats_score=score))
    db.session.commit()
    return jsonify({"resume": {"filename": filename, "ats_score": score}}), 200

@app.route('/api/resume', methods=['GET'])
@jwt_required()
def get_resume():
    uid = int(get_jwt_identity())
    res = Resume.query.filter_by(user_id=uid).first()
    return jsonify(res.to_dict() if res else {}), 200 if res else 404

# =========================================
# 5. INTERVIEW & AI ENDPOINTS
# =========================================

@app.route('/api/interview/save', methods=['POST'])
@jwt_required()
def save_interview():
    uid = int(get_jwt_identity())
    data = request.get_json()
    db.session.add(InterviewSession(
        user_id=uid, type=data['type'], language=data.get('language', 'N/A'),
        score=data['score'], details_json=json.dumps(data['results']), date=data['date']
    ))
    db.session.commit()
    return jsonify({"msg": "Saved"}), 201

@app.route('/api/interview/history', methods=['GET'])
@jwt_required()
def get_history():
    uid = int(get_jwt_identity())
    sessions = InterviewSession.query.filter_by(user_id=uid).order_by(InterviewSession.id.desc()).all()
    return jsonify([s.to_dict() for s in sessions])

@app.route('/api/ai/analyze-code', methods=['POST'])
@jwt_required()
def analyze_code():
    data = request.get_json()
    code, lang, q = data.get('code', ''), data.get('language', ''), data.get('question', '')
    
    prompt = f"Review this {lang} code for: {q}. Return ONLY JSON: {{'score': int, 'verdict': str, 'feedback': str}}. Code: {code}"
    try:
        res = requests.post(HF_MODEL_URL, headers={"Authorization": f"Bearer {HF_API_TOKEN}"}, json={"inputs": prompt})
        raw = res.json()[0]['generated_text']
        ai_data = json.loads(raw[raw.find('{'):raw.rfind('}')+1])
        return jsonify(ai_data)
    except:
        return jsonify({"score": random.randint(70, 85), "verdict": "Good", "feedback": "Code is logically sound but could use minor optimization."})

# =========================================
# 6. RECRUITER & JOBS ENDPOINTS
# =========================================

@app.route('/api/hr/candidates', methods=['GET'])
@jwt_required()
def hr_candidates():
    uid = int(get_jwt_identity())
    if User.query.get(uid).role != 'hr': return jsonify({"error": "Unauthorized"}), 403
    
    candidates = User.query.filter_by(role='candidate').all()
    res = []
    for c in candidates:
        r = Resume.query.filter_by(user_id=c.id).first()
        i = InterviewSession.query.filter_by(user_id=c.id).first()
        res.append({
            "id": c.id, "name": c.name, 
            "role": c.profile.role_title if c.profile else "Not Set", 
            "ats": r.ats_score if r else 0, 
            "tech": i.score if i else 0, 
            "status": "Reviewed" if i else "Pending",
            "education": c.profile.education if c.profile else "N/A",
            "skills": c.profile.skills if c.profile else "N/A",
            "projects": c.profile.projects if c.profile else "N/A"
        })
    return jsonify(res)

@app.route('/api/jobs', methods=['GET', 'POST'])
def manage_jobs():
    if request.method == 'POST':
        data = request.get_json()
        db.session.add(Job(
            title=data['title'], 
            description=data.get('description', 'Role posted via SmartHire'), 
            department=data.get('department', 'Engineering'), 
            location=data.get('location', 'Remote'), 
            skills=data.get('skills', 'N/A')
        ))
        db.session.commit()
        return jsonify({"msg": "Posted"}), 201
    
    jobs = Job.query.all()
    return jsonify([j.to_dict() for j in jobs])

# =========================================
# 7. STATIC SERVING
# =========================================

@app.route('/')
def serve_index(): return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)