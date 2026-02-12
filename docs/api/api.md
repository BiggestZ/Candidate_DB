# Candidate DB API Documentation

## Overview
This API provides an AI-powered interface for searching and interacting with a candidate database.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "Candidate DB API"
}
```

---

### 2. Chat Endpoint (Main Entry Point)
**POST** `/chat`

Main endpoint that accepts user messages, classifies intent, and returns appropriate responses.

**Request Body:**
```json
{
  "message": "Find me senior Python developers in San Francisco",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "message": "Found 5 candidate(s) matching your search",
  "intent": "search",
  "confidence": 0.95,
  "data": {
    "candidates": [
      {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "github_url": "https://github.com/johndoe",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "role": "Senior Python Developer",
        "score": 0.92
      }
    ],
    "count": 5
  }
}
```

**For Chat Intent:**
```json
{
  "message": "How can I help you?",
  "intent": "chat",
  "confidence": null,
  "data": null
}
```

**Flow:**
1. User message → Intent classification (LLM)
2. If **SEARCH** intent detected → Retrieve candidates → Return results with message
3. If **CHAT** intent detected → Return conversational response
4. If **UNKNOWN** intent → Return error message

---

### 3. Direct Search Endpoint
**POST** `/search`

Direct semantic search endpoint for internal use or when you want to bypass intent classification.

**Request Body:**
```json
{
  "semantic_query": "experienced React developer with TypeScript skills",
  "filters": {
    "role": "Frontend Developer"
  },
  "limit": 10
}
```

**Response:**
```json
[
  {
    "id": 1,
    "full_name": "Jane Smith",
    "email": "jane@example.com",
    "github_url": "https://github.com/janesmith",
    "linkedin_url": "https://linkedin.com/in/janesmith",
    "role": "Frontend Developer",
    "score": 0.89
  }
]
```

---

## Running the API

### Start the server:
```bash
cd /Users/Zahir/Desktop/Candidate_DB
uvicorn apis.main:app --reload --port 8000
```

### Example curl requests:

**Chat:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Find senior engineers with 5+ years experience"}'
```

**Direct Search:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "semantic_query": "machine learning engineer with Python",
    "limit": 5
  }'
```

**Health Check:**
```bash
curl "http://localhost:8000/health"
```

---

## Architecture

```
User Input
    ↓
[/chat endpoint]
    ↓
[ChatAgent - LLM Intent Classification]
    ↓
    ├─→ [Search Intent] → [RetrievalAgent] → [search_candidates()] → Results
    │
    └─→ [Chat Intent] → Conversational Response
```

**Direct path (optional):**
```
User → [/search endpoint] → [search_candidates()] → Results
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `500` - Internal server error

Error response format:
```json
{
  "detail": "Error message description"
}
```
