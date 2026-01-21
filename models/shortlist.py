from extensions import db


class Shortlist(db.Model):
    __tablename__ = "shortlists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="shortlisted")
