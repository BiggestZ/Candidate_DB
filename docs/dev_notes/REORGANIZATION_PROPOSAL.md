# Project Reorganization Proposal

## Current Issues 🔴

1. **Confusing naming**: `Chatbot/gen_ai/` doesn't clearly describe what it does (it's your entire backend!)
2. **Too much nesting**: `Chatbot/gen_ai/agents/...` - unnecessary depth
3. **Inconsistent naming**: Mix of `Chatbot/` (capital) and `apis/` (lowercase)
4. **Scattered docs**: `.md` files everywhere
5. **Unused files**: `main.py` is just a placeholder
6. **Tests folder**: Should be lowercase `tests/` per Python convention
7. **Unclear separation**: Hard to see what's API, what's backend logic, what's UI

---

## Proposed Structure ✅

```
candidate_db/                    # Root (rename from Candidate_DB)
│
├── backend/                     # Core AI/ML logic (was Chatbot/gen_ai/)
│   ├── agents/                  # AI agents
│   │   ├── __init__.py
│   │   ├── chat_agent.py
│   │   ├── retrieval_agent.py
│   │   ├── base.py
│   │   └── types.py
│   │
│   ├── llm/                     # LLM providers & config
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── config.py
│   │   ├── router.py
│   │   ├── response_parser.py
│   │   └── providers/
│   │       ├── openai.py
│   │       ├── anthropic.py
│   │       └── gemini.py
│   │
│   ├── retrieval/               # Search & retrieval (was retriever/)
│   │   ├── __init__.py
│   │   └── search.py
│   │
│   ├── schemas/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── intent.py            # Renamed from intent_schema.py
│   │   ├── search.py            # Renamed from search_schema.py
│   │   ├── candidate.py         # Renamed from candidate_schema.py
│   │   └── chat.py              # Renamed from chat_schema.py
│   │
│   ├── services/                # Business logic services
│   │   ├── embeddings.py
│   │   └── candidate_indexer.py
│   │
│   ├── prompts/                 # LLM prompts
│   │   ├── intent/
│   │   ├── chat/
│   │   └── system/
│   │
│   └── evaluator/               # Metrics & evaluation
│       ├── __init__.py
│       ├── metrics.py
│       └── logger.py
│
├── api/                         # FastAPI routes (was apis/)
│   ├── __init__.py
│   ├── main.py
│   ├── deps.py
│   └── routes/
│       ├── __init__.py
│       ├── chat.py              # Renamed from chat_api.py
│       ├── search.py            # Renamed from search_api.py
│       └── health.py            # Renamed from health_api.py
│
├── frontend/                    # UI layer (was Chatbot/gen_ai/interface/)
│   └── streamlit_app.py         # Renamed from app.py
│
├── database/                    # Database layer
│   ├── __init__.py
│   ├── connection.py
│   ├── models.py                # SQLAlchemy models (if needed)
│   └── migrations/
│
├── tests/                       # Test suite (was Tests/)
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_api.py
│   └── test_search.py
│
├── docs/                        # All documentation
│   ├── API.md                   # API documentation
│   ├── FRONTEND_OPTIONS.md      # Frontend comparison
│   ├── ARCHITECTURE.md          # System architecture
│   └── DEPLOYMENT.md            # Deployment guide
│
├── scripts/                     # Utility scripts
│   ├── start_api.sh
│   ├── start_frontend.sh
│   └── seed_database.py
│
├── .env                         # Environment variables
├── .gitignore
├── docker-compose.yml           # Already in root ✅
├── pyproject.toml
├── README.md                    # Main readme
└── QUICKSTART.md                # Quick start guide

```

---

## Key Improvements 🎯

### 1. **Clearer naming**
- `Chatbot/gen_ai/` → `backend/` (describes what it is)
- `apis/` → `api/` (singular, standard convention)
- `retriever/` → `retrieval/` (clearer)
- `Tests/` → `tests/` (lowercase, Python convention)

### 2. **Less nesting**
- Removed unnecessary `gen_ai/` level
- Everything is now 1-2 levels max from root

### 3. **Better organization**
- **`backend/`** - All AI/ML logic
- **`api/`** - All HTTP endpoints
- **`frontend/`** - All UI code
- **`database/`** - All DB code
- **`tests/`** - All tests
- **`docs/`** - All documentation
- **`scripts/`** - Utility scripts

### 4. **Removed redundancy**
- `*_schema.py` → just `.py` (schemas/ folder makes it clear)
- `*_api.py` → just `.py` (routes/ folder makes it clear)
- Deleted unused `main.py`

### 5. **Standard Python conventions**
- All folders lowercase with underscores
- Clear separation of concerns
- Follows Flask/FastAPI project patterns

---

## Migration Steps

### Option A: Automated (Recommended)
I can write a script to do all the moves/renames automatically.

### Option B: Manual
I can guide you through each step with commands.

### Option C: Gradual
Move one section at a time, test, then continue.

---

## What Changes in Your Code

### Import statements will change:
```python
# OLD
from Chatbot.gen_ai.agents.chat_agent import ChatAgent
from Chatbot.gen_ai.schemas.intent_schema import Intent

# NEW
from backend.agents.chat_agent import ChatAgent
from backend.schemas.intent import Intent
```

### API startup will change:
```bash
# OLD
uvicorn apis.main:app --reload

# NEW
uvicorn api.main:app --reload
```

### Frontend startup stays similar:
```bash
# OLD
streamlit run Chatbot/gen_ai/interface/ui/app.py

# NEW
streamlit run frontend/streamlit_app.py
```

---

## Benefits of This Structure

✅ **Easier to navigate** - Clear what each folder does
✅ **Standard conventions** - Follows Python/FastAPI best practices
✅ **Easier onboarding** - New developers understand structure immediately
✅ **Better for deployment** - Clear separation of components
✅ **Scales better** - Room to add more features without confusion
✅ **Professional** - Looks like a production-ready project

---

## Questions Before We Start?

1. **Do you want me to do this reorganization?**
2. **Automated script or step-by-step manual?**
3. **Any parts you want to keep as-is?**
4. **Want to rename root folder `Candidate_DB` → `candidate_db` too?** (lowercase is more standard)
