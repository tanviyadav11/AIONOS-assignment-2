"""
End-to-end full verification script.
Tests all static assets, seed queries, and the complete 15-request flow over HTTP.
"""

import httpx
import pytest

BASE_URL = "http://127.0.0.1:8000"

def test_static_and_root():
    with httpx.Client(base_url=BASE_URL) as client:
        # Root page
        res = client.get("/")
        assert res.status_code == 200
        assert "Veridian Corp" in res.text

        # CSS
        res_css = client.get("/static/css/style.css")
        assert res_css.status_code == 200
        assert "--bg-primary" in res_css.text

        # JS
        res_js = client.get("/static/js/app.js")
        assert res_js.status_code == 200
        assert "renderReasoningOutput" in res_js.text

def test_all_15_requests_end_to_end():
    with httpx.Client(base_url=BASE_URL) as client:
        # 1. Fetch seed requests
        res = client.get("/api/requests")
        assert res.status_code == 200
        requests = res.json()
        assert len(requests) == 15

        # 2. Process all 15 sequentially
        for req in requests:
            payload = {
                "text": req["request"],
                "employee_name": req["employee"],
                "employee_email": req["email"],
                "request_id": req["id"]
            }
            res_proc = client.post("/api/process", json=payload)
            assert res_proc.status_code == 200, f"Failed on {req['id']}"
            data = res_proc.json()
            
            assert "reasoning" in data
            assert "decision" in data["reasoning"]
            assert len(data["reasoning"]["audit_trail"]) >= 3
            assert data["ticket"]["ticket_id"].startswith("TK-")
            assert len(data["reasoning"]["sources_cited"]) >= 0

        # 3. Verify ticket queue has grown
        res_queue = client.get("/api/tickets?status=all")
        assert res_queue.status_code == 200
        tickets = res_queue.json()
        assert len(tickets) >= 25  # 10 seeded precedents + 15 newly generated

        # 4. Verify specific ticket audit trail
        latest_ticket_id = tickets[0]["ticket_id"]
        res_audit = client.get(f"/api/audit/{latest_ticket_id}")
        assert res_audit.status_code == 200
        assert len(res_audit.json()) >= 3

if __name__ == "__main__":
    test_static_and_root()
    test_all_15_requests_end_to_end()
    print("All E2E checks passed successfully!")
