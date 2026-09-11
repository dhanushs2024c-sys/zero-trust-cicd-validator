"""
Scenario 2 — Malicious Dependency Attack Simulation
Simulates: Package substitution / checksum tampering in dependency lockfile
Expected Outcome: BUILD BLOCKED (Exit code 1)
"""

import sys
import shutil
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
    print("SCENARIO 2: MALICIOUS DEPENDENCY SUPPLY-CHAIN ATTACK")
    print("==========================================================")

    demo_dir = PROJECT_ROOT / "demo" / "vulnerable-project"
    lock_file = demo_dir / "package-lock.json"
    backup_file = demo_dir / "package-lock.json.bak"

    # 1. Back up original lockfile
    shutil.copyfile(lock_file, backup_file)

    try:
        # 2. Inject simulated tamper: mutate React integrity hash
        with open(lock_file, "r", encoding="utf-8") as f:
            content = f.read()

        tampered_content = content.replace(
            "sha512-/3IjMdb2L9QbBdWiW5e3P2/npwGJF85ozlB50TxKMA7ET1U9hMWn665P23H4YFBuTu8gxGGiSofVN5E/v1H44g==",
            "sha512-TAMPERED_MALICIOUS_SUBSTITUTION_ATTACK_HASH_abcdef1234567890abcdef1234567890=="
        )
        with open(lock_file, "w", encoding="utf-8") as f:
            f.write(tampered_content)

        print("[!] Injected tampered cryptographic signature into package-lock.json (lodash/react)")

        # 3. Simulate verified commit
        commit_res = CommitVerificationResult(
            commit_hash="b2c3d4e5f67890abcdef1234567890abcdef1234",
            short_hash="b2c3d4e",
            author_name="Dhanush",
            author_email="dhanush1108samu@gmail.com",
            committer_name="Dhanush",
            committer_email="dhanush1108samu@gmail.com",
            commit_date="2026-09-11 12:00:00 UTC",
            commit_message="chore: update npm dependencies",
            signed=True,
            signature_type="SSH",
            signature_valid=True,
            trusted_developer=True,
            status="PASS",
            details="Commit b2c3d4e cryptographically verified with SSH signature."
        )

        # 4. Verify dependencies
        dep_verifier = DependencyVerifier(project_path=demo_dir)
        dep_res = dep_verifier.verify_dependencies()
        print(f"[!] Dependency Verification Result: {dep_res.status}")
        print(f"    Mismatched Hashes Detected   : {dep_res.mismatched_count}")

        # 5. Verify runner
        runner_verifier = RunnerIntegrityVerifier(project_root=PROJECT_ROOT)
        runner_res = runner_verifier.verify_runner()

        # 6. Policy evaluation
        engine = PolicyEngine()
        decision = engine.evaluate(commit_res, dep_res, runner_res)

        print("----------------------------------------------------------")
        print(f"FINAL DECISION: {decision.decision} (Exit Code: {0 if decision.decision == 'ALLOW' else 1})")
        print("----------------------------------------------------------")
        print("Reasons:")
        for r in decision.reasons:
            print(f"  ✗ {r}")

        assert decision.decision == "BLOCK", f"Expected BLOCK but got {decision.decision}"
        assert dep_res.mismatched_count > 0, "Expected at least 1 mismatched dependency"
        print("\n✓ SCENARIO 2 PASSED: Supply-chain dependency attack successfully BLOCKED!")
        return 1

    finally:
        # Restore clean backup
        if backup_file.exists():
            shutil.copyfile(backup_file, lock_file)
            backup_file.unlink()
            print("[✓] Restored clean package-lock.json")


if __name__ == "__main__":
    code = run()
    sys.exit(0 if code == 1 else 2)
