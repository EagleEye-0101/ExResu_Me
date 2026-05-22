from pydantic import BaseModel, Field, field_validator

from resume_engine.utils.phone import format_phone_display


class Experience(BaseModel):
    company: str
    title: str
    location: str = ""
    start_date: str = Field(..., description="MM/YYYY format")
    end_date: str = Field(default="", description="MM/YYYY, Present, or empty")
    bullets: list[str] = Field(default_factory=list, min_length=1)


class Education(BaseModel):
    institution: str
    degree: str
    field: str = ""
    graduation_date: str = Field(default="", description="MM/YYYY or year")
    gpa: str = ""


class Certification(BaseModel):
    name: str
    issuer: str = ""
    date: str = ""


class ResumeData(BaseModel):
    full_name: str
    email: str
    phone: str
    phone_country_code: str = "+1"
    location: str = ""
    linkedin: str = ""
    headline: str = ""
    summary: str = ""
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Valid email required")
        return v.strip()

    def to_text(self) -> str:
        lines = [
            self.full_name,
            f"{self.email} | {format_phone_display(self.phone_country_code, self.phone)}",
            self.location,
            "",
            self.headline,
            "",
            "SUMMARY",
            self.summary,
            "",
            "EXPERIENCE",
        ]
        for exp in self.experience:
            lines.append(f"{exp.title} | {exp.company}")
            lines.append(f"{exp.start_date} - {exp.end_date}")
            lines.extend(f"- {b}" for b in exp.bullets)
            lines.append("")
        lines.append("EDUCATION")
        for edu in self.education:
            lines.append(f"{edu.degree} - {edu.institution} ({edu.graduation_date})")
        lines.append("")
        lines.append("SKILLS")
        lines.append(", ".join(self.skills))
        if self.certifications:
            lines.append("")
            lines.append("CERTIFICATIONS")
            for cert in self.certifications:
                lines.append(f"{cert.name} ({cert.issuer}) {cert.date}")
        return "\n".join(lines)


class ResumeGenerateRequest(BaseModel):
    profile_id: int
    job_description: str
    provider: str | None = None
    model: str | None = None
