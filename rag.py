# rag.py

import json
import re
from pdf_utils import get_relevant_context
from ai import generate_with_gemini, generate_with_ollama


RAG_KEYS = [
    "answer",
    "definitions",
    "sections",
    "learning",
    "search_suggestions",
    "sources",
]


def empty_rag_result(message):
    return {key: message for key in RAG_KEYS}


def clean_json_text(content):
    content = content.strip()

    if content.startswith("```"):
        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        content = re.sub(
            r"\s*```$",
            "",
            content,
        )

    start = content.find("{")
    end = content.rfind("}")

    if start != -1 and end != -1:
        content = content[start : end + 1]

    return content.strip()


def parse_rag_response(content):
    try:
        parsed = json.loads(clean_json_text(content))

        return {key: str(parsed.get(key, "No content returned.")) for key in RAG_KEYS}

    except Exception:
        return {
            "answer": content,
            "definitions": "",
            "sections": "",
            "learning": "",
            "search_suggestions": "",
            "sources": "",
        }


def build_rag_prompt(
    context,
    question,
    language,
):
    lang_map = {
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu",
    }

    language_name = lang_map.get(
        language,
        "English",
    )

    return f"""
You are LearnLite-RAG.

Answer ONLY from the supplied document context.

Respond strictly in {language_name}.

Document Context:

{context}

Question:

{question}

Return ONLY valid JSON.

{{
  "answer":"Short answer summary",
  "definitions":"Key terms and concepts",
  "sections":"Most relevant section names from the document",
  "learning":"Topics the learner should study next",
  "search_suggestions":"Two useful searches",
  "sources":"Evidence from the supplied document"
}}
""".strip()


def get_document_answer(
    markdown_text,
    question,
    target_lang,
    provider,
    api_key="",
    gemini_model="gemini-2.5-flash",
    ollama_model="",
):
    try:
        context = get_relevant_context(
            markdown_text,
            question,
        )


        prompt = build_rag_prompt(
            context=context,
            question=question,
            language=target_lang,
        )

        provider = provider.lower()

        if provider == "ollama":
            result = generate_with_ollama(
                prompt,
                ollama_model,
            )

        else:
            result = generate_with_gemini(
                prompt,
                api_key,
                gemini_model,
            )

        if "answer" in result:
            return result

        return parse_rag_response(
            result.get(
                "eli15",
                str(result),
            )
        )

    except Exception as e:
        return empty_rag_result(f"RAG Error: {e}")
