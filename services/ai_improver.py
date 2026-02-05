from services.ai_service import SmartHireAI

class AIResumeImprover:
    """
    Resume improvement using unified AI service
    """
    
    def __init__(self):
        self.ai = SmartHireAI()
    
    def improve_resume(self, original_text, ats_feedback, current_score):
        """
        Improve resume - delegates to unified AI
        """
        return self.ai.improve_resume(original_text, ats_feedback, current_score)
