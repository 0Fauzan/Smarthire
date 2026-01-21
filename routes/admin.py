from flask import Blueprint, jsonify, request
from extensions import db

from models.resume import Resume
from models.interview_answer import InterviewAnswer
from models.communication import CommunicationAssessment
from models.shortlist import Shortlist

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# -------------------------------------------------
# 1. VIEW ALL CANDIDATES
# -------------------------------------------------
@admin_bp.route("/candidates", methods=["GET"])
def view_candidates():
    resumes = Resume.query.all()

    return jsonify([
        {
            "user_id": r.user_id,
            "name": r.full_name,
            "role": r.role,
            "skills": r.technical_skills
        } for r in resumes
    ])


# -------------------------------------------------
# 2. CANDIDATE FULL PROFILE (HR VIEW)
# -------------------------------------------------
@admin_bp.route("/candidate/<int:user_id>", methods=["GET"])
def candidate_profile(user_id):
    resume = Resume.query.filter_by(user_id=user_id).first()
    answers = InterviewAnswer.query.filter_by(user_id=user_id).all()
    communication = CommunicationAssessment.query.filter_by(user_id=user_id).all()

    if not resume:
        return jsonify({"error": "Candidate not found"}), 404

    avg_confidence = (
        sum(a.confidence_score for a in answers) / len(answers)
        if answers else 0
    )

    avg_communication = (
        sum(c.score for c in communication) / len(communication)
        if communication else 0
    )

    final_score = round(
        (avg_confidence * 0.7) + (avg_communication * 0.3)
    )

    return jsonify({
        "resume": resume.to_dict(),
        "scores": {
            "confidence": round(avg_confidence),
            "communication": round(avg_communication),
            "final_score": final_score
        }
    })


# -------------------------------------------------
# 3. SORT / FILTER CANDIDATES BY SCORE
# -------------------------------------------------
@admin_bp.route("/ranked-candidates", methods=["GET"])
def ranked_candidates():
    resumes = Resume.query.all()
    ranking = []

    for r in resumes:
        answers = InterviewAnswer.query.filter_by(user_id=r.user_id).all()
        communication = CommunicationAssessment.query.filter_by(user_id=r.user_id).all()

        if not answers:
            continue

        avg_conf = sum(a.confidence_score for a in answers) / len(answers)
        avg_comm = (
            sum(c.score for c in communication) / len(communication)
            if communication else 60
        )

        final_score = round((avg_conf * 0.7) + (avg_comm * 0.3))

        ranking.append({
            "user_id": r.user_id,
            "name": r.full_name,
            "final_score": final_score
        })

    ranking.sort(key=lambda x: x["final_score"], reverse=True)
    return jsonify(ranking)


# -------------------------------------------------
# 4. SHORTLIST CANDIDATE
# -------------------------------------------------
@admin_bp.route("/shortlist/<int:user_id>", methods=["POST"])
def shortlist_candidate(user_id):
    record = Shortlist(user_id=user_id)
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "message": f"Candidate {user_id} shortlisted"
    })


# -------------------------------------------------
# 5. VIEW SHORTLISTED CANDIDATES
# -------------------------------------------------
@admin_bp.route("/shortlisted", methods=["GET"])
def shortlisted_candidates():
    records = Shortlist.query.all()

    return jsonify([
        {
            "user_id": r.user_id,
            "status": r.status
        } for r in records
    ])
