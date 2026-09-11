"""
Unit Tests for Commit Verification Engine
Tests signed commits, unsigned commits, invalid signatures, unknown developers, and trusted developers.
"""

import pytest
from pathlib import Path
from backend.app.config import TrustedDeveloper, PROJECT_ROOT
from backend.app.services.commit_verifier import CommitVerifier
from backend.app.schemas.validation import CommitVerificationResult


def test_commit_verifier_non_git_repo(tmp_path):
    """Ensure verifier returns FAIL when run against a non-git directory."""
    verifier = CommitVerifier(repo_path=tmp_path)
    res = verifier.verify_commit()
    assert res.status == "FAIL"
    assert not res.signed
    assert not res.signature_valid
    assert not res.trusted_developer
    assert "not a valid Git repository" in res.details


def test_check_trusted_developer_match():
    """Verify trusted developer email and key matching logic."""
    verifier = CommitVerifier(repo_path=PROJECT_ROOT)
    verifier.trusted_developers = [
        TrustedDeveloper(
            name="Hari Prasath D",
            email="24mis0187@vitstudent.ac.in",
            key_id="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKeyHariPrasathZeroTrust2026",
            fingerprint="SHA256:HP9876543210HariPrasathDevSecOpsVIT24MIS0187",
            type="ssh",
            role="DevSecOps Lead",
            enabled=True
        ),
        TrustedDeveloper(
            name="Dhanush",
            email="dhanush1108samu@gmail.com",
            key_id="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKeyDhanushZeroTrust2026",
            type="ssh",
            role="Security Architect",
            enabled=True
        )
    ]

    # Matching developer by email
    is_trusted, dev = verifier._check_trusted_developer(
        author_email="24mis0187@vitstudent.ac.in",
        signer_info="Hari Prasath D <24mis0187@vitstudent.ac.in>",
        signer_key=None,
        sig_type="SSH"
    )
    assert is_trusted is True
    assert dev.name == "Hari Prasath D"

    # Matching developer by key fingerprint
    is_trusted, dev = verifier._check_trusted_developer(
        author_email="another@example.com",
        signer_info=None,
        signer_key="SHA256:HP9876543210HariPrasathDevSecOpsVIT24MIS0187",
        sig_type="SSH"
    )
    assert is_trusted is True

    # Untrusted attacker email
    is_trusted, dev = verifier._check_trusted_developer(
        author_email="attacker@exploit.org",
        signer_info="Attacker <attacker@exploit.org>",
        signer_key="SHA256:FAKEKEY000000000000000000000000000000000",
        sig_type="SSH"
    )
    assert is_trusted is False
    assert dev is None


def test_signature_detection_ssh():
    """Verify detection of SSH signatures in raw commit objects."""
    verifier = CommitVerifier(repo_path=PROJECT_ROOT)
    raw_ssh_commit = """tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904
author Developer <dev@example.com> 1726056000 +0000
committer Developer <dev@example.com> 1726056000 +0000
gpgsig -----BEGIN SSH SIGNATURE-----
U1NIU0lHAAAAAQAAADMAAAALc3NoLWVkMjU1MTkAAAAg...
-----END SSH SIGNATURE-----

Initial commit message
"""
    sig_type, payload = verifier._detect_signature(raw_ssh_commit)
    assert sig_type == "SSH"
    assert "BEGIN SSH SIGNATURE" in payload


def test_signature_detection_gpg():
    """Verify detection of GPG signatures in raw commit objects."""
    verifier = CommitVerifier(repo_path=PROJECT_ROOT)
    raw_gpg_commit = """tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904
author Developer <dev@example.com> 1726056000 +0000
committer Developer <dev@example.com> 1726056000 +0000
gpgsig -----BEGIN PGP SIGNATURE-----
Version: GnuPG v2
iQEcBAABCAAGBQJk...
-----END PGP SIGNATURE-----

Initial commit message
"""
    sig_type, payload = verifier._detect_signature(raw_gpg_commit)
    assert sig_type == "GPG"
    assert "BEGIN PGP SIGNATURE" in payload


def test_signature_detection_none():
    """Verify detection of unsigned commits."""
    verifier = CommitVerifier(repo_path=PROJECT_ROOT)
    raw_unsigned = """tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904
author Developer <dev@example.com> 1726056000 +0000
committer Developer <dev@example.com> 1726056000 +0000

Unsigned commit message
"""
    sig_type, payload = verifier._detect_signature(raw_unsigned)
    assert sig_type == "NONE"
    assert payload is None
