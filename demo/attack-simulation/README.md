# Safe Attack Simulation Suite

## Overview
This directory contains safe, isolated simulation scripts demonstrating the **Zero-Trust CI/CD Pipeline Validator** blocking real-world software supply chain and host tampering threats.

> **SAFETY NOTICE & DISCLAIMER**
> **SIMULATION ONLY:** No real malware, destructive payloads, network exploits, or persistent modifications are used.
> All scenarios execute strictly inside temporary, isolated test directories or variables and cleanly restore original state upon completion.

---

## Demonstrated Scenarios

### Scenario 1 — Legitimate Secure Build
- **Trigger**: Cryptographically signed Git commit (`ssh-ed25519` key registered in `configs/trusted_developers.yaml`), all Python & Node.js lockfile hashes matching declared baselines, and clean runner environment.
- **Enforcement**:
  - Commit verification: `PASS`
  - Dependency integrity: `PASS`
  - Runner integrity: `CLEAN`
  - Security score: `98-100/100`
- **Verdict**: `BUILD ALLOWED` (Exit code: `0`)
- **Execution**:
  ```bash
  python demo/attack-simulation/simulate_scenario1_legitimate.py
  ```

---

### Scenario 2 — Malicious Dependency Attack (Supply Chain Poisoning)
- **Vector**: An attacker modifies an upstream package or lockfile hash in `package-lock.json` or `poetry.lock`, attempting to substitute a legitimate library with a tampered artifact.
- **Enforcement**:
  - SHA-512 / SHA-256 integrity verification detects hash divergence:
    `Expected: sha512-/3IjMdb2L9... | Actual: sha512-TAMPERED_MALICIOUS_SUBSTITUTION...`
  - Zero-Trust policy: `block_dependency_mismatch = true`
- **Verdict**: `BUILD BLOCKED` (Exit code: `1`)
- **Execution**:
  ```bash
  python demo/attack-simulation/simulate_scenario2_dependency_attack.py
  ```

---

### Scenario 3 — Forged / Unsigned Commit Attack
- **Vector**: A malicious actor attempts to trigger a CI/CD build using an unsigned Git commit or a commit signed by an unauthorized identity (`untrusted-attacker@darkweb-exploit.org`).
- **Enforcement**:
  - Commit verification detects missing cryptographic signature and untrusted identity.
  - Zero-Trust policy: `require_signed_commit = true`, `require_trusted_developer = true`
- **Verdict**: `BUILD BLOCKED` (Exit code: `1`)
- **Execution**:
  ```bash
  python demo/attack-simulation/simulate_scenario3_invalid_commit.py
  ```

---

### Scenario 4 — Runner Host Tampering Attack
- **Vector**: A compromised CI build agent where an attacker has modified configuration files (`configs/policy.yaml`) or injected dynamic linker hijacking hooks (`LD_PRELOAD=/tmp/attacker_hook.so`).
- **Enforcement**:
  - Cryptographic baseline hash comparison detects altered files.
  - Environment variable auditor flags critical injection vectors (`LD_PRELOAD`, `DYLD_INSERT_LIBRARIES`).
  - Runner status: `TAMPERED`
  - Zero-Trust policy: `require_runner_integrity = true`
- **Verdict**: `BUILD BLOCKED` (Exit code: `1`)
- **Execution**:
  ```bash
  python demo/attack-simulation/simulate_scenario4_runner_tampering.py
  ```

---

## Running the Complete Demonstration Suite

Run all 4 scenarios with automated verification in a single command:

```bash
python demo/attack-simulation/run_all_simulations.py
```
