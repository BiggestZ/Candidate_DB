# Quick Start Guide

## 1) Start Postgres + pgvector

```bash
cd /Users/Zahir/Desktop/Candidate_DB
docker-compose up -d
```

Expected database settings:
- Host: `localhost`
- Port: `5432`
- DB: `candidates`
- User: `postgres`
- Password: `postgres`

## 2) Run migrations

```bash
python -c "from database.migrate import run_migrations; run_migrations()"
```

## 3) Start API

```bash
uvicorn apis.main:app --reload --port 8000
```

API URLs:
- `http://localhost:8000/health`
- `http://localhost:8000/docs`
- `http://localhost:8000/chat`
- `http://localhost:8000/search`
- `http://localhost:8000/candidates`

## 4) Start React frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:
- `http://localhost:5173`

If needed, set API base URL in `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 5) Run tests

```bash
pytest -q
```

## Smoke test

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Find senior Python developers in NYC"}'
```
