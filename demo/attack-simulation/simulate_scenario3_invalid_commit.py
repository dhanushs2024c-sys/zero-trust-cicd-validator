"""
Scenario 3 — Invalid Commit Attack Simulation
Simulates: Unsigned commit or commit signed by unauthorized/unknown developer
Expected Outcome: BUILD BLOCKED (Exit code 1)
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
    print("SCENARIO 3: FORGED / UNSIGNED COMMIT ATTACK")
    print("==========================================================")

    # 1. Simulate forged commit by untrusted developer
    commit_res = CommitVerificationResult(
        commit_hash="deadbeef99887766554433221100ffeeddccbbaa",
        short_hash="deadbee",
        author_name="Attacker",
        author_email="untrusted-attacker@darkweb-exploit.org",
        committer_name="Attacker",
        committer_email="untrusted-attacker@darkweb-exploit.org",
        commit_date="2026-09-11 12:08:00 UTC",
        commit_message="backdoor: bypass pipeline controls",
        signed=False,
        signature_type="NONE",
        signature_valid=False,
        trusted_developer=False,
        status="FAIL",
        details="Commit deadbee is unsigned. Zero-Trust policy mandates cryptographic signatures from trusted developers."
    )
    print(f"[!] Commit Verification Result: {commit_res.status}")
    print(f"    Author: {commit_res.author_email} (Trusted: {commit_res.trusted_developer})")

    # 2. Dependencies check
    demo_dir = PROJECT_ROOT / "demo" / "vulnerable-project"
    dep_verifier = DependencyVerifier(project_path=demo_dir)
    dep_res = dep_verifier.verify_dependencies()

    # 3. Runner check
    runner_verifier = RunnerIntegrityVerifier(project_root=PROJECT_ROOT)
    runner_res = runner_verifier.verify_runner()

    # 4. Policy evaluation
    engine = PolicyEngine()
    decision = engine.evaluate(commit_res, dep_res, runner_res)

    print("----------------------------------------------------------")
    print(f"FINAL DECISION: {decision.decision} (Exit Code: {0 if decision.decision == 'ALLOW' else 1})")
    print("----------------------------------------------------------")
    print("Reasons:")
    for r in decision.reasons:
        print(f"  ✗ {r}")

    assert decision.decision == "BLOCK", f"Expected BLOCK but got {decision.decision}"
    assert not commit_res.trusted_developer, "Expected trusted_developer to be False"
    print("\n✓ SCENARIO 3 PASSED: Forged/unsigned commit attack successfully BLOCKED!")
    return 1


if __name__ == "__main__":
    code = run()
    sys.exit(0 if code == 1 else 2)
