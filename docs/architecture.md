# Architecture Documentation: Zero-Trust CI/CD Pipeline Validator

## 1. Executive Summary

The **Zero-Trust CI/CD Pipeline Validator** provides a lightweight, cryptographic security validation gate that executes **before** a CI/CD build starts. Operating under the fundamental Zero-Trust paradigm:

> **"Never trust the commit, dependency, or runner environment automatically. Verify everything before allowing the build. Fail closed by default."**

If any required security check fails or cannot be verified, the validator returns a non-zero exit code (`1`), immediately terminating the pipeline before untrusted code or tampered dependencies can execute in the build runner.

---

## 2. High-Level System Architecture

```text
                                Developer Commit / CI Event
                                              │
                                              ▼
                        ┌───────────────────────────────────────────┐
                        │      zt-validator (CLI / API Agent)       │
                        └─────────────────────┬─────────────────────┘
                                              │
                   ┌──────────────────────────┼──────────────────────────┐
                   ▼                          ▼                          ▼
       ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
       │ 1. Commit Verifier    │  │ 2. Dep Verifier       │  │ 3. Runner Integrity   │
       ├───────────────────────┤  ├───────────────────────┤  ├───────────────────────┤
       │ • Extract commit sig  │  │ • Parse manifests     │  │ • Baseline hash check │
       │ • OpenSSH / OpenPGP   │  │ • Python lock / reqs  │  │ • Sensitive dir audit │
       │ • Match against       │  │ • Node package-lock   │  │ • Suspicious env vars │
       │   trusted_devs.yaml   │  │ • Hash comparison     │  │ • Process telemetry   │
       └───────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘
                   │                          │                          │
                   └──────────────────────────┼──────────────────────────┘
                                              │
                                              ▼
                                 ┌─────────────────────────┐
                                 │      Policy Engine      │
                                 ├─────────────────────────┤
                                 │ • Evaluate rules        │
                                 │ • Fail-closed logic     │
                                 │ • Security score (0-100)│
                                 └────────────┬────────────┘
                                              │
                         ┌────────────────────┴────────────────────┐
                         │                                         │
                    PASS │                                    FAIL │
                         ▼                                         ▼
            ┌─────────────────────────┐               ┌─────────────────────────┐
            │   BUILD ALLOWED (0)     │               │    BUILD BLOCKED (1)    │
            │  Pipeline continues     │               │  Pipeline halts aborts  │
            └─────────────────────────┘               └─────────────────────────┘
                         │                                         │
                         └────────────────────┬────────────────────┘
                                              ▼
                                 ┌─────────────────────────┐
                                 │ Audit Logger & Database │
                                 │ (SQLite & JSONL Ledger) │
                                 └────────────┬────────────┘
                                              │
                                              ▼
                                 ┌─────────────────────────┐
                                 │ React SOC Dashboard UI  │
                                 │ (Real-time DevSecOps)   │
                                 └─────────────────────────┘
```

---

## 3. Core Subsystems

### A. Commit Verification Engine (`backend/app/services/commit_verifier.py`)
- **Inspection**: Extracts raw commit headers using Git CLI (`git cat-file -p <ref>`).
- **Signature Parsing**: Detects presence of `BEGIN SSH SIGNATURE` or `BEGIN PGP SIGNATURE`. Unsigned commits are immediately flagged.
- **Cryptographic Verification**:
  - Uses `git -c gpg.ssh.allowedSignersFile=<path> log -1 --format=%G?` to cryptographically verify SSH signatures.
  - Verifies GPG signatures via `git verify-commit` or OpenPGP packet inspection.
- **Identity Matching**: Compares signing key ID, public key, and email against whitelist in `configs/trusted_developers.yaml`. Hardcoded keys are prohibited.
- **Statuses**: `PASS` (valid signature & trusted), `FAIL` (unsigned, invalid, or untrusted).

### B. Dependency Integrity Engine (`backend/app/services/dependency_verifier.py`)
- **Multi-Ecosystem Detection**: Auto-detects Python (`requirements.txt`, `poetry.lock`, `pyproject.toml`) and Node.js (`package.json`, `package-lock.json`).
- **Cryptographic Lockfile Verification**:
  - Python: Parses `--hash=sha256:<hex>` from requirements and locked wheel/tarball hashes from `poetry.lock`.
  - Node.js: Validates Subresource Integrity hashes (`sha512-...` / `sha256-...`) across `packages` and `dependencies` trees.
- **Granular Classification**:
  - `VERIFIED`: Pinned with cryptographic hash in lockfile.
  - `UNVERIFIED`: Declared without locked hash (e.g. unpinned `requirements.txt`).
  - `MISMATCH`: Actual checksum diverges from locked baseline (detected tampering).
  - `MISSING`: Expected package or lockfile not found.
  - `ERROR`: Parsing/syntax error.
- **Zero-Trust Rule**: Never silently marks an unverified package as verified.

### C. CI/CD Runner Integrity Engine (`backend/app/services/runner_integrity.py`)
- **Cryptographic Baseline**: Hashing critical runner scripts, configs, and binaries using SHA-256 (`configs/integrity_baseline.json`).
- **File Diffing**: Compares current runtime hashes against baseline (detects `MODIFIED`, `DELETED`, `NEW`).
- **Environment Hijacking Audit**: Detects dangerous variables often used in CI/CD pipeline poisoning:
  - `LD_PRELOAD`, `LD_LIBRARY_PATH` (dynamic linker hijacking)
  - `DYLD_INSERT_LIBRARIES`, `DYLD_LIBRARY_PATH` (macOS injection)
  - `PYTHONPATH` tampering (arbitrary module injection)
  - `NODE_OPTIONS` (malicious startup hooks)
- **PATH Anomaly Scanning**: Detects world-writable or temporary directories prepended to system `PATH`.
- **Process Telemetry**: Scans active processes using `psutil` for unauthorized sniffers or debuggers.
- **Technical Accuracy Disclaimer**:
  > *"Runner integrity checks provide evidence of tampering within the configured detection scope; they cannot mathematically prove that the entire host is uncompromised."*

### D. Zero-Trust Policy Engine (`backend/app/services/policy_engine.py`)
- **Declarative Configuration**: Evaluates all results against `configs/policy.yaml`.
- **Enforcement Rules**:
  - `require_signed_commit`
  - `require_trusted_developer`
  - `block_unverified_dependencies`
  - `block_dependency_mismatch`
  - `require_runner_integrity`
  - `fail_closed`
- **Security Score (0-100)**: Reflects policy compliance level across commit (35 pts), dependencies (35 pts), and runner (30 pts).
- **Verdict**: `ALLOW` or `BLOCK`.

### E. Append-Only Audit Logger (`backend/app/services/audit_logger.py`)
- Writes immutable structured audit events to SQLite database (`security_events` table) and appends to `logs/audit.jsonl`.
- Records run ID, timestamp, severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`), category, message, details, and pipeline action (`BUILD_ALLOWED`, `BUILD_BLOCKED`).
- Read-only from the application perspective.

### F. SOC Dashboard UI (`frontend/`)
- Built with React, TypeScript, Vite, and Tailwind CSS.
- Features executive build banner, 4 pillar cards, interactive visual pipeline, validation history, commit inspector, dependency table, runner telemetry, security audit log, and attack simulation lab.
