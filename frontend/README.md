# Candidate DB Frontend (Vite + React)

Sleek chatbot UI for interacting with the FastAPI Candidate DB backend.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

By default, the UI sends chat requests to:

- `http://localhost:8000/chat`

If your backend is on a different URL, create `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Build

```bash
npm run build
```
