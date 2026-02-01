import random
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

COMPANIES = [
    "TechGiant", "DataFlow", "CloudNine", "InnovateSoft", "ByteMe", 
    "CyberPulse", "LogicGate", "NebulaSystems", "PixelPerfect", "QuantEdge",
    "SilverLinings", "Terraformers", "VectorLabs", "WaveLength", "ZenithTech"
]

ROLES = {
    "Software Engineering": [
        "Full Stack Developer", "Backend Engineer", "Frontend Developer", 
        "Site Reliability Engineer", "DevOps Engineer", "Mobile Developer (iOS/Android)",
        "Embedded Systems Engineer", "Quality Assurance Engineer", "Security Engineer"
    ],
    "Data Science": [
        "Data Scientist", "Machine Learning Engineer", "Data Engineer", 
        "Business Intelligence Analyst", "AI Research Scientist", "Data Architect"
    ],
    "Product Management": [
        "Product Manager", "Associate Product Manager", "Technical Product Manager",
        "Product Owner", "Product Marketing Manager"
    ]
}

LOCATIONS = ["Remote", "New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA", "London, UK", "Berlin, DE", "Tokyo, JP"]

DESCRIPTIONS = [
    "We are looking for a passionate professional to join our team and help us build the next generation of our platform.",
    "Join a fast-paced team dedicated to solving complex problems and delivering high-quality solutions to our global customers.",
    "Be part of an innovative company where you can grow your skills and contribute to impactful projects.",
    "Seeking a collaborative individual who thrives in a dynamic environment and is eager to make a difference.",
    "Help us shape the future of tech by bringing your expertise and creativity to our talented engineering group."
]

REQUIREMENTS = [
    "3+ years of experience in the field. Proficiency in Python or JavaScript.",
    "Strong problem-solving skills and experience with cloud technologies (AWS/GCP).",
    "Bachelor's degree in CS or related field. Excellent communication skills.",
    "Ability to work in a cross-functional team and mentor junior members.",
    "Experience with SQL and NoSQL databases. Familiarity with Agile methodologies."
]

def seed_database():
    db = SessionLocal()
    try:
        # Check if jobs already exist
        if db.query(models.Job).count() > 0:
            print("Database already seeded.")
            return

        jobs = []
        for i in range(100):
            dept = random.choice(list(ROLES.keys()))
            title = random.choice(ROLES[dept])
            company = random.choice(COMPANIES)
            location = random.choice(LOCATIONS)
            full_title = f"{title} - {dept} ({location})"
            
            job = models.Job(
                title=full_title,
                company=company,
                description=random.choice(DESCRIPTIONS),
                requirements=random.choice(REQUIREMENTS)
            )
            jobs.append(job)
        
        db.add_all(jobs)
        db.commit()
        print(f"Successfully seeded {len(jobs)} jobs.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
