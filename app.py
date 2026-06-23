import os

from flask import Flask, render_template, request
from dotenv import load_dotenv

from ai import DEFAULT_GEMINI_MODEL, get_explanation, get_ollama_models
from translations import TRANSLATIONS

load_dotenv()

app = Flask(__name__)


def count_words(text: str) -> int:
    return len([word for word in text.strip().split() if word])


@app.route("/", methods=["GET", "POST"])
def index():
    selected_lang = request.form.get("lang", "en")
    t = TRANSLATIONS.get(selected_lang, TRANSLATIONS["en"])

    provider = request.form.get("provider", "gemini")
    gemini_model = (
        request.form.get("gemini_model", DEFAULT_GEMINI_MODEL).strip()
        or DEFAULT_GEMINI_MODEL
    )
    api_key = request.form.get("api_key", "")
    user_text = request.form.get("user_text", "")

    # On Vercel, localhost belongs to the cloud function, not the user's laptop.
    # So we skip Ollama probing in deployment to avoid slow failed requests.
    running_on_vercel = bool(os.getenv("VERCEL"))
    if running_on_vercel:
        ollama_models = []
        ollama_status = "Ollama local inference is available when running LearnLite locally. The deployed version supports Gemini BYOK."
    else:
        ollama_models, ollama_status = get_ollama_models()

    selected_ollama_model = request.form.get("ollama_model", "")
    if not selected_ollama_model and ollama_models:
        selected_ollama_model = ollama_models[0]

    results = None
    error = ""
    word_count = count_words(user_text)

    if request.method == "POST" and request.form.get("action") == "explain":
        if not user_text.strip():
            error = "Please enter a topic or paragraph."
        elif word_count > 700:
            error = (
                f"Please keep the input within 700 words. Current count: {word_count}."
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

    return render_template(
        "index.html",
        t=t,
        selected_lang=selected_lang,
        provider=provider,
        results=results,
        error=error,
        user_text=user_text,
        word_count=word_count,
        gemini_model=gemini_model,
        api_key_present=bool(api_key),
        ollama_models=ollama_models,
        ollama_status=ollama_status,
        selected_ollama_model=selected_ollama_model,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
