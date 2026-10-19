import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.generate_test import router as generate_test_router
from backend.app.routes.history import router as history_router
from backend.app.routes.minimize import router as minimize_router
from backend.app.routes.reproduce import router as reproduce_router
from backend.app.security import require_api_key

app = FastAPI(
    title="ReproForge API",
    description="Python bug reproduction and test-case minimization tool",
    version="0.1.0",
)

origins = os.environ.get(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:5174"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_methods=["*"],
    allow_headers=["*"],
)

protected = [Depends(require_api_key)]
app.include_router(reproduce_router, dependencies=protected)
app.include_router(minimize_router, dependencies=protected)
app.include_router(generate_test_router, dependencies=protected)
app.include_router(history_router, dependencies=protected)


@app.get("/")
def home():
    return {
        "message": "Welcome to ReproForge!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
