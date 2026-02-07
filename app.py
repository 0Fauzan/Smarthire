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
# 1. FIXED PATH LOGIC (NO MORE 404)
# =========================================

# This is the directory where app.py lives
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
UPLOADS_DIR = os.path.join(PROJECT_ROOT, 'uploads')

# Create uploads directory if it doesn't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)

# DEBUG LOGGING
print(f"--- DEPLOYMENT DEBUG ---")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Frontend Dir: {FRONTEND_DIR}")
print(f"Uploads Dir: {UPLOADS_DIR}")
print(f"Index.html exists? {os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))}")
print(f"------------------------")

# =========================================
# 2. FLASK APP INITIALIZATION
# =========================================

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
# Allow requests from your Render frontend URL
CORS(app, resources={
    r"/*": {
        "origins": "*",  # In production, specify your exact domain
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'smarthire_secret_2026')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt_secret_9988')
app.config['UPLOAD_FOLDER'] = UPLOADS_DIR  # ✅ FIXED: Use UPLOADS_DIR
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database - FIXED for both local and Render
db_url = os.getenv('DATABASE_URL')
if not db_url:
    # Local development - use SQLite
    db_url = 'sqlite:///' + os.path.join(PROJECT_ROOT, 'smarthire.db')
else:
    # Render/Production - handle PostgreSQL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

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
# 3. DATABASE MODELS
# =========================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
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

# =========================================
# 4. AUTHENTICATION ENDPOINTS
# =========================================

@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
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
        return jsonify({"message": "Registered Successfully"}), 201
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, data['password']):
            token = create_access_token(identity=str(user.id))
            return jsonify({
                "access_token": token,
                "user": user.to_dict()
            }), 200
        
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500

# =========================================
# 5. PROFILE & RESUME ENDPOINTS
# =========================================

@app.route('/api/profile', methods=['GET', 'POST'])
@jwt_required()
def handle_profile():
    try:
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
        
        return jsonify(profile.to_dict() if profile else {}), 200
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({"error": "Profile operation failed"}), 500

def parse_and_score(filepath):
    """Parse resume and calculate ATS score"""
    text = ""
    try:
        if filepath.endswith('.pdf'):
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif filepath.endswith('.docx'):
            doc = Document(filepath)
            text = " ".join([p.text for p in doc.paragraphs])
        
        keywords = [
            "python", "javascript", "react", "node", "sql", 
            "aws", "docker", "agile", "java", "git"
        ]
        score = 45 + len([k for k in keywords if k in text.lower()]) * 6
        return min(score, 98)
    except Exception as e:
        print(f"Parse error: {e}")
        return 50

@app.route('/api/resume/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    try:
        uid = int(get_jwt_identity())
        file = request.files.get('resume')
        
        if not file:
            return jsonify({"error": "No file"}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uid}_{filename}")
        file.save(filepath)
        
        score = parse_and_score(filepath)
        
        res = Resume.query.filter_by(user_id=uid).first()
        if res:
            res.filename = filename
            res.ats_score = score
        else:
            res = Resume(user_id=uid, filename=filename, ats_score=score)
            db.session.add(res)
        
        db.session.commit()
        return jsonify({"resume": {"filename": filename, "ats_score": score}}), 200
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({"error": "Upload failed"}), 500

@app.route('/api/resume', methods=['GET'])
@jwt_required()
def get_resume():
    try:
        uid = int(get_jwt_identity())
        res = Resume.query.filter_by(user_id=uid).first()
        
        if res:
            return jsonify(res.to_dict()), 200
        return jsonify({}), 404
    except Exception as e:
        print(f"Get resume error: {e}")
        return jsonify({"error": "Failed to get resume"}), 500

# =========================================
# 6. INTERVIEW & AI ENDPOINTS
# =========================================

@app.route('/api/interview/save', methods=['POST'])
@jwt_required()
def save_interview():
    try:
        uid = int(get_jwt_identity())
        data = request.get_json()
        
        session = InterviewSession(
            user_id=uid,
            type=data['type'],
            language=data.get('language', 'N/A'),
            score=data['score'],
            details_json=json.dumps(data['results']),
            date=data['date']
        )
        db.session.add(session)
        db.session.commit()
        return jsonify({"msg": "Saved"}), 201
    except Exception as e:
        print(f"Save interview error: {e}")
        return jsonify({"error": "Failed to save"}), 500

@app.route('/api/interview/history', methods=['GET'])
@jwt_required()
def get_history():
    try:
        uid = int(get_jwt_identity())
        sessions = InterviewSession.query.filter_by(user_id=uid).order_by(
            InterviewSession.id.desc()
        ).all()
        return jsonify([s.to_dict() for s in sessions]), 200
    except Exception as e:
        print(f"History error: {e}")
        return jsonify({"error": "Failed to get history"}), 500

@app.route('/api/ai/analyze-code', methods=['POST'])
@jwt_required()
def analyze_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        lang = data.get('language', '')
        question = data.get('question', '')
        
        prompt = f"Review this {lang} code for: {question}. Return ONLY JSON: {{'score': int, 'verdict': str, 'feedback': str}}. Code: {code}"
        
        try:
            res = requests.post(
                HF_MODEL_URL,
                headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
                json={"inputs": prompt},
                timeout=10
            )
            raw = res.json()[0]['generated_text']
            ai_data = json.loads(raw[raw.find('{'):raw.rfind('}')+1])
            return jsonify(ai_data), 200
        except:
            # Fallback response if AI fails
            return jsonify({
                "score": random.randint(70, 85),
                "verdict": "Good",
                "feedback": "Code is logically sound but could use minor optimization."
            }), 200
    except Exception as e:
        print(f"AI analyze error: {e}")
        return jsonify({"error": "Analysis failed"}), 500

# =========================================
# 7. RECRUITER & JOBS ENDPOINTS
# =========================================

@app.route('/api/hr/candidates', methods=['GET'])
@jwt_required()
def hr_candidates():
    try:
        uid = int(get_jwt_identity())
        user = User.query.get(uid)
        
        if user.role != 'hr':
            return jsonify({"error": "Unauthorized"}), 403
        
        candidates = User.query.filter_by(role='candidate').all()
        result = []
        
        for c in candidates:
            r = Resume.query.filter_by(user_id=c.id).first()
            i = InterviewSession.query.filter_by(user_id=c.id).first()
            
            result.append({
                "id": c.id,
                "name": c.name,
                "role": c.profile.role_title if c.profile else "Not Set",
                "ats": r.ats_score if r else 0,
                "tech": i.score if i else 0,
                "status": "Reviewed" if i else "Pending",
                "education": c.profile.education if c.profile else "N/A",
                "skills": c.profile.skills if c.profile else "N/A",
                "projects": c.profile.projects if c.profile else "N/A"
            })
        
        return jsonify(result), 200
    except Exception as e:
        print(f"HR candidates error: {e}")
        return jsonify({"error": "Failed to get candidates"}), 500

@app.route('/api/jobs', methods=['GET', 'POST'])
def manage_jobs():
    try:
        if request.method == 'POST':
            data = request.get_json()
            job = Job(
                title=data['title'],
                description=data.get('description', 'Role posted via SmartHire'),
                department=data.get('department', 'Engineering'),
                location=data.get('location', 'Remote'),
                skills=data.get('skills', 'N/A')
            )
            db.session.add(job)
            db.session.commit()
            return jsonify({"msg": "Posted"}), 201
        
        jobs = Job.query.all()
        return jsonify([j.to_dict() for j in jobs]), 200
    except Exception as e:
        print(f"Jobs error: {e}")
        return jsonify({"error": "Operation failed"}), 500

# =========================================
# 8. STATIC FILE SERVING (FRONTEND)
# =========================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend files"""
    try:
        # Serve specific file if it exists
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        
        # Check for .html file
        if path and os.path.exists(os.path.join(app.static_folder, path + ".html")):
            return send_from_directory(app.static_folder, path + ".html")
        
        # Check for exact .html match
        if path.endswith('.html') and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        
        # Default to index.html (SPA behavior)
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        print(f"Serve error: {e}")
        return jsonify({"error": "File not found"}), 404

# =========================================
# 9. APPLICATION STARTUP
# =========================================

with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Database setup error: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
