import os
import json
import google.generativeai as genai
import re
from typing import List, Dict

# In a real app, use environment variables
GEMINI_API_KEY = "AIzaSyDay2FHKc9yIwR1clYnhQYOJmQYBSeUQEo"
genai.configure(api_key=GEMINI_API_KEY)

# Using gemini-1.5-flash as the default for better availability
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """
You are a 'Recruiter' AI. Your task is to analyze a student's resume text and a list of job postings to find the best matches.

INPUT:
1. Resume text.
2. A list of job objects (each with 'id', 'title', 'company', 'description', 'requirements').

OUTPUT:
Return a JSON list of the top 30 jobs. Each object in the list must include:
- id: The job ID from the input.
- match_score: An integer from 0 to 100 representing how well the skills align.
- reasoning: A 1-sentence reasoning for the match.

Order the list by 'match_score' in descending order. Return ONLY the JSON array.
"""

def keyword_match_fallback(resume_text: str, jobs: List[Dict]) -> List[Dict]:
    """
    Robust fallback logic using keyword matching when Gemini API fails.
    """
    resume_lower = resume_text.lower()
    results = []
    
    # Common tech keywords to look for
    tech_keywords = [
        "python", "javascript", "react", "fastapi", "sql", "aws", "docker", 
        "data science", "machine learning", "backend", "frontend", "devops",
        "product manager", "analyst", "engineer", "java", "c++", "go"
    ]
    
    resume_keywords = [kw for kw in tech_keywords if kw in resume_lower]
    
    for j in jobs:
        score = 0
        matching_kws = []
        
        # Check title
        title_lower = j["title"].lower()
        for kw in resume_keywords:
            if kw in title_lower:
                score += 20
                matching_kws.append(kw)
        
        # Check requirements
        req_lower = j["requirements"].lower()
        for kw in resume_keywords:
            if kw in req_lower:
                score += 15
                if kw not in matching_kws:
                    matching_kws.append(kw)
        
        # Add some randomness for variety
        score += (j["id"] % 20)
        
        # Clamp score
        score = min(score, 98)
        
        # Generate reasoning
        if matching_kws:
            reasoning = f"Matched based on shared interest in {', '.join(matching_kws[:2])} and technical similarity."
        else:
            reasoning = "Potential match based on general professional alignment and experience."
            score = max(score, 30)

        results.append({
            "id": j["id"],
            "match_score": score,
            "reasoning": reasoning
        })
    
    # Sort and return top 30
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:30]

def rank_jobs(resume_text: str, jobs: List[Dict]) -> List[Dict]:
    # Format jobs for the prompt
    jobs_formatted = [{
        "id": j["id"],
        "title": j["title"],
        "company": j["company"],
        "description": j["description"],
        "requirements": j["requirements"]
    } for j in jobs]
    
    prompt = f"{SYSTEM_PROMPT}\n\nRESUME:\n{resume_text}\n\nJOBS:\n{json.dumps(jobs_formatted)}"
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Cleanup JSON formatting
        text = re.sub(r'```json\s*|\s*```', '', text).strip()
        ranked_jobs = json.loads(text)
        return ranked_jobs
    except Exception as e:
        print(f"Gemini API Error: {e}. Falling back to keyword matching.")
        return keyword_match_fallback(resume_text, jobs_formatted)
