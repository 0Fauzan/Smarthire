from extensions import db


class InterviewAnswer(db.Model):
    __tablename__ = "interview_answers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    question_no = db.Column(db.Integer, nullable=False)

    video_path = db.Column(db.String(400))

    total_frames = db.Column(db.Integer)
    frames_with_face = db.Column(db.Integer)
    face_percentage = db.Column(db.Float)

    confidence_score = db.Column(db.Integer)
