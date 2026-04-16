# Candidate DB Architecture

## 1. Purpose

Candidate DB is an AI-assisted recruiting system with:
- FastAPI backend for chat/search/candidate management
- PostgreSQL + pgvector for candidate storage and semantic retrieval
- React + Vite frontend for user interaction

## 2. High-Level System

```text
[React Frontend]
      |
      v
[FastAPI: apis/main.py]
      |
      +--> /chat       -> ChatAgent -> Intent routing -> (LLM chat OR RetrievalAgent)
      +--> /search     -> retrieval.search.search_candidates
      +--> /candidates -> candidate_service (CRUD + re-embedding)
      |
      v
[PostgreSQL + pgvector]
  - candidates
  - candidate_profiles (skills + embedding)
  - candidate_resume
```

## 3. Repository Structure

```text
apis/
  main.py                # FastAPI app + router wiring
  routes/
    chat_api.py          # Conversational entrypoint (/chat)
    search_api.py        # Direct semantic retrieval (/search)
    candidates_api.py    # CRUD + management search (/candidates)
    health_api.py

backend/
  agents/                # Orchestration layer (chat + retrieval coordination)
  intent/                # Intent detection/routing
  retrieval/             # Vector search implementation
  service/               # Candidate domain operations (create/update/delete/indexing)
  schema/                # Pydantic request/response contracts
  llm/                   # LLM provider abstraction and prompt loading
  prompts/               # Prompt templates by function
  evaluator/             # Logging + metrics helpers

database/
  connection.py          # DB connection context manager
  migrate.py             # Migration runner
  migrations/            # SQL migration files

frontend/               # React app
tests/                  # Python tests
docs/                   # API + design notes
```

## 4. Request Flows

### 4.1 Chat Flow (`POST /chat`)
1. `apis/routes/chat_api.py` receives `ChatMessage`.
2. `ChatAgent.run()` checks:
   - DB count query shortcut, or
   - intent classification (`search`, `chat`, or `unknown`).
3. If intent is `search`: delegate to `RetrievalAgent`, return candidates.
4. If intent is `chat`: load prompt + call configured LLM provider.
5. Return standardized `ChatResponse`.

### 4.2 Direct Search Flow (`POST /search`)
1. `apis/routes/search_api.py` accepts `CandidateSearchParams`.
2. `backend/retrieval/search.py`:
   - embeds query text,
   - runs vector similarity SQL against `candidate_profiles.embedding`,
   - joins candidate metadata from `candidates`.
3. Returns ranked `CandidateSearchResult[]`.

### 4.3 Candidate Management Flow (`/candidates`)
- `GET /candidates`: structured filtering for management UI use cases.
- `POST /candidates`: insert candidate row + profile row + generated embedding.
- `PUT /candidates/{id}`: merge updates, regenerate text/embedding, update records.
- `DELETE /candidates/{id}`: remove dependent rows then candidate row.

## 5. Data Model (Current Core)

- `candidates`: canonical profile metadata (`full_name`, `email`, `recent_role`, links, location, years).
- `candidate_profiles`: searchable enrichment (`summary`, CSV `skills`, `embedding`, embedding metadata).
- `candidate_resume`: referenced in delete path for cleanup.

Semantic ranking is computed using pgvector distance (`<->`) and converted to a score in query results.

## 6. Configuration and Runtime

- Python: `>=3.11,<3.12` (see `pyproject.toml`)
- API server entrypoint: `uvicorn apis.main:app --reload --port 8000`
- DB connection env vars (`.env`):
  - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- LLM provider keys required for chat/embedding paths (OpenAI by default in chat route initialization).

## 7. Design Notes and Tradeoffs

- Clear separation exists between API, orchestration, domain services, and persistence.
- `ChatAgent` currently combines intent routing and response orchestration (simple and effective, but centralizes behavior).
- Management search and semantic retrieval are intentionally separated into different endpoints for predictable UX.
- Skills are stored as CSV text in `candidate_profiles.skills`; simple but not ideal for strict normalization/analytics.

## 8. Extension Points

- Add new LLM providers under `backend/llm/providers/` and wire in `backend/llm/config.py`.
- Add new intent types in `backend/schema/intent_schema.py` + `backend/intent/intent_router.py`.
- Add new retrieval filters in `backend/retrieval/search.py` and schema contracts.
- Add new API surfaces in `apis/routes/` and register router in `apis/main.py`.

## 9. Operational Checklist

1. Start DB container (`docker-compose up -d`).
2. Run migrations (`database/migrate.py`).
3. Start API (`uvicorn apis.main:app ...`).
4. Start frontend (`frontend/`, `npm run dev`).
5. Validate with:
   - `GET /health`
   - `POST /chat`
   - `POST /search`
   - `/candidates` CRUD
