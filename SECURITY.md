# Security Policy

## Supported Versions

The latest release of LearnLite is currently supported with security fixes.

## Reporting a Vulnerability

Please do not publicly disclose security vulnerabilities.

Report issues privately to the project maintainers.

## File Upload Security

- Uploaded PDFs are validated by extension and size (10 MB limit).
- Filenames are sanitised with `werkzeug.utils.secure_filename` and prefixed
  with a UUID to prevent path-traversal and filename-collision attacks.
- Temporary files are deleted immediately after processing in a `finally` block.

## API Key Handling

- User-supplied API keys are never stored to disk or logged.
- Keys are read from the POST body per-request and discarded after use.
- The `GEMINI_API_KEY` environment variable is supported as a server-side
  alternative; it is never exposed in responses.

## Known Limitations

- The `/uploads` folder is used for transient PDF processing only.
  It should not be publicly accessible in production deployments.
- Ollama inference is disabled on Vercel (cloud deployments) to prevent
  server-side SSRF via arbitrary host parameters.
