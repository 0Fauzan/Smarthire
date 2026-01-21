from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.user import User
from models.company import Company

from services.hr_ranking import calculate_candidate_score, classify_candidate
from services.recommendation_engine import (
    recommend_companies,
    recommend_candidates
)

hr_bp = Blueprint("hr", __name__)
def hr_dashboard():
    user = get_jwt_identity()

    if user["role"] != "hr":
         return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"message": f"Welcome to the HR dashboard, {user['name']}!"}), 200

# -------------------------------------------------
# HR dashboard (health check)
# -------------------------------------------------
@hr_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return jsonify({
        "features": [
            "Candidate Ranking & Shortlisting",
            "Interview Score Review",
            "Talent–Company Recommendation Engine"
        ]
    })


# -------------------------------------------------
# Rank all candidates
# -------------------------------------------------
@hr_bp.route("/rank-candidates", methods=["GET"])
def rank_candidates():
    candidates = User.query.filter_by(role="candidate").all()

    ranked = []

    for candidate in candidates:
        scores = calculate_candidate_score(candidate.id)
        status = classify_candidate(scores["total_score"])

        ranked.append({
            "user_id": candidate.id,
            "name": candidate.name,
            "resume_score": scores["resume_score"],
            "interview_score": scores["interview_score"],
            "total_score": scores["total_score"],
            "status": status
        })

    ranked.sort(key=lambda x: x["total_score"], reverse=True)

    return jsonify({
        "message": "Candidates ranked successfully",
        "candidates": ranked
    })


# -------------------------------------------------
# Add company (for demo / testing)
# -------------------------------------------------
@hr_bp.route("/add-company", methods=["POST"])
def add_company():
    data = request.json

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    company = Company(
        name=data["name"],
        role=data["role"],
        required_skills=",".join(data.get("required_skills", []))
    )

    db.session.add(company)
    db.session.commit()

    return jsonify({
        "message": "Company added successfully",
        "company": company.to_dict()
    })


# -------------------------------------------------
# Recommend companies for a candidate
# -------------------------------------------------
@hr_bp.route("/recommend-companies/<int:user_id>", methods=["GET"])
def recommend_companies_for_candidate(user_id):
    results = recommend_companies(user_id)

    return jsonify({
        "message": "Company recommendations generated",
        "recommendations": results
    })


# -------------------------------------------------
# Recommend candidates for a company
# -------------------------------------------------
@hr_bp.route("/recommend-candidates/<int:company_id>", methods=["GET"])
def recommend_candidates_for_company(company_id):
    results = recommend_candidates(company_id)

    return jsonify({
        "message": "Candidate recommendations generated",
        "candidates": results
    })
