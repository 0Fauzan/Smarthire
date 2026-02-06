import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Load environment variables, with fallback defaults for local development
SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
HF_API_TOKEN = os.getenv('HF_API_TOKEN', 'your_default_hf_api_token')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///local.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Define your models here
class ExampleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Define your routes here
@app.route('/api/example', methods=['GET'])
def get_example():
    examples = ExampleModel.query.all()
    return jsonify([example.name for example in examples])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# WSGI application callable for Gunicorn
application = app