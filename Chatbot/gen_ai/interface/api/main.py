# Minimal for now
from fastapi import FastAPI
from api.routes.health import router as health_router
from api.routes.retrieval import router as retrieval_router

app = FastAPI(
    title="Candidate DB API",
    version="0.1"
)

app.include_router(health_router)
app.include_router(retrieval_router)