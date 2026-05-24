import re
from collections import Counter

# Common tech/business skills for boosting extraction
SKILL_DICTIONARY = {
    "python", "java", "javascript", "typescript", "react", "node", "nodejs", "sql",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "agile", "scrum", "ci/cd",
    "machine learning", "data analysis", "excel", "power bi", "tableau", "leadership",
    "communication", "project management", "rest api", "fastapi", "django", "flask",
    "postgresql", "mongodb", "redis", "linux", "html", "css", "next.js", "nextjs",
    "tensorflow", "pytorch", "nlp", "etl", "devops", "microservices", "api",
    "stakeholder", "cross-functional", "saas", "b2b", "kpi", "roi", "seo", "crm",
    "salesforce", "jira", "confluence", "figma", "ui/ux", "customer success",
    "business analysis", "requirements gathering", "testing", "qa", "selenium",
    "c++", "c#", ".net", "spring", "hibernate", "graphql", "kafka", "spark",
    "hadoop", "snowflake", "databricks", "airflow", "dbt", "terraform", "ansible",
    "pmp", "itil", "six sigma", "lean", "budgeting", "forecasting", "negotiation",
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "as", "is", "was", "are", "were", "been", "be", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might", "must",
    "shall", "can", "need", "our", "your", "their", "this", "that", "these", "those",
    "we", "you", "they", "it", "he", "she", "who", "which", "what", "when", "where",
    "why", "how", "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "just", "about", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "again", "further", "then", "once", "here", "there",
    "any", "work", "working", "role", "position", "job", "team", "company", "years",
    "year", "experience", "required", "preferred", "including", "ability", "skills",
    "responsibilities", "qualifications", "description", "applicant", "candidate",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _extract_from_dictionary(text: str) -> list[str]:
    normalized = _normalize(text)
    found = []
    for skill in SKILL_DICTIONARY:
        if skill in normalized:
            found.append(skill)
    return found


def _extract_rake(text: str) -> list[str]:
    try:
        from rake_nltk import Rake

        r = Rake(min_length=2, max_length=4)
        r.extract_keywords_from_text(text)
        phrases = r.get_ranked_phrases()[:30]
        return [p.lower().strip() for p in phrases if len(p) > 2]
    except Exception:
        return []


def _extract_capitalized_terms(text: str) -> list[str]:
    """Extract likely acronyms and proper nouns from JD."""
    tokens = re.findall(r"\b[A-Z][A-Za-z0-9+#./-]{1,30}\b", text)
    return [t.lower() for t in tokens if len(t) > 1]


def _extract_requirements_lines(text: str) -> list[str]:
    keywords = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if re.match(r"^[-•*]\s+", line) or re.search(
            r"\b(required|must|preferred|experience with)\b", line, re.I
        ):
            words = re.findall(r"\b[a-zA-Z+#.]{3,25}\b", line.lower())
            keywords.extend(w for w in words if w not in STOPWORDS)
    return keywords


def extract_jd_keywords(job_description: str, max_keywords: int = 40) -> list[str]:
    """Extract ranked keywords from a job description."""
    if not job_description or not job_description.strip():
        return []

    text = job_description.strip()
    candidates: list[str] = []
    candidates.extend(_extract_from_dictionary(text))
    candidates.extend(_extract_rake(text))
    candidates.extend(_extract_capitalized_terms(text))
    candidates.extend(_extract_requirements_lines(text))

    # Bigrams from lines with "experience"
    for match in re.finditer(
        r"(?:experience with|proficient in|knowledge of)\s+([^.;\n]+)",
        text,
        re.I,
    ):
        chunk = match.group(1).lower()
        parts = re.split(r"[,/&]| and ", chunk)
        candidates.extend(p.strip() for p in parts if 2 < len(p.strip()) < 40)

    # Frequency filter
    cleaned = []
    for c in candidates:
        c = _normalize(c)
        if len(c) < 2 or c in STOPWORDS:
            continue
        cleaned.append(c)

    counts = Counter(cleaned)
    ranked = [kw for kw, _ in counts.most_common(max_keywords)]
    return ranked[:max_keywords]


def match_keywords(resume_text: str, keywords: list[str]) -> tuple[list[str], list[str]]:
    """Return (matched, missing) keyword lists."""
    normalized = _normalize(resume_text)
    matched = []
    missing = []
    for kw in keywords:
        if kw in normalized or kw.replace(" ", "") in normalized.replace(" ", ""):
            matched.append(kw)
        else:
            missing.append(kw)
    return matched, missing
