from models.resume import Resume
from models.company import Company


def match_score(candidate_skills, company_skills):
    if not candidate_skills or not company_skills:
        return 0

    candidate_set = set(candidate_skills)
    company_set = set(company_skills)

    matched = candidate_set.intersection(company_set)
    score = int((len(matched) / len(company_set)) * 100)

    return score


# ------------------------------------
# Recommend companies for a candidate
# ------------------------------------
def recommend_companies(user_id):
    resume = Resume.query.filter_by(user_id=user_id).first()
    companies = Company.query.all()

    if not resume or not resume.technical_skills:
        return []

    candidate_skills = resume.technical_skills.split(",")

    recommendations = []

    for company in companies:
        score = match_score(
            candidate_skills,
            company.required_skills.split(",")
            if company.required_skills else []
        )

        recommendations.append({
            "company": company.name,
            "role": company.role,
            "match_percentage": score
        })

    return sorted(recommendations, key=lambda x: x["match_percentage"], reverse=True)


# ------------------------------------
# Recommend candidates for a company
# ------------------------------------
def recommend_candidates(company_id):
    company = Company.query.get(company_id)
    resumes = Resume.query.all()

    if not company or not company.required_skills:
        return []

    company_skills = company.required_skills.split(",")

    matches = []

    for resume in resumes:
        if not resume.technical_skills:
            continue

        score = match_score(
            resume.technical_skills.split(","),
            company_skills
        )

        matches.append({
            "user_id": resume.user_id,
            "name": resume.full_name,
            "match_percentage": score
        })

    return sorted(matches, key=lambda x: x["match_percentage"], reverse=True)
