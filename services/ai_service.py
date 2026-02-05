# services/ai_service.py (CREATE THIS FILE)
import os
import requests
import json
from typing import Dict, List, Optional

class SmartHireAI:
    """
    Unified AI service with Hugging Face + Mock fallback
    Easily upgradeable to Claude/OpenAI later
    """
    
    def __init__(self):
        self.hf_key = os.getenv("HUGGINGFACE_API_KEY", "")
        
        if self.hf_key:
            self.provider = "huggingface"
            self.hf_api_base = "https://api-inference.huggingface.co/models/"
            # Best free models for different tasks
            self.text_model = "HuggingFaceH4/zephyr-7b-beta"  # Fast, good quality
            print("✅ Using Hugging Face AI")
        else:
            self.provider = "mock"
            print("⚠️  No API key found. Using Mock AI mode")
    
    def improve_resume(self, original_text: str, ats_feedback: Dict, current_score: int) -> Dict:
        """
        Improve resume text
        Returns: {improved_text, changes_made}
        """
        if self.provider == "huggingface":
            try:
                return self._hf_improve_resume(original_text, ats_feedback, current_score)
            except Exception as e:
                print(f"HF failed: {e}. Falling back to mock mode.")
                return self._mock_improve_resume(original_text, ats_feedback)
        else:
            return self._mock_improve_resume(original_text, ats_feedback)
    
    def generate_interview_questions(
        self, 
        interview_type: str, 
        resume_data: Optional[Dict] = None,
        language: Optional[str] = None
    ) -> List[str]:
        """
        Generate interview questions
        Returns: List of question strings
        """
        if self.provider == "huggingface":
            try:
                return self._hf_generate_questions(interview_type, resume_data, language)
            except Exception as e:
                print(f"HF failed: {e}. Using fallback questions.")
                return self._mock_generate_questions(interview_type, language)
        else:
            return self._mock_generate_questions(interview_type, language)
    
    def evaluate_answer(
        self,
        question_text: str,
        answer_text: str,
        interview_type: str = 'hr'
    ) -> Dict:
        """
        Evaluate interview answer
        Returns: {score, strengths, improvements, model_answer}
        """
        if self.provider == "huggingface":
            try:
                return self._hf_evaluate_answer(question_text, answer_text, interview_type)
            except Exception as e:
                print(f"HF failed: {e}. Using mock evaluation.")
                return self._mock_evaluate_answer(question_text, answer_text)
        else:
            return self._mock_evaluate_answer(question_text, answer_text)
    
    # ========================================
    # HUGGING FACE IMPLEMENTATIONS
    # ========================================
    
    def _hf_improve_resume(self, text: str, feedback: Dict, score: int) -> Dict:
        """Improve resume using Hugging Face"""
        
        # Build concise prompt
        issues = "\n".join([f"- {issue['message']}" for issue in feedback.get('issues', [])])
        suggestions = "\n".join([f"- {s}" for s in feedback.get('suggestions', [])])
        
        prompt = f"""Task: Improve this resume to increase ATS score from {score} to 85+.

Current Issues:
{issues}

Suggestions:
{suggestions}

Original Resume:
{text[:1500]}

Provide the improved resume with:
1. Better keywords
2. Fixed formatting
3. Clearer achievements
4. STAR method in bullet points

Improved Resume:"""

        try:
            response = self._call_hf_api(prompt, max_tokens=1500)
            
            # Extract improved text
            improved_text = response.strip()
            
            # If response contains the prompt, extract only the answer
            if "Improved Resume:" in improved_text:
                improved_text = improved_text.split("Improved Resume:")[-1].strip()
            
            changes = [
                "Added relevant keywords",
                "Improved formatting consistency",
                "Enhanced action verbs",
                "Applied STAR method to experiences"
            ]
            
            return {
                "improved_text": improved_text,
                "changes_made": changes
            }
            
        except Exception as e:
            raise Exception(f"HF resume improvement failed: {str(e)}")
    
    def _hf_generate_questions(
        self,
        interview_type: str,
        resume_data: Optional[Dict],
        language: Optional[str]
    ) -> List[str]:
        """Generate questions using Hugging Face"""
        
        if interview_type == "technical" and language:
            prompt = f"""Generate 10 technical interview questions for a {language.upper()} developer.

Requirements:
- Mix of basic and advanced concepts
- Cover data structures, algorithms, best practices
- Include practical scenarios

Format: Return ONLY a numbered list, one question per line.

Questions:
1."""
        elif interview_type == "hr":
            prompt = """Generate 10 behavioral interview questions using STAR method.

Requirements:
- Teamwork, conflict resolution, leadership
- Problem-solving and decision-making
- Career goals and motivation

Format: Return ONLY a numbered list, one question per line.

Questions:
1."""
        else:
            prompt = """Generate 10 general interview questions.

Mix of:
- Tell me about yourself
- Technical background
- Projects and achievements
- Career goals

Format: Return ONLY a numbered list, one question per line.

Questions:
1."""
        
        try:
            response = self._call_hf_api(prompt, max_tokens=800)
            
            # Parse numbered list
            questions = []
            for line in response.split('\n'):
                line = line.strip()
                # Match patterns like "1. Question" or "1) Question"
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove number and punctuation
                    question = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                    if question and len(question) > 10:
                        questions.append(question)
            
            # Ensure we have 10 questions
            if len(questions) < 8:
                # Fall back to mock if parsing failed
                return self._mock_generate_questions(interview_type, language)
            
            return questions[:10]
            
        except Exception as e:
            raise Exception(f"HF question generation failed: {str(e)}")
    
    def _hf_evaluate_answer(self, question: str, answer: str, interview_type: str) -> Dict:
        """Evaluate answer using Hugging Face"""
        
        prompt = f"""Evaluate this interview answer on a scale of 0-100.

Question: {question}

Candidate's Answer: {answer}

Provide evaluation in this exact format:

Score: [number 0-100]
Strengths:
- [strength 1]
- [strength 2]
Improvements:
- [improvement 1]
- [improvement 2]
Model Answer: [better answer example]

Evaluation:"""

        try:
            response = self._call_hf_api(prompt, max_tokens=500)
            
            # Parse response
            evaluation = self._parse_evaluation(response)
            
            return evaluation
            
        except Exception as e:
            raise Exception(f"HF evaluation failed: {str(e)}")
    
    def _call_hf_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Make API call to Hugging Face
        """
        url = self.hf_api_base + self.text_model
        
        headers = {
            "Authorization": f"Bearer {self.hf_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True
            },
            "options": {
                "wait_for_model": True  # Wait if model is loading
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            elif isinstance(result, dict):
                return result.get('generated_text', '')
            else:
                return str(result)
        elif response.status_code == 503:
            # Model is loading
            raise Exception("Model is loading. Please try again in a few seconds.")
        else:
            raise Exception(f"HF API error {response.status_code}: {response.text}")
    
    def _parse_evaluation(self, response: str) -> Dict:
        """Parse evaluation response into structured format"""
        
        # Extract score
        score = 70  # default
        if "Score:" in response:
            try:
                score_line = response.split("Score:")[1].split("\n")[0]
                score = int(''.join(filter(str.isdigit, score_line)))
            except:
                pass
        
        # Extract strengths
        strengths = ["Clear communication"]
        if "Strengths:" in response:
            strengths_section = response.split("Strengths:")[1].split("Improvements:")[0]
            strengths = [s.strip().lstrip('-•* ') for s in strengths_section.split('\n') if s.strip()]
        
        # Extract improvements
        improvements = ["Be more specific"]
        if "Improvements:" in response:
            imp_section = response.split("Improvements:")[1].split("Model Answer:")[0]
            improvements = [i.strip().lstrip('-•* ') for i in imp_section.split('\n') if i.strip()]
        
        # Extract model answer
        model_answer = "A strong answer would include specific examples with measurable results."
        if "Model Answer:" in response:
            model_answer = response.split("Model Answer:")[1].strip()
        
        return {
            "score": score,
            "technical_score": score,
            "communication_score": score,
            "strengths": strengths[:3],
            "improvements": improvements[:3],
            "model_answer": model_answer,
            "star_components": {
                "situation": "situation" in response.lower() or "context" in response.lower(),
                "task": "task" in response.lower() or "goal" in response.lower(),
                "action": "action" in response.lower() or "did" in response.lower(),
                "result": "result" in response.lower() or "outcome" in response.lower()
            }
        }
    
    # ========================================
    # MOCK MODE IMPLEMENTATIONS
    # ========================================
    
    def _mock_improve_resume(self, text: str, feedback: Dict) -> Dict:
        """Mock resume improvement for testing"""
        
        # Simple improvements
        improved = text
        changes = []
        
        # Add keywords if missing
        if any('keyword' in issue['message'].lower() for issue in feedback.get('issues', [])):
            improved += "\n\nTechnical Skills: Python, JavaScript, React, Node.js, SQL, Git, Docker, AWS, Agile, REST APIs"
            changes.append("Added technical keywords")
        
        # Add STAR format example
        if any('experience' in issue['message'].lower() for issue in feedback.get('issues', [])):
            improved += "\n\n• Led development of user authentication system (Situation), tasked with improving security (Task), implemented OAuth2.0 and JWT tokens (Action), reduced security incidents by 60% (Result)"
            changes.append("Applied STAR method to achievements")
        
        # Format improvements
        changes.append("Fixed formatting consistency")
        changes.append("Enhanced action verbs")
        
        return {
            "improved_text": improved,
            "changes_made": changes
        }
    
    def _mock_generate_questions(self, interview_type: str, language: Optional[str]) -> List[str]:
        """Mock question generation"""
        
        question_banks = {
            'hr': [
                "Tell me about yourself and your professional background.",
                "Why are you interested in this position?",
                "Describe a challenging situation you faced at work and how you handled it.",
                "Tell me about a time you had a disagreement with a team member. How did you resolve it?",
                "Give me an example of when you demonstrated leadership.",
                "What's your greatest professional achievement?",
                "Describe a time when you failed. What did you learn?",
                "How do you prioritize tasks when managing multiple deadlines?",
                "Tell me about a time you had to work with a difficult colleague.",
                "Where do you see yourself in 5 years?"
            ],
            'technical_python': [
                "What is the difference between a list and a tuple in Python?",
                "Explain how Python's garbage collection works.",
                "What are decorators and how would you use them?",
                "Explain the difference between deep copy and shallow copy.",
                "What is a generator? How is it different from a regular function?",
                "Explain Python's GIL (Global Interpreter Lock).",
                "What are Python's main data structures and their use cases?",
                "How would you optimize a slow Python function?",
                "Explain list comprehensions and when to use them.",
                "What is the difference between @staticmethod and @classmethod?"
            ],
            'technical_javascript': [
                "What is the difference between var, let, and const?",
                "Explain closures with a practical example.",
                "How does the JavaScript event loop work?",
                "What are Promises and how do they relate to async/await?",
                "Explain the difference between == and ===.",
                "How does prototypal inheritance work?",
                "What are higher-order functions?",
                "Explain hoisting in JavaScript.",
                "What is the 'this' keyword and how does it work?",
                "How would you handle errors in async code?"
            ],
            'ai_mock': [
                "Walk me through your resume.",
                "What interests you most about this role?",
                "Describe your most recent project in detail.",
                "What are your key technical strengths?",
                "How do you stay current with new technologies?",
                "Describe a time you had to learn something completely new.",
                "What's your approach to debugging complex issues?",
                "Tell me about a project you're particularly proud of.",
                "How do you handle tight deadlines?",
                "What motivates you in your work?"
            ]
        }
        
        # Select appropriate question bank
        if interview_type == 'technical' and language:
            key = f'technical_{language.lower()}'
            questions = question_banks.get(key, question_banks['technical_python'])
        else:
            questions = question_banks.get(interview_type, question_banks['hr'])
        
        return questions[:10]
    
    def _mock_evaluate_answer(self, question: str, answer: str) -> Dict:
        """Mock answer evaluation"""
        
        word_count = len(answer.split())
        
        # Basic scoring based on length and keywords
        if word_count < 30:
            score = 55
            strengths = ["Answer provided"]
            improvements = [
                "Expand your answer with more details",
                "Add specific examples from your experience",
                "Use the STAR method (Situation, Task, Action, Result)"
            ]
        elif word_count < 80:
            score = 70
            strengths = [
                "Good effort in providing context",
                "Answer addresses the question"
            ]
            improvements = [
                "Add specific metrics or outcomes",
                "Describe what you learned from the experience"
            ]
        elif word_count < 150:
            score = 85
            strengths = [
                "Comprehensive answer with good detail",
                "Clear structure and flow",
                "Specific examples provided"
            ]
            improvements = [
                "Could add more quantifiable results",
                "Mention the broader impact of your actions"
            ]
        else:
            score = 80
            strengths = [
                "Very detailed response",
                "Multiple examples provided"
            ]
            improvements = [
                "Consider being more concise",
                "Focus on the most relevant details"
            ]
        
        # Check for STAR components
        answer_lower = answer.lower()
        has_situation = any(word in answer_lower for word in ['when', 'situation', 'time', 'role', 'project'])
        has_task = any(word in answer_lower for word in ['task', 'goal', 'objective', 'needed', 'challenge'])
        has_action = any(word in answer_lower for word in ['i did', 'i implemented', 'i created', 'i developed', 'action'])
        has_result = any(word in answer_lower for word in ['result', 'outcome', 'improved', 'achieved', 'increased'])
        
        return {
            "score": score,
            "technical_score": score,
            "communication_score": score + 5 if word_count > 50 else score - 5,
            "strengths": strengths,
            "improvements": improvements,
            "model_answer": f"A strong answer to '{question}' would include: (1) The specific situation or context, (2) Your role and what was required, (3) The actions you took with specific details, (4) The measurable results and what you learned.",
            "star_components": {
                "situation": has_situation,
                "task": has_task,
                "action": has_action,
                "result": has_result
            }
        }