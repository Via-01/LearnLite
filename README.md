# LearnLite deployment notes

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Optional local `.env`

Create a `.env` file only for local development:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Do not commit `.env`. The app also supports BYOK by letting users paste a Gemini API key in the UI.

## Deploy to Vercel

1. Push this folder to GitHub.
2. Import the GitHub repo in Vercel.
3. Framework preset can be left as automatic. Vercel detects Flask from `requirements.txt` and the top-level `app` object in `app.py`.
4. Deploy.

## Important Ollama note

Ollama Local AI works only when the app is run locally on a machine where Ollama is installed and running. On Vercel or any cloud deployment, `localhost:11434` refers to the cloud server, not the user's laptop.

So:

- Deployed version: Gemini BYOK works.
- Local version: Gemini BYOK and Ollama Local AI work.
