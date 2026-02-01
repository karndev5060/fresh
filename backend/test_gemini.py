import requests
import json

BASE_URL = "http://localhost:8000"

def test_gemini_matching():
    print("--- Testing Gemini Job Matching ---")
    
    # 1. Login Student
    print("\n1. Logging in Student...")
    login_data = {
        "username": "student_test",
        "password": "password123"
    }
    res = requests.post(f"{BASE_URL}/login", data=login_data)
    if res.status_code == 200:
        student_token = res.json()["access_token"]
        print("SUCCESS: Student logged in.")
    else:
        print(f"FAILED: {res.status_code} - {res.text}")
        return

    # 2. Test /match-jobs
    print("\n2. Testing /match-jobs with Gemini...")
    resume_text = """
    Experienced Software Engineer with proficiency in Python, FastAPI, and React. 
    Strong background in building scalable web applications and integrating AI models.
    Expertise in SQL databases and cloud deployments.
    """
    res = requests.post(
        f"{BASE_URL}/match-jobs", 
        json={"resume_text": resume_text},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    if res.status_code == 200:
        results = res.json()
        print(f"SUCCESS: Received {len(results)} matches.")
        if len(results) > 0:
            print("\nTop Match:")
            top = results[0]
            print(f"Title: {top['title']}")
            print(f"Score: {top['match_score']}%")
            print(f"Reasoning: {top['reasoning']}")
    else:
        print(f"FAILED: {res.status_code} - {res.text}")

if __name__ == "__main__":
    test_gemini_matching()
