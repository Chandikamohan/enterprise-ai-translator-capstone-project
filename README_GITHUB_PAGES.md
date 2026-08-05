# Enterprise AI Translator

This repository serves two purposes:

1. Application source code for the Streamlit-based AI translator.
2. A GitHub Pages static documentation site generated from this README.

## GitHub Pages setup

The GitHub Actions workflow `.github/workflows/pages.yml` copies `README.md` into `docs/_site/index.md` and publishes it to GitHub Pages on every push to `main`.

## What is hosted on Pages

- A static project landing page with setup instructions.
- A summary of features, architecture, and deployment.
- No dynamic Streamlit app is hosted on Pages; the page documents how to run the app locally or in Docker.
