# Zero-Trust CI/CD Pipeline Validator
### Cryptographic Verification and Tamper-Proofing for Secure Build Environments

[![Zero-Trust Security Gate](https://img.shields.io/badge/Security-Zero--Trust%20Fail--Closed-red.svg)](#)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](#)
[![React Dashboard](https://img.shields.io/badge/Dashboard-React%20%7C%20TypeScript%20%7C%20Tailwind-cyan.svg)](#)
[![Tests](https://img.shields.io/badge/Tests-26%20Passed-brightgreen.svg)](#)

---

## Team Members
- **HARI PRASATH D [24MIS0187]** - DevSecOps Lead & Architecture
- **DHANUSH [24MIS0253]** - Security Architect & Verification Engines

---

## 1. Problem Statement

Modern software engineering depends heavily on automated CI/CD pipelines (such as GitHub Actions, Jenkins, and GitLab CI). However, the standard build environment implicitly trusts:
1. **The Commit**: Assuming that any code pushed to a branch or pull request is authored by a legitimate developer.
2. **The Dependencies**: Assuming that packages downloaded from registries (PyPI, npm) match what developers tested and intended.
3. **The Runner Environment**: Assuming that the build agent, container, or virtual machine has not been tampered with, backdoored, or injected with malicious environment variables.

Software supply-chain attacks (such as SolarWinds, Codecov, and 3CX) demonstrate that attackers actively target the build pipeline itself to inject backdoors into trusted release binaries.

---

## 2. Motivation & Core Security Principle

Traditional security scanners run *during* or *after* compilation, which is already too late if the runner itself or its build script has been hijacked.

The **Zero-Trust CI/CD Pipeline Validator** introduces an immutable cryptographic validation gate that executes **BEFORE** any build commands run:

```text
Developer Commit
      │
      ▼
Commit Verification ────────── FAIL ──────────> BLOCK BUILD (Exit 1)
      │
      ▼
Dependency Verification ────── FAIL ──────────> BLOCK BUILD (Exit 1)
      │
      ▼
Runner Integrity Audit ─────── FAIL ──────────> BLOCK BUILD (Exit 1)
      │
      ▼
Policy Engine ──────────────── FAIL ──────────> BLOCK BUILD (Exit 1)
      │
     PASS
      │
      ▼
ALLOW BUILD (Exit 0)
```

### Core Principle
> **"Never trust the commit, dependency, or runner environment automatically. Verify everything before allowing the build. Fail closed by default."**

---

## 3. Project Objectives

- **Cryptographic Commit Verification**: Ensure every commit is cryptographically signed (SSH or GPG) and verified against authorized identities in `configs/trusted_developers.yaml`.
- **Dependency Integrity Verification**: Verify SHA-256 and SHA-512 cryptographic hashes across Python (`requirements.txt`, `poetry.lock`) and Node.js (`package-lock.json`), preventing package substitution and tampering.
- **CI/CD Runner Host Integrity**: Maintain a cryptographic baseline hash of critical configs, scripts, and validator binaries (`configs/integrity_baseline.json`), and inspect runner environment variables (detecting `LD_PRELOAD`, `DYLD_INSERT_LIBRARIES`, `PYTHONPATH` hijacking).
- **Zero-Trust Policy Engine**: Declaratively enforce fail-closed security rules via `configs/policy.yaml`.
- **Real-Time SOC Dashboard**: Provide security teams and developers with visibility into pipeline stage gates, visual verification graphs, and append-only audit event ledgers.
- **Fail-Closed CI Integration**: Standardized exit codes (`0` = PASS, `1` = BLOCK, `2` = Config error, `3` = Internal error) that stop GitHub Actions and Jenkins pipelines on violation.

---

## 4. Key Features

- **Commit Verification Module**:
  - Validates SSH commit signatures (OpenSSH RFC 8332 / sshsig format with dynamic `allowed_signers`).
  - Validates GPG commit signatures with OpenPGP verification.
  - Verifies signing key against `configs/trusted_developers.yaml`.
- **Dependency Verification Module**:
  - Parses `--hash=sha256:...` in Python `requirements.txt`.
  - Parses locked package integrity hashes in `poetry.lock`.
  - Parses npm Subresource Integrity (`sha512-...` / `sha256-...`) in `package-lock.json`.
  - Distinguishes statuses: `VERIFIED`, `UNVERIFIED`, `MISMATCH`, `MISSING`, `ERROR`.
- **Runner Integrity Module**:
  - Generates and verifies cryptographic SHA-256 baseline hashes.
  - Audits dangerous environment variables (`LD_PRELOAD`, `DYLD_INSERT_LIBRARIES`, `NODE_OPTIONS`, `PYTHONPATH`).
  - Scans active processes with `psutil` for unauthorized diagnostic or packet sniffing tools.
  - Implements mandatory technical scope disclaimer.
- **Append-Only Security Audit Trail**:
  - Structured audit events saved to SQLite and immutable `logs/audit.jsonl`.
  - Non-modifiable historical records.
- **Interactive SOC Dashboard**:
  - Visual Pipeline Execution Graph with real-time pass/blocked branch rendering.
  - 5-scenario Attack Simulation Lab.
  - Historical run inspector and JSON diff modal.

---

## 5. Technology Stack

- **Backend**: Python 3.11+
  - `FastAPI`, `Uvicorn`, `Pydantic v2`, `Cryptography`, `GitPython`, `PyYAML`, `psutil`, `pytest`, `httpx`, `Typer`, `Rich`
- **Frontend**:
  - React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **Database**:
  - SQLite (with direct upgrade path to PostgreSQL)
- **CI/CD Integrations**:
  - GitHub Actions Composite Action (`integrations/github/action.yml`)
  - Jenkins Declarative Pipeline (`integrations/jenkins/Jenkinsfile`)
- **Containerization**:
  - Multi-stage Dockerfile and Docker Compose

---

## 6. Project Structure

```text
zero-trust-cicd-validator/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application & static asset serving
│   │   ├── config.py                   # Pydantic configuration & YAML loaders
│   │   ├── models/
│   │   │   └── database.py             # SQLite database layer & audit storage
│   │   ├── schemas/
│   │   │   └── validation.py           # Pydantic schemas for requests/responses
│   │   ├── services/
│   │   │   ├── commit_verifier.py      # Git SSH & GPG signature verification
│   │   │   ├── dependency_verifier.py  # Python & Node.js lockfile hash auditor
│   │   │   ├── runner_integrity.py     # Baseline hashing & environment audit
│   │   │   ├── policy_engine.py        # Fail-closed Zero-Trust policy evaluator
│   │   │   ├── audit_logger.py         # Append-only structured JSONL logger
│   │   │   └── validator.py            # Master pipeline orchestrator
│   │   └── api/
│   │       ├── endpoints.py            # REST API endpoints
│   │       └── demo_routes.py          # Attack simulation endpoints
│   ├── tests/                          # 26 automated unit & integration tests
│   └── requirements.txt                # Production backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.tsx             # SOC navigation sidebar
│   │   │   ├── Header.tsx              # Telemetry top bar
│   │   │   └── VisualPipeline.tsx      # Interactive stage-gate diagram
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx       # Executive overview & status cards
│   │   │   ├── ValidationRunsPage.tsx  # Historical runs table & inspector
│   │   │   ├── CommitVerifierPage.tsx  # Deep commit inspection
│   │   │   ├── DependencyInspectorPage.tsx # Python & Node package tables
│   │   │   ├── RunnerIntegrityPage.tsx # Host baseline diffs & env audit
│   │   │   ├── SecurityEventsPage.tsx  # Append-only audit trail
│   │   │   ├── PolicyConfigPage.tsx    # Policy rules & developer whitelist
│   │   │   └── DemoLabPage.tsx         # Interactive 5-scenario attack lab
│   │   ├── services/
│   │   │   └── api.ts                  # REST API client
│   │   ├── types/                      # TypeScript definitions
│   │   ├── App.tsx                     # Main layout & router
│   │   └── main.tsx                    # React entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── validator/
│   └── cli.py                          # Standalone CLI tool (`zt-validator`)
│
├── configs/
│   ├── policy.yaml                     # Zero-Trust policy rules
│   ├── trusted_developers.yaml         # Authorized developer key whitelist
│   └── integrity_baseline.json         # Cryptographic baseline hashes
│
├── demo/
│   ├── vulnerable-project/             # Real demo project (Python & npm)
│   └── attack-simulation/              # 4 safe, local attack scenarios
│       ├── simulate_scenario1_legitimate.py
│       ├── simulate_scenario2_dependency_attack.py
│       ├── simulate_scenario3_invalid_commit.py
│       ├── simulate_scenario4_runner_tampering.py
│       └── run_all_simulations.py      # Master simulation runner
│
├── integrations/
│   ├── github/
│   │   ├── action.yml                  # Composite GitHub Action
│   │   └── workflow-example.yml        # Sample workflow
│   └── jenkins/
│       └── Jenkinsfile                 # Jenkins declarative pipeline
│
├── docs/
│   ├── architecture.md                 # Detailed architecture & data flows
│   ├── threat-model.md                 # STRIDE threat analysis matrix
│   ├── installation.md                 # Step-by-step installation guide
│   ├── github-actions.md               # GitHub Actions setup guide
│   ├── jenkins.md                      # Jenkins integration guide
│   └── demo.md                         # Demonstration walkthrough
│
├── pytest.ini                          # Test configuration
├── Dockerfile                          # Multi-stage container definition
├── docker-compose.yml                  # Container orchestration
└── README.md                           # Master project documentation
```

---

## 7. Installation & Quick Start

### Option A: Local Python & Node Setup
```bash
# 1. Clone repository
git clone <repo-url> zero-trust-cicd-validator
cd zero-trust-cicd-validator

# 2. Set up virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .\.venv\Scripts\Activate.ps1

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Build frontend dashboard
cd frontend
npm install
npm run build
cd ..

# 5. Start unified API and Dashboard server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Open **`http://127.0.0.1:8000`** in your browser to access the SOC Dashboard.

### Option B: Docker Compose
```bash
docker compose up --build
```

---

## 8. Command-Line Interface (CLI)

The validator operates as a standalone CLI tool that can be embedded into shell scripts, Makefiles, or CI/CD runners:

```bash
python validator/cli.py validate
```

### Subcommands:
- `validate`: Runs complete 3-stage validation pipeline.
- `verify-commit`: Inspects commit signature and matches against trusted developers.
- `verify-dependencies`: Audits lockfiles for cryptographic hash integrity.
- `verify-runner`: Checks current runner files against cryptographic baseline.
- `baseline`: Generates or updates `configs/integrity_baseline.json`.
- `status`: Displays active policy rules and trusted developer registrations.

### Terminal Output Examples:

#### Validation PASS (Build Allowed):
```text
╔═══════════════════════════════════════════════════════════════╗
║          ZERO-TRUST CI/CD PIPELINE VALIDATOR                  ║
║      Cryptographic Verification & Tamper-Proofing             ║
╚═══════════════════════════════════════════════════════════════╝

[1/3] Commit Verification
      ✓ Signed with SSH
      ✓ Cryptographic signature valid
      ✓ Trusted developer: 24mis0187@vitstudent.ac.in
      Status: [ PASS ]

[2/3] Dependency Verification
      Total dependencies scanned : 7
      Cryptographically verified : 7
      Status: [ PASS ]

[3/3] Runner Integrity
      Baseline files checked     : 9
      Matching baseline hashes   : 9
      Integrity Score            : 100/100
      Status: [ CLEAN ]

===============================================================
FINAL DECISION: BUILD ALLOWED (Score: 100/100)
===============================================================
Reason:
  ✓ All Zero-Trust security checks passed. Build environment and code integrity verified.

Audit Run ID: RUN-20260911103607-D930FF
```

#### Validation FAIL (Build Blocked):
```text
[2/3] Dependency Verification
      Total dependencies scanned : 7
      Cryptographically verified : 6
      ✗ Hash mismatches          : 1
      Status: [ FAIL ]

===============================================================
FINAL DECISION: BUILD BLOCKED (Score: 35/100)
===============================================================
Reason(s):
  ✗ Dependency Integrity Failure: 1 dependency hash mismatch(es) detected.
```

### Standardized Exit Codes:
- `0`: Validation Passed (**BUILD ALLOWED**)
- `1`: Validation Failed (**BUILD BLOCKED**)
- `2`: Configuration Error
- `3`: Internal Validator Error

---

## 9. CI/CD Pipeline Integrations

### GitHub Actions Integration
Add the pre-build validation gate to your workflow:
```yaml
jobs:
  pre-build-verification:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Zero-Trust Gate
        uses: ./integrations/github
        with:
          commit-ref: ${{ github.sha }}

  build:
    needs: pre-build-verification
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: ./build.sh
```

### Jenkins Pipeline Integration
Add the validation stage to your `Jenkinsfile`:
```groovy
stage('Zero-Trust Validation Gate') {
    steps {
        sh 'python3 -m validator.cli validate --path "${WORKSPACE}"'
    }
}
```

---

## 10. Safe Demonstration Attack Scenarios

The suite includes 4 safe, self-contained simulation scenarios in `demo/attack-simulation/`:

```bash
python demo/attack-simulation/run_all_simulations.py
```

| Scenario | Trigger / Attack Vector | Verification Gate | Expected Decision | Exit Code |
| :--- | :--- | :--- | :--- | :--- |
| **Scenario 1: Legitimate Build** | Signed commit (`ssh-ed25519`) + valid dependency hashes + clean runner | All Gates Pass | **BUILD ALLOWED** | `0` |
| **Scenario 2: Malicious Dependency** | Simulated package substitution / tampered lockfile hash | Dependency Verifier | **BUILD BLOCKED** | `1` |
| **Scenario 3: Forged / Unsigned Commit** | Unsigned commit or unauthorized author identity | Commit Verifier | **BUILD BLOCKED** | `1` |
| **Scenario 4: Runner Host Tampering** | Modified baseline file or injected `LD_PRELOAD` variable | Runner Verifier | **BUILD BLOCKED** | `1` |

---

## 11. Automated Testing

The project includes an extensive automated test suite with **26 unit and integration tests** covering all modules:

```bash
python -m pytest
```

Test coverage includes:
- Commit signature verification (SSH, GPG, unsigned, invalid keys, non-git directory handling).
- Dependency lockfile parsing (Python requirements `--hash`, Poetry locked wheels, npm Subresource Integrity, unverified handling).
- Runner integrity verification (baseline generation, file tampering detection, missing file detection, environment variable auditing).
- Policy engine rules (all-pass ALLOW, fail-closed enforcement, score calculation).
- REST API endpoints and simulation triggers.

---

## 12. Explicit Limitations & Defense-in-Depth Context

1. **Host Proving Limits**: Runner integrity checks provide evidence of tampering within the configured detection scope; they **cannot mathematically prove that the entire host is uncompromised**. Kernel rootkits or host virtualization compromises remain an external risk.
2. **Ecosystem Metadata Availability**: Dependency verification depends on the availability of cryptographic lockfiles (`package-lock.json`, `poetry.lock`, or hashed `requirements.txt`). An unpinned project cannot be verified unless locked.
3. **Private Key Protection**: If a trusted developer's private SSH or GPG key is physically stolen, commits signed with that key will appear valid until the key is revoked in `configs/trusted_developers.yaml`.
4. **Defense-in-Depth**: This tool is designed to operate alongside container isolation, ephemeral runners, and cryptographic attestations (SLSA/in-toto).

---

## 13. Future Enhancements

- **Sigstore & Cosign Integration**: Native support for keyless OIDC commit and container image signing.
- **SLSA Provenance Generation**: Automatic in-toto attestation generation upon validation pass.
- **Rekor Transparency Log**: Querying public or private transparency logs for verifiable build provenance.
- **Hardware Attestation**: TPM 2.0 remote runner attestation for enterprise bare-metal build nodes.
- **PostgreSQL & SIEM Export**: Streaming audit events to Splunk, Datadog, or Elasticsearch via Syslog/CEF.
