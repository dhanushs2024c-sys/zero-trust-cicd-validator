"""
Scenario 4 — Runner Tampering Attack Simulation
Simulates: Environment variable hijacking (LD_PRELOAD) & runner tampering
Expected Outcome: BUILD BLOCKED (Exit code 1)
"""

import os
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
    print("SCENARIO 4: CI/CD RUNNER HOST TAMPERING SIMULATION")
    print("==========================================================")

    # 1. Inject simulated runner tampering (LD_PRELOAD dynamic linker hijack)
    os.environ["LD_PRELOAD"] = "/tmp/simulated_untrusted_library_shim.so"
    print("[!] Injected dangerous environment variable: LD_PRELOAD=/tmp/simulated_untrusted_library_shim.so")

    try:
        # 2. Simulate valid commit
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
            details="Commit cryptographically verified."
        )

        # 3. Verify dependencies
        demo_dir = PROJECT_ROOT / "demo" / "vulnerable-project"
        dep_verifier = DependencyVerifier(project_path=demo_dir)
        dep_res = dep_verifier.verify_dependencies()

        # 4. Verify runner environment (should detect LD_PRELOAD)
        runner_verifier = RunnerIntegrityVerifier(project_root=PROJECT_ROOT)
        runner_res = runner_verifier.verify_runner()
        print(f"[!] Runner Integrity Audit: {runner_res.status} (Score: {runner_res.integrity_score}/100)")
        print(f"    Flagged Environment Anomalies: {runner_res.suspicious_env_vars_count}")

        # 5. Policy evaluation
        engine = PolicyEngine()
        decision = engine.evaluate(commit_res, dep_res, runner_res)

        print("----------------------------------------------------------")
        print(f"FINAL DECISION: {decision.decision} (Exit Code: {0 if decision.decision == 'ALLOW' else 1})")
        print("----------------------------------------------------------")
        print("Reasons:")
        for r in decision.reasons:
            print(f"  ✗ {r}")

        assert decision.decision == "BLOCK", f"Expected BLOCK but got {decision.decision}"
        assert runner_res.status in ("TAMPERED", "WARNING"), f"Expected TAMPERED or WARNING but got {runner_res.status}"
        print("\n✓ SCENARIO 4 PASSED: Host environment tampering attack successfully BLOCKED!")
        return 1

    finally:
        # Clean up injected environment variable
        os.environ.pop("LD_PRELOAD", None)
        print("[✓] Cleaned up injected LD_PRELOAD variable.")


if __name__ == "__main__":
    code = run()
    sys.exit(0 if code == 1 else 2)
