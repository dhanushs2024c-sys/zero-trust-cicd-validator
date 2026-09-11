"""
Unit Tests for Runner Host Integrity Verification Engine
Tests baseline generation, file modification detection, missing file detection,
and environment variable auditing.
"""

import os
import json
from pathlib import Path
from backend.app.services.runner_integrity import RunnerIntegrityVerifier, REQUIRED_DISCLAIMER


def test_baseline_generation_and_clean_verify(tmp_path):
    """Test generating a baseline and verifying a clean file matches."""
    crit_file = tmp_path / "critical_script.py"
    crit_file.write_text("print('clean script')", encoding="utf-8")

    baseline_path = tmp_path / "integrity_baseline.json"
    verifier = RunnerIntegrityVerifier(project_root=tmp_path, baseline_path=baseline_path)

    # 1. Create baseline
    verifier.create_baseline(paths_to_monitor=["critical_script.py"])
    assert baseline_path.exists()

    # 2. Verify runner
    res = verifier.verify_runner(check_env=False, check_procs=False, check_path=False)
    assert res.status == "CLEAN"
    assert res.integrity_score == 100
    assert res.matched_files_count == 1
    assert res.tampered_files_count == 0
    assert res.disclaimer == REQUIRED_DISCLAIMER


def test_runner_modified_file_detected(tmp_path):
    """Test modification of a baseline file causes TAMPERED status."""
    crit_file = tmp_path / "config.yaml"
    crit_file.write_text("setting: original", encoding="utf-8")

    baseline_path = tmp_path / "integrity_baseline.json"
    verifier = RunnerIntegrityVerifier(project_root=tmp_path, baseline_path=baseline_path)
    verifier.create_baseline(paths_to_monitor=["config.yaml"])

    # Tamper with the file
    crit_file.write_text("setting: TAMPERED_MALICIOUS_EDIT", encoding="utf-8")

    res = verifier.verify_runner(check_env=False, check_procs=False, check_path=False)
    assert res.status == "TAMPERED"
    assert res.tampered_files_count == 1
    assert res.matched_files_count == 0
    assert res.file_checks[0].status == "MODIFIED"


def test_runner_missing_file_detected(tmp_path):
    """Test deletion of a baseline file causes TAMPERED status."""
    crit_file = tmp_path / "validator_binary.py"
    crit_file.write_text("print('binary')", encoding="utf-8")

    baseline_path = tmp_path / "integrity_baseline.json"
    verifier = RunnerIntegrityVerifier(project_root=tmp_path, baseline_path=baseline_path)
    verifier.create_baseline(paths_to_monitor=["validator_binary.py"])

    # Delete the file
    crit_file.unlink()

    res = verifier.verify_runner(check_env=False, check_procs=False, check_path=False)
    assert res.status == "TAMPERED"
    assert res.missing_files_count == 1
    assert res.file_checks[0].status == "DELETED"


def test_suspicious_env_var_flagged(tmp_path):
    """Test injection of dangerous LD_PRELOAD environment variable."""
    verifier = RunnerIntegrityVerifier(project_root=tmp_path)
    os.environ["LD_PRELOAD"] = "/tmp/fake_hook.so"

    try:
        res = verifier.verify_runner(check_env=True, check_procs=False, check_path=False)
        assert res.status == "TAMPERED"
        assert res.suspicious_env_vars_count > 0
        flagged_vars = [e.variable for e in res.env_checks]
        assert "LD_PRELOAD" in flagged_vars
    finally:
        os.environ.pop("LD_PRELOAD", None)
