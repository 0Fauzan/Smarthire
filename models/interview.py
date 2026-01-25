# models/interview.py
from extensions import db
from datetime import datetime

class Interview(db.Model):
    __tablename__ = "interviews"
    
    # Primary Info
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=True)
    
    # Interview Type
    interview_type = db.Column(db.String(50), nullable=False)  # hr, technical, ai_mock, coding
    language = db.Column(db.String(50), nullable=True)  # For technical: python, java, javascript
    
    # Status
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, abandoned
    
    # Scores
    overall_score = db.Column(db.Integer)  # 0-100 final score
    technical_score = db.Column(db.Integer)  # Technical accuracy
    communication_score = db.Column(db.Integer)  # Clarity, structure
    confidence_score = db.Column(db.Integer)  # Body language (for video)
    star_method_score = db.Column(db.Integer)  # STAR framework usage
    
    # Performance Metrics
    total_questions = db.Column(db.Integer, default=0)
    questions_answered = db.Column(db.Integer, default=0)
    average_response_time = db.Column(db.Integer)  # Average seconds per answer
    duration_seconds = db.Column(db.Integer)  # Total interview duration
    
    # AI Feedback (JSON)
    ai_feedback = db.Column(db.JSON)
    """
    ai_feedback structure:
    {
        "overall_assessment": "Strong technical knowledge but answers lack specificity",
        "strengths": ["Clear communication", "Good examples"],
        "improvements": ["Add more metrics", "Use STAR method consistently"],
        "weak_areas": ["conflict_resolution", "leadership"],
        "readiness_level": "interview_ready"  # needs_practice, almost_ready, interview_ready
    }
    """
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    questions = db.relationship('InterviewQuestion', backref='interview', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Interview {self.id} ({self.interview_type}) - Score: {self.overall_score}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "resume_id": self.resume_id,
            "interview_type": self.interview_type,
            "language": self.language,
            "status": self.status,
            "overall_score": self.overall_score,
            "technical_score": self.technical_score,
            "communication_score": self.communication_score,
            "confidence_score": self.confidence_score,
            "star_method_score": self.star_method_score,
            "total_questions": self.total_questions,
            "questions_answered": self.questions_answered,
            "average_response_time": self.average_response_time,
            "duration_seconds": self.duration_seconds,
            "ai_feedback": self.ai_feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def get_readiness_status(self):
        """Get interview readiness level"""
        if not self.overall_score:
            return "Not Completed"
        if self.overall_score >= 85:
            return "Interview Ready"
        elif self.overall_score >= 70:
            return "Almost Ready"
        else:
            return "Needs Practice"
    
    def get_score_color(self):
        """Get color for frontend"""
        if not self.overall_score:
            return "gray"
        if self.overall_score >= 85:
            return "green"
        elif self.overall_score >= 70:
            return "yellow"
        else:
            return "red"
    
    def calculate_overall_score(self):
        """Calculate weighted overall score"""
        if not self.technical_score or not self.communication_score:
            return None
        
        # Weighted average
        weights = {
            'technical': 0.40,
            'communication': 0.30,
            'confidence': 0.15,
            'star_method': 0.15
        }
        
        score = (
            self.technical_score * weights['technical'] +
            self.communication_score * weights['communication'] +
            (self.confidence_score or 75) * weights['confidence'] +
            (self.star_method_score or 75) * weights['star_method']
        )
        
        return round(score)
