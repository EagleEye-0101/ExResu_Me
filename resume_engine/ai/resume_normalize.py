"""Map varied AI JSON shapes into flat ResumeData fields."""

from __future__ import annotations

import re
from typing import Any

from resume_engine.schemas.profile import ProfileResponse

_NESTED_CONTACT_KEYS = frozenset(
    {
        "personal_information",
        "contact",
        "contact_info",
        "contact_information",
        "personal_info",
        "header",
        "contact_details",
        "details",
    }
)

_ARRAY_KEYS = frozenset(
    {
        "experience",
        "work_experience",
        "employment",
        "professional_experience",
        "education",
        "education_history",
        "certifications",
        "licenses",
    }
)

_CONTACT_FIELD_HINTS = frozenset(
    {
        "email",
        "phone",
        "full_name",
        "name",
        "phone_number",
        "mobile",
        "linkedin",
        "location",
        "address",
        "headline",
    }
)

_WRAPPER_KEYS = frozenset(
    {
        "resume",
        "data",
        "result",
        "response",
        "content",
        "output",
        "json",
        "payload",
        "body",
    }
)


def _is_contact_like(block: dict) -> bool:
    return bool(set(block.keys()) & _CONTACT_FIELD_HINTS)


def _is_skills_bucket(value: Any) -> bool:
    return isinstance(value, dict) and bool(
        set(value.keys()) & {"technical_skills", "soft_skills", "hard_skills", "core_competencies"}
    )


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        parts = [_as_str(v) for v in value if _as_str(v)]
        return "\n".join(parts) if len(parts) > 1 else (parts[0] if parts else "")
    if isinstance(value, dict):
        for key in ("text", "content", "summary", "description", "value"):
            if key in value:
                return _as_str(value[key])
        return ""
    return str(value).strip()


def _pick(data: dict, *keys: str) -> str:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return _as_str(data[key])
    return ""


def _unwrap_ai_payload(data: Any) -> dict[str, Any]:
    """Lift resume/data/result wrappers some models add around the real JSON."""
    if not isinstance(data, dict):
        return {}
    current = dict(data)
    for _ in range(8):
        changed = False
        for key in _WRAPPER_KEYS:
            inner = current.get(key)
            if isinstance(inner, dict):
                merged = {**current, **inner}
                for wrapper in _WRAPPER_KEYS:
                    merged.pop(wrapper, None)
                current = merged
                changed = True
        if not changed:
            break
    return current


def _flatten_nested(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively lift contact fields from header / contact_info / etc. to top level."""
    if not isinstance(data, dict):
        return {}
    flat: dict[str, Any] = {}
    for key, value in data.items():
        if key in _ARRAY_KEYS:
            flat[key] = value
            continue
        if key == "skills":
            flat["skills"] = value
            continue
        if isinstance(value, dict) and (
            key in _NESTED_CONTACT_KEYS or _is_contact_like(value)
        ):
            if key == "skills" and _is_skills_bucket(value):
                flat["skills"] = value
                continue
            inner = _flatten_nested(value)
            for inner_key, inner_val in inner.items():
                if inner_key in _ARRAY_KEYS or inner_key == "skills":
                    flat[inner_key] = inner_val
                elif inner_key not in flat or flat[inner_key] in (None, "", [], {}):
                    flat[inner_key] = inner_val
            continue
        flat[key] = value
    extracted = _extract_contact_from_any_nesting(data)
    for key, value in extracted.items():
        if key not in flat or flat[key] in (None, "", [], {}):
            flat[key] = value
    return flat


def _normalize_experience(items: Any) -> list[dict]:
    if not isinstance(items, list):
        return []
    out: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        bullets = item.get("bullets")
        if not bullets:
            for alt in ("responsibilities", "achievements", "highlights", "description", "duties"):
                if alt in item:
                    bullets = item[alt]
                    break
        if isinstance(bullets, str):
            bullets = [b.strip() for b in bullets.split("\n") if b.strip()]
        elif not isinstance(bullets, list):
            bullets = []
        bullets = [_as_str(b) for b in bullets if _as_str(b)]
        if not bullets:
            bullets = ["Contributed to team goals and deliverables."]

        out.append(
            {
                "company": _pick(item, "company", "employer", "organization", "org"),
                "title": _pick(item, "title", "role", "position", "job_title"),
                "location": _pick(item, "location", "city"),
                "start_date": _pick(item, "start_date", "start", "from"),
                "end_date": _pick(item, "end_date", "end", "to") or "Present",
                "bullets": bullets,
            }
        )
    return out


def _normalize_education(items: Any) -> list[dict]:
    if not isinstance(items, list):
        return []
    out: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "institution": _pick(item, "institution", "school", "university", "college"),
                "degree": _pick(item, "degree", "qualification", "program"),
                "field": _pick(item, "field", "major", "concentration"),
                "graduation_date": _pick(item, "graduation_date", "graduation", "year", "end_date"),
                "gpa": _pick(item, "gpa"),
            }
        )
    return out


def _normalize_skills_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [s.strip() for s in re.split(r"[,;|\n]+", value) if s.strip()]
    if isinstance(value, list):
        return [_as_str(s) for s in value if _as_str(s)]
    return []


def _normalize_skills(value: Any) -> list[str]:
    """Accept list, string, or {technical_skills, soft_skills, ...} objects."""
    if isinstance(value, dict):
        merged: list[str] = []
        seen: set[str] = set()
        for key in (
            "skills",
            "technical_skills",
            "soft_skills",
            "hard_skills",
            "core_competencies",
            "tools",
            "languages",
        ):
            for skill in _normalize_skills_list(value.get(key)):
                key_lower = skill.lower()
                if key_lower not in seen:
                    seen.add(key_lower)
                    merged.append(skill)
        return merged
    return _normalize_skills_list(value)


def _collect_skills(data: dict[str, Any]) -> list[str]:
    """Gather skills from any common AI key placement."""
    chunks: list[str] = []
    for key in ("skills", "technical_skills", "soft_skills", "core_competencies"):
        raw = data.get(key)
        if raw is not None:
            chunks.extend(_normalize_skills(raw))
    # Top-level skills might be the nested dict itself (only key named skills)
    if not chunks and isinstance(data.get("skills"), dict):
        chunks = _normalize_skills(data["skills"])
    seen: set[str] = set()
    out: list[str] = []
    for s in chunks:
        k = s.lower()
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out


def _auto_skill_groups(skills: list[str]) -> list[dict]:
    """Split flat skills into ATS-friendly categories when AI did not provide groups."""
    lang_kw = {"python", "javascript", "typescript", "java", "go", "rust", "c", "c++", "sql", "swift"}
    tool_kw = {"react", "node", "docker", "kubernetes", "aws", "git", "linux", "api", "fastapi", "django"}
    languages: list[str] = []
    tools: list[str] = []
    other: list[str] = []
    for s in skills:
        low = s.lower()
        if any(k in low for k in lang_kw):
            languages.append(s)
        elif any(k in low for k in tool_kw):
            tools.append(s)
        else:
            other.append(s)
    groups: list[dict] = []
    if languages:
        groups.append({"label": "Programming Languages", "skills": languages})
    if tools:
        groups.append({"label": "Tools & Frameworks", "skills": tools})
    if other:
        groups.append({"label": "Other Skills", "skills": other})
    return groups or [{"label": "Skills", "skills": skills}]


def _normalize_certifications(items: Any) -> list[dict]:
    if not isinstance(items, list):
        return []
    out: list[dict] = []
    for item in items:
        if isinstance(item, str):
            out.append({"name": item.strip(), "issuer": "", "date": ""})
        elif isinstance(item, dict):
            out.append(
                {
                    "name": _pick(item, "name", "certification", "title"),
                    "issuer": _pick(item, "issuer", "organization"),
                    "date": _pick(item, "date", "year"),
                }
            )
    return [c for c in out if c["name"]]


def _extract_contact_from_any_nesting(raw: dict[str, Any]) -> dict[str, Any]:
    """Walk nested header/contact blocks and collect contact fields."""
    found: dict[str, Any] = {}
    stack: list[dict[str, Any]] = [raw]
    seen_ids: set[int] = set()
    while stack:
        node = stack.pop()
        nid = id(node)
        if nid in seen_ids:
            continue
        seen_ids.add(nid)
        for key, value in node.items():
            if key in _CONTACT_FIELD_HINTS and not isinstance(value, (dict, list)):
                if value not in (None, ""):
                    found[key] = value
            elif isinstance(value, dict):
                if key in _NESTED_CONTACT_KEYS or _is_contact_like(value):
                    stack.append(value)
    return found


def _resume_from_normalized(normalized: dict[str, Any]):
    """Build ResumeData from a flat dict — never pass nested header/contact wrappers."""
    from resume_engine.schemas.resume import (
        Activity,
        Certification,
        Education,
        Experience,
        Project,
        ResumeData,
        SkillGroup,
    )

    experience = [Experience(**item) for item in normalized.get("experience", [])]
    education = [Education(**item) for item in normalized.get("education", [])]
    certifications = [Certification(**item) for item in normalized.get("certifications", [])]
    projects = [Project(**item) for item in normalized.get("projects", [])]
    activities = [Activity(**item) for item in normalized.get("activities", [])]
    skill_groups = [SkillGroup(**item) for item in normalized.get("skill_groups", [])]
    return ResumeData(
        full_name=normalized["full_name"],
        email=normalized["email"],
        phone=normalized["phone"],
        phone_country_code=normalized.get("phone_country_code") or "+1",
        location=normalized.get("location") or "",
        linkedin=normalized.get("linkedin") or "",
        github=normalized.get("github") or "",
        headline=normalized.get("headline") or "",
        summary=normalized.get("summary") or "",
        experience=experience,
        education=education,
        skills=list(normalized.get("skills") or []),
        skill_groups=skill_groups,
        projects=projects,
        activities=activities,
        certifications=certifications,
    )


def parse_ai_resume(raw: dict[str, Any], profile: ProfileResponse):
    """Normalize AI JSON then validate as ResumeData (always use this after AI complete)."""
    raw = _unwrap_ai_payload(raw)
    normalized = normalize_ai_resume(raw, profile)
    # Wizard profile always wins for required contact fields
    contact = _extract_contact_from_any_nesting(raw)
    normalized["full_name"] = (
        profile.full_name
        or _pick(contact, "full_name", "name")
        or _pick(normalized, "full_name", "name")
        or "Candidate"
    )
    normalized["email"] = (
        profile.email
        or _pick(contact, "email", "email_address")
        or normalized.get("email", "")
        or "candidate@example.com"
    )
    normalized["phone"] = (
        profile.phone
        or _pick(contact, "phone", "phone_number", "mobile")
        or normalized.get("phone", "")
        or "0000000000"
    )
    return _resume_from_normalized(normalized)


def normalize_ai_resume(raw: dict[str, Any], profile: ProfileResponse) -> dict[str, Any]:
    """Flatten nested AI output; fill missing required fields from the user profile."""
    raw = _unwrap_ai_payload(raw)
    data = _flatten_nested(dict(raw))

    summary = data.get("summary")
    if summary is None:
        summary = (
            data.get("professional_summary")
            or data.get("profile_summary")
            or data.get("objective")
        )
    summary_str = _as_str(summary)

    experience = (
        data.get("experience")
        or data.get("work_experience")
        or data.get("employment")
        or data.get("professional_experience")
        or []
    )

    education = data.get("education") or data.get("education_history") or []
    skills = _collect_skills(data)
    certifications = data.get("certifications") or data.get("licenses") or []

    phone = _pick(data, "phone", "phone_number", "mobile", "telephone") or profile.phone
    email = _pick(data, "email", "email_address") or profile.email
    if "@" not in email:
        email = profile.email

    full_name = _pick(data, "full_name", "name") or profile.full_name

    exp = _normalize_experience(experience) or _normalize_experience(
        [e.model_dump() if hasattr(e, "model_dump") else e for e in profile.experience]
    )
    edu = _normalize_education(education) or _normalize_education(
        [e.model_dump() if hasattr(e, "model_dump") else e for e in profile.education]
    )
    if not skills:
        skills = list(profile.skills)

    skill_groups_raw = data.get("skill_groups")
    skill_groups: list[dict] = []
    if isinstance(skill_groups_raw, list) and skill_groups_raw:
        for g in skill_groups_raw:
            if isinstance(g, dict):
                skill_groups.append(g)
            elif hasattr(g, "model_dump"):
                skill_groups.append(g.model_dump())
    elif len(skills) >= 5:
        skill_groups = _auto_skill_groups(skills)

    projects_raw = data.get("projects") if isinstance(data.get("projects"), list) else []
    activities_raw = data.get("activities") if isinstance(data.get("activities"), list) else []

    return {
        "full_name": full_name or "Candidate",
        "email": email or "candidate@example.com",
        "phone": phone or "0000000000",
        "phone_country_code": _pick(data, "phone_country_code", "country_code")
        or getattr(profile, "phone_country_code", None)
        or "+1",
        "location": _pick(data, "location", "address", "city") or profile.location or "",
        "linkedin": _pick(data, "linkedin", "linkedin_url") or profile.linkedin or "",
        "github": _pick(data, "github", "github_url") or "",
        "headline": _pick(data, "headline", "professional_headline", "title")
        or profile.headline
        or "",
        "summary": summary_str
        or profile.summary_notes
        or "Professional summary pending.",
        "experience": exp,
        "education": edu,
        "skills": skills,
        "skill_groups": skill_groups,
        "projects": projects_raw,
        "activities": activities_raw,
        "certifications": _normalize_certifications(certifications)
        or _normalize_certifications(profile.certifications),
    }
