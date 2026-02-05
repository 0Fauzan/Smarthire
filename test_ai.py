# test_ai.py
from services.ai_service import SmartHireAI

# Initialize AI
ai = SmartHireAI()

print(f"Provider: {ai.provider}")
print("\n" + "="*50)

# Test 1: Question Generation
print("\n1. Testing Question Generation:")
questions = ai.generate_interview_questions('hr')
for i, q in enumerate(questions[:3], 1):
    print(f"   {i}. {q}")

# Test 2: Answer Evaluation
print("\n2. Testing Answer Evaluation:")
question = "Tell me about a time you faced a challenge."
answer = "In my previous role at XYZ Corp, I faced a major deadline challenge. The client needed a feature in 2 weeks instead of 4. I organized daily standups, broke the work into smaller tasks, and we delivered on time. The client was impressed and gave us more business."

evaluation = ai.evaluate_answer(question, answer, 'hr')
print(f"   Score: {evaluation['score']}/100")
print(f"   Strengths: {evaluation['strengths']}")
print(f"   Improvements: {evaluation['improvements']}")

# Test 3: Resume Improvement
print("\n3. Testing Resume Improvement:")
resume = "Software Engineer. Worked at ABC Company. Used Python and JavaScript."
feedback = {
    'issues': [{'message': 'Missing keywords', 'severity': 'high'}],
    'suggestions': ['Add more technical details']
}
improved = ai.improve_resume(resume, feedback, 65)
print(f"   Changes: {improved['changes_made']}")
print(f"   Improved text (first 200 chars): {improved['improved_text'][:200]}...")

print("\n" + "="*50)
print("✅ All tests completed!")
