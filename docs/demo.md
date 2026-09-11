# Demonstration Walkthrough: Attack Simulations

## Overview

This guide provides step-by-step instructions for running and verifying the **Zero-Trust CI/CD Pipeline Validator** demonstration attack suite.

> **SAFETY NOTICE:** All attack scenarios are strictly local simulations that run against isolated test fixtures. No malicious network calls, persistent system changes, or actual malware are executed.

---

## 1. Running Simulations via Web Dashboard

1. Start the server:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
   ```
2. Open your browser to `http://localhost:8000` (or `http://localhost:5173` if running Vite dev server).
3. Navigate to the **Attack Simulation Lab** tab in the sidebar.
4. Observe the 5 interactive scenario buttons:
   - **[ Run Secure Build ]** → Triggers Scenario 1 (`BUILD ALLOWED`)
   - **[ Simulate Dependency Attack ]** → Triggers Scenario 2 (`BUILD BLOCKED`)
   - **[ Simulate Invalid Commit ]** → Triggers Scenario 3 (`BUILD BLOCKED`)
   - **[ Simulate Runner Tampering ]** → Triggers Scenario 4 (`BUILD BLOCKED`)
   - **[ Reset Demo Environment ]** → Restores clean baseline
5. Watch the real-time **Visual Pipeline Graph** update its branch paths and color indicators dynamically.

---

## 2. Running Simulations via Command Line

Run individual simulation scenarios directly in the terminal:

### Scenario 1: Legitimate Build
```bash
python demo/attack-simulation/simulate_scenario1_legitimate.py
```
**Expected Output:**
```text
==========================================================
SCENARIO 1: LEGITIMATE SECURE BUILD VERIFICATION
==========================================================
[1/3] Commit Verification   : PASS (Signed & Trusted)
[2/3] Dependency Integrity  : PASS
[3/3] Runner Host Integrity : CLEAN (Score: 100/100)
----------------------------------------------------------
FINAL DECISION: ALLOW (Exit Code: 0)
----------------------------------------------------------
```

### Scenario 2: Malicious Dependency Attack
```bash
python demo/attack-simulation/simulate_scenario2_dependency_attack.py
```
**Expected Output:**
```text
==========================================================
SCENARIO 2: MALICIOUS DEPENDENCY SUPPLY-CHAIN ATTACK
==========================================================
[!] Injected tampered cryptographic signature into package-lock.json
[!] Dependency Verification Result: FAIL
    Mismatched Hashes Detected   : 1
----------------------------------------------------------
FINAL DECISION: BLOCK (Exit Code: 1)
----------------------------------------------------------
```

### Scenario 3: Forged / Unsigned Commit Attack
```bash
python demo/attack-simulation/simulate_scenario3_invalid_commit.py
```
**Expected Output:**
```text
==========================================================
SCENARIO 3: FORGED / UNSIGNED COMMIT ATTACK
==========================================================
[!] Commit Verification Result: FAIL
    Author: untrusted-attacker@darkweb-exploit.org (Trusted: False)
----------------------------------------------------------
FINAL DECISION: BLOCK (Exit Code: 1)
----------------------------------------------------------
```

### Scenario 4: Runner Host Tampering Attack
```bash
python demo/attack-simulation/simulate_scenario4_runner_tampering.py
```
**Expected Output:**
```text
==========================================================
SCENARIO 4: CI/CD RUNNER HOST TAMPERING SIMULATION
==========================================================
[!] Injected dangerous environment variable: LD_PRELOAD=/tmp/simulated_untrusted_library_shim.so
[!] Runner Integrity Audit: TAMPERED
----------------------------------------------------------
FINAL DECISION: BLOCK (Exit Code: 1)
----------------------------------------------------------
```

### Run Entire Suite Automatically
```bash
python demo/attack-simulation/run_all_simulations.py
```
Verifies that all 4 scenarios produce the exact expected Zero-Trust enforcement verdicts!
