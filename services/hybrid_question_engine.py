from models.resume import Resume
from models.interview_answer import InterviewAnswer
from services.hf_question_engine import hf_generate_questions

# =================================================
# RULE-BASED QUESTION BANK (FALLBACK)
# =================================================

QUESTION_BANK = {
    "basic": {
        "General": [
            "Introduce yourself.",
            "Explain your main project.",
            "What subjects are you most comfortable with?"
        ]
    },
    "medium": {
        "Python": [
            "What is the difference between list and tuple in Python?",
            "How does Python handle memory management?"
        ],
        "Flask": [
            "How does Flask handle routing?",
            "Explain Flask Blueprints."
        ],
        "Linux": [
            "What is a process in Linux?",
            "Explain chmod and chown."
        ]
    },
    "hard": {
        "Python": [
            "Explain Python decorators with real use cases.",
            "How would you optimize Python code for performance?"
        ],
        "Flask": [
            "Explain Flask request lifecycle.",
            "How would you design a scalable Flask application?"
        ],
        "Linux": [
            "How does Linux manage processes internally?",
            "Explain signals and process states in Linux."
        ]
    }
}

# =================================================
# CONFIDENCE → DIFFICULTY MAPPING
# =================================================

def get_confidence_level(user_id):
    """
    Determines difficulty level based on
    average confidence score from video analysis
    """
    answers = InterviewAnswer.query.filter_by(user_id=user_id).all()

    if not answers:
        return "basic"

    avg_confidence = sum(a.confidence_score for a in answers) / len(answers)

    if avg_confidence >= 75:
        return "hard"
    elif avg_confidence >= 60:
        return "medium"
    else:
        return "basic"


# =================================================
# RULE-BASED QUESTION GENERATOR (FALLBACK)
# =================================================

def rule_based_questions(resume, level, max_questions=4):
    questions = []
    bank = QUESTION_BANK.get(level, {})

    skills = []
    if resume and resume.technical_skills:
        skills = [s.strip() for s in resume.technical_skills.split(",")]

    for skill in skills:
        if skill in bank:
            questions.extend(bank[skill])
        if len(questions) >= max_questions:
            break

    if not questions:
        questions = bank.get("General", [])

    return questions[:max_questions]


# =================================================
# HYBRID AI QUESTION ENGINE (FINAL)
# =================================================

def generate_hybrid_questions(user_id, max_questions=4):
    """
    HYBRID QUESTION ENGINE

    Priority:
    1) Hugging Face FREE AI (CV-aware + difficulty-aware)
    2) Rule-based fallback (guaranteed output)
    """

    resume = Resume.query.filter_by(user_id=user_id).first()
    difficulty = get_confidence_level(user_id)

    skills = resume.technical_skills if resume else ""
    projects = resume.project_title if resume else ""

    # ---------------- AI PROMPT ----------------
    prompt = f"""
You are an AI technical interviewer.

Generate {max_questions} {difficulty}-level interview questions.

Candidate details:
Skills: {skills}
Projects: {projects}

Rules:
- Questions must be concise
- Mix technical and conceptual questions
- Do not number the questions
- Do not repeat questions
"""

    # ---------------- TRY AI (FREE HF) ----------------
    try:
        ai_questions = hf_generate_questions(prompt, max_questions)

        if ai_questions and len(ai_questions) >= 2:
            return {
                "source": "HuggingFace AI",
                "difficulty": difficulty,
                "questions": ai_questions
            }

    except Exception:
        pass  # Silent fail → fallback

    # ---------------- FALLBACK (RULE-BASED) ----------------
    fallback_questions = rule_based_questions(
        resume, difficulty, max_questions
    )

    return {
        "source": "Rule-Based Fallback",
        "difficulty": difficulty,
        "questions": fallback_questions
    }
