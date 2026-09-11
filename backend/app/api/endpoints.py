"""
REST API Endpoints for Zero-Trust CI/CD Pipeline Validator
Serves real-time validation, security events, audit logs, configuration, and demo simulations.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body

from backend.app.config import (
    load_policy,
    load_trusted_developers,
    PROJECT_ROOT,
    DEFAULT_POLICY_PATH,
    DEFAULT_TRUSTED_DEVS_PATH,
    DEFAULT_BASELINE_PATH
)
from backend.app.schemas.validation import (
    ValidationRunRequest,
    ValidationRunResponse,
    BaselineGenerateRequest,
    BaselineGenerateResponse,
    SecurityEvent,
    CommitVerificationResult,
    DependencyVerificationResult,
    RunnerIntegrityResult
)
from backend.app.services.validator import PipelineValidator
from backend.app.services.commit_verifier import CommitVerifier
from backend.app.services.dependency_verifier import DependencyVerifier
from backend.app.services.runner_integrity import RunnerIntegrityVerifier
from backend.app.models.database import db
from backend.app.services.audit_logger import audit_logger

router = APIRouter(prefix="/api", tags=["validator"])


@router.get("/health")
def get_health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "zero-trust-cicd-validator",
        "version": "1.0.0",
        "zero_trust_mode": "FAIL_CLOSED"
    }


@router.get("/status")
def get_status():
    """Return overall validator readiness, policy, and trusted developers."""
    policy = load_policy()
    devs = load_trusted_developers()
    baseline_exists = DEFAULT_BASELINE_PATH.exists()
    return {
        "status": "READY",
        "policy": policy.model_dump(),
        "trusted_developers_count": len(devs),
        "baseline_configured": baseline_exists,
        "database_connected": True
    }


@router.post("/validate", response_model=ValidationRunResponse)
def run_validation(req: Optional[ValidationRunRequest] = None):
    """Execute complete Zero-Trust validation pipeline."""
    target_path = Path(req.target_directory) if req and req.target_directory else PROJECT_ROOT
    commit_ref = req.commit_ref if req and req.commit_ref else "HEAD"

    validator = PipelineValidator(project_root=target_path)
    res = validator.validate(commit_ref=commit_ref)
    return res


@router.get("/runs")
def list_runs(limit: int = Query(50, ge=1, le=200)):
    """List historical validation runs."""
    return db.list_runs(limit=limit)


@router.get("/runs/{run_id}")
def get_run(run_id: str):
    """Retrieve detailed validation run data."""
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return run


@router.get("/events")
def list_events(
    limit: int = Query(100, ge=1, le=500),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Retrieve append-only security audit log events."""
    return db.list_events(limit=limit, severity=severity, category=category)


@router.post("/baseline", response_model=BaselineGenerateResponse)
def generate_baseline(req: Optional[BaselineGenerateRequest] = None):
    """Generate or update runner integrity baseline hashes."""
    target_path = Path(req.target_directory) if req and req.target_directory else PROJECT_ROOT
    output_path = Path(req.output_path) if req and req.output_path else DEFAULT_BASELINE_PATH

    verifier = RunnerIntegrityVerifier(project_root=target_path, baseline_path=output_path)
    data = verifier.create_baseline(output_path=output_path)

    return BaselineGenerateResponse(
        success=True,
        generated_at=data["generated_at"],
        file_path=str(output_path),
        total_files_hashed=len(data.get("files", {})),
        files=data.get("files", {})
    )


@router.get("/dependencies", response_model=DependencyVerificationResult)
def get_dependencies(path: Optional[str] = Query(None)):
    """Run standalone dependency integrity verification."""
    target_path = Path(path) if path else PROJECT_ROOT
    verifier = DependencyVerifier(project_path=target_path)
    policy = load_policy()
    return verifier.verify_dependencies(block_unverified=policy.block_unverified_dependencies)


@router.get("/commits", response_model=CommitVerificationResult)
def get_commit_status(commit: str = Query("HEAD"), path: Optional[str] = Query(None)):
    """Run standalone commit verification."""
    target_path = Path(path) if path else PROJECT_ROOT
    verifier = CommitVerifier(repo_path=target_path)
    return verifier.verify_commit(commit_ref=commit)


@router.get("/runner", response_model=RunnerIntegrityResult)
def get_runner_status(path: Optional[str] = Query(None)):
    """Run standalone runner integrity audit."""
    target_path = Path(path) if path else PROJECT_ROOT
    verifier = RunnerIntegrityVerifier(project_root=target_path)
    return verifier.verify_runner()


@router.get("/config")
def get_config():
    """View active policy and trusted developers."""
    policy = load_policy()
    devs = load_trusted_developers()
    return {
        "policy": policy.model_dump(),
        "trusted_developers": [d.model_dump() for d in devs]
    }
