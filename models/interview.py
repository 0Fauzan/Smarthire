from extensions import db


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    # Stored as plain text for now
    answers = db.Column(db.Text)

    # Mock AI scores
    technical_score = db.Column(db.Integer)
    communication_score = db.Column(db.Integer)
    confidence_score = db.Column(db.Integer)

    final_score = db.Column(db.Integer)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "technical_score": self.technical_score,
            "communication_score": self.communication_score,
            "confidence_score": self.confidence_score,
            "final_score": self.final_score
        }
