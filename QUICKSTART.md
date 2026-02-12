# Quick Start Guide

## What Was Built

### 1. Fixed Agent Architecture ✅
- Fixed `ChatAgent` bug (LLMProvider → LLMClient)
- Updated to use existing `Intent` and `CandidateSearchParams` schemas
- Added natural language responses for search results
- Added "DB is currently empty" message when no results

### 2. Built FastAPI Backend ✅
- **`/chat`** - Main endpoint for all user input (handles intent classification)
- **`/search`** - Direct search endpoint (for internal/future use)
- **`/health`** - API health check

### 3. Updated Streamlit Frontend ✅
- Now calls `/chat` API instead of direct database access
- Properly handles search and chat intents
- Shows API connection status
- Better error handling

---

## How to Run

### Step 0: Start the Database (First Time)
```bash
cd /Users/Zahir/Desktop/Candidate_DB

# Start PostgreSQL with pgvector
docker-compose up -d

# Check it's running
docker ps
```

Database will be available at: `localhost:5432`
- Database: `candidates`
- User: `postgres`
- Password: `postgres`

### Terminal 1: Start the API
```bash
cd /Users/Zahir/Desktop/Candidate_DB

# Start FastAPI server
uvicorn apis.main:app --reload --port 8000
```

API will be at: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Terminal 2: Start Streamlit
```bash
cd /Users/Zahir/Desktop/Candidate_DB

# Start Streamlit app
streamlit run Chatbot/gen_ai/interface/ui/app.py
```

App will open at: http://localhost:8501

---

## Testing the Flow

### 1. Test API directly (using curl)

**Chat endpoint:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Find senior Python developers"}'
```

**Search endpoint:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "semantic_query": "Python developer",
    "limit": 5
  }'
```

**Health check:**
```bash
curl "http://localhost:8000/health"
```

### 2. Test via Streamlit UI

1. Open http://localhost:8501
2. Check sidebar shows "✅ API Connected"
3. Try these queries:
   - "Find senior Python developers"
   - "Show me React engineers"
   - "Hello, how are you?" (should trigger chat intent)

### 3. Test via API Docs (Swagger)

1. Open http://localhost:8000/docs
2. Click on `/chat` → "Try it out"
3. Enter test message and execute

---

## Architecture Flow

```
┌─────────────┐
│  User Input │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Streamlit Frontend │ (Port 8501)
└──────┬──────────────┘
       │ HTTP POST
       ▼
┌─────────────────────┐
│   FastAPI /chat     │ (Port 8000)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│    ChatAgent        │
│  (Intent Classify)  │
└──────┬──────────────┘
       │
       ├─→ SEARCH Intent
       │        │
       │        ▼
       │   ┌────────────────┐
       │   │ RetrievalAgent │
       │   └────────┬───────┘
       │            │
       │            ▼
       │   ┌────────────────┐
       │   │ search_candidates()│
       │   │  (pgvector)    │
       │   └────────┬───────┘
       │            │
       │            ▼
       │      [Candidates]
       │
       └─→ CHAT Intent
                │
                ▼
         [Chat Response]
```

---

## Stopping Services

```bash
# Stop API (Ctrl+C in Terminal 1)
# Stop Streamlit (Ctrl+C in Terminal 2)

# Stop database
docker-compose down

# Stop database and remove data (⚠️ deletes all data)
docker-compose down -v
```

---

## Common Issues

### "Cannot connect to API"
- Make sure FastAPI is running on port 8000
- Check: `curl http://localhost:8000/health`

### "DB is currently empty"
- Your database has no candidates yet
- Add some test candidates first

### Import errors in API
- Make sure you're in the project root
- Check Python path is set correctly

### LLM not responding
- Check your OpenAI API key is set
- Verify environment variables are loaded

---

## Next Steps

1. **Add test data** to your database
2. **Test intent classification** with various queries
3. **Improve chat responses** (currently just placeholder)
4. **Add session management** for conversation history
5. **Deploy** when ready (see FRONTEND_OPTIONS.md for deployment strategies)

---

## File Structure

```
Candidate_DB/
├── apis/
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── chat_api.py      # /chat endpoint
│   │   ├── search_api.py    # /search endpoint
│   │   └── health_api.py    # /health endpoint
│   ├── api.md               # API documentation
│   └── FRONTEND_OPTIONS.md  # Frontend comparison
├── Chatbot/gen_ai/
│   ├── agents/
│   │   ├── chat_agent.py    # Intent classification
│   │   └── retrieval_agent.py # Search logic
│   ├── interface/ui/
│   │   └── app.py           # Streamlit frontend
│   └── schemas/
│       ├── intent_schema.py # Intent models
│       └── search_schema.py # Search models
└── QUICKSTART.md            # This file
```
