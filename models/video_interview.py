from extensions import db


class VideoInterview(db.Model):
    __tablename__ = "video_interviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    video_path = db.Column(db.String(400))

    total_frames = db.Column(db.Integer)
    frames_with_face = db.Column(db.Integer)
    face_percentage = db.Column(db.Float)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "video_path": self.video_path,
            "total_frames": self.total_frames,
            "frames_with_face": self.frames_with_face,
            "face_percentage": self.face_percentage
        }
