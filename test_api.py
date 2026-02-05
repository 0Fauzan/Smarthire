import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, response=None):
    """Print test results with colors"""
    symbol = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
    print(f"{symbol} {name}")
    if response:
        print(f"   Response: {json.dumps(response, indent=2)[:200]}...")
    print()

def test_auth():
    """Test authentication endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("🔐 TESTING AUTHENTICATION")
    print(f"{'='*60}{Colors.END}\n")
    
    # Test 1: Register new user
    print("Test 1: Register new user")
    data = {
        "name": "Test User",
        "email": f"test_{int(time.time())}@example.com",
        "password": "password123",
        "role": "candidate"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        success = response.status_code == 201
        print_test("Register User", success, response.json() if success else {"error": response.text})
        
        if success:
            # Save email for login test
            test_email = data["email"]
            
            # Test 2: Login
            print("Test 2: Login with registered user")
            login_data = {
                "email": test_email,
                "password": "password123"
            }
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            success = response.status_code == 200
            
            if success:
                token = response.json().get("access_token")
                print_test("Login User", success, {"token_received": bool(token)})
                return token
            else:
                print_test("Login User", False, {"error": response.text})
                return None
    except Exception as e:
        print_test("Authentication Tests", False, {"error": str(e)})
        return None

def test_resume(token):
    """Test resume endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("📄 TESTING RESUME ENDPOINTS")
    print(f"{'='*60}{Colors.END}\n")
    
    if not token:
        print(f"{Colors.RED}⚠️  Skipping resume tests (no auth token){Colors.END}\n")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: Create sample resume file
    print("Test 3: Upload resume")
    
    # Create a sample resume text file
    resume_content = """
John Doe
Software Engineer
Email: john@example.com | Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 5 years of expertise in full-stack development.

EXPERIENCE
Senior Developer at Tech Corp (2020 - Present)
- Developed RESTful APIs using Python and Flask
- Implemented CI/CD pipelines reducing deployment time by 40%
- Led a team of 3 junior developers

EDUCATION
Bachelor of Science in Computer Science
MIT University, 2019

SKILLS
Python, JavaScript, React, Node.js, SQL, Docker, AWS, Git
"""
    
    # Save to file
    with open('/tmp/test_resume.txt', 'w') as f:
        f.write(resume_content)
    
    try:
        # Upload as text file (treating as docx for testing)
        files = {'file': ('resume.txt', open('/tmp/test_resume.txt', 'rb'), 'text/plain')}
        
        # Note: This might fail if strict file type checking is enabled
        # We'll test the endpoint structure regardless
        response = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files=files)
        
        if response.status_code == 201:
            resume_data = response.json()
            resume_id = resume_data.get("resume_id")
            print_test("Upload Resume", True, resume_data)
            
            # Test 4: Get resume details
            if resume_id:
                print("Test 4: Get resume details")
                response = requests.get(f"{BASE_URL}/resume/{resume_id}", headers=headers)
                success = response.status_code == 200
                print_test("Get Resume", success, response.json() if success else {"error": response.text})
                
                # Test 5: List all resumes
                print("Test 5: List all resumes")
                response = requests.get(f"{BASE_URL}/resume/list", headers=headers)
                success = response.status_code == 200
                print_test("List Resumes", success, response.json() if success else {"error": response.text})
                
                return resume_id
        else:
            print_test("Upload Resume", False, {"error": response.text, "note": "File upload may require PDF/DOCX"})
            return None
            
    except Exception as e:
        print_test("Resume Tests", False, {"error": str(e)})
        return None

def test_ats(token, resume_id):
    """Test ATS analyzer endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("🎯 TESTING ATS ANALYZER")
    print(f"{'='*60}{Colors.END}\n")
    
    if not token or not resume_id:
        print(f"{Colors.RED}⚠️  Skipping ATS tests (need resume){Colors.END}\n")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 6: Analyze resume
    print("Test 6: Re-analyze resume")
    try:
        response = requests.post(f"{BASE_URL}/ats/analyze/{resume_id}", headers=headers)
        success = response.status_code == 200
        print_test("ATS Analysis", success, response.json() if success else {"error": response.text})
        
        # Test 7: Improve resume
        print("Test 7: AI improve resume")
        response = requests.post(f"{BASE_URL}/ats/improve/{resume_id}", headers=headers)
        success = response.status_code in [200, 403]  # 403 if free tier limit
        result = response.json() if response.status_code == 200 else {"note": "Free tier limit or already improved"}
        print_test("AI Improvement", success, result)
        
        # Test 8: Get ATS tips
        print("Test 8: Get ATS tips")
        response = requests.get(f"{BASE_URL}/ats/tips", headers=headers)
        success = response.status_code == 200
        print_test("ATS Tips", success, response.json() if success else {"error": response.text})
        
    except Exception as e:
        print_test("ATS Tests", False, {"error": str(e)})

def test_interview(token, resume_id):
    """Test interview endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("🎤 TESTING INTERVIEW SYSTEM")
    print(f"{'='*60}{Colors.END}\n")
    
    if not token:
        print(f"{Colors.RED}⚠️  Skipping interview tests (no auth token){Colors.END}\n")
        return
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 9: Start interview
    print("Test 9: Start HR interview")
    try:
        data = {
            "resume_id": resume_id,
            "interview_type": "hr"
        }
        response = requests.post(f"{BASE_URL}/interview/start", headers=headers, json=data)
        success = response.status_code == 201
        
        if success:
            interview_data = response.json()
            interview_id = interview_data.get("interview_id")
            first_question_id = interview_data.get("first_question", {}).get("id")
            print_test("Start Interview", success, interview_data)
            
            # Test 10: Submit answer
            if first_question_id:
                print("Test 10: Submit answer to first question")
                answer_data = {
                    "question_id": first_question_id,
                    "answer": "In my previous role at Tech Corp, I faced a major challenge when our main server crashed during peak hours. I was tasked with restoring service quickly. I coordinated with the DevOps team, implemented a backup solution, and we were back online in 2 hours. This reduced downtime by 60% compared to previous incidents. I learned the importance of having robust backup systems.",
                    "time_taken": 120
                }
                response = requests.post(f"{BASE_URL}/interview/answer", headers=headers, json=answer_data)
                success = response.status_code == 200
                print_test("Submit Answer", success, response.json() if success else {"error": response.text})
            
            # Test 11: Get interview history
            print("Test 11: Get interview history")
            response = requests.get(f"{BASE_URL}/interview/history", headers=headers)
            success = response.status_code == 200
            print_test("Interview History", success, response.json() if success else {"error": response.text})
            
            return interview_id
        else:
            print_test("Start Interview", False, {"error": response.text})
            return None
            
    except Exception as e:
        print_test("Interview Tests", False, {"error": str(e)})
        return None

def test_candidate(token):
    """Test candidate endpoints"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("👤 TESTING CANDIDATE ENDPOINTS")
    print(f"{'='*60}{Colors.END}\n")
    
    if not token:
        print(f"{Colors.RED}⚠️  Skipping candidate tests (no auth token){Colors.END}\n")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 12: Get dashboard
    print("Test 12: Get candidate dashboard")
    try:
        response = requests.get(f"{BASE_URL}/candidate/dashboard", headers=headers)
        success = response.status_code == 200
        print_test("Candidate Dashboard", success, response.json() if success else {"error": response.text})
    except Exception as e:
        print_test("Candidate Tests", False, {"error": str(e)})

def main():
    """Run all tests"""
    print(f"\n{Colors.GREEN}")
    print("="*60)
    print("🚀 SMARTHIRE BACKEND API TEST SUITE")
    print("="*60)
    print(f"{Colors.END}")
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"\n{Colors.GREEN}✅ Server is running{Colors.END}\n")
    except:
        print(f"\n{Colors.RED}❌ ERROR: Server is not running!")
        print(f"Please start the server with: python3 app.py{Colors.END}\n")
        return
    
    # Run tests
    token = test_auth()
    resume_id = test_resume(token)
    test_ats(token, resume_id)
    interview_id = test_interview(token, resume_id)
    test_candidate(token)
    
    # Summary
    print(f"\n{Colors.GREEN}")
    print("="*60)
    print("✅ TEST SUITE COMPLETED")
    print("="*60)
    print(f"{Colors.END}")
    print("\nNote: Some tests may fail due to:")
    print("  - File upload restrictions (PDF/DOCX only)")
    print("  - Free tier limits")
    print("  - Missing routes")
    print("\nThis is normal during development!")

if __name__ == "__main__":
    main()