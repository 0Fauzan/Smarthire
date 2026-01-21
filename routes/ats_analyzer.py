import re
from flask import Blueprint, jsonify
from models.user import User
from routes.resume_parser import extract_text_from_pdf, extract_text_from_docx
import os

ats_bp = Blueprint("ats", __name__)

# -------------------------------
# ATS KEYWORDS (BASELINE)
# -------------------------------
SKILLS = [
    "python", "java", "c", "c++", "sql", "mysql", "postgresql",
    "html", "css", "javascript", "react", "node", "flask",
    "django", "git", "github", "linux", "docker", "kubernetes",
    "aws", "azure", "devops", "machine learning", "ai"
]

EDUCATION_KEYWORDS = [
    "b.tech", "bachelor", "master", "m.tech", "degree",
    "computer science", "engineering", "information technology"
]

EXPERIENCE_KEYWORDS = [
    "intern", "internship", "experience", "project",
    "worked on", "developed", "implemented"
]


# -------------------------------
# UTILITIES
# -------------------------------
def normalize(text):
    return re.sub(r"\s+", " ", text.lower())


def extract_keywords(text, keyword_list):
    found = []
    for keyword in keyword_list:
        if keyword in text:
            found.append(keyword)
    return list(set(found))


# -------------------------------
# ATS ANALYSIS ROUTE
# -------------------------------
@ats_bp.route("/analyze/<email>", methods=["GET"])
def analyze_resume(email):

    user = User.query.filter_by(email=email).first()

    if not user or not user.resume_path:
        return jsonify({"error": "Resume not found"}), 404

    file_path = user.resume_path

    if not os.path.exists(file_path):
        return jsonify({"error": "Resume file missing"}), 404

    # Extract text
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    text = normalize(text)

    # ATS extraction
    skills_found = extract_keywords(text, SKILLS)
    education_found = extract_keywords(text, EDUCATION_KEYWORDS)
    experience_found = extract_keywords(text, EXPERIENCE_KEYWORDS)

    # -------------------------------
    # ATS SCORING LOGIC (REALISTIC)
    # -------------------------------
    score = 0
    score += min(len(skills_found) * 5, 50)        # Skills: max 50
    score += min(len(experience_found) * 10, 30)   # Experience: max 30
    score += 20 if education_found else 0           # Education: max 20

    score = min(score, 100)

    return jsonify({
        "ats_score": score,
        "skills_detected": skills_found,
        "education_detected": education_found,
        "experience_signals": experience_found,
        "resume_strength": (
            "Strong" if score >= 75 else
            "Average" if score >= 50 else
            "Weak"
        )
    }), 200
