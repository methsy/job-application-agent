from app.schemas.job_requirements import JobRequirementsExtracted
from app.services.ollama_service import (
    generate_with_ollama,
    parse_ollama_json_response,
)


def extract_job_requirements_from_listing(
    title: str,
    company: str,
    location: str,
    raw_description: str,
) -> JobRequirementsExtracted:
    prompt = build_job_requirement_extraction_prompt(
        title=title,
        company=company,
        location=location,
        raw_description=raw_description,
    )

    response_text = generate_with_ollama(prompt)
    response_json = parse_ollama_json_response(response_text)

    extracted = JobRequirementsExtracted.model_validate(response_json)

    return clean_extracted_job_requirements(extracted)


def build_job_requirement_extraction_prompt(
    title: str,
    company: str,
    location: str,
    raw_description: str,
) -> str:
    return f"""
You are a job advertisement analysis agent.

Your task is to extract structured job requirements from the supplied job listing.

Rules:
- Return valid JSON only.
- Do not include markdown.
- Do not invent requirements.
- Only include information supported by the job listing.
- If something is not available, use an empty string or empty list.
- Keep skill names concise.
- Separate required skills from preferred or nice-to-have skills.
- If the wording says "required", "must have", "essential", "requires", or "requiring", place those skills in required_skills.
- If the wording says "preferred", "nice to have", "desirable", "bonus", or "experience with X is desirable", place those skills in preferred_skills.
- Also place desirable, preferred, bonus, or nice-to-have items in nice_to_have.
- Extract responsibilities from action phrases such as "design", "build", "develop", "maintain", "support", "test", "deploy", "troubleshoot", "monitor", "integrate", "document", and "collaborate".
- Extract domain from the job title and responsibilities. Examples: "backend software engineering", "data engineering", "integration development", "frontend development", "DevOps/platform engineering".
- Extract employment_type if the text says full-time, part-time, contract, permanent, temporary, or casual.
- Extract work_arrangement if the text says remote, hybrid, onsite, on-site, office-based, or flexible.
- Put strict eligibility constraints in hard_requirements, such as citizenship, clearance, work rights, mandatory certifications, or required years of experience.
- Extract keywords_for_ats by combining important required skills, preferred skills, tools, technologies, methodologies, responsibilities, and domain terms.
- You may infer seniority from the job title if the title clearly states it, for example Senior, Lead, Principal, Junior, Graduate, or Mid-level.
- You may infer location from the supplied location field.
- Do not leave keywords_for_ats empty if the job listing contains skills, tools, responsibilities, or domain terms.
- Do not leave responsibilities empty if the job listing contains action-oriented work the candidate is expected to perform.
- Treat phrases under "You will bring", "About You", "Essential skills", "Required skills", "You must have", or "The successful candidate will have" as required_skills unless they are explicitly marked desirable, preferred, bonus, nice-to-have, or highly regarded.
- If a requirement says "at least one of A, B, C", keep it as one grouped requirement, for example "at least one of NET/C#, Java, Python, JavaScript, or TypeScript".
- Do not put "desirable but not essential" items in hard_requirements.
- Do not put "highly regarded", "preferred", "desirable", or "nice to have" items in hard_requirements.
- Only extract application_deadline if the job ad explicitly says applications close, closing date, deadline, or apply by. Do not use page dates, print dates, or timestamps as application deadlines.
- Include all major required skills, preferred skills, responsibilities, tools, technologies, methodologies, and seniority terms in keywords_for_ats.
- Put only strict eligibility constraints in hard_requirements, such as mandatory citizenship, mandatory clearance, mandatory work rights, mandatory certification, or non-negotiable years of experience. Do not include desirable or preferred items.
- If the job ad says "at least one of A, B, C", "one of A, B, C", or "A, B, C or D", keep that as a single grouped requirement instead of splitting it into separate required skills. Example: "at least one of NET/C#, Java, Python, JavaScript, or TypeScript".

Return JSON with exactly this structure:
{{
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "seniority": "",
  "domain": "",
  "employment_type": "",
  "work_arrangement": "",
  "location": "",
  "salary_range": "",
  "application_deadline": "",
  "hard_requirements": [],
  "nice_to_have": [],
  "keywords_for_ats": []
}}

Job title:
{title}

Company:
{company}

Location:
{location}

Job advertisement:
\"\"\"
{raw_description}
\"\"\"
"""


def clean_extracted_job_requirements(
    extracted: JobRequirementsExtracted,
) -> JobRequirementsExtracted:
    extracted.hard_requirements = clean_hard_requirements(
        hard_requirements=extracted.hard_requirements,
        nice_to_have=extracted.nice_to_have,
    )

    if not extracted.nice_to_have and extracted.preferred_skills:
        extracted.nice_to_have = extracted.preferred_skills

    if not extracted.keywords_for_ats:
        extracted.keywords_for_ats = build_keywords_for_ats(extracted)

    extracted.required_skills = deduplicate_preserving_order(extracted.required_skills)
    extracted.required_skills = group_alternative_programming_languages(
    extracted.required_skills
)
    extracted.preferred_skills = deduplicate_preserving_order(extracted.preferred_skills)
    extracted.responsibilities = deduplicate_preserving_order(extracted.responsibilities)
    extracted.hard_requirements = deduplicate_preserving_order(extracted.hard_requirements)
    extracted.nice_to_have = deduplicate_preserving_order(extracted.nice_to_have)
    extracted.keywords_for_ats = deduplicate_preserving_order(extracted.keywords_for_ats)

    return extracted


def clean_hard_requirements(
    hard_requirements: list[str],
    nice_to_have: list[str],
) -> list[str]:
    cleaned = []

    non_hard_phrases = [
        "desirable",
        "not essential",
        "preferred",
        "highly regarded",
        "nice to have",
        "bonus",
    ]

    for requirement in hard_requirements:
        normalized = requirement.lower()

        if any(phrase in normalized for phrase in non_hard_phrases):
            nice_to_have.append(requirement)
            continue

        if "degree" in normalized or "bachelor" in normalized:
            nice_to_have.append(requirement)
            continue

        cleaned.append(requirement)

    return cleaned


def build_keywords_for_ats(
    extracted: JobRequirementsExtracted,
) -> list[str]:
    keywords = []

    keywords.extend(extracted.required_skills)
    keywords.extend(extracted.preferred_skills)
    keywords.extend(extracted.responsibilities)
    keywords.extend(extracted.nice_to_have)

    if extracted.seniority:
        keywords.append(extracted.seniority)

    if extracted.domain:
        keywords.append(extracted.domain)

    if extracted.employment_type:
        keywords.append(extracted.employment_type)

    if extracted.work_arrangement:
        keywords.append(extracted.work_arrangement)

    if extracted.location:
        keywords.append(extracted.location)

    return deduplicate_preserving_order(keywords)


def deduplicate_preserving_order(values: list[str]) -> list[str]:
    seen = set()
    result = []

    for value in values:
        cleaned = value.strip()
        normalized = cleaned.lower()

        if not cleaned or normalized in seen:
            continue

        seen.add(normalized)
        result.append(cleaned)

    return result


def group_alternative_programming_languages(required_skills: list[str]) -> list[str]:
    language_group = [
        "NET/C#",
        ".NET/C#",
        "C#",
        "Java",
        "Python",
        "JavaScript",
        "TypeScript",
    ]

    normalized_required = {
        skill.strip().lower(): skill.strip()
        for skill in required_skills
    }

    found_languages = []

    for language in language_group:
        normalized_language = language.lower()

        if normalized_language in normalized_required:
            found_languages.append(normalized_required[normalized_language])

    if len(found_languages) < 2:
        return required_skills

    grouped_requirement = "at least one of " + ", ".join(found_languages)

    cleaned_required_skills = [
        skill
        for skill in required_skills
        if skill.strip() not in found_languages
    ]

    cleaned_required_skills.insert(0, grouped_requirement)

    return deduplicate_preserving_order(cleaned_required_skills)
