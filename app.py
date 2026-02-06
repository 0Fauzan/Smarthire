import os

# Get configuration values from environment variables
SECRET_KEY = os.environ.get('SECRET_KEY')
HF_API_TOKEN = os.environ.get('HF_API_TOKEN')

# Set port; default to 8080 if not set
PORT = int(os.environ.get('PORT', 8080))

# Update database URI based on environment
if os.environ.get('DATABASE_URL'):
    DATABASE_URI = os.environ['DATABASE_URL']  # PostgreSQL for production
else:
    DATABASE_URI = 'sqlite:///local.db'  # SQLite for local development

# Existing code continues...
