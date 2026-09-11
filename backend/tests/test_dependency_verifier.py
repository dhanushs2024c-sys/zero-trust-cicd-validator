"""
Unit Tests for Dependency Verification Engine
Tests locked hashes, unverified dependencies, mismatches, and multi-ecosystem parsing.
"""

import json
from pathlib import Path
from backend.app.services.dependency_verifier import DependencyVerifier


def test_requirements_with_sha256(tmp_path):
    """Test requirements.txt containing pinned SHA-256 hashes."""
    req = tmp_path / "requirements.txt"
    req.write_text(
        "requests==2.31.0 --hash=sha256:58cd2187c01e70e6e26505bca751777aa9f2f0b7f5304ac726abf254e2640301\n"
        "urllib3==2.2.1 --hash=sha256:450b73889241eb7614d9cf422dd81f335b71cb61d9a206cb9fb08d4a6f2355bb\n",
        encoding="utf-8"
    )

    verifier = DependencyVerifier(project_path=tmp_path)
    res = verifier.verify_dependencies()

    assert res.status == "PASS"
    assert res.total_dependencies == 2
    assert res.verified_count == 2
    assert res.mismatched_count == 0
    assert res.unverified_count == 0


def test_requirements_unverified_blocked(tmp_path):
    """Test requirements.txt without hashes fails when block_unverified is True."""
    req = tmp_path / "requirements.txt"
    req.write_text("requests==2.31.0\nurllib3==2.2.1\n", encoding="utf-8")

    verifier = DependencyVerifier(project_path=tmp_path)
    res = verifier.verify_dependencies(block_unverified=True)

    assert res.status == "FAIL"
    assert res.unverified_count == 2
    assert res.verified_count == 0
    assert "lack cryptographic integrity hashes" in res.details


def test_requirements_unverified_warning_when_allowed(tmp_path):
    """Test requirements.txt without hashes yields WARNING when block_unverified is False."""
    req = tmp_path / "requirements.txt"
    req.write_text("requests==2.31.0\n", encoding="utf-8")

    verifier = DependencyVerifier(project_path=tmp_path)
    res = verifier.verify_dependencies(block_unverified=False)

    assert res.status == "WARNING"
    assert res.unverified_count == 1


def test_package_lock_verified(tmp_path):
    """Test package-lock.json with valid SHA-512 integrity hashes."""
    pkg_lock = tmp_path / "package-lock.json"
    lock_data = {
        "name": "test-pkg",
        "lockfileVersion": 3,
        "packages": {
            "node_modules/react": {
                "version": "18.2.0",
                "integrity": "sha512-c283948192384910238401923849102839102384910283901283901283901283"
            }
        }
    }
    pkg_lock.write_text(json.dumps(lock_data), encoding="utf-8")

    verifier = DependencyVerifier(project_path=tmp_path)
    res = verifier.verify_dependencies()

    assert res.status == "PASS"
    assert res.verified_count == 1
    assert res.items[0].verification_method == "lockfile_sha512"


def test_package_lock_mismatch_fails(tmp_path):
    """Test package-lock.json with tampered integrity string."""
    pkg_lock = tmp_path / "package-lock.json"
    lock_data = {
        "name": "test-pkg",
        "lockfileVersion": 3,
        "packages": {
            "node_modules/malicious": {
                "version": "1.0.0",
                "integrity": "sha512-TAMPERED_SUBSTITUTION_ATTACK_000011112222333344445555"
            }
        }
    }
    pkg_lock.write_text(json.dumps(lock_data), encoding="utf-8")

    verifier = DependencyVerifier(project_path=tmp_path)
    res = verifier.verify_dependencies()

    assert res.status == "FAIL"
    assert res.mismatched_count == 1
    assert "Cryptographic hash mismatch" in res.details


def test_empty_workspace_passes(tmp_path):
    """Test directory with no dependencies passes gracefully."""
    verifier = DependencyVerifier(project_path=tmp_path)
    res = verifier.verify_dependencies()
    assert res.status == "PASS"
    assert res.total_dependencies == 0
