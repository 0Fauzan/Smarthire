import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # --- Database Configuration ---
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL") or
        'sqlite:///' + os.path.join(BASE_DIR, 'database', 'smarthire.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- Security & JWT ---
    # Read from .env file (secure way)
    SECRET_KEY = os.getenv("SECRET_KEY", "1Oi1UJMrkfnJA_SNjoqyqFDwvS5KCcGB31nzjOuLRes")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "3TEmaq5h7U8kAKDUTCNaBmnNbNscDpy04awXQLI2XjA")
    
    # --- File Management ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    RESUME_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'resumes')
    ALLOWED_RESUME_EXTENSIONS = {'pdf', 'docx', 'doc'}
    
    # --- AI Settings ---
    # Read from .env file
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # HuggingFace model
    HF_MODEL_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    
    # Environment
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"
