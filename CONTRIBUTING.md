# Contributing to LearnLite

Thank you for your interest in contributing to LearnLite!

## Development Setup

1. Clone the repository.

```bash
git clone <repo-url>
cd learnlite
```

2. Create a virtual environment.

```bash
python -m venv .venv
```

Activate it:

Windows:

```bash
.venv\Scripts\activate
```

Linux/Mac:

```bash
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Create a `.env` file from `.env.example`.

## Coding Guidelines

* Follow PEP8 conventions.
* Add type hints whenever practical.
* Write descriptive commit messages.
* Keep functions small and focused.

## Pull Requests

* Create a feature branch.
* Ensure CI passes.
* Update documentation if necessary.
* Submit a pull request with a clear description.
