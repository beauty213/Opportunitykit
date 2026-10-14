from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    college = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    department = Column(String, nullable=True)
    current_year = Column(String, nullable=True)
    graduation_year = Column(Integer, nullable=True)
    cgpa = Column(String, nullable=True)
    skills = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    resume_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    income = Column(String, nullable=True)
    category = Column(String, nullable=True)
    documents = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=True)
    remote = Column(String, nullable=True)
    deadline = Column(String, nullable=True)
    application_url = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    verification_status = Column(String, default="unverified")
    last_checked = Column(String, nullable=True)
    requirements = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, nullable=False)
    status = Column(String, default="saved")
    application_date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    reminder_date = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, nullable=False)
    summary = Column(JSON, default=dict)
    details = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
