from typing import Dict, List
from services.ai_service import SmartHireAI


class InterviewEvaluator:
    """
    Interview answer evaluation using unified AI
    """

    def __init__(self):
        self.ai = SmartHireAI()

    def evaluate_answer(
        self,
        question_text: str,
        answer_text: str,
        interview_type: str = "hr",
    ) -> Dict:
        """
        Evaluate single answer via unified AI service.
        """
        return self.ai.evaluate_answer(
            question_text=question_text,
            answer_text=answer_text,
            interview_type=interview_type,
        )
    
    def _evaluate_behavioral_answer(self, question, answer):
        """
        Evaluate behavioral/HR answer using STAR framework
        """
        prompt = f"""You are an expert HR interviewer evaluating a candidate's answer.

Question: {question}

Candidate's Answer:
{answer}

Evaluate this answer on a 0-100 scale based on:
1. STAR Method Usage (Did they describe Situation, Task, Action, Result?)
2. Specificity (Concrete examples vs vague statements)
3. Relevance (Directly answers the question)
4. Communication (Clear, well-organized, appropriate length)
5. Impact (Shows measurable results and learning)

Provide detailed feedback in JSON format:
{{
  "score": 75,
  "technical_score": 75,
  "communication_score": 80,
  "star_components": {{
    "situation": true,
    "task": true,
    "action": true,
    "result": false
  }},
  "strengths": ["Clear structure", "Good example"],
  "improvements": ["Add specific metrics", "Mention what you learned"],
  "model_answer": "A strong answer would be: In my previous role at...",
  "time_quality": "appropriate"
}}

Be specific and constructive in feedback.
"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            evaluation = json.loads(response_text)
            
            # Ensure required fields
            if 'score' not in evaluation:
                evaluation['score'] = 70
            if 'strengths' not in evaluation:
                evaluation['strengths'] = ["Answer provided"]
            if 'improvements' not in evaluation:
                evaluation['improvements'] = ["Could be more specific"]
            
            return evaluation
            
        except Exception as e:
            print(f"Evaluation error: {e}")
            # Return fallback evaluation
            return self._fallback_evaluation(answer)
    
    def _evaluate_technical_answer(self, question, answer):
        """
        Evaluate technical answer
        """
        prompt = f"""You are a senior technical interviewer evaluating a candidate's answer.

Question: {question}

Candidate's Answer:
{answer}

Evaluate on a 0-100 scale based on:
1. Technical Accuracy (Is the answer correct?)
2. Depth of Understanding (Surface level vs deep knowledge)
3. Clarity of Explanation (Can non-experts understand?)
4. Completeness (Did they cover all aspects?)
5. Practical Application (Real-world relevance)

Provide feedback in JSON format:
{{
  "score": 80,
  "technical_score": 85,
  "communication_score": 75,
  "strengths": ["Technically accurate", "Good examples"],
  "improvements": ["Could explain trade-offs", "Add code example"],
  "model_answer": "A comprehensive answer would include...",
  "accuracy": "correct"
}}
"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            print(f"Technical evaluation error: {e}")
            return self._fallback_evaluation(answer)
    
    def _evaluate_general_answer(self, question, answer):
        """
        Evaluate general interview answer
        """
        prompt = f"""Evaluate this interview answer on a 0-100 scale.

Question: {question}
Answer: {answer}

Provide JSON feedback:
{{
  "score": 75,
  "technical_score": 75,
  "communication_score": 80,
  "strengths": ["Clear communication"],
  "improvements": ["Be more specific"],
  "model_answer": "A better answer would..."
}}
"""

        try:
            message = self.client.messages.create(
                model="claude-haiku-4-20250514",  # Faster model for general eval
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            print(f"General evaluation error: {e}")
            return self._fallback_evaluation(answer)
    
    def _fallback_evaluation(self, answer):
        """
        Simple fallback when AI fails
        """
        word_count = len(answer.split())
        
        # Basic scoring based on length
        if word_count < 30:
            score = 50
            feedback = "Answer is too brief. Provide more detail."
        elif word_count < 80:
            score = 65
            feedback = "Good start, but could be more comprehensive."
        elif word_count < 150:
            score = 75
            feedback = "Solid answer with good detail."
        else:
            score = 70
            feedback = "Comprehensive but could be more concise."
        
        return {
            "score": score,
            "technical_score": score,
            "communication_score": score,
            "strengths": ["Answer provided"],
            "improvements": [feedback],
            "model_answer": "A strong answer would include specific examples and measurable results.",
            "star_components": {
                "situation": False,
                "task": False,
                "action": False,
                "result": False
            }
        }
    
    def generate_overall_feedback(self, questions: List, overall_score: int) -> Dict:
        """
        Generate summary feedback for entire interview.
        This stays local (no extra AI calls) and looks at per‑question scores.
        """
        # Analyze patterns
        low_scoring = [q for q in questions if q.score and q.score < 70]
        high_scoring = [q for q in questions if q.score and q.score >= 85]

        # Identify weak areas
        weak_areas = []
        for q in low_scoring:
            if q.ai_evaluation:
                star = q.ai_evaluation.get("star_components", {})
                if not star.get("result"):
                    weak_areas.append("result_oriented_answers")
                if not star.get("situation"):
                    weak_areas.append("context_setting")

        # Overall assessment
        if overall_score >= 85:
            assessment = "Excellent performance! You're interview-ready."
            readiness = "interview_ready"
        elif overall_score >= 70:
            assessment = "Good performance with room for improvement."
            readiness = "almost_ready"
        else:
            assessment = "Needs more practice before live interviews."
            readiness = "needs_practice"

        strengths: List[str] = []
        improvements: List[str] = []

        if len(high_scoring) > len(low_scoring):
            strengths.append("Consistently strong answers across multiple questions.")

        if "result_oriented_answers" in weak_areas:
            improvements.append(
                "Add measurable results and clear outcomes to your answers."
            )

        if "context_setting" in weak_areas:
            improvements.append(
                "Set the scene more clearly at the start of each answer (who, what, when, where)."
            )

        if not improvements:
            improvements.append(
                "Keep practicing to maintain and further improve consistency."
            )

        return {
            "overall_assessment": assessment,
            "readiness_level": readiness,
            "strengths": strengths or ["Answer quality was adequate."],
            "improvements": improvements,
            "weak_areas": list(set(weak_areas)),
            "questions_mastered": len(high_scoring),
            "questions_need_work": len(low_scoring),
        }
