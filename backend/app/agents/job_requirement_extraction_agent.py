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

    return JobRequirementsExtracted.model_validate(response_json)



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
