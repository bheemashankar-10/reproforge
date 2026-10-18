
from fastapi import FastAPI
from backend.app.routes.reproduce import router as reproduce_router
from backend.app.routes.minimize import router as minimize_router
from backend.app.routes.generate_test import router as generate_test_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ReproForge API",
    description="Python bug reproduction and test-case minimization tool",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(reproduce_router)
app.include_router(minimize_router)
app.include_router(generate_test_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to ReproForge!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
