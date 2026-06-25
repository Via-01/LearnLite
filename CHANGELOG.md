# Changelog

All notable changes to this project will be documented here.

## [Unreleased]

### Added

- LearnLite-RAG mode: upload a PDF and ask questions answered from its content
- `rag.py`: clean RAG pipeline with `get_document_answer`, `build_rag_prompt`, `empty_rag_result`
- `pdf_utils.py`: `extract_pdf_markdown`, `split_sections`, `get_relevant_context`, `extract_headings`
- `ai.py`: `generate_rag_output` with RAG-specific JSON parser (`parse_rag_response`)
- `ai.py`: internal `_call_gemini_raw` / `_call_ollama_raw` helpers separating network calls from parsing
- Secure file handling in `app.py`: `werkzeug.utils.secure_filename` + UUID prefix + temp-file cleanup
- Graceful error propagation: all RAG errors surface as user-readable messages, never tracebacks
- `werkzeug`, `pymupdf`, and `pymupdf4llm` added to `requirements.txt` and `pyproject.toml`

### Fixed

- RAG response never parsed correctly: `generate_with_gemini`/`generate_with_ollama` returned
  `SECTION_KEYS` dicts; RAG path now uses `generate_rag_output` which calls `parse_rag_response`
- `rag.py` imported from `ai` but used its own duplicate `clean_json_text`/`parse_rag_response`; duplicates removed
- `"answer" in result` check in old `get_document_answer` was always `False` (result keys were
  `SECTION_KEYS`), causing every RAG response to fall into the wrong parse branch
- `pdf_file.filename` used directly as save path — replaced with `secure_filename` + UUID
- Uploaded temp files were never deleted after processing
- `pymupdf` and `pymupdf4llm` were missing from `pyproject.toml`

## [0.1.0]

### Added

- Flask web application
- Gemini integration
- Ollama integration
- Multilingual support
- Responsive UI
- Internationalization support
