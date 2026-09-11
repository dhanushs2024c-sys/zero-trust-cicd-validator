"""
FastAPI Application Entry Point for Zero-Trust CI/CD Pipeline Validator
Initializes routes, CORS, lifespan database checks, and static dashboard assets.
"""

from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import PROJECT_ROOT, DEFAULT_BASELINE_PATH
from backend.app.api.endpoints import router as api_router
from backend.app.api.demo_routes import demo_router
from backend.app.services.runner_integrity import RunnerIntegrityVerifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure baseline exists
    if not DEFAULT_BASELINE_PATH.exists():
        verifier = RunnerIntegrityVerifier()
        verifier.create_baseline()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title="Zero-Trust CI/CD Pipeline Validator API",
    description="Cryptographic Verification and Tamper-Proofing for Secure Build Environments",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local dev and web dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(api_router)
app.include_router(demo_router)

# Mount static frontend build if present
frontend_dist = PROJECT_ROOT / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
