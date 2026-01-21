from extensions import db


class CommunicationAssessment(db.Model):
    __tablename__ = "communication_assessments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
