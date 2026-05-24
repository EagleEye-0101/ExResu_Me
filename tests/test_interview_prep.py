import pytest

from resume_engine.features.interview import _normalize_questions, generate_interview_questions
from resume_engine.schemas.resume import Experience, ResumeData


def test_normalize_questions_aliases():
    raw = [{"q": "Tell me about yourself", "hint": "Be brief"}]
    out = _normalize_questions(raw)
    assert len(out) == 1
    assert out[0]["question"] == "Tell me about yourself"
    assert "tip" in out[0]


@pytest.mark.asyncio
async def test_generate_interview_questions_mock(monkeypatch):
    class FakeAI:
        async def complete(self, messages, json_schema=None):
            return {
                "questions": [
                    {"question": f"Q{i}?", "tip": f"Tip {i}"} for i in range(10)
                ]
            }

    monkeypatch.setattr(
        "resume_engine.features.interview.get_provider",
        lambda *a, **k: FakeAI(),
    )
    resume = ResumeData(
        full_name="Test User",
        email="t@test.com",
        phone="1234567890",
        summary="Engineer",
        experience=[
            Experience(
                company="Co",
                title="Dev",
                start_date="01/2020",
                bullets=["Built apps"],
            )
        ],
    )
    qs = await generate_interview_questions(resume, "Python developer role", "ollama", {})
    assert len(qs) == 10


@pytest.mark.asyncio
async def test_generate_interview_empty_raises(monkeypatch):
    class FakeAI:
        async def complete(self, messages, json_schema=None):
            return {"questions": []}

    monkeypatch.setattr(
        "resume_engine.features.interview.get_provider",
        lambda *a, **k: FakeAI(),
    )
    resume = ResumeData(
        full_name="Test",
        email="t@test.com",
        phone="1234567890",
        summary="x",
        experience=[
            Experience(company="C", title="T", start_date="01/2020", bullets=["a"]),
        ],
    )
    with pytest.raises(ValueError, match="no interview questions"):
        await generate_interview_questions(resume, "job", "ollama", {})
