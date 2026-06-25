# rag.py

import logging

from pdf_utils import get_relevant_context
from ai import generate_rag_output

logger = logging.getLogger(__name__)

RAG_KEYS = [
    "answer",
    "definitions",
    "sections",
    "learning",
    "search_suggestions",
    "sources",
]


def empty_rag_result(message: str) -> dict:
    return {key: message for key in RAG_KEYS}


def build_rag_prompt(context: str, question: str, language: str) -> str:
    lang_map = {
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu",
    }
    language_name = lang_map.get(language, "English")

    return f"""You are LearnLite-RAG.

Answer ONLY from the supplied document context.

Respond strictly in {language_name}.

Document Context:

{context}

Question:

{question}

Return ONLY valid JSON with exactly these keys:

{{
  "answer": "Short answer summary",
  "definitions": "Key terms and concepts",
  "sections": "Most relevant section names from the document",
  "learning": "Topics the learner should study next",
  "search_suggestions": "Two useful searches",
  "sources": "Evidence from the supplied document"
}}""".strip()


def get_document_answer(
    markdown_text: str,
    question: str,
    target_lang: str,
    provider: str,
    api_key: str = "",
    gemini_model: str = "gemini-2.5-flash",
    ollama_model: str = "",
) -> dict:
    if not markdown_text or not markdown_text.strip():
        return empty_rag_result(
            "The PDF could not be parsed or contains no readable text."
        )

    if not question or not question.strip():
        return empty_rag_result("Please enter a question.")

    try:
        context = get_relevant_context(markdown_text, question)

        if not context or not context.strip():
            return empty_rag_result(
                "No relevant sections were found in the document for your question."
            )

        prompt = build_rag_prompt(
            context=context,
            question=question,
            language=target_lang,
        )

        result = generate_rag_output(
            prompt=prompt,
            provider=provider,
            api_key=api_key,
            gemini_model=gemini_model,
            ollama_model=ollama_model,
        )

        for key in RAG_KEYS:
            if key not in result:
                result[key] = ""

        return result

    except Exception as exc:
        logger.exception("RAG pipeline error")
        return empty_rag_result(
            f"An error occurred while processing your question: {exc}"
        )
