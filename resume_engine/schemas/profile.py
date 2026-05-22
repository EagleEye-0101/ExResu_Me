from pydantic import BaseModel, Field


class ExperienceInput(BaseModel):
    company: str
    title: str
    location: str = ""
    start_date: str
    end_date: str = "Present"
    bullets: list[str] = Field(default_factory=list)


class EducationInput(BaseModel):
    institution: str
    degree: str
    field: str = ""
    graduation_date: str = ""
    gpa: str = ""


class ProfileCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str = ""
    linkedin: str = ""
    target_role: str = ""
    years_experience: int = 0
    headline: str = ""
    summary_notes: str = ""
    experience: list[ExperienceInput] = Field(default_factory=list)
    education: list[EducationInput] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[dict] = Field(default_factory=list)


class ProfileUpdate(ProfileCreate):
    pass


class ProfileResponse(ProfileCreate):
    id: int

    model_config = {"from_attributes": True}
