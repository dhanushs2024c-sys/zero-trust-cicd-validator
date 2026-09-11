# ZERO-TRUST CI/CD PIPELINE VALIDATOR

## Cryptographic Verification and Tamper-Proofing for Secure Build Environments

You are an expert cybersecurity software engineer, DevSecOps engineer, Python developer, CI/CD engineer, and security architect.

Build a complete working project called:

**Zero-Trust CI/CD Pipeline Validator**

The project must be a functional cybersecurity tool, not just a UI prototype.

The goal is to create a lightweight security validation layer that executes BEFORE a CI/CD build and determines whether the build should be allowed or blocked.

The system must implement Zero-Trust principles:

> Never trust the commit, dependency, or runner environment automatically. Verify everything before allowing the build.

---

# 1. PROJECT OBJECTIVE

Develop a security validation agent compatible with:

* GitHub Actions
* Jenkins
* Local Git repositories

The validator must perform three major security checks:

### A. Commit Signature Verification

Verify that the latest Git commit is:

* Signed
* Cryptographically valid
* Created by a trusted developer
* Not forged or modified

Support:

* GPG signatures
* SSH commit signatures where possible

### B. Dependency Integrity Verification

Before the build starts:

* Read project dependency files
* Identify dependencies
* Calculate/verify cryptographic hashes where available
* Compare against trusted/locked dependency information
* Detect modified or unexpected dependencies
* Support Python and Node.js projects initially

Support:

* `requirements.txt`
* `package-lock.json`
* `npm` dependency metadata
* Python lock/hash information where available

Use SHA-256 or stronger cryptographic hashing.

Where package ecosystem signatures/attestations are available, support them as an additional verification mechanism.

IMPORTANT:

Do not falsely assume that every npm or pip package has a directly verifiable cryptographic signature.

The validator should use the strongest available verification mechanism and clearly report which mechanism was used.

### C. CI/CD Runner Integrity Verification

Check whether the build environment has been tampered with.

Implement practical lightweight checks such as:

* Critical file integrity
* Configuration file integrity
* Validator executable/script integrity
* Unexpected modifications
* Suspicious environment variables
* Unexpected processes where reasonably detectable
* Unexpected files in configured sensitive directories
* Baseline hash comparison

The system should generate a runner integrity score/status:

* CLEAN
* WARNING
* TAMPERED

---

# 2. CORE SECURITY PRINCIPLE

The pipeline must follow:

```text
Developer Commit
      |
      v
Commit Verification
      |
      | FAIL
      +----------> BLOCK BUILD
      |
      v
Dependency Verification
      |
      | FAIL
      +----------> BLOCK BUILD
      |
      v
Runner Integrity Verification
      |
      | FAIL
      +----------> BLOCK BUILD
      |
      v
Policy Engine
      |
      +---- PASS ----> ALLOW BUILD
      |
      +---- FAIL ----> BLOCK BUILD
```

The validator must fail securely.

If a required security check cannot be completed, the default behavior should be:

```text
BLOCK BUILD
```

unless the configuration explicitly allows warning/fallback behavior.

---

# 3. TECHNOLOGY STACK

Use the following technologies unless there is a strong technical reason to change them:

## Backend

Python 3.11+

Recommended libraries:

* FastAPI
* Pydantic
* cryptography
* GitPython where useful
* PyYAML
* psutil
* pytest

Use Python standard library wherever possible for security-sensitive operations.

## Frontend

Build a clean modern dashboard using:

* React
* TypeScript
* Vite
* Tailwind CSS

If the existing Antigravity environment strongly favors another frontend stack, use an equivalent modern stack.

## Database

Use SQLite initially.

Store:

* validation runs
* security events
* commit verification results
* dependency verification results
* runner integrity results
* policy decisions
* timestamps
* audit information

The architecture should allow migration to PostgreSQL later.

---

# 4. PROJECT STRUCTURE

Create a professional repository structure similar to:

```text
zero-trust-cicd-validator/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── commit_verifier.py
│   │   │   ├── dependency_verifier.py
│   │   │   ├── runner_integrity.py
│   │   │   ├── policy_engine.py
│   │   │   ├── audit_logger.py
│   │   │   └── validator.py
│   │   ├── api/
│   │   └── utils/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   └── package.json
│
├── validator/
│   ├── cli.py
│   ├── config.yaml
│   └── scripts/
│
├── integrations/
│   ├── github/
│   │   └── action.yml
│   └── jenkins/
│       └── Jenkinsfile
│
├── demo/
│   ├── vulnerable-project/
│   ├── malicious-dependency/
│   ├── attack-simulation/
│   └── README.md
│
├── configs/
│   ├── policy.yaml
│   ├── trusted_developers.yaml
│   └── integrity_baseline.json
│
├── docs/
│   ├── architecture.md
│   ├── threat-model.md
│   ├── installation.md
│   ├── github-actions.md
│   ├── jenkins.md
│   └── demo.md
│
├── tests/
│
├── .gitignore
├── README.md
├── docker-compose.yml
└── Dockerfile
```

You may modify the structure if needed, but maintain clear separation between:

* Security logic
* API
* Frontend
* CI/CD integrations
* Demo
* Tests
* Configuration

---

# 5. COMMAND-LINE INTERFACE

Create a CLI so the validator can run without the dashboard.

Example:

```bash
zt-validator validate
```

Additional commands:

```bash
zt-validator verify-commit
zt-validator verify-dependencies
zt-validator verify-runner
zt-validator baseline
zt-validator status
```

Expected output:

```text
╔══════════════════════════════════════════╗
║     ZERO-TRUST CI/CD VALIDATOR           ║
╚══════════════════════════════════════════╝

[1/3] Commit Verification
      ✓ Signature valid
      ✓ Trusted developer
      Status: PASS

[2/3] Dependency Verification
      ✓ All dependency hashes verified
      Status: PASS

[3/3] Runner Integrity
      ✓ Environment integrity verified
      Status: PASS

--------------------------------------------
FINAL DECISION: BUILD ALLOWED
--------------------------------------------
```

Failure example:

```text
[1/3] Commit Verification
      ✗ Invalid commit signature
      Status: FAIL

--------------------------------------------
FINAL DECISION: BUILD BLOCKED
--------------------------------------------

Reason:
Commit signature verification failed.
```

The CLI must return meaningful exit codes:

```text
0 = validation passed
1 = validation failed
2 = configuration error
3 = internal validator error
```

This is important because GitHub Actions and Jenkins can use the exit code to stop the pipeline.

---

# 6. COMMIT VERIFICATION MODULE

Implement a `CommitVerifier`.

Requirements:

1. Detect the current Git commit.
2. Obtain commit metadata.
3. Detect whether it is signed.
4. Verify the cryptographic signature.
5. Determine the signing identity.
6. Compare against trusted developers.
7. Produce structured results.

Example result:

```json
{
  "commit": "abc123",
  "author": "developer@example.com",
  "signed": true,
  "signature_type": "GPG",
  "signature_valid": true,
  "trusted_developer": true,
  "status": "PASS"
}
```

Failure:

```json
{
  "commit": "abc123",
  "signed": true,
  "signature_type": "GPG",
  "signature_valid": false,
  "trusted_developer": false,
  "status": "FAIL"
}
```

Use actual Git/GPG/SSH verification commands where appropriate.

Do NOT create fake cryptographic verification.

---

# 7. TRUSTED DEVELOPER CONFIGURATION

Create:

```text
configs/trusted_developers.yaml
```

Example:

```yaml
developers:
  - name: Developer One
    email: developer1@example.com
    key_id: KEY_ID_HERE
    type: gpg

  - name: Developer Two
    email: developer2@example.com
    key_id: KEY_ID_HERE
    type: ssh
```

The validator should support adding/removing trusted developers through configuration.

Never hard-code trusted identities inside the Python source code.

---

# 8. DEPENDENCY VERIFICATION

Create:

```text
dependency_verifier.py
```

The module should detect the project type.

For Python:

```text
requirements.txt
pyproject.toml
poetry.lock
```

For Node:

```text
package.json
package-lock.json
```

Use lockfiles and cryptographic hashes where available.

For every dependency produce:

```json
{
  "name": "example-package",
  "version": "1.2.3",
  "expected_hash": "...",
  "actual_hash": "...",
  "verification_method": "lockfile_sha256",
  "status": "PASS"
}
```

If mismatch occurs:

```json
{
  "status": "FAIL",
  "reason": "Dependency integrity mismatch"
}
```

The system must clearly distinguish:

* VERIFIED
* UNVERIFIED
* MISMATCH
* MISSING
* ERROR

Do not silently mark an unverified dependency as verified.

---

# 9. RUNNER INTEGRITY

Create:

```text
runner_integrity.py
```

Implement a baseline mechanism.

Example:

```bash
zt-validator baseline
```

This generates:

```text
configs/integrity_baseline.json
```

Store hashes for configured critical files.

On every validation:

```text
Current Hash
     |
     v
Compare with Baseline
     |
     +---- Match ------> PASS
     |
     +---- Mismatch ---> FAIL
```

Also implement reasonable environment checks.

For example:

* PATH anomalies
* suspicious environment variables
* modified validator files
* modified configuration files
* unexpected files
* selected process checks
* system information

Avoid claiming that these checks can prove the entire runner is uncompromised.

The UI/report must clearly say:

> "Runner integrity checks provide evidence of tampering within the configured detection scope; they cannot mathematically prove that the entire host is uncompromised."

This is important for technical correctness.

---

# 10. POLICY ENGINE

Create:

```text
policy_engine.py
```

Example:

```yaml
policy:
  require_signed_commit: true
  require_trusted_developer: true
  block_unverified_dependencies: true
  block_dependency_mismatch: true
  require_runner_integrity: true
  fail_closed: true
```

The policy engine decides:

```text
ALLOW
BLOCK
WARNING
```

The final decision must be based on all required checks.

---

# 11. VALIDATION API

Create REST APIs.

Example endpoints:

```text
GET  /api/health

POST /api/validate

GET  /api/runs

GET  /api/runs/{id}

GET  /api/events

GET  /api/status

POST /api/baseline

GET  /api/dependencies

GET  /api/commits

GET  /api/runner
```

Example:

```http
POST /api/validate
```

Response:

```json
{
  "run_id": "RUN-001",
  "commit": {
    "status": "PASS"
  },
  "dependencies": {
    "status": "PASS"
  },
  "runner": {
    "status": "PASS"
  },
  "final_decision": "ALLOW"
}
```

---

# 12. DASHBOARD

Create a professional cybersecurity dashboard.

The dashboard should immediately show:

```text
ZERO-TRUST PIPELINE SECURITY
```

Main cards:

```text
┌─────────────────┐
│ BUILD STATUS    │
│     ALLOWED     │
└─────────────────┘

┌─────────────────┐
│ COMMIT          │
│ ✓ VERIFIED      │
└─────────────────┘

┌─────────────────┐
│ DEPENDENCIES    │
│ ✓ VERIFIED      │
└─────────────────┘

┌─────────────────┐
│ RUNNER          │
│ ✓ INTEGRITY OK  │
└─────────────────┘
```

Include:

### Security Score

Example:

```text
Security Score
     96/100
```

Do not represent the score as mathematically proving security.

### Recent Validation Runs

Columns:

```text
Run ID
Timestamp
Commit
Commit Status
Dependency Status
Runner Status
Final Decision
```

### Security Events

Display:

```text
Timestamp
Severity
Category
Message
Source
Status
```

Severity:

* INFO
* LOW
* MEDIUM
* HIGH
* CRITICAL

---

# 13. VISUAL PIPELINE STATUS

Add a visual pipeline:

```text
COMMIT
  ✓
  |
  v
DEPENDENCIES
  ✓
  |
  v
RUNNER
  ✓
  |
  v
POLICY
  ✓
  |
  v
BUILD
ALLOWED
```

When an attack occurs:

```text
COMMIT
  ✓
  |
  v
DEPENDENCIES
  ✗
  |
  v
BUILD
BLOCKED
```

Use clear visual indicators for PASS/WARNING/FAIL.

---

# 14. SECURITY EVENT LOG

Every validation must produce an audit event.

Example:

```json
{
  "timestamp": "2026-09-11T10:30:00Z",
  "run_id": "RUN-001",
  "event": "DEPENDENCY_HASH_MISMATCH",
  "severity": "CRITICAL",
  "dependency": "example-package",
  "expected": "abc...",
  "actual": "def...",
  "action": "BUILD_BLOCKED"
}
```

Audit logs must be append-only from the application's perspective.

Do not allow normal users to modify historical events through the dashboard.

---

# 15. GITHUB ACTIONS INTEGRATION

Create:

```text
integrations/github/action.yml
```

The GitHub Action should run BEFORE the build.

Example workflow:

```yaml
name: Zero Trust Validation

on:
  push:
  pull_request:

jobs:
  security-validation:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Zero-Trust Validator
        run: |
          zt-validator validate

      - name: Build
        run: |
          echo "Build starts only after validation passes"
```

The validator must return a non-zero exit code if the security policy fails.

---

# 16. JENKINS INTEGRATION

Create:

```text
integrations/jenkins/Jenkinsfile
```

Example flow:

```groovy
pipeline {
    stages {

        stage('Zero-Trust Validation') {
            steps {
                sh 'zt-validator validate'
            }
        }

        stage('Build') {
            steps {
                sh './build.sh'
            }
        }
    }
}
```

The build stage must never execute if validation fails.

---

# 17. DEMONSTRATION ATTACK

This project MUST include a safe simulated supply-chain attack.

Create:

```text
demo/attack-simulation/
```

The demonstration should show:

### Scenario 1 — Legitimate Build

```text
Signed commit
      +
Trusted developer
      +
Valid dependency
      +
Clean runner

= BUILD ALLOWED
```

### Scenario 2 — Malicious Dependency

Simulate a dependency whose expected cryptographic identity differs from the detected identity.

Example:

```text
Expected:
SHA256 = AAA111

Detected:
SHA256 = BBB222
```

Validator:

```text
DEPENDENCY INTEGRITY FAILURE
BUILD BLOCKED
```

### Scenario 3 — Invalid Commit

Simulate an unsigned or invalidly signed commit.

Result:

```text
COMMIT VERIFICATION FAILURE
BUILD BLOCKED
```

### Scenario 4 — Runner Tampering

Modify a monitored test file/configuration after generating the baseline.

Result:

```text
RUNNER INTEGRITY FAILURE
BUILD BLOCKED
```

The attack must be completely local and harmless.

Do NOT create real malware, persistence mechanisms, credential theft, destructive code, or real-world exploitation.

---

# 18. DEMO MODE

Create a demo mode accessible from the dashboard.

Buttons:

```text
[ Run Secure Build ]

[ Simulate Dependency Attack ]

[ Simulate Invalid Commit ]

[ Simulate Runner Tampering ]

[ Reset Demo Environment ]
```

When clicking:

**Run Secure Build**

show:

```text
✓ Commit verified
✓ Developer trusted
✓ Dependencies verified
✓ Runner verified
✓ Policy passed

BUILD ALLOWED
```

When clicking:

**Simulate Dependency Attack**

show:

```text
⚠ SIMULATED SUPPLY-CHAIN ATTACK

Dependency integrity mismatch detected.

Expected hash:
abc123...

Actual hash:
xyz789...

BUILD BLOCKED
```

Include a clear banner:

```text
SIMULATION ONLY
No real malware or external systems are affected.
```

---

# 19. THREAT MODEL

Create:

```text
docs/threat-model.md
```

Document threats including:

* Compromised developer credentials
* Unsigned commits
* Forged commits
* Malicious dependencies
* Dependency substitution
* Dependency tampering
* Compromised CI runner
* Modified build scripts
* Environment poisoning
* Pipeline configuration tampering

For each threat document:

```text
Threat
Attack Vector
Impact
Detection Mechanism
Mitigation
Residual Risk
```

---

# 20. TESTING

Write extensive unit and integration tests.

Test:

### Commit verification

* Valid signed commit
* Unsigned commit
* Invalid signature
* Unknown developer
* Trusted developer

### Dependencies

* Correct hash
* Incorrect hash
* Missing hash
* Unavailable dependency metadata
* Multiple dependencies
* Python project
* Node project

### Runner

* Valid baseline
* Modified file
* Missing file
* New unexpected file
* Invalid baseline

### Policy

* Everything passes
* Commit failure
* Dependency failure
* Runner failure
* Multiple failures
* Fail-closed behavior

### API

Test all major endpoints.

### CI

Test that:

```text
Validation PASS -> Build executes
Validation FAIL -> Build does not execute
```

---

# 21. SECURITY REQUIREMENTS

Follow secure coding practices.

Implement:

* Input validation
* Safe subprocess execution
* No shell injection
* Secure temporary files
* Proper file permissions
* No hardcoded secrets
* No hardcoded private keys
* No credentials in logs
* Sanitized error messages
* Structured audit logging
* Fail-closed defaults
* Configuration validation

Never execute arbitrary commands supplied directly by users.

---

# 22. CONFIGURATION

Create a central configuration file.

Example:

```yaml
validator:
  fail_closed: true

commit:
  require_signature: true
  require_trusted_developer: true

dependencies:
  require_integrity: true
  algorithm: sha256
  block_unverified: true

runner:
  integrity_check: true
  check_environment: true
  check_processes: true

audit:
  enabled: true
```

Allow configuration through environment variables where appropriate.

---

# 23. DOCKER SUPPORT

Create:

```text
Dockerfile
docker-compose.yml
```

The project should be easy to start.

Example:

```bash
docker compose up --build
```

The README must explain how to start:

```text
Backend
Frontend
Database
Demo
```

---

# 24. README

Create a professional README containing:

1. Project title
2. Problem statement
3. Motivation
4. Objectives
5. Features
6. Architecture
7. Technologies
8. Installation
9. Configuration
10. CLI usage
11. GitHub Actions integration
12. Jenkins integration
13. Dashboard
14. Attack simulation
15. Testing
16. Threat model
17. Limitations
18. Future enhancements
19. Team members

Team members:

```text
HARI PRASATH D [24MIS0187]
DHANUSH [24MIS0253]
```

---

# 25. LIMITATIONS

Explicitly document limitations.

For example:

* Runner integrity checks cannot prove complete host security.
* Dependency verification depends on available ecosystem metadata.
* GPG/SSH trust configuration must be managed securely.
* A compromised trusted signing key remains a risk.
* Hash verification proves integrity relative to the trusted hash source; it does not by itself prove software is benign.
* Container/VM isolation may be required for stronger runner assurance.

Do not make unrealistic claims such as:

> "This tool guarantees that the software is completely secure."

Instead describe it as a defense-in-depth security control.

---

# 26. FUTURE ENHANCEMENTS

Document possible future features:

* Sigstore integration
* SLSA provenance
* in-toto attestations
* SBOM verification
* Rekor transparency log verification
* OIDC identity verification
* Remote attestation
* TPM-based runner verification
* Kubernetes admission integration
* PostgreSQL
* Enterprise RBAC
* SIEM integration
* Slack/email alerts

---

# 27. UI DESIGN

Use a professional cybersecurity/SOC style.

Requirements:

* Responsive layout
* Sidebar navigation
* Dashboard
* Validation Runs
* Dependencies
* Commit Verification
* Runner Integrity
* Security Events
* Configuration
* Demo Mode

The interface should look like a real DevSecOps security product, not a basic student CRUD application.

Avoid excessive animations.

Prioritize:

* readability
* clear security status
* useful information
* professional layout

---

# 28. DEVELOPMENT REQUIREMENT

Do not generate only placeholder files.

Implement real functionality.

Do not use:

```text
TODO
IMPLEMENT_ME
fake API response
mock verification
random security score
```

unless explicitly isolated inside the demo/test environment.

The core validator must execute real checks.

---

# 29. DEVELOPMENT PROCESS

First inspect the environment and determine what tools are available.

Then:

### Phase 1

Create the project structure.

### Phase 2

Implement configuration and models.

### Phase 3

Implement commit verification.

### Phase 4

Implement dependency verification.

### Phase 5

Implement runner integrity.

### Phase 6

Implement policy engine.

### Phase 7

Implement CLI.

### Phase 8

Implement FastAPI backend.

### Phase 9

Implement React dashboard.

### Phase 10

Implement GitHub Actions integration.

### Phase 11

Implement Jenkins integration.

### Phase 12

Implement attack simulation.

### Phase 13

Write tests.

### Phase 14

Dockerize the application.

### Phase 15

Write documentation.

After each phase, run tests and fix errors before continuing.

---

# 30. FINAL ACCEPTANCE CRITERIA

The project is considered complete only when the following work:

### Test 1

Valid signed commit + valid dependencies + clean runner:

```text
BUILD ALLOWED
```

### Test 2

Unsigned/invalid commit:

```text
BUILD BLOCKED
```

### Test 3

Dependency integrity mismatch:

```text
BUILD BLOCKED
```

### Test 4

Runner integrity mismatch:

```text
BUILD BLOCKED
```

### Test 5

GitHub Actions:

```text
Validation PASS -> Build
Validation FAIL -> Pipeline stops
```

### Test 6

Jenkins:

```text
Validation PASS -> Build
Validation FAIL -> Pipeline stops
```

### Test 7

Dashboard correctly displays:

* validation status
* commit verification
* dependency verification
* runner integrity
* security events
* historical runs

### Test 8

Demo mode successfully demonstrates the simulated supply-chain attack without using real malware.

---

# 31. IMPORTANT IMPLEMENTATION RULE

Do not skip difficult security functionality by replacing it with simulated output.

If a feature cannot be fully implemented because an external service, signing key, registry, or CI environment is unavailable:

1. Implement the real interface.
2. Detect the unavailable condition.
3. Return `UNAVAILABLE` or `UNVERIFIED`.
4. Apply the configured policy.
5. Clearly document how to configure the real environment.

Never report:

```text
VERIFIED
```

when the system did not actually verify something.

---

# 32. START NOW

Start by creating the complete project structure and implementing the backend security engine first.

Then progressively implement the CLI, API, frontend, CI/CD integrations, attack simulation, tests, Docker configuration, and documentation.

After implementation:

1. Run all tests.
2. Fix all errors.
3. Run the demo attack.
4. Verify that the attack causes BUILD BLOCKED.
5. Verify that the legitimate scenario causes BUILD ALLOWED.
6. Verify GitHub Actions integration.
7. Verify Jenkins integration.
8. Ensure the README contains complete setup instructions.

At the end, provide:

* Project structure
* How to run the application
* How to run tests
* How to run the demo
* How to integrate with GitHub Actions
* How to integrate with Jenkins
* Known limitations
* Future enhancements

Build this as a **real academic cybersecurity project suitable for a final-year/seminar demonstration**, while keeping all attack simulations local, controlled, and harmless.
