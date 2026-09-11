"""
Scenario 1 — Legitimate Build Simulation
Verifies: Signed commit + Trusted developer + Valid dependency hashes + Clean runner
Expected Outcome: BUILD ALLOWED (Exit code 0)
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.dependency_verifier import DependencyVerifier
from backend.app.services.runner_integrity import RunnerIntegrityVerifier
from backend.app.services.policy_engine import PolicyEngine
from backend.app.schemas.validation import CommitVerificationResult


def run():
    print("==========================================================")
    print("SCENARIO 1: LEGITIMATE SECURE BUILD VERIFICATION")
    print("==========================================================")

    # 1. Simulate verified commit by authorized developer
    commit_res = CommitVerificationResult(
        commit_hash="a1b2c3d4e5f67890abcdef1234567890abcdef12",
        short_hash="a1b2c3d",
        author_name="Hari Prasath D",
        author_email="24mis0187@vitstudent.ac.in",
        committer_name="Hari Prasath D",
        committer_email="24mis0187@vitstudent.ac.in",
        commit_date="2026-09-11 12:00:00 UTC",
        commit_message="feat(auth): add zero-trust policy enforcement gate",
        signed=True,
        signature_type="SSH",
        signature_valid=True,
        trusted_developer=True,
        status="PASS",
        details="Commit a1b2c3d cryptographically verified with SSH signature."
    )
    print("[1/3] Commit Verification   : PASS (Signed & Trusted)")

    # 2. Verify clean dependencies in demo/vulnerable-project
    demo_dir = PROJECT_ROOT / "demo" / "vulnerable-project"
    dep_verifier = DependencyVerifier(project_path=demo_dir)
    dep_res = dep_verifier.verify_dependencies()
    print(f"[2/3] Dependency Integrity  : {dep_res.status} ({dep_res.verified_count} verified)")

    # 3. Verify clean runner integrity
    runner_verifier = RunnerIntegrityVerifier(project_root=PROJECT_ROOT)
    runner_res = runner_verifier.verify_runner()
    print(f"[3/3] Runner Host Integrity : {runner_res.status} (Score: {runner_res.integrity_score}/100)")

    # 4. Evaluate through Policy Engine
    engine = PolicyEngine()
    decision = engine.evaluate(commit_res, dep_res, runner_res)

    print("----------------------------------------------------------")
    print(f"FINAL DECISION: {decision.decision} (Exit Code: {0 if decision.decision == 'ALLOW' else 1})")
    print("----------------------------------------------------------")
    assert decision.decision == "ALLOW", f"Expected ALLOW but got {decision.decision}"
    print("✓ SCENARIO 1 PASSED: Legitimate build authorized under Zero-Trust rules.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
