"""
Pydantic Schemas for Zero-Trust CI/CD Pipeline Validator
Defines strictly-typed data models for API requests, responses, and audit records.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CommitVerificationResult(BaseModel):
    commit_hash: str
    short_hash: str
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str
    commit_date: str
    commit_message: str
    signed: bool
    signature_type: str = "NONE"  # 'GPG', 'SSH', 'NONE'
    signature_valid: bool = False
    trusted_developer: bool = False
    signer_identity: Optional[str] = None
    signer_key_id: Optional[str] = None
    status: str = "FAIL"  # 'PASS', 'FAIL', 'WARNING'
    details: str = ""


class DependencyItem(BaseModel):
    name: str
    version: Optional[str] = None
    ecosystem: str  # 'python' or 'npm'
    manifest_file: str
    expected_hash: Optional[str] = None
    actual_hash: Optional[str] = None
    algorithm: Optional[str] = "sha256"
    verification_method: str  # 'lockfile_sha256', 'lockfile_sha512', 'direct_hash', 'manifest_unverified'
    status: str  # 'VERIFIED', 'UNVERIFIED', 'MISMATCH', 'MISSING', 'ERROR'
    details: Optional[str] = None


class DependencyVerificationResult(BaseModel):
    status: str = "FAIL"  # 'PASS', 'FAIL', 'WARNING'
    total_dependencies: int = 0
    verified_count: int = 0
    unverified_count: int = 0
    mismatched_count: int = 0
    missing_count: int = 0
    ecosystems_detected: List[str] = Field(default_factory=list)
    items: List[DependencyItem] = Field(default_factory=list)
    details: str = ""


class RunnerFileCheck(BaseModel):
    path: str
    expected_hash: Optional[str] = None
    actual_hash: Optional[str] = None
    status: str  # 'MATCH', 'MODIFIED', 'DELETED', 'NEW'


class RunnerEnvCheck(BaseModel):
    variable: str
    value: str
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    reason: str


class RunnerProcessCheck(BaseModel):
    pid: int
    name: str
    cmdline: str
    status: str  # 'SUSPICIOUS', 'NORMAL'
    reason: Optional[str] = None


class RunnerIntegrityResult(BaseModel):
    status: str = "TAMPERED"  # 'CLEAN', 'WARNING', 'TAMPERED'
    integrity_score: int = 0  # 0 to 100
    baseline_file_used: Optional[str] = None
    monitored_files_count: int = 0
    matched_files_count: int = 0
    tampered_files_count: int = 0
    missing_files_count: int = 0
    suspicious_env_vars_count: int = 0
    suspicious_processes_count: int = 0
    file_checks: List[RunnerFileCheck] = Field(default_factory=list)
    env_checks: List[RunnerEnvCheck] = Field(default_factory=list)
    process_checks: List[RunnerProcessCheck] = Field(default_factory=list)
    disclaimer: str = (
        "Runner integrity checks provide evidence of tampering within the configured "
        "detection scope; they cannot mathematically prove that the entire host is uncompromised."
    )
    details: str = ""


class PolicyDecision(BaseModel):
    decision: str = "BLOCK"  # 'ALLOW', 'BLOCK', 'WARNING'
    score: int = 0  # Security score 0-100
    reasons: List[str] = Field(default_factory=list)
    rules_evaluated: Dict[str, bool] = Field(default_factory=dict)


class SecurityEvent(BaseModel):
    id: Optional[str] = None
    run_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    severity: str = "INFO"  # 'INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    category: str = "SYSTEM"  # 'COMMIT', 'DEPENDENCY', 'RUNNER', 'POLICY', 'SYSTEM'
    event: str
    source: str = "zt-validator"
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    action: str = "MONITOR_LOGGED"  # 'BUILD_ALLOWED', 'BUILD_BLOCKED', 'MONITOR_LOGGED'


class ValidationRunRequest(BaseModel):
    target_directory: Optional[str] = None
    commit_ref: Optional[str] = "HEAD"
    policy_path: Optional[str] = None
    fail_closed: Optional[bool] = None


class ValidationRunResponse(BaseModel):
    run_id: str
    timestamp: str
    target_directory: str
    commit: CommitVerificationResult
    dependencies: DependencyVerificationResult
    runner: RunnerIntegrityResult
    policy: PolicyDecision
    final_decision: str  # 'ALLOW' or 'BLOCK'
    exit_code: int  # 0 for ALLOW, 1 for BLOCK
    execution_time_ms: float


class BaselineGenerateRequest(BaseModel):
    target_directory: Optional[str] = None
    output_path: Optional[str] = None
    additional_paths: List[str] = Field(default_factory=list)


class BaselineGenerateResponse(BaseModel):
    success: bool
    generated_at: str
    file_path: str
    total_files_hashed: int
    files: Dict[str, str]
