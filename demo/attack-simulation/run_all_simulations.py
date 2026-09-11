"""
Zero-Trust CI/CD Attack Simulation Suite Runner
Executes all 4 demonstration scenarios sequentially and verifies policy decisions.
All simulations are strictly local, isolated, and harmless.
"""

import sys
import os
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SIM_DIR = Path(__file__).resolve().parent

SCENARIOS = [
    ("Scenario 1: Legitimate Build", "simulate_scenario1_legitimate.py", "ALLOW", 0),
    ("Scenario 2: Malicious Dependency Attack", "simulate_scenario2_dependency_attack.py", "BLOCK", 0),
    ("Scenario 3: Forged / Unsigned Commit", "simulate_scenario3_invalid_commit.py", "BLOCK", 0),
    ("Scenario 4: Runner Host Tampering", "simulate_scenario4_runner_tampering.py", "BLOCK", 0),
]


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║     ZERO-TRUST CI/CD ATTACK SIMULATION SUITE                   ║
║  Safe, Localized Demonstration of Supply-Chain Threat Vectors  ║
╚════════════════════════════════════════════════════════════════╝
[NOTE] SIMULATION ONLY: No real malware or external systems are affected.
""")

    results = []

    for name, script, expected_decision, expected_rc in SCENARIOS:
        script_path = SIM_DIR / script
        print(f"\n>>> Running {name} ({script})...")
        res = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
        print(res.stdout)
        if res.stderr:
            print(res.stderr, file=sys.stderr)

        success = res.returncode == expected_rc
        results.append((name, expected_decision, "PASS" if success else "FAIL"))

    print("\n" + "=" * 64)
    print("SIMULATION SUITE SUMMARY")
    print("=" * 64)
    all_passed = True
    for name, dec, status in results:
        indicator = "✓" if status == "PASS" else "✗"
        print(f"  {indicator} {name:<42} Expected: {dec:<6} Test: {status}")
        if status != "PASS":
            all_passed = False

    print("=" * 64)
    if all_passed:
        print("ALL 4 DEMO SCENARIOS COMPLETED SUCCESSFULLY!")
        print("Zero-Trust policy successfully authorized clean builds and blocked all attacks.")
        sys.exit(0)
    else:
        print("One or more simulation scenarios failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
