# 🌍 Enterprise AI Translator

A production-grade AI translation application built with **Google Gemini** and **Streamlit**. Translates text and uploaded documents (TXT, PDF, CSV, Excel) into any of 12 supported languages, with optional text-to-speech (MP3) output — backed by a layered, unit-tested service architecture and a full Docker/Kubernetes/CI-CD deployment pipeline.

> **Status: ✅ Complete — all 10 build phases done.** 22/22 tests passing. Verified end-to-end with a live Gemini API call (real translation + real generated MP3). See [Build Progress](#build-progress) for the full phase-by-phase history.

---

## Table of Contents

- [Features](#features)
- [How to Run](#how-to-run)
  - [1. Local (Python)](#1-local-python)
  - [2. Docker / Docker Compose](#2-docker--docker-compose)
  - [3. Kubernetes](#3-kubernetes)
- [Running Tests](#running-tests)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Build Progress](#build-progress)
- [Architecture Principles](#architecture-principles)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- Translate free-text or uploaded documents between 12 languages via Google Gemini (`google-genai` SDK, using the current **Interactions API**)
- Upload and auto-extract text from **TXT, PDF, CSV, and Excel** files
- Generate speech (MP3) from the translated text via **gTTS**, with an in-browser audio player and download button
- Download the translated text (`.txt`) and audio (`.mp3`)
- Side-by-side original vs. translated view, progress spinners, and friendly error messages
- Per-session caching (`st.cache_data`) so re-translating identical text/language pairs doesn't re-call the API
- Structured rotating logs, custom exception hierarchy, and startup config validation

## How to Run

### 1. Local (Python)

**Prerequisites:** Python 3.11+, a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
cd enterprise-ai-translator

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure your API key
copy .env.example .env          # Windows — or: cp .env.example .env
# then edit .env and set GEMINI_API_KEY=your_real_key

# Run the app
streamlit run app.py
```

Open **http://localhost:8501** in your browser. Enter text (or upload a file), pick a target language, click **Translate**, then optionally click **Generate Speech** to hear/download the audio.

> **Getting a key that actually works:** create it from a **personal Google account** (not an institutional/Workspace-managed one) — some Workspace domains (school/company accounts) have the Generative Language API disabled by admin policy, which surfaces as a `403 PERMISSION_DENIED: "Your project has been denied access"` error even though the key looks valid. See [Troubleshooting](#troubleshooting).

### 2. Docker / Docker Compose

**Prerequisites:** Docker Desktop.

```bash
cd enterprise-ai-translator
copy .env.example .env          # fill in GEMINI_API_KEY
docker compose up --build
```

Serves on **http://localhost:8501**. `outputs/` and `logs/` are bind-mounted so generated audio/log files persist across container restarts.

Without Compose:

```bash
docker build -t ai-translator .
docker run -p 8501:8501 --env-file .env ai-translator
```

### 3. Kubernetes

**Prerequisites:** a running cluster (e.g. Minikube) and `kubectl` configured against it. Full walkthrough in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl create secret generic translator-secret \
  --namespace ai-translator \
  --from-literal=GEMINI_API_KEY=YOUR_GEMINI_API_KEY
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

kubectl get all -n ai-translator
```

## Running Tests

```bash
pytest --cov=. --cov-report=term-missing
```

22 tests, ~90% coverage on non-UI code (all Gemini/gTTS calls mocked — no network calls or API costs during testing). `app.py` is intentionally excluded from unit coverage since it's UI glue; it's instead smoke-tested by launching the live server.

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (**required**) | — |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `APP_ENV` | `development` or `production` | `development` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `MAX_UPLOAD_SIZE_MB` | Max upload file size | `10` |

`config/config.py` validates these at startup and raises `ConfigurationError` if `GEMINI_API_KEY` is missing. **Never commit your real `.env`** — it's gitignored; only `.env.example` (with placeholder values) is tracked.

## Project Structure

```text
enterprise-ai-translator/
├── app.py                  # Streamlit entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── config/
│   ├── __init__.py
│   └── config.py           # Settings loader + startup validation
├── services/
│   ├── __init__.py
│   ├── translator.py        # Gemini translation service (Interactions API, retries + chunking)
│   ├── speech.py             # gTTS text-to-speech (unique-filename MP3 output)
│   ├── file_reader.py         # TXT/PDF/CSV/Excel text extraction
│   └── prompt_builder.py       # Translation prompt construction
├── utils/
│   ├── __init__.py
│   ├── logger.py            # Rotating, structured logging
│   ├── validators.py        # Input/file/language validation
│   ├── exceptions.py        # Custom exception hierarchy
│   ├── helpers.py           # Text chunking, filename generation
│   ├── constants.py         # Supported languages, file types, limits
│   └── network.py           # Forces IPv4 DNS resolution (works around broken-IPv6 hangs)
├── assets/
├── outputs/                 # Generated translations/audio (gitignored)
├── logs/                    # Rotating app logs (gitignored)
├── tests/                   # 22 pytest unit tests
├── docs/                    # ARCHITECTURE.md, DEPLOYMENT.md, API.md, PORTFOLIO.md, INTERVIEW_PREP.md
├── k8s/                     # Namespace, ConfigMap, Secret template, PVCs, Deployment, Service, Ingress, HPA
└── .github/workflows/       # ci-cd.yml (test -> build/push -> deploy)
```

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system diagrams (Mermaid) and design rationale
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — local, Docker, Kubernetes, and CI/CD deployment steps
- [docs/API.md](docs/API.md) — internal service interfaces and exception hierarchy
- [docs/PORTFOLIO.md](docs/PORTFOLIO.md) — resume bullets, project description, skills demonstrated, future enhancements
- [docs/INTERVIEW_PREP.md](docs/INTERVIEW_PREP.md) — project-specific and general Python/Streamlit/Gemini/Docker/Kubernetes/CI-CD Q&A

## Build Progress

### ✅ Phase 1 — Project Planning & Environment Setup
- Repository/folder scaffolding created (`config/`, `services/`, `utils/`, `assets/`, `outputs/`, `logs/`, `tests/`, `docs/`, `k8s/`, `.github/workflows/`)
- `requirements.txt` with pinned minimum versions, `.env.example`, `.gitignore`
- `utils/exceptions.py` — custom exception hierarchy (`ConfigurationError`, `ValidationError`, `FileProcessingError`, `TranslationError`, `SpeechGenerationError`)
- `utils/constants.py`, `utils/logger.py`, `utils/validators.py`, `utils/helpers.py`
- `config/config.py` — environment-backed `Settings` dataclass with startup validation

### ✅ Phase 2 — File Processing & Translation Services
- `services/file_reader.py` — extracts text from TXT, PDF (`pdfplumber`), CSV, and Excel (`pandas`) via a single `read_file()` entry point
- `services/prompt_builder.py` — builds the Gemini translation prompt (preserves grammar/meaning/technical terms)
- `services/translator.py` — `TranslatorService` with automatic text chunking for long inputs and retry/backoff on transient API failures
- 8 passing unit tests (Gemini client mocked, no real API calls)

> **SDK notes:** started with `google-generativeai`, switched to **`google-genai`** after pytest flagged the former as fully deprecated, then later upgraded the call site again from `client.models.generate_content()` to **`client.interactions.create(model=..., input=...)`** — Google's current GA **Interactions API**, the newer replacement for `generateContent`. Verified against the installed SDK's actual method signatures, not just docs.
>
> **Network fix (post-launch bug):** during live testing, "Translate" hung indefinitely with no error. Root cause: some networks resolve Google's API host to an IPv6 address that's unreachable (blocked/broken egress), and the underlying HTTP client had no timeout — so it sat in `SYN_SENT` forever instead of falling back. Fixed two ways: (1) `utils/network.py` monkeypatches `socket.getaddrinfo` to prefer IPv4, applied automatically on `import utils`; (2) `GEMINI_TIMEOUT_SECONDS` (20s) is now actually wired into the Gemini client via `http_options=types.HttpOptions(timeout=...)` (it was defined back in Phase 1 but never passed to the client — a real bug, not just theoretical hardening). Verified live: the same request that previously hung indefinitely (173s once bounded by a 60s timeout, effectively infinite before that) now completes in ~5s.

### ✅ Phase 3 — Text-to-Speech
- `services/speech.py` — `SpeechService.generate()` converts text to an MP3 via gTTS, reusing the same language-name → code map as the translator, with a UUID-based filename per call so concurrent users never collide
- 4 passing tests (gTTS mocked — no real network calls in the test suite)

### ✅ Phase 4 — Streamlit UI
- `app.py` — sidebar with Text/File input mode and target-language selector; translate button with spinner and error surfacing; side-by-side original/translated columns; text download button; on-demand "Generate Speech" with audio player and MP3 download; `st.session_state` keeps translated text/audio across reruns; services built once via `@st.cache_resource`
- Uploaded files are read from a temp file and deleted immediately after extraction (no `uploads/` buildup)

### ✅ Phase 5 — Hardening Pass
- `MAX_TEXT_CHARACTERS` (20,000) enforced inside `validate_text_input()`
- Translation results cached per `(text, language)` pair via `@st.cache_data`, cutting duplicate Gemini calls
- `tests/test_validators.py` added — 10 tests covering every validator branch
- Test suite: 22 passing, ~90% coverage on non-UI code

### ✅ Phase 6 — Docker & Docker Compose
- `Dockerfile` — `python:3.11-slim` base, installs `requirements.txt`, creates `outputs/`/`logs/`, exposes `8501`, includes a `HEALTHCHECK` against Streamlit's `/_stcore/health` endpoint
- `.dockerignore` — excludes venv, git, tests, docs, k8s, and local `outputs/`/`logs/`/`.env` from the build context
- `docker-compose.yml` — single `translator` service, `.env` loaded via `env_file`, `outputs/`/`logs/` bind-mounted

### ✅ Phase 7 — Kubernetes Manifests
- `k8s/namespace.yaml`, `configmap.yaml`, `secret.example.yaml` (template only), `pvc.yaml` (output/logs), `deployment.yaml` (2 replicas, rolling updates, resource limits, readiness/liveness probes), `service.yaml`, `ingress.yaml`, `hpa.yaml` (2–10 replicas at 70% CPU)
- All manifests parsed and validated as well-formed YAML

### ✅ Phase 8 — GitHub Actions CI/CD
- `.github/workflows/ci-cd.yml` — three jobs on push/PR to `main`: **test** (pytest + coverage) → **build-and-push** (Docker image to Docker Hub, tagged `latest` + `<git-sha>`) → **deploy** (rolling `kubectl set image` update)
- Required GitHub Secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `KUBE_CONFIG`

### ✅ Phase 9 — Documentation Set
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md), [`docs/API.md`](docs/API.md)

### ✅ Phase 10 — Final Deliverables
- [`docs/PORTFOLIO.md`](docs/PORTFOLIO.md) — resume bullets, project description, skills demonstrated, target roles, future enhancements
- [`docs/INTERVIEW_PREP.md`](docs/INTERVIEW_PREP.md) — project-specific and general Q&A

### ✅ Live Verification
- Full server smoke test: `streamlit run app.py --server.headless true` → confirmed HTTP 200
- **Real end-to-end run with a live Gemini API key:** translated `"Artificial Intelligence is changing the world."` → `"L'Intelligence Artificielle change le monde."` (French), and `"Good morning! How are you today?"` → Spanish + a real 22KB MP3 generated via gTTS
- Full 22-test suite passing after every change

## Architecture Principles

Clean Architecture, SOLID, DRY, KISS, YAGNI, separation of concerns (UI → services → utils/config), dependency injection at service boundaries, no hardcoded values (constants + env vars only).

## Security Notes

- No secrets committed; `.env` is gitignored, only `.env.example` (placeholder values) is tracked
- API key required via environment variable, validated at startup, never logged
- File type/size validated before any processing occurs
- Kubernetes secret is created imperatively (`kubectl create secret ...`), never checked into the repo — `k8s/secret.example.yaml` is a template only
- CI/CD secrets (`DOCKER_USERNAME`, `DOCKER_PASSWORD`, `KUBE_CONFIG`) live only in GitHub Actions Secrets

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ConfigurationError: GEMINI_API_KEY is not set` | `.env` missing or key not filled in | `copy .env.example .env` and set a real key |
| `403 PERMISSION_DENIED: "Your project has been denied access. Please contact support."` | The Google account/project behind the key is blocked — very common on institutional/Workspace (school, company) domains where an admin has disabled the Generative Language API | Generate a fresh key from a **personal** Google account at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `ModuleNotFoundError` on startup | Dependencies not installed in the active environment | `pip install -r requirements.txt` inside your activated venv |
| "Translating..." spinner never finishes, no error shown | Some networks resolve Google's API host to an unreachable IPv6 address and the connection hangs instead of failing; already patched — `utils/network.py` forces IPv4 and `GEMINI_TIMEOUT_SECONDS` bounds every request to ~20s | If you still see this, check `logs/app.log` for a hung request with no completion line, and confirm you're on the latest `services/translator.py` |
| Streamlit opens but translation fails silently | Check `logs/app.log` — every attempt and failure is logged there with full context | — |
| Docker build/run untested locally | This repo was built in a sandbox with no Docker daemon | Run `docker compose up --build` yourself before relying on it |
| Kubernetes manifests untested against a live cluster | Same sandbox limitation — no `kubectl`/Minikube available here | Validate with `kubectl apply --dry-run=client -f k8s/` first |

## License

Not yet decided — add a `LICENSE` file with your chosen license (MIT is a common default for portfolio projects) before publishing this publicly.
