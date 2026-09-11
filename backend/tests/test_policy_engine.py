"""
Unit Tests for Zero-Trust Policy Engine
Tests all-pass scenario, individual failure vectors, multiple failures, and fail-closed enforcement.
"""

import pytest
from backend.app.config import PolicyRules
from backend.app.services.policy_engine import PolicyEngine
from backend.app.schemas.validation import (
    CommitVerificationResult,
    DependencyVerificationResult,
    RunnerIntegrityResult
)


@pytest.fixture
def clean_commit():
    return CommitVerificationResult(
        commit_hash="a1b2c3d4e5f67890abcdef1234567890abcdef12",
        short_hash="a1b2c3d",
        author_name="Hari Prasath D",
        author_email="24mis0187@vitstudent.ac.in",
        committer_name="Hari Prasath D",
        committer_email="24mis0187@vitstudent.ac.in",
        commit_date="2026-09-11 12:00:00 UTC",
        commit_message="feat: verified commit",
        signed=True,
        signature_type="SSH",
        signature_valid=True,
        trusted_developer=True,
        status="PASS"
    )


@pytest.fixture
def clean_dependencies():
    return DependencyVerificationResult(
        status="PASS",
        total_dependencies=5,
        verified_count=5,
        unverified_count=0,
        mismatched_count=0,
        missing_count=0
    )


@pytest.fixture
def clean_runner():
    return RunnerIntegrityResult(
        status="CLEAN",
        integrity_score=100,
        monitored_files_count=10,
        matched_files_count=10,
        tampered_files_count=0,
        missing_files_count=0
    )


def test_policy_all_pass_allows_build(clean_commit, clean_dependencies, clean_runner):
    """When commit, dependencies, and runner all pass, build is ALLOWED."""
    engine = PolicyEngine(policy=PolicyRules(fail_closed=True))
    decision = engine.evaluate(clean_commit, clean_dependencies, clean_runner)

    assert decision.decision == "ALLOW"
    assert decision.score >= 85
    assert len(decision.reasons) > 0
    assert "passed" in decision.reasons[0].lower()


def test_policy_unsigned_commit_blocks(clean_commit, clean_dependencies, clean_runner):
    """Unsigned commit triggers immediate BUILD BLOCKED."""
    clean_commit.signed = False
    clean_commit.signature_valid = False
    clean_commit.status = "FAIL"

    engine = PolicyEngine(policy=PolicyRules(require_signed_commit=True))
    decision = engine.evaluate(clean_commit, clean_dependencies, clean_runner)

    assert decision.decision == "BLOCK"
    assert any("Commit is unsigned" in r for r in decision.reasons)


def test_policy_untrusted_developer_blocks(clean_commit, clean_dependencies, clean_runner):
    """Valid signature by untrusted developer triggers BUILD BLOCKED."""
    clean_commit.trusted_developer = False
    clean_commit.status = "FAIL"

    engine = PolicyEngine(policy=PolicyRules(require_trusted_developer=True))
    decision = engine.evaluate(clean_commit, clean_dependencies, clean_runner)

    assert decision.decision == "BLOCK"
    assert any("not in authorized trusted_developers.yaml" in r for r in decision.reasons)


def test_policy_dependency_mismatch_blocks(clean_commit, clean_dependencies, clean_runner):
    """Dependency hash mismatch triggers BUILD BLOCKED."""
    clean_dependencies.mismatched_count = 1
    clean_dependencies.status = "FAIL"

    engine = PolicyEngine(policy=PolicyRules(block_dependency_mismatch=True))
    decision = engine.evaluate(clean_commit, clean_dependencies, clean_runner)

    assert decision.decision == "BLOCK"
    assert any("dependency hash mismatch" in r for r in decision.reasons)


def test_policy_runner_tampered_blocks(clean_commit, clean_dependencies, clean_runner):
    """Runner host tampering triggers BUILD BLOCKED."""
    clean_runner.status = "TAMPERED"
    clean_runner.tampered_files_count = 1

    engine = PolicyEngine(policy=PolicyRules(require_runner_integrity=True))
    decision = engine.evaluate(clean_commit, clean_dependencies, clean_runner)

    assert decision.decision == "BLOCK"
    assert any("Runner Integrity Failure" in r for r in decision.reasons)
