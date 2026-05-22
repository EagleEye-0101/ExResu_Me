import re

from resume_engine.ats.keywords import extract_jd_keywords, match_keywords
from resume_engine.schemas.ats import ATSReport, CategoryScore, FixSuggestion
from resume_engine.schemas.resume import ResumeData

ACTION_VERBS = {
    "achieved", "built", "created", "delivered", "designed", "developed", "drove",
    "enhanced", "established", "executed", "generated", "implemented", "improved",
    "increased", "launched", "led", "managed", "optimized", "orchestrated", "owned",
    "performed", "pioneered", "produced", "reduced", "resolved", "scaled", "spearheaded",
    "streamlined", "transformed", "utilized", "accelerated", "analyzed", "automated",
    "collaborated", "coordinated", "decreased", "directed", "engineered", "facilitated",
    "grew", "mentored", "migrated", "modernized", "negotiated", "planned", "secured",
    "standardized", "supervised", "trained", "validated",
}

FIRST_PERSON = re.compile(r"\b(i|my|me|we|our)\b", re.I)
DATE_PATTERN = re.compile(r"^\d{1,2}/\d{4}$|^\d{4}$|^present$", re.I)
QUANT_PATTERN = re.compile(r"\d+%|\$\d+|\d+\+|\d+k|\d+\s*(users|clients|projects|team)")


def _score_keyword_coverage(
    resume: ResumeData, job_description: str
) -> tuple[float, list[str], list[str], list[str]]:
    keywords = extract_jd_keywords(job_description)
    if not keywords:
        return 50.0, [], [], ["No job description provided — keyword score capped"]

    text = resume.to_text()
    matched, missing = match_keywords(text, keywords)
    if not keywords:
        return 0.0, matched, missing, []

    coverage = len(matched) / len(keywords)
    score = min(100.0, coverage * 100)
    details = [
        f"Matched {len(matched)}/{len(keywords)} JD keywords ({coverage:.0%})",
    ]
    if missing[:5]:
        details.append(f"Missing: {', '.join(missing[:5])}" + ("..." if len(missing) > 5 else ""))
    return score, matched, missing, details


def _score_structure(resume: ResumeData) -> tuple[float, list[str], list[FixSuggestion]]:
    fixes: list[FixSuggestion] = []
    score = 100.0
    details: list[str] = []

    if not resume.summary or len(resume.summary.strip()) < 40:
        score -= 25
        fixes.append(
            FixSuggestion(
                category="structure",
                severity="warning",
                message="Summary is missing or too short",
                action="Add a 2-3 line professional summary",
            )
        )
    else:
        details.append("Summary present")

    if not resume.experience:
        score -= 40
        fixes.append(
            FixSuggestion(
                category="structure",
                severity="error",
                message="No work experience entries",
                action="Add at least one experience entry with dates",
            )
        )
    else:
        details.append(f"{len(resume.experience)} experience entries")
        for i, exp in enumerate(resume.experience):
            if not exp.company or not exp.title:
                score -= 15
                fixes.append(
                    FixSuggestion(
                        category="structure",
                        severity="error",
                        message=f"Experience #{i+1} missing company or title",
                        action="Fill company and job title",
                    )
                )
            if not DATE_PATTERN.match(exp.start_date.strip()):
                score -= 10
                fixes.append(
                    FixSuggestion(
                        category="structure",
                        severity="warning",
                        message=f"Experience #{i+1} start date should be MM/YYYY",
                        action=f"Fix start date: {exp.start_date}",
                    )
                )

    if not resume.education:
        score -= 15
        fixes.append(
            FixSuggestion(
                category="structure",
                severity="warning",
                message="No education section",
                action="Add at least one education entry",
            )
        )
    else:
        details.append(f"{len(resume.education)} education entries")

    if not resume.skills or len(resume.skills) < 5:
        score -= 20
        fixes.append(
            FixSuggestion(
                category="structure",
                severity="warning",
                message="Skills section has fewer than 5 items",
                action="Add more relevant skills from the job description",
            )
        )
    else:
        details.append(f"{len(resume.skills)} skills listed")

    required_sections = {
        "summary": bool(resume.summary),
        "experience": bool(resume.experience),
        "education": bool(resume.education),
        "skills": bool(resume.skills),
    }
    present = sum(required_sections.values())
    details.append(f"{present}/4 required sections complete")

    return max(0.0, score), details, fixes


def _score_parseability(resume: ResumeData) -> tuple[float, list[str], list[FixSuggestion]]:
    fixes: list[FixSuggestion] = []
    score = 100.0
    details: list[str] = []

    if not resume.email:
        score -= 30
        fixes.append(
            FixSuggestion(
                category="format",
                severity="error",
                message="Missing email",
                action="Add a professional email address",
            )
        )
    if not resume.phone:
        score -= 20
        fixes.append(
            FixSuggestion(
                category="format",
                severity="error",
                message="Missing phone number",
                action="Add a phone number with area code",
            )
        )

    # Check for ATS-unfriendly patterns in text
    text = resume.to_text()
    if re.search(r"[│┃|]{2,}", text):
        score -= 20
        fixes.append(
            FixSuggestion(
                category="format",
                severity="warning",
                message="Multi-column separators detected",
                action="Use single-column layout only",
            )
        )

    if re.search(r"[^\x00-\x7F]", text):
        details.append("Non-ASCII characters present (may affect some ATS)")

    if resume.linkedin and "linkedin.com" not in resume.linkedin.lower():
        score -= 5
        details.append("LinkedIn URL format may be non-standard")

    details.append("Single-column text format")
    details.append("Standard section headers used")
    return max(0.0, score), details, fixes


def _score_content_quality(resume: ResumeData, job_description: str) -> tuple[float, list[str], list[FixSuggestion]]:
    fixes: list[FixSuggestion] = []
    score = 100.0
    details: list[str] = []

    all_bullets: list[str] = []
    for exp in resume.experience:
        all_bullets.extend(exp.bullets)

    if not all_bullets:
        return 30.0, ["No experience bullets"], fixes

    verb_count = 0
    quant_count = 0
    long_bullets = 0
    first_person_bullets = 0
    keyword_counts: dict[str, int] = {}

    for bullet in all_bullets:
        words = bullet.lower().split()
        if words and words[0] in ACTION_VERBS:
            verb_count += 1
        if QUANT_PATTERN.search(bullet):
            quant_count += 1
        if len(bullet) > 200:
            long_bullets += 1
        if FIRST_PERSON.search(bullet):
            first_person_bullets += 1
        for w in words:
            if len(w) > 3:
                keyword_counts[w] = keyword_counts.get(w, 0) + 1

    total = len(all_bullets)
    verb_ratio = verb_count / total
    quant_ratio = quant_count / total

    if verb_ratio < 0.5:
        score -= 20
        fixes.append(
            FixSuggestion(
                category="content",
                severity="warning",
                message=f"Only {verb_count}/{total} bullets start with action verbs",
                action="Start bullets with verbs like Led, Built, Improved",
            )
        )
    else:
        details.append(f"{verb_count}/{total} bullets use action verbs")

    if quant_ratio < 0.3:
        score -= 15
        fixes.append(
            FixSuggestion(
                category="content",
                severity="info",
                message="Few quantified achievements",
                action="Add metrics: %, $, team size, users impacted",
            )
        )
    else:
        details.append(f"{quant_count}/{total} bullets include metrics")

    if first_person_bullets > 0:
        score -= 10
        fixes.append(
            FixSuggestion(
                category="content",
                severity="warning",
                message="First-person language in bullets",
                action="Remove I/my/we — use implied first person",
            )
        )

    if long_bullets > 0:
        score -= 5
        details.append(f"{long_bullets} bullets exceed 200 characters")

    # Keyword stuffing penalty
    stuffed = [w for w, c in keyword_counts.items() if c > 8]
    if stuffed:
        score -= 15
        fixes.append(
            FixSuggestion(
                category="content",
                severity="warning",
                message="Possible keyword stuffing detected",
                action="Reduce repetition of: " + ", ".join(stuffed[:3]),
            )
        )

    # Headline alignment with JD
    if job_description and resume.headline:
        jd_lower = job_description.lower()
        headline_words = set(resume.headline.lower().split())
        role_terms = [w for w in headline_words if len(w) > 3 and w in jd_lower]
        if role_terms:
            details.append("Headline aligns with job description")
        else:
            score -= 10
            fixes.append(
                FixSuggestion(
                    category="content",
                    severity="info",
                    message="Headline may not match job title",
                    action="Align headline with the role in the job posting",
                )
            )

    if resume.summary and len(resume.summary) > 600:
        score -= 10
        fixes.append(
            FixSuggestion(
                category="content",
                severity="info",
                message="Summary is too long",
                action="Shorten summary to 2-3 lines",
            )
        )

    return max(0.0, score), details, fixes


def score_resume(resume: ResumeData, job_description: str = "") -> ATSReport:
    """Compute weighted ATS composite score."""
    weights = {
        "keyword_coverage": 0.35,
        "structure": 0.20,
        "parseability": 0.25,
        "content_quality": 0.20,
    }

    kw_score, matched, missing, kw_details = _score_keyword_coverage(resume, job_description)
    struct_score, struct_details, struct_fixes = _score_structure(resume)
    parse_score, parse_details, parse_fixes = _score_parseability(resume)
    content_score, content_details, content_fixes = _score_content_quality(resume, job_description)

    if not job_description or not job_description.strip():
        kw_score = min(kw_score, 50.0)

    categories = [
        CategoryScore(
            name="JD Keyword Coverage",
            score=round(kw_score, 1),
            weight=weights["keyword_coverage"],
            weighted_score=round(kw_score * weights["keyword_coverage"], 1),
            details=kw_details,
        ),
        CategoryScore(
            name="Section Structure",
            score=round(struct_score, 1),
            weight=weights["structure"],
            weighted_score=round(struct_score * weights["structure"], 1),
            details=struct_details,
        ),
        CategoryScore(
            name="Parseability / Format",
            score=round(parse_score, 1),
            weight=weights["parseability"],
            weighted_score=round(parse_score * weights["parseability"], 1),
            details=parse_details,
        ),
        CategoryScore(
            name="Content Quality",
            score=round(content_score, 1),
            weight=weights["content_quality"],
            weighted_score=round(content_score * weights["content_quality"], 1),
            details=content_details,
        ),
    ]

    composite = sum(c.weighted_score for c in categories)
    all_fixes = struct_fixes + parse_fixes + content_fixes

    if not job_description or not job_description.strip():
        all_fixes.insert(
            0,
            FixSuggestion(
                category="keyword_coverage",
                severity="warning",
                message="No job description — score capped at 50% for keywords",
                action="Paste the target job description for accurate scoring",
            ),
        )

    if missing:
        all_fixes.append(
            FixSuggestion(
                category="keyword_coverage",
                severity="info",
                message=f"Add missing keywords naturally: {', '.join(missing[:8])}",
                action="Use Re-optimize or edit skills/experience bullets",
            )
        )

    export_blocked = any(f.severity == "error" for f in all_fixes)
    export_warnings = [f.message for f in all_fixes if f.severity in ("error", "warning")]

    return ATSReport(
        composite_score=round(composite, 1),
        categories=categories,
        fixes=all_fixes,
        matched_keywords=matched,
        missing_keywords=missing,
        export_blocked=export_blocked,
        export_warnings=export_warnings[:10],
    )
