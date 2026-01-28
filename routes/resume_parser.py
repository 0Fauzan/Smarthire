# routes/resume_parser.py
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document

from extensions import db
from models.user import User
from models.resume import Resume
from services.ats_scorer import ATSScorer  # We'll create this

resume_bp = Blueprint("resume", __name__)

UPLOAD_FOLDER = "uploads/resumes"
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise Exception(f"PDF parsing error: {str(e)}")

def extract_text_from_docx(path):
    """Extract text from DOCX file"""
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        raise Exception(f"DOCX parsing error: {str(e)}")

# ========================================
# UPLOAD RESUME
# ========================================
@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    """
    Upload and analyze resume
    Returns: Resume ID, ATS score, feedback
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check file in request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDF and DOCX allowed"}), 400
    
    try:
        # Secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{current_user_id}_{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # Extract text
        if file_type == 'pdf':
            original_text = extract_text_from_pdf(file_path)
        else:
            original_text = extract_text_from_docx(file_path)
        
        if not original_text or len(original_text) < 100:
            os.remove(file_path)
            return jsonify({"error": "Resume appears to be empty or unreadable"}), 400
        
        # Parse resume structure
        parsed_data = parse_resume_structure(original_text)
        
        # Calculate ATS score
        ats_scorer = ATSScorer()
        ats_result = ats_scorer.calculate_ats_score(original_text, parsed_data)
        
        # Create Resume record
        resume = Resume(
            user_id=current_user_id,
            filename=filename,
            file_path=file_path,
            original_text=original_text,
            file_size=file_size,
            file_type=file_type,
            parsed_data=parsed_data,
            ats_score=ats_result['score'],
            ats_feedback=ats_result,
            analyzed_at=datetime.utcnow()
        )
        
        db.session.add(resume)
        db.session.commit()
        
        return jsonify({
            "message": "Resume uploaded and analyzed successfully",
            "resume_id": resume.id,
            "filename": filename,
            "ats_score": ats_result['score'],
            "status": resume.get_ats_status(),
            "breakdown": ats_result['breakdown'],
            "issues": ats_result['issues'],
            "suggestions": ats_result['suggestions']
        }), 201
        
    except Exception as e:
        # Cleanup on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

# ========================================
# GET RESUME DETAILS
# ========================================
@resume_bp.route("/<int:resume_id>", methods=["GET"])
@jwt_required()
def get_resume(resume_id):
    """Get resume details and ATS analysis"""
    current_user_id = get_jwt_identity()
    
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user_id).first()
    
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    return jsonify(resume.to_dict()), 200

# ========================================
# GET ALL USER RESUMES
# ========================================
@resume_bp.route("/list", methods=["GET"])
@jwt_required()
def list_resumes():
    """Get all resumes for current user"""
    current_user_id = get_jwt_identity()
    
    resumes = Resume.query.filter_by(user_id=current_user_id).order_by(Resume.created_at.desc()).all()
    
    return jsonify({
        "resumes": [r.to_dict() for r in resumes],
        "count": len(resumes)
    }), 200

# ========================================
# DELETE RESUME
# ========================================
@resume_bp.route("/<int:resume_id>", methods=["DELETE"])
@jwt_required()
def delete_resume(resume_id):
    """Delete resume and file"""
    current_user_id = get_jwt_identity()
    
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user_id).first()
    
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    # Delete file from disk
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete from database
    db.session.delete(resume)
    db.session.commit()
    
    return jsonify({"message": "Resume deleted successfully"}), 200

# ========================================
# HELPER: Parse Resume Structure
# ========================================
def parse_resume_structure(text):
    """
    Extract structured data from resume text
    Returns: Dictionary with sections
    """
    # Basic parsing - we'll improve this with AI later
    import re
    
    sections = {
        "contact": {},
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
        "projects": []
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        sections["contact"]["email"] = email_match.group(0)
    
    # Extract phone
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        sections["contact"]["phone"] = phone_match.group(0)
    
    # Extract skills (common keywords)
    skills_keywords = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'git']
    text_lower = text.lower()
    found_skills = [skill for skill in skills_keywords if skill in text_lower]
    sections["skills"] = found_skills
    
    # More sophisticated parsing would use AI here
    # For now, return basic structure
    
    return sections
