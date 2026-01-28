# routes/ats_analyzer.py
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from extensions import db
from models.user import User
from models.resume import Resume
from services.ats_scorer import ATSScorer
from services.ai_improver import AIResumeImprover  # We'll create this

ats_bp = Blueprint("ats", __name__)

# ========================================
# ANALYZE RESUME (Get ATS Score)
# ========================================
@ats_bp.route("/analyze/<int:resume_id>", methods=["POST"])
@jwt_required()
def analyze_resume(resume_id):
    """
    Re-analyze an existing resume
    Useful if scoring algorithm improves
    """
    current_user_id = get_jwt_identity()
    
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user_id).first()
    
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    try:
        # Re-parse if needed
        from routes.resume_parser import parse_resume_structure
        parsed_data = parse_resume_structure(resume.original_text)
        
        # Re-calculate ATS score
        ats_scorer = ATSScorer()
        ats_result = ats_scorer.calculate_ats_score(resume.original_text, parsed_data)
        
        # Update resume record
        resume.parsed_data = parsed_data
        resume.ats_score = ats_result['score']
        resume.ats_feedback = ats_result
        resume.analyzed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": "Resume re-analyzed successfully",
            "ats_score": ats_result['score'],
            "status": resume.get_ats_status(),
            "breakdown": ats_result['breakdown'],
            "issues": ats_result['issues'],
            "suggestions": ats_result['suggestions'],
            "ai_feedback": ats_result.get('ai_feedback')
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

# ========================================
# IMPROVE RESUME (AI-Powered Rewrite)
# ========================================
@ats_bp.route("/improve/<int:resume_id>", methods=["POST"])
@jwt_required()
def improve_resume(resume_id):
    """
    Use AI to rewrite resume and improve ATS score
    This is the KILLER FEATURE of SmartHire
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Check subscription limits
    if user.subscription_tier == 'free':
        # Check if they've already used AI improvement
        improved_resumes = Resume.query.filter_by(
            user_id=current_user_id, 
            improvement_applied=True
        ).count()
        
        if improved_resumes >= 1:  # Free tier limit
            return jsonify({
                "error": "Free tier limit reached",
                "message": "Upgrade to Pro for unlimited AI improvements",
                "upgrade_required": True
            }), 403
    
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user_id).first()
    
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    if not resume.ats_score:
        return jsonify({"error": "Please analyze resume first"}), 400
    
    if resume.improved_text:
        return jsonify({
            "message": "Resume already improved",
            "improved_text": resume.improved_text,
            "improved_score": resume.improved_score,
            "improvement": resume.improved_score - resume.ats_score
        }), 200
    
    try:
        # Use AI to improve resume
        improver = AIResumeImprover()
        improved_result = improver.improve_resume(
            original_text=resume.original_text,
            ats_feedback=resume.ats_feedback,
            current_score=resume.ats_score
        )
        
        # Re-score improved version
        from routes.resume_parser import parse_resume_structure
        improved_parsed = parse_resume_structure(improved_result['improved_text'])
        
        ats_scorer = ATSScorer()
        new_ats_result = ats_scorer.calculate_ats_score(
            improved_result['improved_text'], 
            improved_parsed
        )
        
        # Update resume record
        resume.improved_text = improved_result['improved_text']
        resume.improved_score = new_ats_result['score']
        resume.improvement_applied = True
        resume.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": "Resume improved successfully",
            "original_score": resume.ats_score,
            "improved_score": new_ats_result['score'],
            "improvement": new_ats_result['score'] - resume.ats_score,
            "improved_text": improved_result['improved_text'],
            "changes_made": improved_result['changes_made'],
            "new_feedback": new_ats_result
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Improvement failed: {str(e)}"}), 500

# ========================================
# COMPARE VERSIONS (Before/After)
# ========================================
@ats_bp.route("/compare/<int:resume_id>", methods=["GET"])
@jwt_required()
def compare_versions(resume_id):
    """
    Show side-by-side comparison of original vs improved
    """
    current_user_id = get_jwt_identity()
    
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user_id).first()
    
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    if not resume.improved_text:
        return jsonify({"error": "No improved version available"}), 400
    
    return jsonify({
        "original": {
            "text": resume.original_text,
            "score": resume.ats_score,
            "feedback": resume.ats_feedback
        },
        "improved": {
            "text": resume.improved_text,
            "score": resume.improved_score
        },
        "improvement": resume.improved_score - resume.ats_score,
        "status_change": {
            "before": resume.get_ats_status(),
            "after": Resume(ats_score=resume.improved_score).get_ats_status()
        }
    }), 200

# ========================================
# DOWNLOAD IMPROVED RESUME
# ========================================
@ats_bp.route("/download/<int:resume_id>", methods=["GET"])
@jwt_required()
def download_improved(resume_id):
    """
    Download improved resume as text file
    Later: Add PDF generation
    """
    current_user_id = get_jwt_identity()
    
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user_id).first()
    
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    if not resume.improved_text:
        return jsonify({"error": "No improved version available"}), 400
    
    from flask import Response
    
    # Create text file response
    return Response(
        resume.improved_text,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=improved_{resume.filename.replace('.pdf', '.txt').replace('.docx', '.txt')}"
        }
    )

# ========================================
# GET ATS TIPS
# ========================================
@ats_bp.route("/tips", methods=["GET"])
@jwt_required()
def get_ats_tips():
    """
    General ATS optimization tips
    """
    tips = [
        {
            "category": "Keywords",
            "tip": "Include relevant technical skills mentioned in job descriptions",
            "example": "Instead of 'coding', use specific languages: Python, Java, JavaScript"
        },
        {
            "category": "Formatting",
            "tip": "Use consistent date formats throughout your resume",
            "example": "Jan 2023 - Present (not 01/2023 mixed with January 2024)"
        },
        {
            "category": "Sections",
            "tip": "Include all standard sections: Contact, Summary, Experience, Education, Skills",
            "example": "Missing sections reduce ATS score by up to 25 points"
        },
        {
            "category": "Length",
            "tip": "Keep resume to 1-2 pages (400-800 words)",
            "example": "Too short looks inexperienced, too long gets skipped"
        },
        {
            "category": "Action Verbs",
            "tip": "Start bullet points with strong action verbs",
            "example": "Use: Built, Developed, Implemented, Led, Improved"
        },
        {
            "category": "Metrics",
            "tip": "Quantify achievements with numbers and percentages",
            "example": "'Improved performance by 40%' vs 'Made things faster'"
        }
    ]
    
    return jsonify({"tips": tips}), 200
