"""Parse uploaded resume files into profile-shaped dict."""

import re
import tempfile
from pathlib import Path


def parse_pdf_text(content: bytes) -> str:
    try:
        import fitz  # pymupdf

        doc = fitz.open(stream=content, filetype="pdf")
        parts: list[str] = []
        for page in doc:
            parts.append(page.get_text())
        doc.close()
        return "\n".join(parts)
    except ImportError:
        try:
            import pdfplumber
            from io import BytesIO

            with pdfplumber.open(BytesIO(content)) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except ImportError:
            raise ValueError(
                "PDF support requires pymupdf. Install with: pip install pymupdf"
            ) from None


def parse_txt(content: str) -> dict:
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    name = lines[0] if lines else ""
    email = ""
    phone = ""
    linkedin = ""
    github = ""
    for ln in lines[:12]:
        if "@" in ln and not email:
            m = re.search(r"[\w.+-]+@[\w.-]+\.\w+", ln)
            email = m.group(0) if m else ln.split("|")[0].strip()
        if re.search(r"\d{7,}", ln.replace(" ", "")) and not phone:
            digits = re.sub(r"\D", "", ln)
            if len(digits) >= 7:
                phone = digits[-10:]
        if "linkedin" in ln.lower() and not linkedin:
            linkedin = ln.split(":", 1)[-1].strip() if ":" in ln else ln
        if "github" in ln.lower() and not github:
            github = ln.split(":", 1)[-1].strip() if ":" in ln else ln
    return {
        "full_name": name,
        "email": email or "candidate@example.com",
        "phone": phone or "0000000000",
        "phone_country_code": "+1",
        "linkedin": linkedin,
        "summary_notes": "\n".join(lines[1:30]),
        "experience": [],
        "education": [],
        "skills": [],
    }


def parse_docx(path: Path) -> dict:
    from docx import Document

    doc = Document(str(path))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return parse_txt(text)


def parse_upload_bytes(filename: str, content: bytes) -> dict:
    suffix = Path(filename or "upload.txt").suffix.lower()
    if suffix == ".pdf":
        text = parse_pdf_text(content)
        return parse_txt(text)
    if suffix == ".docx":
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(content)
            tmp.flush()
            return parse_docx(Path(tmp.name))
    return parse_txt(content.decode("utf-8", errors="ignore"))
