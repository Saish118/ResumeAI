"""SQLAlchemy ORM models for ResumeAI persistence layer."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class ResumeAnalysis(Base):
    """Stores parsed resume metadata, text content, predicted role, and candidate experience."""

    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    character_count = Column(Integer, nullable=False)
    page_count = Column(Integer, nullable=True)
    extracted_text = Column(Text, nullable=False)
    predicted_role = Column(String(255), nullable=True)
    role_model_score = Column(Float, nullable=True)
    candidate_experience_years = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    matches = relationship("MatchAnalysis", back_populates="resume_analysis", cascade="all, delete-orphan")


class JobAnalysis(Base):
    """Stores processed job description requirements and skill categorizations."""

    __tablename__ = "job_analyses"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=False, default=list)
    preferred_skills = Column(JSON, nullable=False, default=list)
    minimum_experience_years = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    matches = relationship("MatchAnalysis", back_populates="job_analysis", cascade="all, delete-orphan")


class MatchAnalysis(Base):
    """Stores resume-to-job matching evaluation results, skill overlaps, and evidence comparisons."""

    __tablename__ = "match_analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_analysis_id = Column(Integer, ForeignKey("resume_analyses.id"), nullable=True)
    job_analysis_id = Column(Integer, ForeignKey("job_analyses.id"), nullable=True)
    overall_score = Column(Float, nullable=False)
    matched_required_skills = Column(JSON, nullable=False, default=list)
    missing_required_skills = Column(JSON, nullable=False, default=list)
    matched_preferred_skills = Column(JSON, nullable=False, default=list)
    missing_preferred_skills = Column(JSON, nullable=False, default=list)
    experience_status = Column(String(50), nullable=False)
    candidate_experience_years = Column(Float, nullable=True)
    required_experience_years = Column(Integer, nullable=True)
    semantic_evidence_matches = Column(JSON, nullable=False, default=list)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    resume_analysis = relationship("ResumeAnalysis", back_populates="matches")
    job_analysis = relationship("JobAnalysis", back_populates="matches")
