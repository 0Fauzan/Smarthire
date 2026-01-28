# services/interview_engine.py (CREATE THIS FILE)
import os
import json
from anthropic import Anthropic

class InterviewEngine:
    """
    Generates adaptive interview questions using AI
    Questions are personalized based on resume and interview type
    """
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if api_key:
            self.client = Anthropic(api_key=api_key)
            self.use_ai = True
        else:
            self.use_ai = False
            print("Warning: ANTHROPIC_API_KEY not set. Using fallback questions.")
        
        # Fallback question banks
        self.question_banks = {
            'hr': [
                "Tell me about yourself and your background.",
                "Why are you interested in this role?",
                "Describe a time when you faced a significant challenge at work. How did you handle it?",
                "Tell me about a time you had a conflict with a coworker. How did you resolve it?",
                "Describe a situation where you showed leadership.",
                "What's your greatest professional achievement?",
                "Tell me about a time you failed and what you learned.",
                "How do you prioritize tasks when you have multiple deadlines?",
                "Describe a time when you had to work with a difficult team member.",
                "Where do you see yourself in 5 years?"
            ],
            'technical': {
                'python': [
                    "What is the difference between a list and a tuple in Python?",
                    "Explain how Python's garbage collection works.",
                    "What are decorators in Python and how do you use them?",
                    "Explain the difference between deep copy and shallow copy.",
                    "What is a generator in Python? How is it different from a regular function?",
                    "Explain the GIL (Global Interpreter Lock) in Python.",
                    "What are Python's data structures? When would you use each?",
                    "How does Python handle memory management?"
                ],
                'java': [
                    "What is the difference between abstract classes and interfaces?",
                    "Explain Java's memory model (heap vs stack).",
                    "What are the main principles of OOP?",
                    "Explain the difference between ArrayList and LinkedList.",
                    "What is the purpose of the 'final' keyword?",
                    "How does garbage collection work in Java?",
                    "Explain Java's exception handling mechanism.",
                    "What are Java Streams and how do you use them?"
                ],
                'javascript': [
                    "What is the difference between var, let, and const?",
                    "Explain closures in JavaScript with an example.",
                    "What is the event loop and how does it work?",
                    "Explain promises and async/await.",
                    "What is the difference between == and ===?",
                    "How does prototypal inheritance work?",
                    "What are higher-order functions?",
                    "Explain the concept of hoisting."
                ]
            },
            'ai_mock': [
                "Walk me through your resume.",
                "What interests you about this position?",
                "Describe your most recent project in detail.",
                "What are your technical strengths?",
                "How do you stay updated with new technologies?",
                "Describe a time you had to learn something new quickly.",
                "What's your approach to debugging complex issues?",
                "Tell me about a project you're proud of."
            ]
        }
    
    def generate_questions(self, interview_type, resume_data=None, language=None):
        """
        Generate interview questions
        Returns: List of question strings
        """
        if self.use_ai and resume_data:
            # Use AI to generate personalized questions
            return self._generate_ai_questions(interview_type, resume_data, language)
        else:
            # Use fallback questions
            return self._get_fallback_questions(interview_type, language)
    
    def _generate_ai_questions(self, interview_type, resume_data, language):
        """
        Use Claude AI to generate personalized questions
        """
        # Extract relevant resume info
        skills = resume_data.get('parsed_data', {}).get('skills', [])
        experience = resume_data.get('parsed_data', {}).get('experience', [])
        
        if interview_type == 'technical':
            prompt = self._build_technical_prompt(language, skills)
        elif interview_type == 'hr':
            prompt = self._build_hr_prompt(experience, skills)
        else:  # ai_mock
            prompt = self._build_ai_mock_prompt(resume_data)
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON response
            response_text = message.content[0].text.strip()
            
            # Extract JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            questions = json.loads(response_text)
            
            # Validate it's a list
            if isinstance(questions, list) and len(questions) >= 8:
                return questions[:10]  # Max 10 questions
            else:
                print("AI returned invalid format, using fallback")
                return self._get_fallback_questions(interview_type, language)
            
        except Exception as e:
            print(f"AI question generation failed: {e}")
            return self._get_fallback_questions(interview_type, language)
    
    def _build_hr_prompt(self, experience, skills):
        """Build prompt for HR/behavioral questions"""
        exp_text = experience[0] if experience else "entry level"
        skills_text = ", ".join(skills[:5]) if skills else "general"
        
        return f"""You are an experienced HR interviewer. Generate 10 behavioral interview questions for a candidate.

Candidate Profile:
- Experience Level: {exp_text}
- Key Skills: {skills_text}

Requirements:
1. Use STAR method framework (Situation, Task, Action, Result)
2. Mix of: teamwork, conflict resolution, problem-solving, leadership
3. Questions should be specific and relevant to their experience level
4. Include 2-3 questions about specific skills they listed
5. Progressive difficulty (start easier, get harder)

Return ONLY a JSON array of 10 question strings, no other text:
["question 1", "question 2", ...]

Examples of good questions:
- "Tell me about a time you had to resolve a conflict within your team."
- "Describe a situation where you had to learn a new technology quickly."
- "Give me an example of when you improved a process or system."
"""
    
    def _build_technical_prompt(self, language, skills):
        """Build prompt for technical questions"""
        lang = language or 'python'
        skills_text = ", ".join(skills[:5]) if skills else "general programming"
        
        return f"""You are a technical interviewer for a {lang.upper()} developer position.

Candidate Skills: {skills_text}

Generate 10 technical interview questions covering:
1. Core {lang} concepts (syntax, data structures)
2. Advanced topics (memory management, concurrency)
3. Best practices and design patterns
4. Problem-solving and algorithms
5. Real-world scenarios

Requirements:
- Mix theoretical questions with practical scenarios
- Progressive difficulty
- Questions should test depth of knowledge
- Include questions about their listed skills

Return ONLY a JSON array of 10 question strings, no other text:
["question 1", "question 2", ...]

Examples:
- "Explain the difference between {lang}'s list and tuple. When would you use each?"
- "How would you optimize a function that's running slowly?"
- "Describe how you'd design a caching system."
"""
    
    def _build_ai_mock_prompt(self, resume_data):
        """Build prompt for general AI mock interview"""
        return f"""You are conducting a general job interview. Generate 10 interview questions.

Candidate Resume Summary:
{json.dumps(resume_data.get('parsed_data', {}), indent=2)[:500]}

Requirements:
1. Start with "Tell me about yourself"
2. Mix behavioral and technical questions
3. Ask about specific projects/experiences from their resume
4. Include questions about strengths, weaknesses, career goals
5. Progressive difficulty

Return ONLY a JSON array of 10 question strings, no other text:
["question 1", "question 2", ...]
"""
    
    def _get_fallback_questions(self, interview_type, language):
        """
        Return pre-defined questions when AI unavailable
        """
        if interview_type == 'technical' and language:
            lang_questions = self.question_banks['technical'].get(language.lower())
            if lang_questions:
                return lang_questions[:10]
            return self.question_banks['technical']['python'][:10]
        
        return self.question_banks.get(interview_type, self.question_banks['hr'])[:10]
