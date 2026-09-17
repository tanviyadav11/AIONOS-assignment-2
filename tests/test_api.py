"""
Integration tests for FastAPI REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.store import store

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_store():
    store.reset_to_seed()

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["company"] == "Veridian Corp"

def test_get_requests():
    response = client.get("/api/requests")
    assert response.status_code == 200
    requests = response.json()
    assert len(requests) == 15
    assert requests[0]["id"] == "REQ-01"

def test_get_tickets():
    response = client.get("/api/tickets")
    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) >= 10
    assert any(t["ticket_id"] == "TK-1043" for t in tickets)

def test_process_request_endpoint():
    payload = {
        "text": "Guest Wi-Fi for visitor tomorrow",
        "employee_name": "Vikram Chawla",
        "employee_email": "vikram.chawla@veridiancorp.example",
        "request_id": "REQ-02"
    }
    response = client.post("/api/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["reasoning"]["decision"] == "AUTO_RESOLVED"
    assert data["ticket"]["ticket_id"] == "TK-1052"
    assert "KB-07" in data["reasoning"]["matched_kb_ids"]

def test_audit_endpoint():
    # Process a request
    payload = {
        "text": "Laptop completely dead, ~3.5 yrs old",
        "employee_name": "Aditi Sharma",
        "employee_email": "aditi.sharma@veridiancorp.example",
        "request_id": "REQ-01"
    }
    res = client.post("/api/process", json=payload)
    tid = res.json()["ticket"]["ticket_id"]

    # Fetch audit
    audit_res = client.get(f"/api/audit/{tid}")
    assert audit_res.status_code == 200
    steps = audit_res.json()
    assert len(steps) >= 3
    assert steps[0]["step_name"] == "Intake & Classification"
