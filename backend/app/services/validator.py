"""
Master Orchestration Engine for Zero-Trust CI/CD Pipeline Validator
Coordinates commit verification, dependency verification, runner integrity audit,
policy evaluation, database persistence, and audit logging.
"""

import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

from backend.app.config import PROJECT_ROOT, DEFAULT_POLICY_PATH, DEFAULT_TRUSTED_DEVS_PATH, DEFAULT_BASELINE_PATH
from backend.app.schemas.validation import ValidationRunResponse, ValidationRunRequest
from backend.app.services.commit_verifier import CommitVerifier
from backend.app.services.dependency_verifier import DependencyVerifier
from backend.app.services.runner_integrity import RunnerIntegrityVerifier
from backend.app.services.policy_engine import PolicyEngine
from backend.app.models.database import db
from backend.app.services.audit_logger import audit_logger


class PipelineValidator:
    def __init__(
        self,
        project_root: Optional[Path] = None,
        policy_path: Optional[Path] = None,
        trusted_devs_path: Optional[Path] = None,
        baseline_path: Optional[Path] = None
    ):
        self.project_root = Path(project_root) if project_root else PROJECT_ROOT
        self.policy_path = Path(policy_path) if policy_path else DEFAULT_POLICY_PATH
        self.trusted_devs_path = Path(trusted_devs_path) if trusted_devs_path else DEFAULT_TRUSTED_DEVS_PATH
        self.baseline_path = Path(baseline_path) if baseline_path else DEFAULT_BASELINE_PATH

        self.commit_verifier = CommitVerifier(repo_path=self.project_root, trusted_devs_path=self.trusted_devs_path)
        self.dependency_verifier = DependencyVerifier(project_path=self.project_root)
        self.runner_verifier = RunnerIntegrityVerifier(project_root=self.project_root, baseline_path=self.baseline_path)
        self.policy_engine = PolicyEngine()

    def validate(
        self,
        commit_ref: str = "HEAD",
        fail_closed: Optional[bool] = None
    ) -> ValidationRunResponse:
        """
        Execute complete Zero-Trust validation pipeline:
        1. Commit Signature Verification
        2. Dependency Integrity Verification
        3. Runner Environment Integrity Verification
        4. Policy Engine Evaluation
        5. Database Storage & Structured Audit Trail
        """
        start_time = time.perf_counter()
        run_id = f"RUN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        # 1. Commit Verification
        commit_res = self.commit_verifier.verify_commit(commit_ref=commit_ref)

        # 2. Dependency Verification
        dep_res = self.dependency_verifier.verify_dependencies(
            block_unverified=self.policy_engine.policy.block_unverified_dependencies
        )

        # 3. Runner Integrity Verification
        runner_res = self.runner_verifier.verify_runner(
            check_env=self.policy_engine.policy.check_environment_variables,
            check_procs=self.policy_engine.policy.check_processes,
            check_path=self.policy_engine.policy.check_path_anomalies
        )

        # 4. Policy Engine Decision
        policy_decision = self.policy_engine.evaluate(
            commit_res=commit_res,
            dep_res=dep_res,
            runner_res=runner_res
        )

        final_decision = policy_decision.decision
        exit_code = 0 if final_decision == "ALLOW" else 1
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response = ValidationRunResponse(
            run_id=run_id,
            timestamp=timestamp,
            target_directory=str(self.project_root),
            commit=commit_res,
            dependencies=dep_res,
            runner=runner_res,
            policy=policy_decision,
            final_decision=final_decision,
            exit_code=exit_code,
            execution_time_ms=elapsed_ms
        )

        # 5. Persist run to SQLite database
        try:
            db.save_run(response)
        except Exception as e:
            audit_logger.log_event(
                event_name="DATABASE_RUN_SAVE_ERROR",
                severity="HIGH",
                category="SYSTEM",
                message=f"Failed to save run to database: {str(e)}",
                run_id=run_id
            )

        return response
