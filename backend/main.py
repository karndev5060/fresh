from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import models, database, auth, gemini_service, asyncio, json
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@app.post("/register", response_model=models.UserOut)
def register(user: models.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=models.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/jobs", response_model=List[models.JobOut])
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return jobs

@app.post("/jobs", response_model=models.JobOut)
def create_job(job: models.JobCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.employer:
        raise HTTPException(status_code=403, detail="Only employers can post jobs")
    
    new_job = models.Job(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@app.get("/me", response_model=models.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/match-jobs")
def match_jobs(resume_data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # ... (Existing matching logic)
    pass

@app.websocket("/ws/match")
async def websocket_match_jobs(websocket: WebSocket):
    await websocket.accept()
    db = next(get_db())
    
    try:
        data = await websocket.receive_text()
        msg = json.loads(data)
        token = msg.get("token")
        resume_text = msg.get("resume_text")

        # 1. Authenticate
        payload = auth.decode_token(token)
        if not payload:
            await websocket.send_json({"error": "Invalid token"})
            await websocket.close()
            return
        
        username = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user or user.role != models.UserRole.student:
            await websocket.send_json({"error": "Unauthorized"})
            await websocket.close()
            return

        # 2. Thinking phase
        await websocket.send_json({"status": "thinking", "message": "Analyzing resume with Gemini AI..."})
        await asyncio.sleep(2) # Visual pause

        # 3. Ranking phase
        jobs = db.query(models.Job).all()
        jobs_list = [{"id": j.id, "title": j.title, "company": j.company, "description": j.description, "requirements": j.requirements} for j in jobs]
        
        ranked_results = gemini_service.rank_jobs(resume_text, jobs_list)
        
        # Merge with full job details
        final_results = []
        job_map = {j["id"]: j for j in jobs_list}
        for match in ranked_results:
            job_id = match.get("id")
            if job_id in job_map:
                final_results.append({
                    **job_map[job_id],
                    "match_score": match.get("match_score", 0),
                    "reasoning": match.get("reasoning", "No reasoning provided.")
                })
        
        await websocket.send_json({"status": "ranked", "jobs": final_results[:30]})
        await asyncio.sleep(1)

        # 4. Auto-Apply phase for top 10
        top_10 = final_results[:10]
        for job in top_10:
            await websocket.send_json({"status": "applying", "job_id": job["id"], "job_title": job["title"]})
            await asyncio.sleep(1.5) # Simulate application process
            await websocket.send_json({"status": "applied", "job_id": job["id"]})

        await websocket.send_json({"status": "complete", "message": "Successfully applied to top 10 matches!"})
        
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        db.close()
