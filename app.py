import os

# Use environment variables for sensitive information
SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
HF_API_TOKEN = os.environ.get('HF_API_TOKEN', 'default_hf_api_token')

# ... (rest of your app.py code here)