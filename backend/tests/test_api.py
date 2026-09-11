"""
Integration Tests for REST API Endpoints
Tests health, status, validation, runs, events, config, and simulation endpoints.
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["zero_trust_mode"] == "FAIL_CLOSED"


def test_api_status(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "READY"
    assert "policy" in data
    assert data["trusted_developers_count"] >= 2


def test_api_runs_list(client):
    res = client.get("/api/runs")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_api_events_list(client):
    res = client.get("/api/events")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_api_config(client):
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert "policy" in data
    assert "trusted_developers" in data


def test_api_demo_scenarios(client):
    """Test the 4 simulation endpoints and verify correct decision enforcement."""
    # Scenario 1: Legitimate
    r1 = client.post("/api/demo/run-legitimate")
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["final_decision"] == "ALLOW"
    assert d1["exit_code"] == 0

    # Scenario 2: Dependency attack
    r2 = client.post("/api/demo/simulate-dependency-attack")
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["final_decision"] == "BLOCK"
    assert d2["exit_code"] == 1

    # Scenario 3: Invalid commit
    r3 = client.post("/api/demo/simulate-invalid-commit")
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["final_decision"] == "BLOCK"
    assert d3["exit_code"] == 1

    # Scenario 4: Runner tampering
    r4 = client.post("/api/demo/simulate-runner-tampering")
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["final_decision"] == "BLOCK"
    assert d4["exit_code"] == 1

    # Scenario 5: Reset
    r5 = client.post("/api/demo/reset")
    assert r5.status_code == 200
    assert r5.json()["status"] == "RESET_COMPLETED"
