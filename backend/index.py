from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import os
from tempfile import NamedTemporaryFile
import json

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser

app = FastAPI(title="Resume Parser API", version="1.0.0")


class ResumeOutput(BaseModel):
    """Structured output from resume parsing"""
    structured_profile: List[str] = Field(
        description="Structured student profile with facts only. Includes education, projects, internships, skills, links, and constraints such as location, remote, visa, and start date."
    )
    bullet_bank: List[str] = Field(
        description="Normalized achievement bullets tied to specific projects or experiences, reusable across applications."
    )
    answer_library: List[str] = Field(
        description="Reusable answers for common application questions like work authorization, availability, relocation, and salary expectations."
    )
    proof_pack: List[str] = Field(
        description="3 to 8 links or artifacts that validate claims in the student profile (portfolio items, demos, GitHub repos, case studies)."
    )
    rules: List[str] = Field(
        description="Hard rules the agent must follow: do not invent experience, numbers, titles, or achievements. Only ground all claims in the student-provided data."
    )


def initialize_llm():
    """Initialize the Gemini LLM"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=api_key
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Resume Parser API is running"}


@app.post("/parse-resume", response_model=ResumeOutput)
async def parse_resume(
    resume: UploadFile = File(..., description="Resume PDF file"),
    linkedin_text: Optional[str] = Form(None, description="Optional LinkedIn profile text"),
    portfolio_links: Optional[str] = Form(None, description="Optional comma-separated portfolio links"),
    github_links: Optional[str] = Form(None, description="Optional comma-separated GitHub links"),
    projects: Optional[str] = Form(None, description="Optional comma-separated project descriptions")
):
    """
    Parse a resume PDF and extract structured information.
    
    Returns:
    - Structured student profile
    - Bullet bank of achievements
    - Answer library for common questions
    - Proof pack of supporting links
    """
    
    # Validate file type
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file temporarily
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await resume.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Load PDF
        loader = PDFPlumberLoader(tmp_file_path)
        documents = loader.load()
        
        if not documents:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        resume_text = documents[0].page_content
        
        # Initialize parser and LLM
        parser = PydanticOutputParser(pydantic_object=ResumeOutput)
        llm = initialize_llm()
        
        # Build prompt
        prompt = f"""
Extract from Resume
Optional: LinkedIn text, portfolio links, GitHub, projects
Outputs (minimum):
Structured Student Profile (facts only, editable JSON is ideal)
education, projects, internships, skills, links, constraints (location, remote, visa, start date)
Bullet Bank
normalized achievement bullets tied to specific projects or experiences
Answer Library
reusable answers for common application questions (work authorization, availability, relocation, salary expectations if provided)
Proof Pack
3 to 8 links or artifacts that back up claims (portfolio items, demos, GitHub repos, case studies)

Resume:
{resume_text}

{f"LinkedIn: {linkedin_text}" if linkedin_text else ""}
{f"Portfolio Links: {portfolio_links}" if portfolio_links else ""}
{f"GitHub Links: {github_links}" if github_links else ""}
{f"Projects: {projects}" if projects else ""}

{parser.get_format_instructions()}
"""
        
        # Invoke LLM
        raw = llm.invoke(prompt)
        result = parser.invoke(raw)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        return result
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.post("/parse-resume-text")
async def parse_resume_text(
    resume_text: str = Form(..., description="Resume text content"),
    linkedin_text: Optional[str] = Form(None),
    portfolio_links: Optional[str] = Form(None),
    github_links: Optional[str] = Form(None),
    projects: Optional[str] = Form(None)
):
    """
    Parse resume from raw text instead of PDF.
    Useful for testing or when you already have extracted text.
    """
    
    try:
        # Initialize parser and LLM
        parser = PydanticOutputParser(pydantic_object=ResumeOutput)
        llm = initialize_llm()
        
        # Build prompt
        prompt = f"""
Extract from Resume
Optional: LinkedIn text, portfolio links, GitHub, projects
Outputs (minimum):
Structured Student Profile (facts only, editable JSON is ideal)
education, projects, internships, skills, links, constraints (location, remote, visa, start date)
Bullet Bank
normalized achievement bullets tied to specific projects or experiences
Answer Library
reusable answers for common application questions (work authorization, availability, relocation, salary expectations if provided)
Proof Pack
3 to 8 links or artifacts that back up claims (portfolio items, demos, GitHub repos, case studies)

Resume:
{resume_text}

{f"LinkedIn: {linkedin_text}" if linkedin_text else ""}
{f"Portfolio Links: {portfolio_links}" if portfolio_links else ""}
{f"GitHub Links: {github_links}" if github_links else ""}
{f"Projects: {projects}" if projects else ""}

{parser.get_format_instructions()}
"""
        
        # Invoke LLM
        raw = llm.invoke(prompt)
        result = parser.invoke(raw)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)