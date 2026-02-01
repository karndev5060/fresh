from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
import enum
from database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserRole(str, enum.Enum):
    student = "student"
    employer = "employer"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    requirements: str

class JobCreate(JobBase):
    pass

class JobOut(JobBase):
    id: int

    class Config:
        from_attributes = True

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(SqlEnum(UserRole))

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    description = Column(String)
    requirements = Column(String)

class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(SqlEnum(ApplicationStatus), default=ApplicationStatus.pending)

    student = relationship("User")
    job = relationship("Job")
