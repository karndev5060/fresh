# 🚀 CareerAI Portal: The Autonomous Job Search Agent

CareerAI is a cutting-edge, AI-powered recruitment and job search platform designed to bridge the gap between students and high-impact technical roles. 

Powered by **Gemini 1.5 Pro**, the platform features an autonomous multi-agent system that handles everything from resume analysis and "Professional Identity" generation to automated application tailoring and integrity auditing.

## ✨ Core Features

### 🤖 Multi-Agent AI System
- **The Profile Agent**: Scans resumes to extract "Professional Identity Artifacts"—highlighting the top 5 high-impact technical achievements and categorized skill profiles.
- **The Recruiter Agent**: Performs deep-semantic matching between student resumes and job requirements, providing instant compatibility scores.
- **The Auditor Agent**: A safety and integrity layer that identifies "fabricated skills" in resumes to ensure high-quality, honest matches for employers.
- **The Application Tailor**: Automatically prepares students for individual roles by analyzing skill gaps and predicting potential interview questions.

### 🌓 Mixed-Mode Professional UI
- **Student Dashboard**: A streamlined interface for pasting resumes, discovering matched roles, and tracking application progress via real-time WebSockets.
- **Employer Dashboard**: A comprehensive platform for posting technical roles and reviewing candidate "Artifacts" at a glance.
- **The "Artifact Card"**: A premium, dark-themed summary card that represents a student's technical soul, designed for instant employer scannability.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.13), SQLAlchemy (SQLite), Uvicorn.
- **Frontend**: React (Vite), Vanilla CSS (Mixed-Mode Custom Design).
- **AI Engine**: Google Gemini 1.5 Pro.
- **Real-time**: WebSockets for live status updates during the AI "Thinking" and "Auditing" phases.

## 🏁 Getting Started

### Prerequisites
- Python 3.13+
- Node.js & npm
- Gemini API Key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`:
   ```env
   GEMINI_API_KEY=your_api_key_here
   SECRET_KEY=your_jwt_secret
   ```
5. Launch the server:
   ```bash
   python -m uvicorn main:app --port 8000
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Launch the development server:
   ```bash
   npm run dev
   ```

## 📜 License
MIT License - Created for the Future of Recruitment.
