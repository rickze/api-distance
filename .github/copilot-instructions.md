# Copilot / AI Agent Instructions (project-specific)

This repository is a minimal FastAPI service. The goal of these instructions is to help AI coding agents be immediately productive by describing the project's structure, conventions, and run/debug workflows.

**Quick Overview**
- **Repo type:** single-file FastAPI HTTP service
- **Key files:** `main.py` (app entrypoint), `requirements.txt` (dependencies)
- **How it runs:** `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

**Architecture & Patterns**
- **Single FastAPI app:** The FastAPI application instance is created in `main.py` as `app`. All endpoints are defined using decorator-style route functions (e.g. `@app.get("/ping")`).
- **Pydantic usage:** `pydantic.BaseModel` is imported in `main.py`. Expect request/response models to be defined inline or in new modules when the project grows.
- **No frameworks or service layers present:** There are currently no separate routers, services, or persistence layers — changes should preserve the simple layout unless adding clear separation (new folders like `app/`, `routers/`, `models/`).

**Developer workflows (explicit commands)**
- **Install deps:** `pip install -r requirements.txt`
- **Run locally (PowerShell):**
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- **Health check:** GET `http://127.0.0.1:8000/ping` should return `{"status":"ok"}`.

**Project-specific conventions**
- **Entrypoint name:** Keep the FastAPI instance named `app` in `main.py` so tooling (uvicorn) can import `main:app` without adjustment.
- **Small-scope changes:** Because this repo is single-file and minimal, prefer small, obvious edits (add endpoints, models) rather than broad refactors. If you add new modules, place them under top-level directories and update imports.

**Integration points & dependencies**
- **Dependencies declared:** `requirements.txt` lists `fastapi` and `uvicorn`.
- **External integrations:** None present. When adding integrations (databases, external APIs), add configuration and environment-awareness (e.g., env vars, `.env`) and document them in `README.md`.

**When editing code — concrete examples**
- To add a new GET endpoint, follow the `@app.get(...)` pattern in `main.py` and return JSON-compatible types (dicts, Pydantic models).
- To accept JSON input, create a `pydantic` model and annotate the handler parameter: `def create(item: ItemModel):` where `ItemModel` subclasses `BaseModel`.
- When adding new files, update `requirements.txt` only for added runtime dependencies.

**What to avoid or be cautious about**
- Don't change the `app` variable name in `main.py` without updating run commands or CI.
- Avoid adding heavy frameworks or complex dependency injection for now — keep the repository lightweight and explicit.

**Files to inspect for context**
- `main.py` — primary reference for existing route style and app setup.
- `requirements.txt` — runtime dependencies.

If any of this is unclear or you'd like the file to include additional examples (tests, Dockerfile, CI steps), tell me which area to expand and I'll update the instructions.
