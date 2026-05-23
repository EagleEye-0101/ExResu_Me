from resume_engine.ai.resume_normalize import normalize_ai_resume
from resume_engine.schemas.profile import ProfileResponse


def _profile() -> ProfileResponse:
    return ProfileResponse(
        id=1,
        full_name="Jane Doe",
        email="jane@example.com",
        phone="5551234567",
        phone_country_code="+1",
        location="NYC",
        linkedin="",
        target_role="Engineer",
        years_experience=3,
        headline="Software Engineer",
        summary_notes="Built web apps.",
        experience=[
            {
                "company": "Acme",
                "title": "Dev",
                "start_date": "01/2020",
                "end_date": "Present",
                "bullets": ["Shipped features"],
            }
        ],
        education=[],
        skills=["Python", "React", "SQL"],
    )


def test_header_nested_contact():
    raw = {
        "header": {
            "full_name": "Alex Kim",
            "email": "alex@test.com",
            "phone": "5559998888",
            "headline": "Engineer",
        },
        "summary": "Ready to work.",
        "experience": [
            {
                "company": "Co",
                "title": "Dev",
                "start_date": "01/2022",
                "bullets": ["Built APIs"],
            }
        ],
        "skills": ["Go"],
        "certifications": [],
    }
    from resume_engine.schemas.resume import ResumeData

    from resume_engine.ai.resume_normalize import parse_ai_resume

    profile = _profile()
    resume = parse_ai_resume(raw, profile)
    # Wizard profile contact always wins over AI nesting
    assert resume.full_name == profile.full_name
    assert resume.email == profile.email
    assert resume.phone == profile.phone
    assert len(resume.experience) >= 1


def test_contact_info_and_skills_object():
    raw = {
        "contact_info": {
            "name": "Sam Lee",
            "email": "sam@work.com",
            "phone": "5550001111",
        },
        "summary": "Builder.",
        "skills": {
            "technical_skills": ["Python", "SQL"],
            "soft_skills": ["Leadership"],
        },
        "experience": [],
    }
    out = normalize_ai_resume(raw, _profile())
    assert out["full_name"] == "Sam Lee"
    assert out["email"] == "sam@work.com"
    assert set(out["skills"]) >= {"Python", "SQL", "Leadership"}


def test_wrapped_resume_key_with_header():
    raw = {
        "resume": {
            "header": {
                "full_name": "Wrapped Name",
                "email": "wrap@test.com",
                "phone": "5551112222",
            },
            "summary": "Wrapped summary.",
            "experience": [
                {
                    "company": "Co",
                    "title": "Dev",
                    "start_date": "03/2021",
                    "bullets": ["Delivered"],
                }
            ],
            "skills": ["Rust"],
        }
    }
    from resume_engine.ai.resume_normalize import parse_ai_resume

    profile = _profile()
    resume = parse_ai_resume(raw, profile)
    assert resume.full_name == profile.full_name
    assert resume.summary == "Wrapped summary."
    assert len(resume.experience) == 1


def test_nested_personal_information_and_list_summary():
    raw = {
        "personal_information": {
            "name": "AI Name",
            "email": "ai@example.com",
            "phone": "999",
        },
        "summary": ["Line one.", "Line two."],
        "work_experience": [
            {
                "company": "Co",
                "title": "Role",
                "start_date": "06/2021",
                "responsibilities": ["Did work"],
            }
        ],
        "skills": "Python, Go",
    }
    out = normalize_ai_resume(raw, _profile())
    assert out["full_name"] == "AI Name"
    assert out["email"] == "ai@example.com"
    assert out["summary"] == "Line one.\nLine two."
    assert len(out["experience"]) == 1
    assert out["experience"][0]["bullets"] == ["Did work"]
    assert out["skills"] == ["Python", "Go"]
