# models/resume.py
from extensions import db
from datetime import datetime

class Resume(db.Model):
    __tablename__ = "resumes"
    
    # Primary Info
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File Info
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)  # Path to uploaded file
    original_text = db.Column(db.Text)  # Extracted text from PDF/DOCX
    file_size = db.Column(db.Integer)  # Size in bytes
    file_type = db.Column(db.String(10))  # pdf, docx, doc
    
    # Parsed Data (JSON - flexible storage)
    parsed_data = db.Column(db.JSON)  # Store all parsed resume data as JSON
    
    # ATS Analysis (CRITICAL for SmartHire)
    ats_score = db.Column(db.Integer)  # 0-100
    ats_feedback = db.Column(db.JSON)  # Detailed breakdown
    """
    ats_feedback structure:
    {
        "score": 75,
        "breakdown": {
            "keywords": 80,
            "formatting": 70,
            "completeness": 75,
            "length": 85
        },
        "issues": [
            {"type": "keywords", "severity": "high", "message": "Missing: Python, React"},
            {"type": "formatting", "severity": "medium", "message": "Inconsistent dates"}
        ],
        "suggestions": [
            "Add technical keywords: API, cloud, CI/CD",
            "Use consistent date format: MM/YYYY"
        ]
    }
    """
    
    # AI Improved Version
    improved_text = db.Column(db.Text)  # AI-rewritten resume
    improved_score = db.Column(db.Integer)  # Score after AI improvement
    improvement_applied = db.Column(db.Boolean, default=False)
    
    # Status
    is_primary = db.Column(db.Boolean, default=True)  # User's main resume
    status = db.Column(db.String(20), default='active')  # active / archived
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = db.Column(db.DateTime)  # When ATS analysis was done
    
    def __repr__(self):
        return f"<Resume {self.filename} (Score: {self.ats_score})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "ats_score": self.ats_score,
            "ats_feedback": self.ats_feedback,
            "improved_score": self.improved_score,
            "improvement_applied": self.improvement_applied,
            "parsed_data": self.parsed_data,
            "is_primary": self.is_primary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
        }
    
    def get_ats_status(self):
        """Get human-readable ATS status"""
        if not self.ats_score:
            return "Not Analyzed"
        if self.ats_score >= 85:
            return "Excellent"
        elif self.ats_score >= 70:
            return "Good"
        else:
            return "Needs Improvement"
    
    def get_score_color(self):
        """Get color code for frontend display"""
        if not self.ats_score:
            return "gray"
        if self.ats_score >= 85:
            return "green"
        elif self.ats_score >= 70:
            return "yellow"
        else:
            return "red"
