# AGENTS.md

## Project Overview

LearnLite is an AI-powered multilingual educational assistant built with Flask.

---

## Architecture

### app.py

Responsibilities:

* Flask routes
* User interface rendering
* Request handling
* Language selection

---

### ai.py

Responsibilities:

* Gemini integration
* Ollama integration
* Prompt construction
* AI response generation

---

### translations.py

Responsibilities:

* Language dictionaries
* Internationalization support
* UI translations

---

## AI Providers

### Gemini

Cloud-based LLM.

Requirements:

* API key
* Internet connection

### Ollama

Local inference engine.

Requirements:

```bash
ollama serve
```

---

## Supported Languages

* English
* Hindi
* Telugu

---

## Development Notes

When introducing new features:

* Keep language strings centralized.
* Maintain compatibility with both Gemini and Ollama.
* Ensure responsive UI behavior.
