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


class SkillGroup(BaseModel):
    label: str
    skills: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str
    context: str = ""
    start_date: str = ""
    end_date: str = ""
    bullets: list[str] = Field(default_factory=list)


class Activity(BaseModel):
    title: str
    bullets: list[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    full_name: str
    email: str
    phone: str
    phone_country_code: str = "+1"
    location: str = ""
    linkedin: str = ""
    github: str = ""
    headline: str = ""
    summary: str = ""
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    skill_groups: list[SkillGroup] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    activities: list[Activity] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Valid email required")
        return v.strip()

    def effective_skill_groups(self) -> list[SkillGroup]:
        if self.skill_groups:
            return self.skill_groups
        if self.skills:
            return [SkillGroup(label="Skills", skills=list(self.skills))]
        return []

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
        ]
        if self.education:
            lines.append("EDUCATION")
            for edu in self.education:
                lines.append(f"{edu.degree} - {edu.institution} ({edu.graduation_date})")
            lines.append("")
        if self.skills or self.skill_groups:
            lines.append("SKILLS")
            for group in self.effective_skill_groups():
                lines.append(f"{group.label}: {', '.join(group.skills)}")
            lines.append("")
        lines.append("EXPERIENCE")
        for exp in self.experience:
            lines.append(f"{exp.title} | {exp.company}")
            lines.append(f"{exp.start_date} - {exp.end_date}")
            lines.extend(f"- {b}" for b in exp.bullets)
            lines.append("")
        if self.projects:
            lines.append("PROJECTS")
            for proj in self.projects:
                lines.append(proj.name)
                lines.extend(f"- {b}" for b in proj.bullets)
            lines.append("")
        if self.activities:
            lines.append("ACTIVITIES")
            for act in self.activities:
                lines.append(act.title)
                lines.extend(f"- {b}" for b in act.bullets)
            lines.append("")
        if self.certifications:
            lines.append("CERTIFICATIONS")
            for cert in self.certifications:
                lines.append(f"{cert.name} ({cert.issuer}) {cert.date}")
        return "\n".join(lines)


class ResumeGenerateRequest(BaseModel):
    profile_id: int
    job_description: str
    provider: str | None = None
    model: str | None = None
    template_id: str = "professional"
