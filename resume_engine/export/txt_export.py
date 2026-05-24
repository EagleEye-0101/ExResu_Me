from pathlib import Path

from resume_engine.schemas.resume import ResumeData


def export_txt(resume: ResumeData, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(resume.to_text(), encoding="utf-8")
    return output_path
