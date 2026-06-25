# ai.py

import json
import logging
import os
import re
from typing import Any, Dict, List, Tuple

import requests

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"

SECTION_KEYS = [
    "points",
    "eli15",
    "terms",
    "prerequisites",
    "next_topics",
    "search_suggestions",
]

RAG_KEYS = [
    "answer",
    "definitions",
    "sections",
    "learning",
    "search_suggestions",
    "sources",
]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------


def build_prompt(text: str, target_lang: str) -> str:
    lang_map = {"en": "English", "hi": "Hindi", "te": "Telugu"}
    language_name = lang_map.get(target_lang, "English")

    return f"""You are LearnLite, a beginner-friendly educational assistant.
Explain the user's topic or paragraph strictly in {language_name}.

Return ONLY valid JSON. Do not use markdown code fences.
The JSON object must have exactly these keys:

{{
  "points": ["3 to 5 short main points"],
  "eli15": "A simple explanation for a 15 year old",
  "terms": {{"term": "definition"}},
  "prerequisites": ["concepts the learner should know first"],
  "next_topics": ["what the learner should learn next"],
  "search_suggestions": ["exactly two Google search suggestions"]
}}

If the input is random characters or meaningless, do not invent an explanation.
Instead, politely say the input is unclear and ask for a real topic or paragraph.

User content:
{text}""".strip()


# ---------------------------------------------------------------------------
# Empty / error sentinels
# ---------------------------------------------------------------------------


def empty_result(message: str) -> Dict[str, str]:
    return {key: message for key in SECTION_KEYS}


def empty_rag_result(message: str) -> Dict[str, str]:
    return {key: message for key in RAG_KEYS}


# ---------------------------------------------------------------------------
# JSON utilities
# ---------------------------------------------------------------------------


def clean_json_text(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
        content = re.sub(r"\s*```$", "", content)

    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        content = content[start : end + 1]
    return content.strip()


def format_value(value: Any) -> str:
    """Convert model JSON values into clean human-readable text.

    Gemini/Ollama may return lists or dictionaries even when the prompt asks for
    strings. Rendering raw Python lists looks ugly, so normalize them here.
    """
    if value is None:
        return "No content returned."

    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                if len(item) == 1:
                    key, val = next(iter(item.items()))
                    lines.append(f"• {key}: {format_value(val).replace(chr(10), ' ')}")
                else:
                    compact = "; ".join(
                        f"{k}: {format_value(v).replace(chr(10), ' ')}"
                        for k, v in item.items()
                    )
                    lines.append(f"• {compact}")
            else:
                lines.append(f"• {str(item).strip()}")
        return "\n".join(lines).strip()

    if isinstance(value, dict):
        lines = []
        for key, val in value.items():
            pretty_key = str(key).replace("_", " ").title()
            lines.append(f"• {pretty_key}: {format_value(val).replace(chr(10), ' ')}")
        return "\n".join(lines).strip()

    text = str(value).strip()
    text = re.sub(r"\s*;\s*", "\n• ", text)
    if text.startswith("• ") or "\n• " not in text:
        return text
    return "• " + text


# ---------------------------------------------------------------------------
# Response parsers
# ---------------------------------------------------------------------------


def parse_response(content: str) -> Dict[str, str]:
    """Parse a LearnLite (SECTION_KEYS) JSON response."""
    try:
        parsed = json.loads(clean_json_text(content))
        return {
            key: format_value(parsed.get(key, "No content returned."))
            for key in SECTION_KEYS
        }
    except Exception:
        return {
            "points": "The model returned text, but not valid JSON.",
            "eli15": content.strip() or "No response text returned.",
            "terms": "Try again, or use a different model/provider.",
            "prerequisites": "",
            "next_topics": "",
            "search_suggestions": "",
        }


def parse_rag_response(content: str) -> Dict[str, str]:
    """Parse a LearnLite-RAG (RAG_KEYS) JSON response."""
    try:
        parsed = json.loads(clean_json_text(content))
        return {
            key: format_value(parsed.get(key, "No content returned."))
            for key in RAG_KEYS
        }
    except Exception:
        return {
            "answer": content.strip() or "No response text returned.",
            "definitions": "Could not parse definitions.",
            "sections": "",
            "learning": "",
            "search_suggestions": "",
            "sources": "",
        }


# ---------------------------------------------------------------------------
# Low-level AI callers  (return raw text so callers choose the parser)
# ---------------------------------------------------------------------------


def _call_gemini_raw(prompt: str, api_key: str, model: str) -> str:
    """Call Gemini and return the raw text content, or raise on error."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta"
        f"/models/{model}:generateContent"
    )
    payload: Any = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }
    response = requests.post(url, params={"key": api_key}, json=payload, timeout=45)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_ollama_raw(prompt: str, model: str, host: str) -> str:
    """Call Ollama and return the raw text content, or raise on error."""
    payload: Any = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.2},
    }
    response = requests.post(
        f"{host.rstrip('/')}/api/generate", json=payload, timeout=90
    )
    response.raise_for_status()
    return response.json().get("response", "")


# ---------------------------------------------------------------------------
# Public high-level generators
# ---------------------------------------------------------------------------


def generate_with_gemini(
    prompt: str, api_key: str, model: str = DEFAULT_GEMINI_MODEL
) -> Dict[str, str]:
    """LearnLite (SECTION_KEYS) Gemini call."""
    api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    model = (model or DEFAULT_GEMINI_MODEL).strip()

    if not api_key:
        return empty_result(
            "Please paste a Gemini API key, or set GEMINI_API_KEY in your .env file."
        )

    try:
        raw = _call_gemini_raw(prompt, api_key, model)
        return parse_response(raw)
    except requests.HTTPError as exc:
        resp = exc.response
        status = resp.status_code if resp is not None else "unknown"
        body = resp.text if resp is not None else ""
        return empty_result(f"Gemini error {status}: {body}")
    except Exception as exc:
        return empty_result(f"Gemini connection error: {exc}")


def generate_with_ollama(
    prompt: str, model: str, host: str = DEFAULT_OLLAMA_HOST
) -> Dict[str, str]:
    """LearnLite (SECTION_KEYS) Ollama call."""
    if os.getenv("VERCEL"):
        return empty_result(
            "Ollama Local AI works when LearnLite is run locally with Ollama installed. "
            "On cloud deployments, localhost refers to the deployment server, so use Gemini BYOK here."
        )

    model = (model or "").strip()
    if not model:
        return empty_result(
            "No Ollama model selected. Start Ollama and pull a model first, "
            "for example: ollama pull llama3.2:1b"
        )

    try:
        raw = _call_ollama_raw(prompt, model, host)
        return parse_response(raw)
    except requests.HTTPError as exc:
        resp = exc.response
        status = resp.status_code if resp is not None else "unknown"
        body = resp.text if resp is not None else ""
        return empty_result(f"Ollama error {status}: {body}")
    except Exception as exc:
        return empty_result(f"Ollama connection error: {exc}")


def generate_rag_output(
    prompt: str,
    provider: str,
    api_key: str = "",
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    ollama_model: str = "",
) -> Dict[str, str]:
    """
    RAG-specific AI call.  Uses RAG_KEYS parser regardless of provider.
    Always returns a dict — never raises.
    """
    provider = (provider or "gemini").lower()

    try:
        if provider == "ollama":
            if os.getenv("VERCEL"):
                return empty_rag_result(
                    "Ollama Local AI works when LearnLite is run locally with Ollama installed. "
                    "On cloud deployments, use Gemini BYOK here."
                )
            model = (ollama_model or "").strip()
            if not model:
                return empty_rag_result(
                    "No Ollama model selected. Pull a model first, "
                    "for example: ollama pull llama3.2:1b"
                )
            raw = _call_ollama_raw(prompt, model, DEFAULT_OLLAMA_HOST)
        else:
            # gemini (default)
            resolved_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
            if not resolved_key:
                return empty_rag_result(
                    "Please paste a Gemini API key, or set GEMINI_API_KEY in your .env file."
                )
            resolved_model = (gemini_model or DEFAULT_GEMINI_MODEL).strip()
            raw = _call_gemini_raw(prompt, resolved_key, resolved_model)

        return parse_rag_response(raw)

    except requests.HTTPError as exc:
        resp = exc.response
        status = resp.status_code if resp is not None else "unknown"
        body = resp.text if resp is not None else ""
        logger.error("RAG AI HTTP error %s: %s", status, body)
        return empty_rag_result(f"AI provider error {status}: {body[:200]}")
    except Exception as exc:
        logger.exception("RAG AI generation error")
        return empty_rag_result(f"AI generation error: {exc}")


# ---------------------------------------------------------------------------
# Ollama discovery
# ---------------------------------------------------------------------------


def get_ollama_models(host: str = DEFAULT_OLLAMA_HOST) -> Tuple[List[str], str]:
    """Return installed Ollama model names and an optional status message."""
    try:
        response = requests.get(f"{host.rstrip('/')}/api/tags", timeout=3)
        if response.status_code != 200:
            return [], f"Ollama responded with status {response.status_code}."
        data = response.json()
        models = [
            item.get("name") for item in data.get("models", []) if item.get("name")
        ]
        return models, ""
    except Exception:
        return [], "Ollama is not running. Start Ollama to use local AI."


# ---------------------------------------------------------------------------
# Main entry point for LearnLite mode
# ---------------------------------------------------------------------------


def get_explanation(
    text: str,
    target_lang: str,
    provider: str,
    api_key: str = "",
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    ollama_model: str = "",
) -> Dict[str, str]:
    prompt = build_prompt(text, target_lang)
    provider = (provider or "gemini").lower()

    if provider == "ollama":
        return generate_with_ollama(prompt, ollama_model)
    return generate_with_gemini(prompt, api_key, gemini_model)
