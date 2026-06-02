from app.schemas.candidate_profile import CandidateProfileExtracted
from app.services.ollama_service import (
    generate_with_ollama,
    parse_ollama_json_response,
)


def extract_candidate_profile_from_cv(raw_text: str) -> CandidateProfileExtracted:
    prompt = build_cv_profile_extraction_prompt(raw_text)

    response_text = generate_with_ollama(prompt)
    response_json = parse_ollama_json_response(response_text)

    return CandidateProfileExtracted.model_validate(response_json)


def build_cv_profile_extraction_prompt(raw_text: str) -> str:
    return f"""
You are a CV analysis agent.

Your task is to extract a structured candidate profile from the supplied CV text.

Rules:
- Return valid JSON only.
- Do not include markdown.
- Do not invent experience.
- Only include information supported by the CV text.
- If something is not available, use an empty string or empty list.
- Keep skill names concise.
- Separate core skills from secondary skills.
- Infer seniority only from role titles, years of experience, and responsibility level in the CV.

Return JSON with exactly this structure:
{{
  "target_roles": [],
  "core_skills": [],
  "secondary_skills": [],
  "seniority": "",
  "domains": [],
  "experience_summary": [
    {{
      "company": "",
      "role": "",
      "summary": ""
    }}
  ],
  "location_preferences": [],
  "work_arrangement_preferences": []
}}

CV text:
\"\"\"
{raw_text}
\"\"\"
"""
