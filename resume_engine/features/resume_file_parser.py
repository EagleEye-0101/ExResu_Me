"""Parse uploaded resume files into ResumeData for ATS check and interview prep."""

from __future__ import annotations

import re
from pathlib import Path

from resume_engine.features.import_parser import parse_docx, parse_txt, parse_pdf_text
from resume_engine.schemas.resume import Activity, Education, Experience, Project, ResumeData, SkillGroup


_SECTION_MARKERS = {
    "education": re.compile(r"^education\b", re.I),
    "skills": re.compile(r"^skills?\b", re.I),
    "experience": re.compile(
        r"^(professional\s+)?experience\b|^(work\s+)?experience\b|employment\b",
        re.I,
    ),
    "projects": re.compile(r"^projects?\b", re.I),
    "activities": re.compile(r"^activities|awards\b", re.I),
    "summary": re.compile(r"^(professional\s+)?summary\b|profile\b|objective\b", re.I),
    "certifications": re.compile(r"^certifications?\b", re.I),
}


def _split_sections(text: str) -> dict[str, list[str]]:
    lines = [ln.strip() for ln in text.splitlines()]
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for ln in lines:
        if not ln:
            continue
        matched = None
        for name, pattern in _SECTION_MARKERS.items():
            if pattern.match(ln):
                matched = name
                break
        if matched:
            current = matched
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(ln)
    return sections


def _parse_bullets(lines: list[str]) -> list[str]:
    bullets: list[str] = []
    for ln in lines:
        if re.match(r"^[\u2022\u25e6\-\*◦•]\s*", ln) or ln.startswith("- "):
            bullets.append(re.sub(r"^[\u2022\u25e6\-\*◦•]\s*", "", ln).strip())
        elif bullets and len(ln) > 20:
            bullets[-1] += " " + ln
        elif len(ln) > 15:
            bullets.append(ln)
    return bullets


def _parse_experience_block(lines: list[str]) -> list[Experience]:
    entries: list[Experience] = []
    current: dict | None = None
    for ln in lines:
        if re.match(r"^[\u2022\u25e6\-\*◦•]", ln) or ln.startswith("- "):
            if current:
                current.setdefault("bullets", []).append(
                    re.sub(r"^[\u2022\u25e6\-\*◦•]\s*", "", ln).strip()
                )
            continue
        if current and current.get("bullets"):
            entries.append(
                Experience(
                    company=current.get("company", "Company"),
                    title=current.get("title", "Role"),
                    location=current.get("location", ""),
                    start_date=current.get("start_date", "01/2020"),
                    end_date=current.get("end_date", "Present"),
                    bullets=current["bullets"],
                )
            )
            current = None
        parts = re.split(r"\s{2,}|\t", ln)
        if len(parts) >= 2:
            current = {
                "company": parts[0],
                "location": parts[-1] if len(parts) > 2 else "",
                "title": parts[1] if len(parts) == 2 else parts[1],
                "start_date": "01/2020",
                "end_date": "Present",
                "bullets": [],
            }
        elif current is None:
            current = {
                "company": ln[:80],
                "title": "Role",
                "location": "",
                "start_date": "01/2020",
                "end_date": "Present",
                "bullets": [],
            }
        else:
            date_m = re.search(
                r"([A-Za-z]+\s+\d{4})\s*[-–]\s*([A-Za-z]+\s+\d{4}|Present)",
                ln,
                re.I,
            )
            if date_m:
                current["start_date"] = date_m.group(1)[:7]
                current["end_date"] = date_m.group(2)
            else:
                current["title"] = ln
    if current and current.get("bullets"):
        entries.append(
            Experience(
                company=current.get("company", "Company"),
                title=current.get("title", "Role"),
                location=current.get("location", ""),
                start_date=current.get("start_date", "01/2020"),
                end_date=current.get("end_date", "Present"),
                bullets=current["bullets"],
            )
        )
    return entries


def _parse_education(lines: list[str]) -> list[Education]:
    out: list[Education] = []
    for ln in lines:
        if len(ln) < 4:
            continue
        out.append(
            Education(
                institution=ln.split("—")[0].strip() if "—" in ln else ln[:60],
                degree=ln,
                field="",
                graduation_date="",
            )
        )
    return out[:5]


def _parse_skills(lines: list[str]) -> tuple[list[str], list[SkillGroup]]:
    flat: list[str] = []
    groups: list[SkillGroup] = []
    for ln in lines:
        if ":" in ln and len(ln.split(":")[0]) < 40:
            label, rest = ln.split(":", 1)
            skills = [s.strip() for s in re.split(r"[,;]", rest) if s.strip()]
            if skills:
                groups.append(SkillGroup(label=label.strip(), skills=skills))
                flat.extend(skills)
        else:
            flat.extend(s.strip() for s in re.split(r"[,;]", ln) if s.strip())
    return flat, groups


def text_to_resume_data(text: str, profile_hint: dict | None = None) -> ResumeData:
    """Heuristic conversion of resume plain text to ResumeData."""
    hint = profile_hint or {}
    sections = _split_sections(text)
    header_lines = sections.get("header", [])
    name = hint.get("full_name") or (header_lines[0] if header_lines else "Candidate")
    email = hint.get("email", "")
    phone = hint.get("phone", "")
    for ln in header_lines[:10]:
        if "@" in ln and not email:
            m = re.search(r"[\w.+-]+@[\w.-]+\.\w+", ln)
            email = m.group(0) if m else ln
        if re.search(r"\d{7,}", ln.replace(" ", "")) and not phone:
            digits = re.sub(r"\D", "", ln)
            if len(digits) >= 7:
                phone = digits[-10:]

    summary_lines = sections.get("summary", [])
    summary = " ".join(summary_lines) if summary_lines else "\n".join(header_lines[1:4])

    exp_lines = sections.get("experience", [])
    experience = _parse_experience_block(exp_lines)
    if not experience and hint.get("experience"):
        experience = [Experience(**e) for e in hint["experience"]]

    edu = _parse_education(sections.get("education", []))
    flat_skills, skill_groups = _parse_skills(sections.get("skills", []))

    projects: list[Project] = []
    for ln in sections.get("projects", [])[:20]:
        if not re.match(r"^[\u2022\u25e6\-\*◦•]", ln):
            projects.append(Project(name=ln[:120], bullets=[]))
        elif projects:
            projects[-1].bullets.append(re.sub(r"^[\u2022\u25e6\-\*◦•]\s*", "", ln))

    activities: list[Activity] = []
    for ln in sections.get("activities", []):
        if not re.match(r"^[\u2022\u25e6\-\*◦•]", ln):
            activities.append(Activity(title=ln[:120], bullets=[]))
        elif activities:
            activities[-1].bullets.append(re.sub(r"^[\u2022\u25e6\-\*◦•]\s*", "", ln))

    if not email or "@" not in email:
        email = "candidate@example.com"
    if not phone:
        phone = "0000000000"

    return ResumeData(
        full_name=name,
        email=email,
        phone=phone,
        phone_country_code=hint.get("phone_country_code", "+1"),
        location=hint.get("location", ""),
        linkedin=hint.get("linkedin", ""),
        summary=summary[:2000] if summary else "Imported resume.",
        experience=experience
        or [
            Experience(
                company="See uploaded resume",
                title="Role",
                start_date="01/2020",
                end_date="Present",
                bullets=["Review and edit imported content in the editor."],
            )
        ],
        education=edu,
        skills=flat_skills or list(hint.get("skills") or []),
        skill_groups=skill_groups,
        projects=projects,
        activities=activities,
    )


def parse_resume_file(path: Path, content: bytes | None = None) -> ResumeData:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        raw = content if content is not None else path.read_bytes()
        text = parse_pdf_text(raw)
        hint = parse_txt(text)
        return text_to_resume_data(text, hint)
    if suffix == ".docx":
        data = parse_docx(path if content is None else _write_temp(path, content))
        text = "\n".join(
            [
                data.get("full_name", ""),
                data.get("email", ""),
                data.get("phone", ""),
                data.get("summary_notes", ""),
            ]
        )
        return text_to_resume_data(text or path.read_text(encoding="utf-8", errors="ignore"), data)
    text = (content or path.read_bytes()).decode("utf-8", errors="ignore")
    hint = parse_txt(text)
    return text_to_resume_data(text, hint)


def _write_temp(path: Path, content: bytes) -> Path:
    import tempfile

    tmp = Path(tempfile.mktemp(suffix=path.suffix))
    tmp.write_bytes(content)
    return tmp
