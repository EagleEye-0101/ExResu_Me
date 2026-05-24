from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.resume_generation import generate_resume_from_profile
from resume_engine.ai.generator import optimize_resume
from resume_engine.ai.provider_ids import normalize_provider_id
from resume_engine.ai.router import list_providers, test_provider
from resume_engine.ats.scorer import score_resume
from resume_engine.config import settings
from resume_engine.db import crud
from resume_engine.db.database import get_db, init_db
from resume_engine.db.settings_store import get_all_settings, get_runtime_config, update_settings
from resume_engine.validation import (
    validate_education_step,
    validate_experience_step,
    validate_job_description,
    validate_profile_step,
    validate_skills_step,
)
from resume_engine.export.docx_export import export_docx
from resume_engine.export.pdf_export import export_pdf
from resume_engine.export.templates.registry import list_templates, render_resume_html, resolve_template_id
from resume_engine.export.txt_export import export_txt
from resume_engine.schemas.profile import ProfileCreate, ProfileResponse
from resume_engine.schemas.resume import ResumeData, ResumeGenerateRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    settings.export_path.mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="ATS Resume Builder API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.features_routes import router as features_router  # noqa: E402
from api.latex_routes import router as latex_router  # noqa: E402

app.include_router(features_router, prefix="/api")
app.include_router(latex_router, prefix="/api")


def get_session():
    yield from get_db()


# --- Profiles ---


@app.get("/api/health")
def health():
    from resume_engine.ai.router import list_providers_ids
    from resume_engine.latex.compiler import is_latex_available

    return {
        "status": "ok",
        "providers": list_providers_ids(),
        "resume_parser": "v4-explicit-build",
        "latex_compiler_available": is_latex_available(),
    }


@app.get("/api/providers")
def providers():
    return list_providers()


@app.get("/api/templates")
def templates_list():
    return list_templates()


class TestProviderRequest(BaseModel):
    provider: str
    model: str | None = None


@app.post("/api/providers/test")
async def providers_test(req: TestProviderRequest, db: Session = Depends(get_session)):
    cfg = get_runtime_config(db)
    provider = normalize_provider_id(req.provider)
    return await test_provider(provider, req.model, cfg)


# --- Settings ---


class SettingsUpdate(BaseModel):
    default_ai_provider: str | None = None
    openai_api_key: str | None = None
    openai_model: str | None = None
    anthropic_api_key: str | None = None
    anthropic_model: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str | None = None
    openrouter_api_key: str | None = None
    openrouter_model: str | None = None
    ollama_base_url: str | None = None
    ollama_model: str | None = None


@app.get("/api/settings")
def settings_get(db: Session = Depends(get_session)):
    return get_all_settings(db)


@app.put("/api/settings")
def settings_put(data: SettingsUpdate, db: Session = Depends(get_session)):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if payload.get("default_ai_provider"):
        payload["default_ai_provider"] = normalize_provider_id(payload["default_ai_provider"])
    return update_settings(db, payload)


@app.get("/api/profiles", response_model=list[ProfileResponse])
def profiles_list(db: Session = Depends(get_session)):
    return crud.list_profiles(db)


@app.post("/api/profiles", response_model=ProfileResponse)
def profiles_create(data: ProfileCreate, db: Session = Depends(get_session)):
    return crud.create_profile(db, data)


@app.get("/api/profiles/{profile_id}", response_model=ProfileResponse)
def profiles_get(profile_id: int, db: Session = Depends(get_session)):
    p = crud.get_profile(db, profile_id)
    if not p:
        raise HTTPException(404, "Profile not found")
    return p


@app.put("/api/profiles/{profile_id}", response_model=ProfileResponse)
def profiles_update(profile_id: int, data: ProfileCreate, db: Session = Depends(get_session)):
    p = crud.update_profile(db, profile_id, data)
    if not p:
        raise HTTPException(404, "Profile not found")
    return p


@app.delete("/api/profiles/{profile_id}")
def profiles_delete(profile_id: int, db: Session = Depends(get_session)):
    if not crud.delete_profile(db, profile_id):
        raise HTTPException(404, "Profile not found")
    return {"ok": True}


# --- Resumes ---


class ResumeListItem(BaseModel):
    id: int
    profile_id: int
    title: str
    status: str
    ats_score: float
    provider: str
    template_id: str
    wizard_step: int
    created_at: str
    updated_at: str


@app.get("/api/resumes/stats")
def resumes_stats(db: Session = Depends(get_session)):
    return crud.resume_stats(db)


@app.get("/api/resumes")
def resumes_list(
    profile_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_session),
):
    rows = crud.list_resumes(db, profile_id, status)
    return [
        ResumeListItem(
            id=r.id,
            profile_id=r.profile_id,
            title=r.title or f"Resume #{r.id}",
            status=r.status or "finished",
            ats_score=r.ats_score,
            provider=r.provider or "",
            template_id=getattr(r, "template_id", None) or "professional",
            wizard_step=r.wizard_step or 0,
            created_at=r.created_at.isoformat() if r.created_at else "",
            updated_at=r.updated_at.isoformat() if r.updated_at else "",
        )
        for r in rows
    ]


@app.get("/api/resumes/{resume_id}")
def resumes_get(resume_id: int, db: Session = Depends(get_session)):
    result = crud.get_resume(db, resume_id)
    if not result:
        raise HTTPException(404, "Resume not found")
    row, resume = result
    if row.status == "draft":
        draft = crud.get_draft(db, resume_id)
        return {
            "id": row.id,
            "profile_id": row.profile_id,
            "title": row.title,
            "status": "draft",
            "job_description": row.job_description,
            "wizard_step": row.wizard_step,
            "provider": row.provider,
            "draft": draft,
        }
    if not resume:
        raise HTTPException(404, "Resume content not found")
    report = score_resume(resume, row.job_description or "")
    return {
        "id": row.id,
        "profile_id": row.profile_id,
        "title": row.title,
        "status": row.status or "finished",
        "job_description": row.job_description,
        "resume": resume.model_dump(),
        "ats_report": report.model_dump(),
        "provider": row.provider,
        "cover_letter": row.cover_letter or "",
        "parent_id": row.parent_id,
        "has_diff": bool(row.previous_resume_json),
        "template_id": getattr(row, "template_id", None) or "professional",
    }


@app.get("/api/resumes/{resume_id}/preview")
def resumes_preview(resume_id: int, template: str | None = None, db: Session = Depends(get_session)):
    from fastapi.responses import HTMLResponse

    result = crud.get_resume(db, resume_id)
    if not result:
        raise HTTPException(404, "Resume not found")
    row, resume = result
    if not resume:
        raise HTTPException(400, "Draft resumes have no preview — generate first")
    tid = resolve_template_id(template or getattr(row, "template_id", None))
    html = render_resume_html(resume, tid)
    return HTMLResponse(content=html)


class TemplateUpdateRequest(BaseModel):
    template_id: str


@app.patch("/api/resumes/{resume_id}/template")
def resumes_set_template(
    resume_id: int, req: TemplateUpdateRequest, db: Session = Depends(get_session)
):
    tid = resolve_template_id(req.template_id)
    row = crud.update_template_id(db, resume_id, tid)
    if not row:
        raise HTTPException(404, "Resume not found")
    return {"id": row.id, "template_id": row.template_id}


class SaveDraftRequest(BaseModel):
    profile: ProfileCreate
    job_description: str = ""
    wizard_step: int = 0
    provider: str = "ollama"
    draft_id: int | None = None
    title: str = ""


@app.post("/api/resumes/draft")
def resumes_save_draft(req: SaveDraftRequest, db: Session = Depends(get_session)):
    profile_dict = req.profile.model_dump()
    errors = validate_profile_step(profile_dict, strict=False)
    if not req.profile.full_name.strip():
        raise HTTPException(400, "Name required to save draft")
    row, profile = crud.save_draft(
        db,
        req.profile,
        req.job_description,
        req.wizard_step,
        req.provider,
        req.draft_id,
        req.title,
    )
    return {
        "id": row.id,
        "profile_id": profile.id,
        "title": row.title,
        "status": "draft",
        "wizard_step": row.wizard_step,
    }


@app.get("/api/resumes/draft/{draft_id}")
def resumes_get_draft(draft_id: int, db: Session = Depends(get_session)):
    draft = crud.get_draft(db, draft_id)
    if not draft:
        raise HTTPException(404, "Draft not found")
    return draft


class ValidateWizardRequest(BaseModel):
    step: int
    profile: ProfileCreate
    job_description: str = ""
    for_generate: bool = False


@app.post("/api/wizard/validate")
def wizard_validate(req: ValidateWizardRequest):
    p = req.profile.model_dump()
    errors: list[str] = []
    if req.step == 0:
        errors = validate_profile_step(p, strict=req.for_generate)
    elif req.step == 1:
        errors = validate_experience_step(p.get("experience", []), for_generate=req.for_generate)
    elif req.step == 2:
        errors = validate_education_step(p.get("education", []))
    elif req.step == 3:
        errors = validate_skills_step(p.get("skills", []), for_generate=req.for_generate)
    elif req.step == 4:
        errors = validate_job_description(req.job_description, required=req.for_generate)
    elif req.for_generate:
        errors = (
            validate_profile_step(p, strict=True)
            + validate_experience_step(p.get("experience", []), for_generate=True)
            + validate_education_step(p.get("education", []))
            + validate_skills_step(p.get("skills", []), for_generate=True)
            + validate_job_description(req.job_description, required=True)
        )
    return {"valid": len(errors) == 0, "errors": errors}


@app.patch("/api/resumes/{resume_id}/status")
def resumes_set_status(resume_id: int, status: str, db: Session = Depends(get_session)):
    if status not in ("draft", "finished"):
        raise HTTPException(400, "Status must be draft or finished")
    row = crud.set_resume_status(db, resume_id, status)
    if not row:
        raise HTTPException(404, "Resume not found")
    return {"id": row.id, "status": row.status}


class GenerateRequest(BaseModel):
    profile_id: int
    job_description: str
    provider: str | None = None
    model: str | None = None
    draft_id: int | None = None
    template_id: str = "professional"


@app.post("/api/resumes/generate")
async def resumes_generate(req: GenerateRequest, db: Session = Depends(get_session)):
    profile = crud.get_profile(db, req.profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")

    p = profile.model_dump()
    errors = (
        validate_profile_step(p, strict=True)
        + validate_experience_step(p.get("experience", []), for_generate=True)
        + validate_education_step(p.get("education", []))
        + validate_skills_step(p.get("skills", []), for_generate=True)
        + validate_job_description(req.job_description, required=True)
    )
    if errors:
        raise HTTPException(400, "; ".join(errors))

    cfg = get_runtime_config(db)
    try:
        resume = await generate_resume_from_profile(
            profile,
            req.job_description,
            normalize_provider_id(req.provider),
            req.model,
            cfg,
        )
    except Exception as e:
        msg = str(e)
        if any(x in msg for x in ("header", "contact_info", "personal_information", "Field required")):
            msg += (
                " Stop the API (Ctrl+C), then run: cd D:\\RESUMEPROJECT && npm run api. "
                "Check http://127.0.0.1:8000/api/health shows resume_parser v4-explicit-build."
            )
        raise HTTPException(500, f"AI generation failed: {msg}") from e

    if not getattr(resume, "phone_country_code", None):
        resume.phone_country_code = getattr(profile, "phone_country_code", None) or "+1"

    report = score_resume(resume, req.job_description)
    provider = normalize_provider_id(
        req.provider or cfg.get("default_ai_provider") or settings.default_ai_provider
    )

    from resume_engine.db.models import ResumeRecord

    template_id = resolve_template_id(req.template_id)
    if req.draft_id:
        row = db.query(ResumeRecord).filter(ResumeRecord.id == req.draft_id).first()
        if row:
            row.status = "finished"
            row.resume_json = resume.model_dump_json()
            row.job_description = req.job_description
            row.ats_score = report.composite_score
            row.provider = provider
            row.template_id = template_id
            row.title = crud._resume_title(resume, profile.full_name, profile.target_role)
            db.commit()
            db.refresh(row)
        else:
            row = crud.save_resume(
                db,
                req.profile_id,
                resume,
                req.job_description,
                report.composite_score,
                provider,
                template_id=template_id,
            )
    else:
        row = crud.save_resume(
            db,
            req.profile_id,
            resume,
            req.job_description,
            report.composite_score,
            provider,
            template_id=template_id,
        )
    return {
        "id": row.id,
        "resume": resume.model_dump(),
        "ats_report": report.model_dump(),
    }


class ScoreRequest(BaseModel):
    resume: ResumeData
    job_description: str = ""


@app.post("/api/resumes/score")
def resumes_score(req: ScoreRequest):
    report = score_resume(req.resume, req.job_description)
    return report.model_dump()


class OptimizeRequest(BaseModel):
    resume_id: int
    provider: str | None = None
    model: str | None = None


@app.post("/api/resumes/optimize")
async def resumes_optimize(req: OptimizeRequest, db: Session = Depends(get_session)):
    result = crud.get_resume(db, req.resume_id)
    if not result:
        raise HTTPException(404, "Resume not found")
    row, resume = result
    report = score_resume(resume, row.job_description or "")
    if not report.missing_keywords:
        return {
            "id": row.id,
            "resume": resume.model_dump(),
            "ats_report": report.model_dump(),
            "message": "No missing keywords to optimize",
        }

    crud.snapshot_before_optimize(db, req.resume_id)
    cfg = get_runtime_config(db)
    try:
        improved = await optimize_resume(
            resume,
            row.job_description or "",
            report.missing_keywords,
            normalize_provider_id(req.provider),
            req.model,
            cfg,
        )
    except Exception as e:
        raise HTTPException(500, f"Optimization failed: {e}") from e

    if not improved.phone_country_code:
        improved.phone_country_code = getattr(resume, "phone_country_code", "+1") or "+1"

    new_report = score_resume(improved, row.job_description or "")
    crud.update_resume_record(db, row.id, improved, new_report.composite_score)
    return {
        "id": row.id,
        "resume": improved.model_dump(),
        "ats_report": new_report.model_dump(),
    }


class UpdateResumeRequest(BaseModel):
    resume: ResumeData


@app.put("/api/resumes/{resume_id}")
def resumes_update(resume_id: int, req: UpdateResumeRequest, db: Session = Depends(get_session)):
    result = crud.get_resume(db, resume_id)
    if not result:
        raise HTTPException(404, "Resume not found")
    row, _ = result
    if row.status == "draft":
        raise HTTPException(400, "Cannot update draft as resume — generate first")
    report = score_resume(req.resume, row.job_description or "")
    crud.update_resume_record(db, resume_id, req.resume, report.composite_score)
    return {
        "id": resume_id,
        "resume": req.resume.model_dump(),
        "ats_report": report.model_dump(),
    }


class ExportRequest(BaseModel):
    format: str = "docx"  # docx, pdf, txt
    template_id: str | None = None


@app.post("/api/resumes/{resume_id}/export")
def resumes_export(resume_id: int, req: ExportRequest, db: Session = Depends(get_session)):
    result = crud.get_resume(db, resume_id)
    if not result:
        raise HTTPException(404, "Resume not found")
    row, resume = result
    if not resume or row.status == "draft":
        raise HTTPException(400, "Finish the resume before exporting")
    report = score_resume(resume, row.job_description or "")

    safe_name = "".join(c if c.isalnum() else "_" for c in resume.full_name)[:40]
    fmt = req.format.lower()
    ext = {"docx": "docx", "pdf": "pdf", "txt": "txt"}.get(fmt, "docx")
    out_path = settings.export_path / f"{safe_name}_resume_{resume_id}.{ext}"

    tid = resolve_template_id(req.template_id or getattr(row, "template_id", None))
    if fmt == "pdf":
        export_pdf(resume, out_path, tid)
    elif fmt == "txt":
        export_txt(resume, out_path)
    else:
        export_docx(resume, out_path, tid)

    return {
        "path": str(out_path),
        "filename": out_path.name,
        "format": fmt,
        "ats_score": report.composite_score,
        "warnings": report.export_warnings,
    }


@app.delete("/api/resumes/{resume_id}")
def resumes_delete(resume_id: int, db: Session = Depends(get_session)):
    if not crud.delete_resume(db, resume_id):
        raise HTTPException(404, "Resume not found")
    return {"ok": True}


@app.get("/api/resumes/{resume_id}/download")
def resumes_download(resume_id: int, format: str = "docx", db: Session = Depends(get_session)):
    result = crud.get_resume(db, resume_id)
    if not result:
        raise HTTPException(404, "Resume not found")
    row, resume = result
    if not resume:
        raise HTTPException(400, "Draft resumes cannot be downloaded — generate first")
    safe_name = "".join(c if c.isalnum() else "_" for c in resume.full_name)[:40]
    fmt = format.lower()
    ext = {"docx": "docx", "pdf": "pdf", "txt": "txt"}.get(fmt, "docx")
    out_path = settings.export_path / f"{safe_name}_resume_{resume_id}.{ext}"

    tid = resolve_template_id(getattr(row, "template_id", None))
    if not out_path.exists():
        if fmt == "pdf":
            export_pdf(resume, out_path, tid)
        elif fmt == "txt":
            export_txt(resume, out_path)
        else:
            export_docx(resume, out_path, tid)

    media = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
        "txt": "text/plain",
    }
    return FileResponse(
        path=str(out_path),
        filename=out_path.name,
        media_type=media.get(fmt, "application/octet-stream"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host=settings.api_host, port=settings.api_port, reload=True)
