from app.agents.cv_profile_extraction_agent import build_cv_profile_extraction_prompt


def test_build_cv_profile_extraction_prompt_contains_cv_text():
    raw_text = "Senior Software Engineer with Java, Python, SQL and AWS."

    prompt = build_cv_profile_extraction_prompt(raw_text)

    assert "CV analysis agent" in prompt
    assert "Return valid JSON only" in prompt
    assert raw_text in prompt
