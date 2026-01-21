def generate_ats_resume(resume):
    """
    Converts Resume DB object into ATS-friendly structured content
    """

    summary = (
        f"{resume.role} with academic background in {resume.degree}. "
        f"Skilled in {resume.technical_skills.replace(',', ', ')} "
        f"with hands-on experience through projects and internships."
    )

    ats_resume = {
        "name": resume.full_name,
        "role": resume.role,
        "summary": summary,

        "skills": resume.technical_skills.split(",") if resume.technical_skills else [],
        "tools": resume.tools.split(",") if resume.tools else [],

        "education": {
            "degree": resume.degree,
            "institution": resume.institution,
            "graduation_year": resume.graduation_year,
            "cgpa": resume.cgpa,
        },

        "project": {
            "title": resume.project_title,
            "description": resume.project_description,
            "technologies": resume.project_tech.split(",") if resume.project_tech else [],
        },

        "experience": resume.experience,
        "profile_image": resume.profile_image,
    }

    return ats_resume
