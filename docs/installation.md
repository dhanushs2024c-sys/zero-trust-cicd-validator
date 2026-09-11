# Installation & Deployment Guide

This guide details how to install, configure, and run the **Zero-Trust CI/CD Pipeline Validator** in local development environments, CI/CD runners, and Docker containers.

---

## Prerequisites

- **Python**: 3.11 or higher
- **Git**: 2.34+ (supporting SSH and GPG commit verification)
- **Node.js**: 18+ (for building the React SOC dashboard)
- **Docker**: (optional, for containerized deployment)

---

## 1. Local Python Setup

### Clone Repository & Create Virtual Environment
```bash
git clone <repo-url> zero-trust-cicd-validator
cd zero-trust-cicd-validator

python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
```

### Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### Verify CLI Tool
```bash
python validator/cli.py status
```

---

## 2. Frontend Dashboard Setup

### Install Dependencies & Build Assets
```bash
cd frontend
npm install
npm run build
cd ..
```
The compiled assets will be placed in `frontend/dist` and automatically served by FastAPI!

### Development Mode (Hot Reload)
To run frontend and backend with hot-reload during development:
- **Terminal 1 (Backend)**:
  ```bash
  python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- **Terminal 2 (Frontend)**:
  ```bash
  cd frontend
  npm run dev
  ```
  Open `http://localhost:5173` in your browser.

---

## 3. Running with Docker Compose

Run the entire system (backend, frontend, database, and telemetry) with a single command:

```bash
docker compose up --build
```
Access the SOC Dashboard at:
```text
http://localhost:8000
```

---

## 4. Initializing Runner Cryptographic Baseline

Before running validations on a new machine or runner, generate the baseline hash of critical files:

```bash
python validator/cli.py baseline
```
This generates `configs/integrity_baseline.json` containing SHA-256 hashes of critical configs, scripts, and validator files.
