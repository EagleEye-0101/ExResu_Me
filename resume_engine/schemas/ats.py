from pydantic import BaseModel, Field


class FixSuggestion(BaseModel):
    category: str
    severity: str  # error, warning, info
    message: str
    action: str = ""


class CategoryScore(BaseModel):
    name: str
    score: float
    weight: float
    weighted_score: float
    details: list[str] = Field(default_factory=list)


class ATSReport(BaseModel):
    composite_score: float
    categories: list[CategoryScore]
    fixes: list[FixSuggestion] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    export_blocked: bool = False
    export_warnings: list[str] = Field(default_factory=list)
