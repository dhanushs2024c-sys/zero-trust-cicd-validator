"""
Zero-Trust CI/CD Runner Integrity Verification Engine
Performs cryptographic baseline hashing, environment variable auditing,
PATH anomaly inspection, and process scanning.

Technical Disclaimer:
Runner integrity checks provide evidence of tampering within the configured detection scope;
they cannot mathematically prove that the entire host is uncompromised.
"""

import os
import sys
import json
import hashlib
import psutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from backend.app.config import PROJECT_ROOT, DEFAULT_BASELINE_PATH
from backend.app.schemas.validation import (
    RunnerIntegrityResult,
    RunnerFileCheck,
    RunnerEnvCheck,
    RunnerProcessCheck
)
from backend.app.services.audit_logger import audit_logger


# Known suspicious environment variables often used in CI/CD pipeline hijacking
SUSPICIOUS_ENV_VARS = {
    "LD_PRELOAD": ("CRITICAL", "Dynamic linker hijacking - can intercept and modify arbitrary syscalls and library calls."),
    "LD_LIBRARY_PATH": ("HIGH", "Custom library path injection - potential shared library pre-loading attack."),
    "DYLD_INSERT_LIBRARIES": ("CRITICAL", "macOS dynamic library injection vector."),
    "DYLD_LIBRARY_PATH": ("HIGH", "macOS dynamic library search path manipulation."),
    "NODE_OPTIONS": ("HIGH", "Node.js startup option injection (e.g. malicious --require flags)."),
    "PYTHONINSPECT": ("MEDIUM", "Python forced interactive debugger mode."),
    "BASH_ENV": ("HIGH", "Bash startup script injection vector on every subshell."),
    "ENV": ("HIGH", "POSIX shell startup file execution vector.")
}

# Processes that should not ordinarily be running inside a clean CI build agent
SUSPICIOUS_PROCESS_NAMES = {
    "wireshark", "tshark", "tcpdump", "ettercap", "mitmproxy", "fiddler",
    "charles", "gdb", "radare2", "ghidra", "ida64", "strace", "ltrace"
}

REQUIRED_DISCLAIMER = (
    "Runner integrity checks provide evidence of tampering within the configured "
    "detection scope; they cannot mathematically prove that the entire host is uncompromised."
)


class RunnerIntegrityVerifier:
    def __init__(
        self,
        project_root: Optional[Path] = None,
        baseline_path: Optional[Path] = None
    ):
        self.project_root = Path(project_root) if project_root else PROJECT_ROOT
        self.baseline_path = Path(baseline_path) if baseline_path else DEFAULT_BASELINE_PATH

    def compute_sha256(self, file_path: Path) -> Optional[str]:
        """Compute SHA-256 hash of a file safely."""
        if not file_path.is_file():
            return None
        h = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def create_baseline(
        self,
        paths_to_monitor: Optional[List[str]] = None,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate a cryptographic baseline of critical files and save to JSON.
        """
        target_output = Path(output_path) if output_path else self.baseline_path
        target_output.parent.mkdir(parents=True, exist_ok=True)

        if not paths_to_monitor:
            paths_to_monitor = [
                "configs/policy.yaml",
                "configs/trusted_developers.yaml",
                "validator/cli.py",
                "backend/app/main.py",
                "backend/app/config.py",
                "backend/app/services/commit_verifier.py",
                "backend/app/services/dependency_verifier.py",
                "backend/app/services/runner_integrity.py",
                "backend/app/services/policy_engine.py",
                "backend/app/services/validator.py"
            ]

        file_hashes: Dict[str, str] = {}
        for rel_path in paths_to_monitor:
            abs_path = self.project_root / rel_path
            if abs_path.is_file():
                h = self.compute_sha256(abs_path)
                if h:
                    file_hashes[rel_path.replace("\\", "/")] = h

        baseline_data = {
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "generator": "zt-validator baseline v1.0.0",
            "project_root": str(self.project_root),
            "monitored_paths": paths_to_monitor,
            "files": file_hashes
        }

        with open(target_output, "w", encoding="utf-8") as f:
            json.dump(baseline_data, f, indent=2)

        audit_logger.log_event(
            event_name="RUNNER_BASELINE_GENERATED",
            severity="INFO",
            category="RUNNER",
            message=f"Cryptographic integrity baseline generated for {len(file_hashes)} files.",
            details={"file_count": len(file_hashes), "baseline_file": str(target_output)},
            action="MONITOR_LOGGED"
        )

        return baseline_data

    def verify_runner(
        self,
        check_env: bool = True,
        check_procs: bool = True,
        check_path: bool = True
    ) -> RunnerIntegrityResult:
        """
        Execute full runner integrity audit against baseline, environment, and system state.
        """
        file_checks: List[RunnerFileCheck] = []
        env_checks: List[RunnerEnvCheck] = []
        process_checks: List[RunnerProcessCheck] = []

        tampered_files = 0
        missing_files = 0
        matched_files = 0

        # 1. Baseline File Audit
        baseline_data = self._load_baseline()
        if not baseline_data or not baseline_data.get("files"):
            # If baseline is missing or empty, generate baseline or flag warning
            if not self.baseline_path.exists():
                self.create_baseline()
                baseline_data = self._load_baseline()

        expected_files = baseline_data.get("files", {}) if baseline_data else {}
        for rel_path, expected_hash in expected_files.items():
            abs_path = self.project_root / rel_path
            if not abs_path.exists():
                file_checks.append(RunnerFileCheck(
                    path=rel_path,
                    expected_hash=expected_hash,
                    actual_hash=None,
                    status="DELETED"
                ))
                missing_files += 1
            else:
                actual_hash = self.compute_sha256(abs_path)
                if actual_hash == expected_hash:
                    file_checks.append(RunnerFileCheck(
                        path=rel_path,
                        expected_hash=expected_hash,
                        actual_hash=actual_hash,
                        status="MATCH"
                    ))
                    matched_files += 1
                else:
                    file_checks.append(RunnerFileCheck(
                        path=rel_path,
                        expected_hash=expected_hash,
                        actual_hash=actual_hash,
                        status="MODIFIED"
                    ))
                    tampered_files += 1

        # 2. Environment Variables Audit
        if check_env:
            env_checks = self._audit_environment_variables()

        # 3. PATH Anomaly Audit
        if check_path:
            path_anomalies = self._audit_path_variable()
            env_checks.extend(path_anomalies)

        # 4. Process Audit
        if check_procs:
            process_checks = self._audit_processes()

        # 5. Compute Status and Integrity Score (0-100)
        critical_env = [e for e in env_checks if e.severity == "CRITICAL"]
        high_env = [e for e in env_checks if e.severity == "HIGH"]
        suspicious_procs = [p for p in process_checks if p.status == "SUSPICIOUS"]

        if tampered_files > 0 or missing_files > 0 or len(critical_env) > 0:
            status = "TAMPERED"
            score = max(0, 50 - (tampered_files * 20) - (len(critical_env) * 25))
            details = (
                f"TAMPERED: Runner integrity failure detected! "
                f"{tampered_files} modified file(s), {missing_files} missing file(s), "
                f"{len(critical_env)} critical environment anomalies."
            )
            severity = "CRITICAL"
        elif len(high_env) > 0 or len(suspicious_procs) > 0:
            status = "WARNING"
            score = max(60, 85 - (len(high_env) * 10) - (len(suspicious_procs) * 15))
            details = (
                f"WARNING: Runner environment anomalies detected: "
                f"{len(high_env)} suspicious environment variables, "
                f"{len(suspicious_procs)} suspicious process(es)."
            )
            severity = "HIGH"
        else:
            status = "CLEAN"
            score = 100
            details = (
                f"CLEAN: Runner integrity verified. All {matched_files} baseline files matched. "
                "Environment variables and system processes conform to baseline policy."
            )
            severity = "INFO"

        result = RunnerIntegrityResult(
            status=status,
            integrity_score=score,
            baseline_file_used=str(self.baseline_path.name) if self.baseline_path.exists() else None,
            monitored_files_count=len(expected_files),
            matched_files_count=matched_files,
            tampered_files_count=tampered_files,
            missing_files_count=missing_files,
            suspicious_env_vars_count=len(env_checks),
            suspicious_processes_count=len(suspicious_procs),
            file_checks=file_checks,
            env_checks=env_checks,
            process_checks=process_checks,
            disclaimer=REQUIRED_DISCLAIMER,
            details=details
        )

        audit_logger.log_event(
            event_name=f"RUNNER_INTEGRITY_{status}",
            severity=severity,
            category="RUNNER",
            message=details,
            details={
                "score": score,
                "tampered_files": tampered_files,
                "missing_files": missing_files,
                "matched_files": matched_files,
                "env_anomalies": len(env_checks),
                "suspicious_procs": len(suspicious_procs)
            },
            action="BUILD_ALLOWED" if status == "CLEAN" else "BUILD_BLOCKED"
        )

        return result

    def _load_baseline(self) -> Optional[Dict[str, Any]]:
        """Safely load JSON baseline file."""
        if not self.baseline_path.exists():
            return None
        try:
            with open(self.baseline_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _audit_environment_variables(self) -> List[RunnerEnvCheck]:
        """Detect presence of known hijacking or dangerous environment variables."""
        checks: List[RunnerEnvCheck] = []
        for var_name, (severity, reason) in SUSPICIOUS_ENV_VARS.items():
            val = os.environ.get(var_name)
            if val is not None and val.strip() != "":
                checks.append(RunnerEnvCheck(
                    variable=var_name,
                    value=val[:100] + ("..." if len(val) > 100 else ""),
                    severity=severity,
                    reason=reason
                ))

        # Check PYTHONPATH tampering (points outside repo or venv)
        pythonpath = os.environ.get("PYTHONPATH")
        if pythonpath:
            checks.append(RunnerEnvCheck(
                variable="PYTHONPATH",
                value=pythonpath[:100],
                severity="MEDIUM",
                reason="Custom PYTHONPATH set; can lead to arbitrary module injection during build."
            ))

        return checks

    def _audit_path_variable(self) -> List[RunnerEnvCheck]:
        """Check for insecure or temp directories placed ahead in PATH."""
        checks: List[RunnerEnvCheck] = []
        path_val = os.environ.get("PATH", "")
        paths = path_val.split(os.pathsep)

        insecure_keywords = ["temp", "tmp", "AppData\\Local\\Temp", "/tmp", "/var/tmp"]
        for idx, p in enumerate(paths[:5]):  # Check first 5 PATH entries
            p_lower = p.lower()
            if any(k.lower() in p_lower for k in insecure_keywords):
                checks.append(RunnerEnvCheck(
                    variable="PATH (Anomaly)",
                    value=p,
                    severity="HIGH",
                    reason=f"Temporary/world-writable directory positioned early in PATH (index {idx}). Potential binary hijacking."
                ))
        return checks

    def _audit_processes(self) -> List[RunnerProcessCheck]:
        """Inspect running processes for suspicious debugging or sniffing tools."""
        checks: List[RunnerProcessCheck] = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    name = (proc.info.get('name') or "").lower()
                    for susp in SUSPICIOUS_PROCESS_NAMES:
                        if susp in name:
                            cmd = " ".join(proc.info.get('cmdline') or [name])
                            checks.append(RunnerProcessCheck(
                                pid=proc.info['pid'],
                                name=proc.info['name'],
                                cmdline=cmd[:120],
                                status="SUSPICIOUS",
                                reason=f"Unauthorized diagnostic or packet sniffing utility detected in runner environment ({susp})."
                            ))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass
        return checks
