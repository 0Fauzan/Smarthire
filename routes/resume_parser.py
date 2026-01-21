import os
from flask import Blueprint, jsonify
from models.user import User
from PyPDF2 import PdfReader
from docx import Document

resume_bp = Blueprint("resume", __name__)

UPLOAD_FOLDER = "uploads/resumes"


def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()


def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs).strip()


@resume_bp.route("/parse/<email>", methods=["GET"])
def parse_resume(email):
    user = User.query.filter_by(email=email).first()

    if not user or not user.resume_path:
        return jsonify({"error": "Resume not found"}), 404

    file_path = user.resume_path

    if not os.path.exists(file_path):
        return jsonify({"error": "File missing on server"}), 404

    try:
        if file_path.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        return jsonify({
            "message": "Resume parsed successfully",
            "text_preview": text[:1500],  # preview only
            "length": len(text)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
