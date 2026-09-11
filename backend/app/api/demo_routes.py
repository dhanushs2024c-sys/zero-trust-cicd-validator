"""
Interactive Attack Simulation API Routes
Enables one-click demonstration of legitimate builds and 3 supply-chain attack vectors.
All simulations are strictly isolated, local, and harmless.
"""

import os
import shutil
from pathlib import Path
from fastapi import APIRouter
from backend.app.config import PROJECT_ROOT
from backend.app.schemas.validation import (
    CommitVerificationResult,
    DependencyVerificationResult,
    RunnerIntegrityResult,
    PolicyDecision,
    ValidationRunResponse,
    DependencyItem,
    RunnerFileCheck,
    RunnerEnvCheck
)
from backend.app.services.audit_logger import audit_logger
from backend.app.models.database import db

demo_router = APIRouter(prefix="/api/demo", tags=["demo"])

DEMO_DIR = PROJECT_ROOT / "demo" / "vulnerable-project"


@demo_router.post("/run-legitimate", response_model=ValidationRunResponse)
def demo_legitimate_build():
    """
    Scenario 1: Legitimate Build
    Signed commit + Trusted developer + Valid dependency hashes + Clean runner = BUILD ALLOWED
    """
    run_id = f"DEMO-LEGIT-{os.urandom(3).hex().upper()}"
    timestamp = "2026-09-11T12:00:00Z"

    commit_res = CommitVerificationResult(
        commit_hash="a1b2c3d4e5f67890abcdef1234567890abcdef12",
        short_hash="a1b2c3d",
        author_name="Hari Prasath D",
        author_email="24mis0187@vitstudent.ac.in",
        committer_name="Hari Prasath D",
        committer_email="24mis0187@vitstudent.ac.in",
        commit_date="2026-09-11 11:45:00 UTC",
        commit_message="feat(auth): add cryptographic zero-trust validation gate",
        signed=True,
        signature_type="SSH",
        signature_valid=True,
        trusted_developer=True,
        signer_identity="Hari Prasath D <24mis0187@vitstudent.ac.in>",
        signer_key_id="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKeyHariPrasathZeroTrust2026",
        status="PASS",
        details="Commit a1b2c3d cryptographically verified with SSH signature by Hari Prasath D."
    )

    dep_items = [
        DependencyItem(
            name="cryptography",
            version="50.0.1",
            ecosystem="python",
            manifest_file="poetry.lock",
            expected_hash="sha256:d8a29b4e7192bc5816c87e912389104fae891234567890abcdef1234567890ab",
            actual_hash="sha256:d8a29b4e7192bc5816c87e912389104fae891234567890abcdef1234567890ab",
            algorithm="sha256",
            verification_method="lockfile_sha256",
            status="VERIFIED",
            details="Verified with locked artifact hash."
        ),
        DependencyItem(
            name="fastapi",
            version="0.141.1",
            ecosystem="python",
            manifest_file="poetry.lock",
            expected_hash="sha256:7b91c2e4f5a8901234567890abcdef1234567890abcdef1234567890abcdef12",
            actual_hash="sha256:7b91c2e4f5a8901234567890abcdef1234567890abcdef1234567890abcdef12",
            algorithm="sha256",
            verification_method="lockfile_sha256",
            status="VERIFIED",
            details="Verified with locked artifact hash."
        ),
        DependencyItem(
            name="react",
            version="18.3.1",
            ecosystem="npm",
            manifest_file="package-lock.json",
            expected_hash="sha512-c283948192384910238401923849102839102384910283901283901283901283",
            actual_hash="sha512-c283948192384910238401923849102839102384910283901283901283901283",
            algorithm="sha512",
            verification_method="lockfile_sha512",
            status="VERIFIED",
            details="Verified with npm Subresource Integrity (sha512)."
        )
    ]

    dep_res = DependencyVerificationResult(
        status="PASS",
        total_dependencies=3,
        verified_count=3,
        unverified_count=0,
        mismatched_count=0,
        missing_count=0,
        ecosystems_detected=["python", "npm"],
        items=dep_items,
        details="PASS: All 3 dependencies cryptographically verified against lockfile baselines."
    )

    runner_res = RunnerIntegrityResult(
        status="CLEAN",
        integrity_score=100,
        baseline_file_used="integrity_baseline.json",
        monitored_files_count=9,
        matched_files_count=9,
        tampered_files_count=0,
        missing_files_count=0,
        suspicious_env_vars_count=0,
        suspicious_processes_count=0,
        file_checks=[
            RunnerFileCheck(path="configs/policy.yaml", status="MATCH", actual_hash="c10fa547..."),
            RunnerFileCheck(path="configs/trusted_developers.yaml", status="MATCH", actual_hash="36777079..."),
            RunnerFileCheck(path="validator/cli.py", status="MATCH", actual_hash="3979fc93...")
        ],
        details="CLEAN: Runner integrity verified. All baseline files matched. No environment tampering detected."
    )

    policy_res = PolicyDecision(
        decision="ALLOW",
        score=98,
        reasons=["All Zero-Trust security checks passed. Build environment and code integrity verified."],
        rules_evaluated={
            "require_signed_commit": True,
            "require_trusted_developer": True,
            "block_unverified_dependencies": True,
            "block_dependency_mismatch": True,
            "require_runner_integrity": True
        }
    )

    response = ValidationRunResponse(
        run_id=run_id,
        timestamp=timestamp,
        target_directory="demo/vulnerable-project (Scenario 1: Legitimate Build)",
        commit=commit_res,
        dependencies=dep_res,
        runner=runner_res,
        policy=policy_res,
        final_decision="ALLOW",
        exit_code=0,
        execution_time_ms=42.5
    )

    db.save_run(response)
    audit_logger.log_event(
        event_name="DEMO_SCENARIO_LEGITIMATE_BUILD",
        severity="INFO",
        category="POLICY",
        message="Demo Scenario 1 Passed: BUILD ALLOWED for legitimate verified build.",
        run_id=run_id,
        action="BUILD_ALLOWED"
    )

    return response


@demo_router.post("/simulate-dependency-attack", response_model=ValidationRunResponse)
def demo_dependency_attack():
    """
    Scenario 2: Malicious Dependency Attack
    Expected hash != Detected hash (Supply-chain package substitution) = BUILD BLOCKED
    """
    run_id = f"DEMO-ATTACK-DEP-{os.urandom(3).hex().upper()}"
    timestamp = "2026-09-11T12:05:00Z"

    commit_res = CommitVerificationResult(
        commit_hash="b2c3d4e5f67890abcdef1234567890abcdef1234",
        short_hash="b2c3d4e",
        author_name="Dhanush",
        author_email="dhanush1108samu@gmail.com",
        committer_name="Dhanush",
        committer_email="dhanush1108samu@gmail.com",
        commit_date="2026-09-11 12:00:00 UTC",
        commit_message="chore: update utility dependencies",
        signed=True,
        signature_type="SSH",
        signature_valid=True,
        trusted_developer=True,
        status="PASS",
        details="Commit b2c3d4e cryptographically verified with SSH signature."
    )

    dep_items = [
        DependencyItem(
            name="malicious-crypto-helper",
            version="1.0.4",
            ecosystem="python",
            manifest_file="poetry.lock",
            expected_hash="sha256:aaa111222333444555666777888999000aaabbbcccdddeeefff0001112223334",
            actual_hash="sha256:TAMPERED_bbb222333444555666777888999000aaabbbcccdddeeefff0001112223334",
            algorithm="sha256",
            verification_method="lockfile_sha256",
            status="MISMATCH",
            details="CRITICAL: Cryptographic hash mismatch! Expected AAA111... but detected BBB222... (Supply-chain package tampering)."
        ),
        DependencyItem(
            name="cryptography",
            version="50.0.1",
            ecosystem="python",
            manifest_file="poetry.lock",
            expected_hash="sha256:d8a29b4e7192bc5816c87e912389104fae891234567890abcdef1234567890ab",
            actual_hash="sha256:d8a29b4e7192bc5816c87e912389104fae891234567890abcdef1234567890ab",
            algorithm="sha256",
            verification_method="lockfile_sha256",
            status="VERIFIED",
            details="Verified with locked artifact hash."
        )
    ]

    dep_res = DependencyVerificationResult(
        status="FAIL",
        total_dependencies=2,
        verified_count=1,
        unverified_count=0,
        mismatched_count=1,
        missing_count=0,
        ecosystems_detected=["python"],
        items=dep_items,
        details="CRITICAL: Cryptographic hash mismatch detected in dependency 'malicious-crypto-helper@1.0.4'."
    )

    runner_res = RunnerIntegrityResult(
        status="CLEAN",
        integrity_score=100,
        monitored_files_count=9,
        matched_files_count=9,
        tampered_files_count=0,
        missing_files_count=0,
        details="CLEAN: Runner baseline verified."
    )

    policy_res = PolicyDecision(
        decision="BLOCK",
        score=35,
        reasons=[
            "Dependency Integrity Failure: 1 dependency hash mismatch(es) detected.",
            "Policy Violation: block_dependency_mismatch is enforced."
        ],
        rules_evaluated={
            "require_signed_commit": True,
            "require_trusted_developer": True,
            "block_unverified_dependencies": True,
            "block_dependency_mismatch": False,
            "require_runner_integrity": True
        }
    )

    response = ValidationRunResponse(
        run_id=run_id,
        timestamp=timestamp,
        target_directory="demo/attack-simulation (Scenario 2: Malicious Dependency Attack)",
        commit=commit_res,
        dependencies=dep_res,
        runner=runner_res,
        policy=policy_res,
        final_decision="BLOCK",
        exit_code=1,
        execution_time_ms=51.2
    )

    db.save_run(response)
    audit_logger.log_event(
        event_name="DEPENDENCY_HASH_MISMATCH",
        severity="CRITICAL",
        category="DEPENDENCY",
        message="Simulated Attack Detected: Hash mismatch on malicious-crypto-helper. Expected AAA111..., actual BBB222...",
        run_id=run_id,
        details={"package": "malicious-crypto-helper", "expected": "AAA111...", "actual": "BBB222..."},
        action="BUILD_BLOCKED"
    )

    return response


@demo_router.post("/simulate-invalid-commit", response_model=ValidationRunResponse)
def demo_invalid_commit():
    """
    Scenario 3: Invalid Commit Attack
    Unsigned or forged commit by untrusted developer = BUILD BLOCKED
    """
    run_id = f"DEMO-ATTACK-COMMIT-{os.urandom(3).hex().upper()}"
    timestamp = "2026-09-11T12:10:00Z"

    commit_res = CommitVerificationResult(
        commit_hash="deadbeef99887766554433221100ffeeddccbbaa",
        short_hash="deadbee",
        author_name="Attacker / Unknown Contributor",
        author_email="untrusted-attacker@darkweb-exploit.org",
        committer_name="Attacker",
        committer_email="untrusted-attacker@darkweb-exploit.org",
        commit_date="2026-09-11 12:08:00 UTC",
        commit_message="backdoor: inject malicious pipeline script",
        signed=False,
        signature_type="NONE",
        signature_valid=False,
        trusted_developer=False,
        status="FAIL",
        details="Commit deadbee is unsigned and from untrusted identity. Zero-Trust policy mandates signed commits from trusted developers."
    )

    dep_res = DependencyVerificationResult(
        status="PASS",
        total_dependencies=2,
        verified_count=2,
        unverified_count=0,
        mismatched_count=0,
        missing_count=0,
        ecosystems_detected=["python"],
        details="PASS: All dependencies verified."
    )

    runner_res = RunnerIntegrityResult(
        status="CLEAN",
        integrity_score=100,
        monitored_files_count=9,
        matched_files_count=9,
        details="CLEAN: Runner integrity verified."
    )

    policy_res = PolicyDecision(
        decision="BLOCK",
        score=20,
        reasons=[
            "Commit Verification Failure: Commit is unsigned. Policy requires cryptographic signatures.",
            "Commit Verification Failure: Signer 'untrusted-attacker@darkweb-exploit.org' is not in authorized trusted_developers.yaml."
        ],
        rules_evaluated={
            "require_signed_commit": False,
            "require_trusted_developer": False,
            "block_unverified_dependencies": True,
            "block_dependency_mismatch": True,
            "require_runner_integrity": True
        }
    )

    response = ValidationRunResponse(
        run_id=run_id,
        timestamp=timestamp,
        target_directory="demo/attack-simulation (Scenario 3: Forged / Unsigned Commit)",
        commit=commit_res,
        dependencies=dep_res,
        runner=runner_res,
        policy=policy_res,
        final_decision="BLOCK",
        exit_code=1,
        execution_time_ms=38.4
    )

    db.save_run(response)
    audit_logger.log_event(
        event_name="COMMIT_SIGNATURE_VERIFICATION_FAILED",
        severity="CRITICAL",
        category="COMMIT",
        message="Simulated Attack Detected: Unsigned commit by untrusted developer untrusted-attacker@darkweb-exploit.org",
        run_id=run_id,
        details={"commit": "deadbee", "author": "untrusted-attacker@darkweb-exploit.org"},
        action="BUILD_BLOCKED"
    )

    return response


@demo_router.post("/simulate-runner-tampering", response_model=ValidationRunResponse)
def demo_runner_tampering():
    """
    Scenario 4: Runner Tampering Attack
    Monitored baseline file modified or suspicious env var injected = BUILD BLOCKED
    """
    run_id = f"DEMO-ATTACK-RUNNER-{os.urandom(3).hex().upper()}"
    timestamp = "2026-09-11T12:15:00Z"

    commit_res = CommitVerificationResult(
        commit_hash="c3d4e5f67890abcdef1234567890abcdef123456",
        short_hash="c3d4e5f",
        author_name="Hari Prasath D",
        author_email="24mis0187@vitstudent.ac.in",
        committer_name="Hari Prasath D",
        committer_email="24mis0187@vitstudent.ac.in",
        commit_date="2026-09-11 12:12:00 UTC",
        commit_message="ci: update build parameters",
        signed=True,
        signature_type="SSH",
        signature_valid=True,
        trusted_developer=True,
        status="PASS",
        details="Commit c3d4e5f cryptographically verified."
    )

    dep_res = DependencyVerificationResult(
        status="PASS",
        total_dependencies=2,
        verified_count=2,
        ecosystems_detected=["python"],
        details="PASS: All dependencies verified."
    )

    runner_res = RunnerIntegrityResult(
        status="TAMPERED",
        integrity_score=15,
        baseline_file_used="integrity_baseline.json",
        monitored_files_count=9,
        matched_files_count=7,
        tampered_files_count=2,
        missing_files_count=0,
        suspicious_env_vars_count=1,
        suspicious_processes_count=0,
        file_checks=[
            RunnerFileCheck(
                path="configs/policy.yaml",
                expected_hash="c10fa547e4829067890abcdef...",
                actual_hash="TAMPERED_000111222333444555...",
                status="MODIFIED"
            ),
            RunnerFileCheck(
                path="validator/cli.py",
                expected_hash="3979fc9382510e9234567890...",
                actual_hash="TAMPERED_999888777666555444...",
                status="MODIFIED"
            )
        ],
        env_checks=[
            RunnerEnvCheck(
                variable="LD_PRELOAD",
                value="/tmp/attacker_hook.so",
                severity="CRITICAL",
                reason="Dynamic linker hijacking - can intercept and modify arbitrary syscalls and library calls."
            )
        ],
        details="TAMPERED: Runner integrity failure detected! 2 modified baseline file(s), 1 critical environment anomaly (LD_PRELOAD injection)."
    )

    policy_res = PolicyDecision(
        decision="BLOCK",
        score=25,
        reasons=[
            "Runner Integrity Failure: Environment status is 'TAMPERED'. Policy requires CLEAN runner.",
            "Cryptographic baseline mismatch: configs/policy.yaml has been modified.",
            "Critical environment injection: LD_PRELOAD detected."
        ],
        rules_evaluated={
            "require_signed_commit": True,
            "require_trusted_developer": True,
            "block_unverified_dependencies": True,
            "block_dependency_mismatch": True,
            "require_runner_integrity": False
        }
    )

    response = ValidationRunResponse(
        run_id=run_id,
        timestamp=timestamp,
        target_directory="demo/attack-simulation (Scenario 4: Runner Host Tampering)",
        commit=commit_res,
        dependencies=dep_res,
        runner=runner_res,
        policy=policy_res,
        final_decision="BLOCK",
        exit_code=1,
        execution_time_ms=44.1
    )

    db.save_run(response)
    audit_logger.log_event(
        event_name="RUNNER_TAMPERING_DETECTED",
        severity="CRITICAL",
        category="RUNNER",
        message="Simulated Attack Detected: Baseline file modification and LD_PRELOAD injection.",
        run_id=run_id,
        details={"tampered_files": ["configs/policy.yaml", "validator/cli.py"], "injected_var": "LD_PRELOAD"},
        action="BUILD_BLOCKED"
    )

    return response


@demo_router.post("/reset")
def demo_reset():
    """
    Scenario 5: Reset Demo Environment
    Restores clean baseline hashes and clears temporary simulation artifacts.
    """
    from backend.app.services.runner_integrity import RunnerIntegrityVerifier
    verifier = RunnerIntegrityVerifier()
    verifier.create_baseline()

    audit_logger.log_event(
        event_name="DEMO_ENVIRONMENT_RESET",
        severity="INFO",
        category="SYSTEM",
        message="Demo simulation environment reset to clean baseline.",
        action="MONITOR_LOGGED"
    )

    return {
        "status": "RESET_COMPLETED",
        "message": "Demo environment successfully restored to clean baseline state."
    }
