# AGENTS.md

Guide for contributors/agents working on `hotel-system`, focused on business logic + API integration.

## Stack

- Frontend: Vue 3 + Vite + Element Plus (`frontend/`)
- Backend: FastAPI + SQLAlchemy (`backend/`)
- i18n: `frontend/src/locales/en.json`, `frontend/src/locales/vi.json`

## Core Rule: Backend-First Validation

- Business validation must happen in backend.
- Frontend should not duplicate full business validation logic.
- Frontend can keep only UX checks (example: missing date range before opening dialog), but source of truth is backend response.

## API Contract Rules

- Keep request/response shape stable and explicit.
- If API changes, update FE call sites in same task.
- Error response should be i18n-friendly:
  - `HTTPException(detail="some.i18n.key")` for general errors.
  - `{ "success": false, "error": { "field_name": "some.i18n.key" } }` for field-level validation errors.
- Avoid raw English error text in new business endpoints.

## i18n Rules

- Any new backend i18n key must be added to both:
  - `frontend/src/locales/en.json`
  - `frontend/src/locales/vi.json`
- Keep `vi.json` valid Vietnamese with accents and UTF-8 encoding.
- Keep key trees aligned between `en.json` and `vi.json`.
