import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "smarthire_secret_key"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "database", "smarthire.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")

    # Image upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "profile_images")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    VIDEO_UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "interview_videos")
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov"}
