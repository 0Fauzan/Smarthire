from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db, jwt
import os
from flask_jwt_extended import JWTManager



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../frontend"))

def create_app():
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        static_url_path=""
    )

    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # -------------------------------
    # Register Blueprints
    # -------------------------------
    from routes.auth import auth_bp
    from routes.candidate import candidate_bp
    from routes.hr import hr_bp
    from routes.admin import admin_bp
    from routes.resume_parser import resume_bp
    from routes.ats_analyzer import ats_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(candidate_bp, url_prefix="/candidate")
    app.register_blueprint(hr_bp, url_prefix="/hr")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(resume_bp, url_prefix="/resume")
    app.register_blueprint(ats_bp, url_prefix="/ats")


    # -------------------------------
    # FRONTEND ROUTES
    # -------------------------------
    @app.route("/")
    def serve_index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:path>")
    def serve_frontend_files(path):
        return send_from_directory(FRONTEND_DIR, path)

    # -------------------------------
    # Create DB tables (DEV only)
    # -------------------------------
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
