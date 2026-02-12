from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apis.routes.health_api import router as health_router
from apis.routes.chat_api import router as chat_router
from apis.routes.search_api import router as search_router

app = FastAPI(
    title="Candidate DB API",
    description="AI-powered candidate search and chat interface",
    version="0.1.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(search_router)

@app.get("/")
async def root():
    return {
        "message": "Candidate DB API",
        "version": "0.1.0",
        "endpoints": [
            "/health - Health check",
            "/chat - AI chat interface with intent classification",
            "/search - Direct candidate search"
        ]
    }