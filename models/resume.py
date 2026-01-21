from extensions import db


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    # Basic Info
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(100))

    # Profile Image (NEW)
    profile_image = db.Column(db.String(300))

    # Education
    degree = db.Column(db.String(100))
    institution = db.Column(db.String(150))
    graduation_year = db.Column(db.String(10))
    cgpa = db.Column(db.String(10))

    # Skills
    technical_skills = db.Column(db.Text)
    tools = db.Column(db.Text)

    # Projects
    project_title = db.Column(db.String(150))
    project_description = db.Column(db.Text)
    project_tech = db.Column(db.Text)

    # Experience
    experience = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "role": self.role,
            "profile_image": self.profile_image,
            "degree": self.degree,
            "institution": self.institution,
            "graduation_year": self.graduation_year,
            "cgpa": self.cgpa,
            "technical_skills": self.technical_skills,
            "tools": self.tools,
            "project_title": self.project_title,
            "project_description": self.project_description,
            "project_tech": self.project_tech,
            "experience": self.experience
        }
