import json

import requests

from app.core.config import settings


class OllamaServiceError(RuntimeError):
    pass


def generate_with_ollama(prompt: str) -> str:
    url = f"{settings.ollama_base_url}/api/generate"

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise OllamaServiceError(f"Ollama request failed: {exc}") from exc

    data = response.json()

    generated_text = data.get("response")

    if not generated_text:
        raise OllamaServiceError("Ollama returned an empty response.")

    return generated_text


def parse_ollama_json_response(response_text: str) -> dict:
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise OllamaServiceError("Ollama response was not valid JSON.") from exc
