import json

from sqlalchemy.orm import Session

from resume_engine.db.models import Profile, ResumeRecord, dumps_json, loads_json
from resume_engine.schemas.profile import ProfileCreate, ProfileResponse
from resume_engine.schemas.resume import ResumeData


def _profile_to_response(row: Profile) -> ProfileResponse:
    return ProfileResponse(
        id=row.id,
        full_name=row.full_name,
        email=row.email,
        phone=row.phone,
        phone_country_code=getattr(row, "phone_country_code", None) or "+1",
        location=row.location or "",
        linkedin=row.linkedin or "",
        target_role=row.target_role or "",
        years_experience=row.years_experience or 0,
        headline=row.headline or "",
        summary_notes=row.summary_notes or "",
        experience=loads_json(row.experience_json, []),
        education=loads_json(row.education_json, []),
        skills=loads_json(row.skills_json, []),
        certifications=loads_json(row.certifications_json, []),
    )


def create_profile(db: Session, data: ProfileCreate) -> ProfileResponse:
    row = Profile(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        phone_country_code=data.phone_country_code or "+1",
        location=data.location,
        linkedin=data.linkedin,
        target_role=data.target_role,
        years_experience=data.years_experience,
        headline=data.headline,
        summary_notes=data.summary_notes,
        experience_json=dumps_json([e.model_dump() for e in data.experience]),
        education_json=dumps_json([e.model_dump() for e in data.education]),
        skills_json=dumps_json(data.skills),
        certifications_json=dumps_json(data.certifications),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _profile_to_response(row)


def update_profile(db: Session, profile_id: int, data: ProfileCreate) -> ProfileResponse | None:
    row = db.query(Profile).filter(Profile.id == profile_id).first()
    if not row:
        return None
    row.full_name = data.full_name
    row.email = data.email
    row.phone = data.phone
    row.phone_country_code = data.phone_country_code or "+1"
    row.location = data.location
    row.linkedin = data.linkedin
    row.target_role = data.target_role
    row.years_experience = data.years_experience
    row.headline = data.headline
    row.summary_notes = data.summary_notes
    row.experience_json = dumps_json([e.model_dump() for e in data.experience])
    row.education_json = dumps_json([e.model_dump() for e in data.education])
    row.skills_json = dumps_json(data.skills)
    row.certifications_json = dumps_json(data.certifications)
    db.commit()
    db.refresh(row)
    return _profile_to_response(row)


def get_profile(db: Session, profile_id: int) -> ProfileResponse | None:
    row = db.query(Profile).filter(Profile.id == profile_id).first()
    return _profile_to_response(row) if row else None


def list_profiles(db: Session) -> list[ProfileResponse]:
    rows = db.query(Profile).order_by(Profile.updated_at.desc()).all()
    return [_profile_to_response(r) for r in rows]


def delete_profile(db: Session, profile_id: int) -> bool:
    row = db.query(Profile).filter(Profile.id == profile_id).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def _resume_title(resume: ResumeData, profile_name: str, target_role: str = "") -> str:
    if resume.headline:
        return resume.headline[:300]
    if target_role:
        return f"{profile_name} — {target_role}"[:300]
    return f"{profile_name} — Resume"[:300]


def save_resume(
    db: Session,
    profile_id: int,
    resume: ResumeData,
    job_description: str,
    ats_score: float,
    provider: str,
    title: str = "",
    template_id: str = "compact",
) -> ResumeRecord:
    profile = get_profile(db, profile_id)
    row = ResumeRecord(
        profile_id=profile_id,
        title=title or _resume_title(resume, resume.full_name, profile.target_role if profile else ""),
        status="finished",
        job_description=job_description,
        resume_json=resume.model_dump_json(),
        ats_score=ats_score,
        provider=provider,
        template_id=template_id or "compact",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_template_id(db: Session, resume_id: int, template_id: str) -> ResumeRecord | None:
    row = db.query(ResumeRecord).filter(ResumeRecord.id == resume_id).first()
    if not row:
        return None
    row.template_id = template_id
    db.commit()
    db.refresh(row)
    return row


def save_draft(
    db: Session,
    profile_data: ProfileCreate,
    job_description: str,
    wizard_step: int,
    provider: str,
    draft_id: int | None = None,
    title: str = "",
) -> tuple[ResumeRecord, ProfileResponse]:
    if draft_id:
        row = db.query(ResumeRecord).filter(ResumeRecord.id == draft_id).first()
        if row:
            profile = update_profile(db, row.profile_id, profile_data)
        else:
            profile = create_profile(db, profile_data)
            row = None
    else:
        profile = create_profile(db, profile_data)
        row = None

    draft_payload = {
        "profile": profile_data.model_dump(),
        "job_description": job_description,
        "wizard_step": wizard_step,
        "provider": provider,
    }
    draft_title = title or f"{profile_data.full_name or 'Untitled'} — {profile_data.target_role or 'Draft'}"

    if row:
        row.profile_id = profile.id
        row.title = draft_title[:300]
        row.status = "draft"
        row.job_description = job_description
        row.draft_json = json.dumps(draft_payload)
        row.wizard_step = wizard_step
        row.provider = provider
        row.resume_json = row.resume_json or "{}"
    else:
        row = ResumeRecord(
            profile_id=profile.id,
            title=draft_title[:300],
            status="draft",
            job_description=job_description,
            resume_json="{}",
            draft_json=json.dumps(draft_payload),
            wizard_step=wizard_step,
            provider=provider,
            ats_score=0.0,
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return row, profile


def get_draft(db: Session, draft_id: int) -> dict | None:
    row = db.query(ResumeRecord).filter(ResumeRecord.id == draft_id).first()
    if not row or row.status != "draft":
        return None
    data = json.loads(row.draft_json) if row.draft_json else {}
    return {
        "id": row.id,
        "profile_id": row.profile_id,
        "title": row.title,
        "status": row.status,
        "wizard_step": row.wizard_step,
        "provider": row.provider,
        "job_description": row.job_description,
        "profile": data.get("profile"),
        "updated_at": row.updated_at.isoformat() if row.updated_at else "",
    }


def set_resume_status(db: Session, resume_id: int, status: str) -> ResumeRecord | None:
    row = db.query(ResumeRecord).filter(ResumeRecord.id == resume_id).first()
    if not row:
        return None
    row.status = status
    db.commit()
    db.refresh(row)
    return row


def resume_stats(db: Session) -> dict:
    rows = db.query(ResumeRecord).all()
    drafts = sum(1 for r in rows if r.status == "draft")
    finished = sum(1 for r in rows if r.status == "finished")
    return {"total": len(rows), "drafts": drafts, "finished": finished}


def update_resume_record(
    db: Session,
    resume_id: int,
    resume: ResumeData,
    ats_score: float,
) -> ResumeRecord | None:
    row = db.query(ResumeRecord).filter(ResumeRecord.id == resume_id).first()
    if not row:
        return None
    row.resume_json = resume.model_dump_json()
    row.ats_score = ats_score
    db.commit()
    db.refresh(row)
    return row


def get_resume(db: Session, resume_id: int) -> tuple[ResumeRecord, ResumeData | None] | None:
    row = db.query(ResumeRecord).filter(ResumeRecord.id == resume_id).first()
    if not row:
        return None
    if row.status == "draft" or not row.resume_json or row.resume_json == "{}":
        return row, None
    resume = ResumeData.model_validate(json.loads(row.resume_json))
    return row, resume


def list_resumes(
    db: Session, profile_id: int | None = None, status: str | None = None
) -> list[ResumeRecord]:
    q = db.query(ResumeRecord)
    if profile_id:
        q = q.filter(ResumeRecord.profile_id == profile_id)
    if status:
        q = q.filter(ResumeRecord.status == status)
    return q.order_by(ResumeRecord.updated_at.desc()).all()


def delete_resume(db: Session, resume_id: int) -> bool:
    row = db.query(ResumeRecord).filter(ResumeRecord.id == resume_id).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def clone_resume(db: Session, resume_id: int, title: str = "") -> ResumeRecord | None:
    result = get_resume(db, resume_id)
    if not result:
        return None
    row, resume = result
    if not resume:
        return None
    new_title = title or f"{row.title or 'Resume'} (copy)"
    new_row = ResumeRecord(
        profile_id=row.profile_id,
        title=new_title[:300],
        status="finished",
        job_description=row.job_description,
        resume_json=resume.model_dump_json(),
        ats_score=row.ats_score,
        provider=row.provider,
        parent_id=row.id,
        template_id=getattr(row, "template_id", None) or "compact",
    )
    db.add(new_row)
    db.commit()
    db.refresh(new_row)
    return new_row


def snapshot_before_optimize(db: Session, resume_id: int) -> None:
    result = get_resume(db, resume_id)
    if not result:
        return
    row, resume = result
    if resume:
        row.previous_resume_json = resume.model_dump_json()
        db.commit()


def save_cover_letter(db: Session, resume_id: int, text: str) -> ResumeRecord | None:
    row = db.query(ResumeRecord).filter(ResumeRecord.id == resume_id).first()
    if not row:
        return None
    row.cover_letter = text
    db.commit()
    db.refresh(row)
    return row
