from typing import List, Optional, Dict
from services.ai_service import SmartHireAI


class InterviewEngine:
    """
    Interview question generation using unified AI
    """

    def __init__(self):
        self.ai = SmartHireAI()

    def generate_questions(
        self,
        interview_type: str,
        resume_data: Optional[Dict] = None,
        language: Optional[str] = None,
    ) -> List[str]:
        """
        Generate interview questions via the unified AI service.
        Fallback behavior (e.g. heuristic questions) is handled
        inside SmartHireAI, so this layer stays very thin.
        """
        return self.ai.generate_interview_questions(
            interview_type=interview_type,
            resume_data=resume_data,
            language=language,
        )
