# LearnLite User Manual

## Overview

LearnLite is an AI-powered multilingual learning assistant that supports:

* English
* Hindi
* Telugu

It provides:

* AI-generated explanations
* Local AI using Ollama
* Cloud AI using Gemini
* Responsive web interface

---

## Getting Started

### 1. Launch the application

Run:

```bash
python app.py
```

Open the URL shown in the terminal.

---

### 2. Select a language

Choose:

* English
* Hindi
* Telugu

---

### 3. Choose an AI provider

#### Gemini

Cloud-based AI.

Requires:

* Gemini API key
* Internet connection

#### Ollama

Local AI model.

Requires:

```bash
ollama serve
```

and an installed model.

---

## Troubleshooting

### Gemini not responding

Check:

* API key configured correctly
* Internet connectivity

### Ollama unavailable

Verify:

```bash
ollama serve
```

is running.

### Translations missing

Ensure `translations.py` contains the required language entries.
