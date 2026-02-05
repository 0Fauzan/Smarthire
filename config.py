import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # --- Database Configuration ---
    # Using the BASE_DIR to correctly locate the database file
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'smarthire.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- Security & JWT ---
    # NOTE: It is best to load this from an environment variable (.env file)
    SECRET_KEY = "1Oi1UJMrkfnJA_SNjoqyqFDwvS5KCcGB31nzjOuLRes"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "3TEmaq5h7U8kAKDUTCNaBmnNbNscDpy04awXQLI2XjA")

    # --- File Management ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

    # --- AI Settings ---
    # This must be loaded in the app.py where the AI client is initialized
    HF_API_TOKEN = os.environ.get("HF_API_TOKEN", "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")
    HF_MODEL_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"