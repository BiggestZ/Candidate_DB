# Candidate DB

AI-assisted candidate search and management system.

This repository combines:
- A FastAPI backend for chat, semantic search, and candidate CRUD
- PostgreSQL + pgvector for retrieval
- A React + Vite frontend with separate pages for:
  - Assistant chat
  - Add candidate
  - Manage candidates (search/edit/delete)0

## What This Repo Does
- Accepts natural-language recruiting queries via `/chat`
- Classifies intent and either responds conversationally or runs retrieval
- Supports direct semantic search via `/search`
- Supports candidate lifecycle APIs via `/candidates`:
  - `POST /candidates` create
  - `GET /candidates` structured management search
  - `PUT /candidates/{candidate_id}` update
  - `DELETE /candidates/{candidate_id}` delete

## Project Layout
- `apis/`: FastAPI app and route modules
  - `apis/main.py`: app bootstrap and router wiring
  - `apis/routes/`: `chat_api.py`, `search_api.py`, `candidates_api.py`, `health_api.py`
- `backend/`: domain logic
  - `agents/`: intent + retrieval orchestration
  - `retrieval/`: vector + SQL search
  - `service/`: candidate create/update/delete/indexing
  - `schema/`: Pydantic models for API contracts
  - `llm/`: provider abstraction/config/prompt loading
- `database/`:
  - `connection.py`: DB connection context manager
  - `migrate.py`: migration runner
  - `migrations/`: SQL migration files
- `frontend/`: React app (Vite)
- `tests/`: schema/prompt and integration-oriented tests
- `docs/`: API docs and backend implementation notes

## Getting Started
Use the quickstart for full setup:
- [QUICKSTART.md](/Users/Zahir/Desktop/Candidate_DB/QUICKSTART.md)

Typical local flow:
1. Start Postgres (`docker-compose up -d`)
2. Run DB migrations
3. Start API (`uvicorn apis.main:app --reload --port 8000`)
4. Start frontend (`cd frontend && npm install && npm run dev`)

## Key URLs (Local)
- API root: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Frontend: `http://localhost:5173`

## API Surface (Current)
- `GET /health`
- `POST /chat`
- `POST /search`
- `GET /candidates` (structured filters for management)
  - Query params: `name`, `role`, `location`, `skill`, `email`, `min_years_experience`, `max_years_experience`, `limit`
- `POST /candidates`
- `PUT /candidates/{candidate_id}`
- `DELETE /candidates/{candidate_id}`

## Important Docs
- API details and examples:
  - [docs/api/api.md](/Users/Zahir/Desktop/Candidate_DB/docs/api/api.md)
- Backend architecture notes:
  - [docs/backend/agents.md](/Users/Zahir/Desktop/Candidate_DB/docs/backend/agents.md)
  - [docs/backend/retrieval.md](/Users/Zahir/Desktop/Candidate_DB/docs/backend/retrieval.md)
  - [docs/backend/service.md](/Users/Zahir/Desktop/Candidate_DB/docs/backend/service.md)
  - [docs/backend/schema.md](/Users/Zahir/Desktop/Candidate_DB/docs/backend/schema.md)

## Environment Notes
- DB credentials are read from `.env` (see quickstart defaults).
- OpenAI key is required for embedding + intent/chat paths.
- Frontend API URL can be overridden with `VITE_API_BASE_URL`.

## Testing
- Python tests: `pytest -q`
- Frontend build check: `cd frontend && npm run build`

If `pytest` is not available in your environment, install test dependencies first.
