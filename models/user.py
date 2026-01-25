# models/user.py
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    
    # Basic Info
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False, default='candidate')  # candidate / hr / admin
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile Info
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    profile_image = db.Column(db.String(300), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # Subscription & Limits
    subscription_tier = db.Column(db.String(20), default='free')  # free / pro / enterprise
    interview_count = db.Column(db.Integer, default=0)  # Track usage
    max_interviews = db.Column(db.Integer, default=2)  # Free tier limit
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    interviews = db.relationship('Interview', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
    
    # Password helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Helper methods
    def can_take_interview(self):
        """Check if user has interview attempts remaining"""
        if self.subscription_tier == 'pro':
            return True
        return self.interview_count < self.max_interviews
    
    def increment_interview_count(self):
        """Increment interview counter"""
        self.interview_count += 1
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary (for API responses)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'profile_image': self.profile_image,
            'subscription_tier': self.subscription_tier,
            'interview_count': self.interview_count,
            'max_interviews': self.max_interviews,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
