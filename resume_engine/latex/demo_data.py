"""Rich demo resume used for LaTeX template gallery and editor."""

from resume_engine.schemas.resume import (
    Activity,
    Certification,
    Education,
    Experience,
    Project,
    ResumeData,
    SkillGroup,
)

DEMO_RESUME = ResumeData(
    full_name="Alexandra Chen",
    email="alexandra.chen@email.com",
    phone="4155550198",
    phone_country_code="+1",
    location="San Francisco, CA",
    linkedin="linkedin.com/in/alexandrachen",
    github="github.com/achen-dev",
    headline="Senior Software Engineer — Distributed Systems & Developer Experience",
    summary=(
        "Full-stack engineer with 7+ years building scalable web platforms and internal "
        "developer tools. Shipped features used by 2M+ users; led migrations cutting "
        "deploy time 40%. Passionate about observability, clean APIs, and mentoring."
    ),
    experience=[
        Experience(
            company="Nimbus Labs",
            title="Senior Software Engineer",
            location="San Francisco, CA",
            start_date="03/2022",
            end_date="Present",
            bullets=[
                "Architected event-driven billing pipeline processing 50K+ events/min with 99.95% uptime",
                "Reduced p95 API latency 35% via query optimization, caching, and connection pooling",
                "Led team of 4 on developer portal; cut onboarding time for new services from 2 weeks to 3 days",
                "Drove adoption of OpenTelemetry across 12 microservices; MTTR improved 28%",
            ],
        ),
        Experience(
            company="Streamline Inc.",
            title="Software Engineer II",
            location="Austin, TX",
            start_date="06/2019",
            end_date="02/2022",
            bullets=[
                "Built React/TypeScript dashboard serving 500K monthly active users",
                "Designed REST and GraphQL APIs in Python (FastAPI) with PostgreSQL and Redis",
                "Implemented CI/CD with GitHub Actions; deployment frequency increased 3x",
                "Mentored 2 interns; both received return offers",
            ],
        ),
    ],
    education=[
        Education(
            institution="University of California, Berkeley",
            degree="B.S. Computer Science",
            field="",
            graduation_date="05/2019",
            gpa="3.7",
        ),
        Education(
            institution="MIT Professional Education",
            degree="Certificate",
            field="Cloud Architecture",
            graduation_date="2021",
            gpa="",
        ),
    ],
    skills=["Python", "TypeScript", "Go", "PostgreSQL", "AWS", "Kubernetes"],
    skill_groups=[
        SkillGroup(label="Languages", skills=["Python", "TypeScript", "Go", "SQL"]),
        SkillGroup(label="Frameworks", skills=["FastAPI", "React", "Next.js", "Node.js"]),
        SkillGroup(label="Infrastructure", skills=["AWS", "Docker", "Kubernetes", "Terraform"]),
        SkillGroup(label="Practices", skills=["System design", "CI/CD", "Observability", "Agile"]),
    ],
    projects=[
        Project(
            name="OpenMetrics Kit",
            context="Open Source",
            start_date="2023",
            end_date="Present",
            bullets=[
                "Lightweight metrics library for Python services; 1.2K GitHub stars",
                "Integrations for Prometheus and Grafana dashboards",
            ],
        ),
        Project(
            name="ResumeFlow CLI",
            context="Side Project",
            start_date="2022",
            end_date="2023",
            bullets=[
                "CLI tool generating ATS-friendly resumes from YAML profiles",
                "Used by 200+ developers in beta program",
            ],
        ),
        Project(
            name="Hackathon Winner — DevCon 2021",
            context="Team Lead",
            start_date="2021",
            end_date="2021",
            bullets=[
                "Built real-time collaboration plugin for VS Code in 48 hours",
            ],
        ),
    ],
    activities=[
        Activity(
            title="Women Who Code — Workshop Lead",
            bullets=[
                "Led monthly workshops on API design and testing for 40+ attendees",
            ],
        ),
        Activity(
            title="Berkeley CS Mentorship Program",
            bullets=[
                "Mentored 3 undergraduates on internships and technical interviews",
            ],
        ),
    ],
    certifications=[
        Certification(name="AWS Solutions Architect Associate", issuer="Amazon", date="2023"),
        Certification(name="Kubernetes Administrator (CKA)", issuer="CNCF", date="2022"),
    ],
)
