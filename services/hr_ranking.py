from models.resume import Resume
from models.interview import Interview


def calculate_candidate_score(user_id):
    """
    Combines resume completeness and interview score
    """

    resume = Resume.query.filter_by(user_id=user_id).first()
    interview = Interview.query.filter_by(user_id=user_id).first()

    resume_score = 0

    if resume:
        fields = [
            resume.full_name,
            resume.role,
            resume.degree,
            resume.institution,
            resume.technical_skills,
            resume.project_title,
            resume.experience,
        ]

        # Each filled field adds weight
        resume_score = sum(1 for f in fields if f) * 5  # max ~35

    interview_score = interview.final_score if interview else 0

    total_score = resume_score + interview_score

    return {
        "user_id": user_id,
        "resume_score": resume_score,
        "interview_score": interview_score,
        "total_score": total_score
    }


def classify_candidate(total_score):
    if total_score >= 80:
        return "Recommended"
    elif total_score >= 60:
        return "Maybe"
    else:
        return "Rejected"
