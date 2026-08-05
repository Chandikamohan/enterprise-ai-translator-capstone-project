# Enterprise AI Translator

Welcome to the static GitHub Pages landing page for the **Enterprise AI Translator** project.

This site is served from the `docs/` folder in the `main` branch and is intended as the public documentation and project overview for the repository.

## What is included here

- Project overview and feature summary
- Setup instructions for local development
- Docker / deployment guidance
- Notes on GitHub Pages hosting

## Running the app

The app itself is a Streamlit application located in `app.py`.

1. Create a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
4. Run:
   ```bash
   streamlit run app.py
   ```

## GitHub Pages status

If the Pages link is not visible yet, please confirm the repository settings use the `main` branch and `/docs` folder source. It can take a few minutes after the first push for the Pages site to become active.

> Expected site URL:
> `https://chandikamohan.github.io/enterprise-ai-translator-capstone-project/`
