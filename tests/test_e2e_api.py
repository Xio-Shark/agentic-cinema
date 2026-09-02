"""
End-to-End API and Web Integration Tests for CineOps Studio.
"""

import pytest
from fastapi.testclient import TestClient
from services.api_server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_health_endpoint(client):
    """Verify health endpoint response."""
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "HEALTHY"
    assert "mcp_tools_available" in data


def test_api_scenarios_endpoint(client):
    """Verify scenario catalog response."""
    r = client.get("/api/scenarios")
    assert r.status_code == 200
    data = r.json()
    assert len(data["scenarios"]) == 2
    ids = [s["id"] for s in data["scenarios"]]
    assert "microservice_rescue" in ids
    assert "agent_observability" in ids


def test_api_production_start_and_clear(client):
    """Verify production triggering."""
    r = client.post(
        "/api/production/start",
        json={
            "scenario_type": "microservice_rescue",
            "mode": "replay",
            "interval_sec": 0.01,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "STARTED"

    r_clear = client.post("/api/production/clear")
    assert r_clear.status_code == 200
    assert r_clear.json()["status"] == "CLEARED"

    # Test agent_observability scenario start
    r_obs = client.post(
        "/api/production/start",
        json={
            "scenario_type": "agent_observability",
            "mode": "replay",
            "interval_sec": 0.01,
        },
    )
    assert r_obs.status_code == 200
    assert r_obs.json()["scenario_type"] == "agent_observability"


def test_static_web_console_serving(client):
    """Verify the web console HTML is served properly."""
    r = client.get("/")
    assert r.status_code == 200
    assert "CineOps Studio" in r.text
    assert "Production Storyboard" in r.text
