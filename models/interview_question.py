# models/interview_question.py (CREATE THIS NEW FILE)
from extensions import db
from datetime import datetime

class InterviewQuestion(db.Model):
    __tablename__ = "interview_questions"
    
    # Primary Info
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    
    # Question Details
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50))  # behavioral, technical, situational
    question_order = db.Column(db.Integer)  # Order in interview (1, 2, 3...)
    
    # Answer
    candidate_answer = db.Column(db.Text)
    time_taken_seconds = db.Column(db.Integer)  # How long to answer
    
    # Evaluation
    score = db.Column(db.Integer)  # 0-100 for this specific answer
    ai_evaluation = db.Column(db.JSON)
    """
    ai_evaluation structure:
    {
        "score": 75,
        "strengths": ["Used STAR method", "Specific example"],
        "improvements": ["Add metrics", "Mention outcome"],
        "star_components": {
            "situation": true,
            "task": true,
            "action": true,
            "result": false  # Missing
        },
        "model_answer": "In my previous role at XYZ Corp (Situation)..."
    }
    """
    
    # Timestamps
    asked_at = db.Column(db.DateTime, default=datetime.utcnow)
    answered_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f"<Question {self.id} (Score: {self.score})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "interview_id": self.interview_id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "question_order": self.question_order,
            "candidate_answer": self.candidate_answer,
            "time_taken_seconds": self.time_taken_seconds,
            "score": self.score,
            "ai_evaluation": self.ai_evaluation,
            "asked_at": self.asked_at.isoformat() if self.asked_at else None,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
        }
