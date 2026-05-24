from resume_engine.ats.scorer import score_resume
from resume_engine.schemas.resume import Certification, Education, Experience, ResumeData


def sample_resume() -> ResumeData:
    return ResumeData(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="5550100",
        phone_country_code="+1",
        location="New York, NY",
        headline="Senior Software Engineer",
        summary="Experienced engineer with 8 years building scalable web applications and leading cross-functional teams.",
        experience=[
            Experience(
                company="Tech Corp",
                title="Senior Software Engineer",
                start_date="01/2020",
                end_date="Present",
                bullets=[
                    "Led team of 5 engineers delivering microservices platform serving 2M users",
                    "Reduced API latency by 40% through optimization and caching",
                    "Implemented CI/CD pipelines using Docker and Kubernetes",
                ],
            )
        ],
        education=[
            Education(
                institution="State University",
                degree="B.S. Computer Science",
                graduation_date="05/2016",
            )
        ],
        skills=["Python", "React", "AWS", "Docker", "Kubernetes", "SQL", "FastAPI"],
        certifications=[Certification(name="AWS Solutions Architect", issuer="Amazon", date="2022")],
    )


def test_score_with_jd():
    jd = """
    Senior Software Engineer
    Requirements:
    - 5+ years Python experience
    - React and TypeScript
    - AWS and Docker
    - Experience with microservices
    - Leadership skills
    """
    report = score_resume(sample_resume(), jd)
    assert report.composite_score > 50
    assert len(report.categories) == 4
    assert report.categories[0].name == "JD Keyword Coverage"


def test_score_without_jd():
    report = score_resume(sample_resume(), "")
    assert report.composite_score > 0
    assert any("job description" in f.message.lower() for f in report.fixes)
