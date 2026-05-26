import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=False)
    phone_country_code = Column(String(8), default="+1")
    location = Column(String(200), default="")
    linkedin = Column(String(300), default="")
    target_role = Column(String(200), default="")
    years_experience = Column(Integer, default=0)
    headline = Column(String(300), default="")
    summary_notes = Column(Text, default="")
    experience_json = Column(Text, default="[]")
    education_json = Column(Text, default="[]")
    skills_json = Column(Text, default="[]")
    certifications_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResumeRecord(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, nullable=False)
    title = Column(String(300), default="")
    status = Column(String(20), default="draft")  # draft | finished
    job_description = Column(Text, default="")
    resume_json = Column(Text, default="{}")
    draft_json = Column(Text, default="")
    wizard_step = Column(Integer, default=0)
    ats_score = Column(Float, default=0.0)
    provider = Column(String(50), default="")
    parent_id = Column(Integer, nullable=True)
    previous_resume_json = Column(Text, default="")
    cover_letter = Column(Text, default="")
    template_id = Column(String(50), default="compact")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, default="")


def dumps_json(data) -> str:
    return json.dumps(data, default=str)


def loads_json(text: str, default=None):
    if not text:
        return default if default is not None else []
    return json.loads(text)
