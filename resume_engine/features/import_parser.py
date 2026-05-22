"""Parse uploaded resume files into profile-shaped dict."""

import re
from pathlib import Path


def parse_txt(content: str) -> dict:
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    name = lines[0] if lines else ""
    email = ""
    phone = ""
    for ln in lines[:8]:
        if "@" in ln and not email:
            email = ln.split("|")[0].strip() if "|" in ln else ln
        if re.search(r"\+?\d[\d\s\-().]{6,}", ln) and not phone:
            m = re.search(r"(\+\d{1,3})?[\s\-]?([\d\s\-().]{7,})", ln)
            if m:
                phone = re.sub(r"[^\d]", "", m.group(2))[-10:]
    return {
        "full_name": name,
        "email": email,
        "phone": phone,
        "phone_country_code": "+1",
        "summary_notes": "\n".join(lines[1:20]),
        "experience": [],
        "education": [],
        "skills": [],
    }


def parse_docx(path: Path) -> dict:
    from docx import Document

    doc = Document(str(path))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return parse_txt(text)
