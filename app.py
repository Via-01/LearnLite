# app.py

import logging
import os
import uuid

from flask import Flask, render_template, request
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from ai import (
    DEFAULT_GEMINI_MODEL,
    get_explanation,
    get_ollama_models,
)
from rag import get_document_answer
from pdf_utils import extract_pdf_markdown
from translations import TRANSLATIONS

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/learnlite_uploads" if os.getenv("VERCEL") else "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def count_words(text: str) -> int:
    return len([word for word in text.strip().split() if word])


@app.route("/", methods=["GET", "POST"])
def index():

    selected_lang = request.form.get("lang", "en")
    t = TRANSLATIONS.get(selected_lang, TRANSLATIONS["en"])

    mode = request.form.get("mode", "learnlite")
    provider = request.form.get("provider", "gemini")
    gemini_model = (
        request.form.get("gemini_model", DEFAULT_GEMINI_MODEL).strip()
        or DEFAULT_GEMINI_MODEL
    )
    api_key = request.form.get("api_key", "")
    user_text = request.form.get("user_text", "")
    question = request.form.get("question", "")

    running_on_vercel = bool(os.getenv("VERCEL"))

    if running_on_vercel:
        ollama_models = []
        ollama_status = (
            "Ollama local inference is available when running LearnLite locally. "
            "The deployed version supports Gemini BYOK."
        )
    else:
        ollama_models, ollama_status = get_ollama_models()

    selected_ollama_model = request.form.get("ollama_model", "")
    if not selected_ollama_model and ollama_models:
        selected_ollama_model = ollama_models[0]

    results = None
    error = ""
    word_count = count_words(user_text)

    if request.method == "POST" and request.form.get("action") == "explain":
        # ====================
        # LearnLite Mode
        # ====================
        if mode == "learnlite":
            if not user_text.strip():
                error = "Please enter a topic or paragraph."
            elif word_count > 700:
                error = (
                    f"Please keep the input within 700 words. "
                    f"Current count: {word_count}."
                )
            else:
                results = get_explanation(
                    text=user_text,
                    target_lang=selected_lang,
                    provider=provider,
                    api_key=api_key,
                    gemini_model=gemini_model,
                    ollama_model=selected_ollama_model,
                )

        # ====================
        # LearnLite-RAG Mode
        # ====================
        elif mode == "rag":
            pdf_file = request.files.get("pdf_file")

            if not pdf_file or not pdf_file.filename:
                error = "Please upload a PDF."
            elif not question.strip():
                error = "Please enter a question."
            elif not pdf_file.filename.lower().endswith(".pdf"):
                error = "Only PDF files are supported."
            else:
                # Check file size before saving
                pdf_file.seek(0, os.SEEK_END)
                file_size = pdf_file.tell()
                pdf_file.seek(0)

                if file_size > MAX_FILE_SIZE:
                    error = "PDF exceeds 10 MB limit."
                else:
                    # Use a unique name to avoid collisions / path-traversal
                    safe_name = (
                        f"{uuid.uuid4().hex}_{secure_filename(pdf_file.filename)}"
                    )
                    file_path = os.path.join(UPLOAD_FOLDER, safe_name)

                    try:
                        pdf_file.save(file_path)
                        logger.info("Saved upload: %s (%d bytes)", file_path, file_size)

                        markdown_text = extract_pdf_markdown(file_path)

                        if markdown_text.startswith("PDF extraction failed"):
                            error = markdown_text
                        else:
                            results = get_document_answer(
                                markdown_text=markdown_text,
                                question=question,
                                target_lang=selected_lang,
                                provider=provider,
                                api_key=api_key,
                                gemini_model=gemini_model,
                                ollama_model=selected_ollama_model,
                            )

                    except Exception as exc:
                        logger.exception("RAG upload/processing error")
                        error = f"Could not process the PDF: {exc}"
                    finally:
                        # Always clean up the temp file
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except OSError:
                            logger.warning("Could not delete temp file: %s", file_path)

    return render_template(
        "index.html",
        t=t,
        mode=mode,
        selected_lang=selected_lang,
        provider=provider,
        results=results,
        error=error,
        user_text=user_text,
        question=question,
        word_count=word_count,
        gemini_model=gemini_model,
        api_key_present=bool(api_key),
        ollama_models=ollama_models,
        ollama_status=ollama_status,
        selected_ollama_model=selected_ollama_model,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
