from app.agents.job_requirement_extraction_agent import (
    build_job_requirement_extraction_prompt,
)


def test_build_job_requirement_extraction_prompt_contains_job_listing_context():
    title = "Senior Software Engineer"
    company = "Example Company"
    location = "Melbourne VIC"
    raw_description = (
        "We are looking for a Senior Software Engineer requiring Java, "
        "Python, SQL, REST APIs, AWS and production support experience."
    )

    prompt = build_job_requirement_extraction_prompt(
        title=title,
        company=company,
        location=location,
        raw_description=raw_description,
    )

    assert "job advertisement analysis agent" in prompt
    assert "Return valid JSON only" in prompt
    assert title in prompt
    assert company in prompt
    assert location in prompt
    assert raw_description in prompt
