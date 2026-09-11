# GitHub Actions Integration Guide

## Overview

The Zero-Trust CI/CD Pipeline Validator integrates into GitHub Actions workflows as a **pre-build verification gate**. It ensures that any PR or commit:
1. Is signed cryptographically by an authorized developer.
2. Contains only locked, cryptographically verified dependencies.
3. Runs in an uncompromised runner environment with no injected variables.

If any check fails, the validator exits with code `1`, causing GitHub Actions to abort the job immediately and prevent the build stage from executing.

---

## 1. Using the Composite Action

The repository includes a composite GitHub Action in `integrations/github/action.yml`.

### Example Workflow (`.github/workflows/ci.yml`)

```yaml
name: Zero-Trust Secure Build Pipeline

on:
  push:
    branches: [ main, master, release/* ]
  pull_request:
    branches: [ main, master ]

jobs:
  pre-build-verification:
    name: 'Gate 0: Zero-Trust Security Verification'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code with Complete History
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # CRITICAL: fetch-depth: 0 required for git commit signature inspection

      - name: Run Zero-Trust CI/CD Validator
        uses: ./integrations/github
        with:
          commit-ref: ${{ github.sha }}
          policy-path: 'configs/policy.yaml'
          fail-closed: 'true'

  build:
    name: 'Build Application'
    needs: pre-build-verification  # Ensures build only starts if verification PASSES
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Build Application
        run: |
          echo "=========================================================="
          echo "ZERO-TRUST VERIFICATION PASSED: BUILD IS AUTHORIZED"
          echo "=========================================================="
          ./build.sh
```

---

## 2. Managing Trusted Developers in CI

Commit signers are configured in `configs/trusted_developers.yaml`:

```yaml
developers:
  - name: "Hari Prasath D"
    email: "24mis0187@vitstudent.ac.in"
    key_id: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKey..."
    type: "ssh"
    enabled: true

  - name: "Dhanush"
    email: "dhanush1108samu@gmail.com"
    key_id: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKey..."
    type: "ssh"
    enabled: true
```

Developers sign their Git commits locally:
```bash
git config user.signingkey "ssh-ed25519 AAAAC..."
git config gpg.format ssh
git commit -S -m "feat: verified commit"
```

---

## 3. Exit Code Enforcement

| Exit Code | Meaning | GitHub Actions Behavior |
| :--- | :--- | :--- |
| `0` | Verification Passed | Workflow proceeds to the `build` job. |
| `1` | Security Policy Violation | Workflow fails; `build` job is aborted. |
| `2` | Configuration Error | Workflow fails immediately. |
| `3` | Internal Validator Error | Workflow fails (fail-closed policy). |
