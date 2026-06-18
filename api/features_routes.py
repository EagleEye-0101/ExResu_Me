"""Additional API routes for extended features."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from resume_engine.ats.keywords import extract_jd_keywords, match_keywords
from resume_engine.ats.scorer import score_resume
from resume_engine.db import crud
from resume_engine.db.settings_store import get_runtime_config
from resume_engine.features.coach import coach_bullet
from resume_engine.features.cover_letter import generate_cover_letter
from resume_engine.ai.provider_ids import normalize_provider_id
from resume_engine.features.import_parser import parse_upload_bytes
from resume_engine.features.interview import generate_interview_questions
from resume_engine.features.resume_file_parser import parse_resume_file
from resume_engine.schemas.profile import ProfileCreate
from resume_engine.schemas.resume import ResumeData

router = APIRouter()


def _get_db():
    from resume_engine.db.database import get_db

    yield from get_db()


class CoachRequest(BaseModel):
    bullet: str = ""
    role: str = ""
    provider: str | None = None


class CloneRequest(BaseModel):
    title: str = ""


@router.post("/resumes/{resume_id}/clone")
def clone_resume(resume_id: int, req: CloneRequest, db: Session = Depends(_get_db)):
    row = crud.clone_resume(db, resume_id, req.title)
    if not row:
        raise HTTPException(404, "Resume not found")
    return {"id": row.id, "title": row.title, "parent_id": row.parent_id}


@router.get("/resumes/{resume_id}/diff")
def resume_diff(resume_id: int, db: Session = Depends(_get_db)):
    import json

    from resume_engine.db.models import ResumeRecord

    row = db.query(ResumeRecord).filter(ResumeRecord.id == resume_id).first()
    if not row:
        raise HTTPException(404, "Not found")
    current = crud.get_resume(db, resume_id)
    if not current:
        raise HTTPException(404, "Not found")
    _, resume = current
    previous = None
    if row.previous_resume_json:
        previous = ResumeData.model_validate(json.loads(row.previous_resume_json))
    return {
        "previous": previous.model_dump() if previous else None,
        "current": resume.model_dump() if resume else None,
    }


@router.get("/resumes/{resume_id}/keyword-heatmap")
def keyword_heatmap(resume_id: int, db: Session = Depends(_get_db)):
    result = crud.get_resume(db, resume_id)
    if not result:
        raise HTTPException(404, "Not found")
    row, resume = result
    if not resume:
        raise HTTPException(400, "No resume content")
    keywords = extract_jd_keywords(row.job_description or "")
    matched, missing = match_keywords(resume.to_text(), keywords)
    return {"keywords": keywords, "matched": matched, "missing": missing}


@router.post("/resumes/{resume_id}/cover-letter")
async def cover_letter(resume_id: int, provider: str | None = None, db: Session = Depends(_get_db)):
    result = crud.get_resume(db, resume_id)
    if not result:
        raise HTTPException(404, "Not found")
    row, resume = result
    if not resume:
        raise HTTPException(400, "Generate resume first")
    cfg = get_runtime_config(db)
    text = await generate_cover_letter(resume, row.job_description or "", provider, cfg)
    crud.save_cover_letter(db, resume_id, text)
    return {"cover_letter": text}


@router.get("/resumes/{resume_id}/cover-letter")
def get_cover_letter(resume_id: int, db: Session = Depends(_get_db)):
    from resume_engine.db.models import ResumeRecord

    row = db.query(ResumeRecord).filter(ResumeRecord.id == resume_id).first()
    if not row:
        raise HTTPException(404, "Not found")
    return {"cover_letter": row.cover_letter or ""}


async def _run_interview_prep(
    resume: ResumeData,
    job_description: str,
    provider: str | None,
    cfg: dict,
) -> list[dict]:
    resolved = normalize_provider_id(provider or cfg.get("default_ai_provider"))
    raw_provider = (provider or cfg.get("default_ai_provider") or "").strip().lower()
    try:
        return await generate_interview_questions(resume, job_description, resolved, cfg)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except Exception as e:
        if resolved == "ollama" or raw_provider == "ollama":
            raise HTTPException(
                400,
                "Ollama is local-only and not available on the live demo. "
                "Use Google AI Studio (Gemini) and ensure GEMINI_API_KEY is set on the API server.",
            ) from e
        raise HTTPException(502, f"Interview prep failed: {e}") from e


@router.post("/resumes/{resume_id}/interview-prep")
async def interview_prep(resume_id: int, provider: str | None = None, db: Session = Depends(_get_db)):
    result = crud.get_resume(db, resume_id)
    if not result:
        raise HTTPException(404, "Not found")
    row, resume = result
    if not resume:
        raise HTTPException(400, "Generate resume first")
    cfg = get_runtime_config(db)
    questions = await _run_interview_prep(resume, row.job_description or "", provider, cfg)
    return {"questions": questions}


@router.post("/coach/bullet")
async def coach(req: CoachRequest, db: Session = Depends(_get_db)):
    cfg = get_runtime_config(db)
    return await coach_bullet(req.bullet, req.role, req.provider, cfg)


@router.post("/import/resume")
async def import_resume(file: UploadFile = File(...), db: Session = Depends(_get_db)):
    content = await file.read()
    data = parse_upload_bytes(file.filename or "upload.txt", content)
    profile = crud.create_profile(db, ProfileCreate(**data))
    return {"profile_id": profile.id, "parsed": data}


@router.post("/ats/check")
async def ats_check(
    file: UploadFile = File(...),
    job_description: str = Form(""),
):
    """Score an uploaded resume without saving to DB."""
    content = await file.read()
    filename = file.filename or "resume.pdf"
    suffix = Path(filename).suffix.lower() or ".txt"
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp.flush()
            resume = parse_resume_file(Path(tmp.name), content)
    except Exception as e:
        raise HTTPException(400, f"Could not parse file: {e}") from e

    report = score_resume(resume, job_description)
    return {
        "resume_summary": {
            "full_name": resume.full_name,
            "email": resume.email,
            "experience_count": len(resume.experience),
            "education_count": len(resume.education),
            "skills_count": len(resume.skills),
        },
        "ats_report": report.model_dump(),
    }


@router.post("/interview/prep")
async def interview_prep_upload(
    job_description: str = Form(""),
    provider: str | None = Form(None),
    resume_id: int | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(_get_db),
):
    """Interview questions from uploaded file or saved resume."""
    cfg = get_runtime_config(db)

    if resume_id:
        result = crud.get_resume(db, resume_id)
        if not result:
            raise HTTPException(404, "Resume not found")
        row, resume = result
        if not resume:
            raise HTTPException(400, "Generate resume first")
        jd = job_description or row.job_description or ""
    elif file and file.filename:
        content = await file.read()
        suffix = Path(file.filename).suffix.lower() or ".txt"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp.flush()
            resume = parse_resume_file(Path(tmp.name), content)
        jd = job_description
        row = None
    else:
        raise HTTPException(400, "Provide resume_id or upload a file")

    questions = await _run_interview_prep(resume, jd, provider, cfg)
    return {
        "questions": questions,
        "resume_id": row.id if row else None,
        "candidate_name": resume.full_name,
    }
