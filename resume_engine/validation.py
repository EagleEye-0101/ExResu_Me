"""Shared validation for profiles, dates, and wizard steps."""

import re
from typing import Any

MONTH_YEAR = re.compile(r"^(0[1-9]|1[0-2])/\d{4}$")
YEAR_ONLY = re.compile(r"^\d{4}$")
EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE = re.compile(r"^[\d\s\-+().]{7,20}$")


def normalize_month_year(value: str) -> str:
    """Convert YYYY-MM (from month input) or loose input to MM/YYYY."""
    v = value.strip()
    if not v:
        return ""
    if MONTH_YEAR.match(v):
        return v
    if re.match(r"^\d{4}-\d{2}$", v):
        y, m = v.split("-")
        return f"{m}/{y}"
    if YEAR_ONLY.match(v):
        return f"01/{v}"
    return v


def is_valid_month_year(value: str, required: bool = True) -> bool:
    if not value or not value.strip():
        return not required
    v = value.strip()
    if v.lower() == "present":
        return True
    return bool(MONTH_YEAR.match(v) or YEAR_ONLY.match(v) or re.match(r"^\d{4}-\d{2}$", v))


def is_valid_end_date(value: str) -> bool:
    if not value or not value.strip():
        return True
    v = value.strip()
    if v.lower() == "present":
        return True
    return is_valid_month_year(v, required=True)


def is_valid_email(value: str) -> bool:
    return bool(value and EMAIL.match(value.strip()))


def is_valid_phone(value: str, country_code: str = "+1") -> bool:
    from resume_engine.utils.phone import validate_phone as vp

    ok, _ = vp(country_code, value)
    return ok


def is_valid_linkedin(value: str) -> bool:
    if not value or not value.strip():
        return True
    v = value.strip().lower()
    return "linkedin.com" in v or v.startswith("http")


def validate_profile_step(data: dict[str, Any], *, strict: bool = False) -> list[str]:
    errors: list[str] = []
    if not (data.get("full_name") or "").strip():
        errors.append("Full name is required")
    if strict or (data.get("email") or "").strip():
        if not is_valid_email(data.get("email", "")):
            errors.append("Valid email is required (e.g. you@company.com)")
    elif strict:
        errors.append("Email is required")
    cc = data.get("phone_country_code") or "+1"
    if strict or (data.get("phone") or "").strip():
        if not is_valid_phone(data.get("phone", ""), cc):
            errors.append("Valid phone number required for selected country code")
    elif strict:
        errors.append("Phone is required")
    if (data.get("linkedin") or "").strip() and not is_valid_linkedin(data.get("linkedin", "")):
        errors.append("LinkedIn should be a full linkedin.com URL")
    years = data.get("years_experience", 0)
    if years is not None and (years < 0 or years > 60):
        errors.append("Years of experience must be between 0 and 60")
    return errors


def validate_experience_step(experience: list[dict], *, for_generate: bool = False) -> list[str]:
    errors: list[str] = []
    if for_generate and not experience:
        errors.append("Add at least one job before generating")
        return errors
    for i, job in enumerate(experience):
        prefix = f"Job {i + 1}"
        if for_generate or job.get("company") or job.get("title"):
            if not (job.get("company") or "").strip():
                errors.append(f"{prefix}: Company is required")
            if not (job.get("title") or "").strip():
                errors.append(f"{prefix}: Job title is required")
            start = job.get("start_date", "")
            if for_generate and not is_valid_month_year(start, required=True):
                errors.append(f"{prefix}: Start date must be MM/YYYY (e.g. 03/2021)")
            elif start and not is_valid_month_year(start, required=False):
                errors.append(f"{prefix}: Invalid start date format")
            end = (job.get("end_date") or "").strip()
            if end and not is_valid_end_date(end):
                errors.append(f"{prefix}: End date must be Present or MM/YYYY")
            if for_generate:
                bullets = [b for b in (job.get("bullets") or []) if b and str(b).strip()]
                if not bullets:
                    errors.append(f"{prefix}: Add at least one bullet point")
    return errors


def validate_education_step(education: list[dict]) -> list[str]:
    errors: list[str] = []
    for i, edu in enumerate(education):
        has_any = any((edu.get(k) or "").strip() for k in ("institution", "degree", "field"))
        if not has_any:
            continue
        if not (edu.get("institution") or "").strip():
            errors.append(f"Education {i + 1}: Institution is required when adding education")
        if not (edu.get("degree") or "").strip():
            errors.append(f"Education {i + 1}: Degree is required when adding education")
        grad = edu.get("graduation_date") or ""
        if grad and not (is_valid_month_year(grad, False) or YEAR_ONLY.match(grad.strip())):
            errors.append(f"Education {i + 1}: Graduation must be YYYY or MM/YYYY")
    return errors


def _normalize_skills(skills: list[str]) -> list[str]:
    """Split combined entries (commas, semicolons, newlines) into separate skills."""
    import re

    out: list[str] = []
    seen: set[str] = set()
    for item in skills:
        for part in re.split(r"[,;|\n]+", item or ""):
            s = re.sub(r"^[\s•\-*]+", "", part.strip())
            if not s:
                continue
            key = s.lower()
            if key not in seen:
                seen.add(key)
                out.append(s)
    return out


def validate_skills_step(skills: list[str], *, for_generate: bool = False) -> list[str]:
    normalized = _normalize_skills(skills)
    if for_generate and len(normalized) < 3:
        return ["Add at least 3 skills before generating (use commas or new lines between each)"]
    return []


def validate_job_description(jd: str, *, required: bool = False) -> list[str]:
    if required and len((jd or "").strip()) < 50:
        return ["Paste the full job description (at least 50 characters)"]
    return []
