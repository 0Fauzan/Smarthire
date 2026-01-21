import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from extensions import db
from models.user import User

candidate_bp = Blueprint("candidate", __name__)

# ===============================
# CONFIG
# ===============================
UPLOAD_FOLDER = "uploads/resumes"
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===============================
# HELPERS
# ===============================
def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# ===============================
# RESUME UPLOAD ROUTE
# ===============================
@candidate_bp.route("/upload-resume", methods=["POST"])
def upload_resume():
    email = request.form.get("email")
    file = request.files.get("resume")

    # Validate request
    if not email:
        return jsonify({"error": "Email is required"}), 400

    if not file:
        return jsonify({"error": "Resume file is required"}), 400

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Invalid file type. Only PDF, DOC, DOCX allowed"
        }), 400

    # Find user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Save file
    filename = secure_filename(file.filename)
    filename = f"user_{user.id}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({"error": "Failed to save file"}), 500

    # Update DB
    user.resume_path = filepath
    db.session.commit()

    return jsonify({
        "message": "Resume uploaded successfully",
        "file": filename
    }), 200

     # ✅ Extract text
    extracted_text = extract_text_from_resume(filepath)

    # ✅ Save to DB
    user.resume_path = filepath
    user.resume_text = extracted_text
    db.session.commit()

    return jsonify({
        "message": "Resume uploaded & parsed successfully",
        "characters": len(extracted_text)
    }), 200
