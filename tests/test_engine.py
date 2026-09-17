"""
Unit and Integration Tests for Veridian Corp IT Support Agent.
Validates all 15 Data Pack Requests (REQ-01 to REQ-15),
Policy Conflict Surfacing (KB-03 vs Asset Management Policy),
Security Violation Detection (KB-09 Forwarding),
and Deterministic Source Citations.
"""

import pytest
from app.models.schemas import DecisionType, CategoryEnum, ProcessRequestPayload
from app.data.seed_data import SEED_REQUESTS
from app.engine.decision_engine import decision_engine
from app.engine.response_builder import response_builder
from app.data.store import store

@pytest.fixture(autouse=True)
def reset_store():
    store.reset_to_seed()

def test_req01_laptop_replacement_policy_conflict():
    """REQ-01: Aditi Sharma - Laptop dead, ~3.5 yrs old.
    Must detect conflict between KB-03 (3-yr) and Asset Policy (4-yr),
    require dual IT + Finance sign-off, and cite TK-1043.
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-01")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.PENDING_APPROVAL
    assert res.category == CategoryEnum.LAPTOP_REPLACEMENT
    assert res.policy_conflict_detected is True
    assert "KB-03" in res.matched_kb_ids
    assert "ASSET-POLICY" in res.matched_kb_ids
    assert "TK-1043" in res.matched_precedents
    assert "Finance Sign-off" in res.approver_if_any
    assert "IT" in res.approver_if_any

def test_req02_guest_wifi_auto_resolved():
    """REQ-02: Vikram Chawla - Guest Wi-Fi for visitor tomorrow.
    Must resolve directly via front-desk kiosk, no IT ticket required (KB-07).
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-02")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.AUTO_RESOLVED
    assert res.category == CategoryEnum.GUEST_WIFI
    assert "KB-07" in res.matched_kb_ids
    assert "TK-1051" in res.matched_precedents

def test_req03_password_lockout():
    """REQ-03: Karan Mehta - Locked out, 6 failed attempts.
    Must require IT manual unlock per KB-01, no approval needed, unstated SLA explicitly noted.
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-03")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.RESOLVED_WITH_INSTRUCTIONS
    assert res.category == CategoryEnum.PASSWORD_RESET
    assert "KB-01" in res.matched_kb_ids
    assert "TK-1049" in res.matched_precedents
    assert "No approval required" in res.approver_if_any or "None" in res.approver_if_any

def test_req04_non_catalog_software():
    """REQ-04: Ritu Bhatia - Install non-catalog data-analysis tool.
    Must route to IT Security review, with explicit 3-5 business days SLA (KB-04).
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-04")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.PENDING_APPROVAL
    assert res.category == CategoryEnum.SOFTWARE_INSTALLATION
    assert "KB-04" in res.matched_kb_ids
    assert "IT Security" in res.approver_if_any
    assert "3–5 business days" in res.sla_if_any or "3-5" in res.sla_if_any

def test_req05_vpn_fte_expired():
    """REQ-05: Sanjay Oberoi - VPN stopped, credentials expired.
    Must provide self-renewal instructions for FTE (KB-02).
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-05")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.RESOLVED_WITH_INSTRUCTIONS
    assert res.category == CategoryEnum.VPN_ACCESS
    assert "KB-02" in res.matched_kb_ids
    assert "TK-1042" in res.matched_precedents

def test_req06_printer_paper_jam():
    """REQ-06: Meera Iyer - 3rd floor printer false paper-jam.
    Must cite KB-05 (restart spooler) and assign technician.
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-06")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.RESOLVED_WITH_INSTRUCTIONS
    assert res.category == CategoryEnum.PRINTER_TROUBLESHOOTING
    assert "KB-05" in res.matched_kb_ids
    assert "TK-1046" in res.matched_precedents

def test_req07_wfh_equipment():
    """REQ-07: Farhan Ali - WFH 4 days/week, needs monitor.
    Must require Manager sign-off + Finance processing, IT ships once approved (KB-10).
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-07")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.PENDING_APPROVAL
    assert res.category == CategoryEnum.WFH_EQUIPMENT
    assert "KB-10" in res.matched_kb_ids
    assert "Manager" in res.approver_if_any
    assert "Finance" in res.approver_if_any

def test_req08_phishing_forward_security_violation():
    """REQ-08: Ananya Reddy - Phishing email forwarded to teammates.
    Must escalate to Security AND explicitly flag that forwarding was a policy violation (KB-09).
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-08")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.ESCALATED_SECURITY
    assert res.category == CategoryEnum.SECURITY_INCIDENT_REPORTING
    assert res.security_violation_flag is True
    assert "KB-09" in res.matched_kb_ids
    assert "violation" in res.security_violation_details.lower()
    assert "TK-1048" in res.matched_precedents

def test_req09_mailbox_full():
    """REQ-09: Rohit Desai - Mailbox full, can't send.
    Must advise archiving, note manager approval needed for increase, capped at 50GB (KB-06).
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-09")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.RESOLVED_WITH_INSTRUCTIONS
    assert res.category == CategoryEnum.EMAIL_MAILBOX_QUOTA
    assert "KB-06" in res.matched_kb_ids
    assert "50GB" in res.reasoning_summary or "50GB" in res.employee_response_text

def test_req10_urgent_admin_access():
    """REQ-10: Kavya Pillai - Wants admin access to finance reporting server, urgent.
    Must reject/require Finance & Manager justification, citing precedent TK-1050.
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-10")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.PENDING_APPROVAL
    assert res.category == CategoryEnum.ADMIN_ACCESS
    assert "TK-1050" in res.matched_precedents
    assert "Finance" in res.approver_if_any

def test_req11_contractor_vpn():
    """REQ-11: Nikhil Bansal - New contractor needs VPN access.
    Must require manager approval via access request form (KB-02).
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-11")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.PENDING_APPROVAL
    assert res.category == CategoryEnum.VPN_ACCESS
    assert "KB-02" in res.matched_kb_ids
    assert "Manager approval" in res.approver_if_any

def test_req12_expense_tool_login():
    """REQ-12: Sneha Kulkarni - Can't log into expense tool.
    Must clarify if active account exists (KB-08).
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-12")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.NEEDS_CLARIFICATION
    assert res.category == CategoryEnum.EXPENSE_SOFTWARE_ACCESS
    assert "KB-08" in res.matched_kb_ids

def test_req13_laptop_flickering_diagnostic_followup():
    """REQ-13: Aman Gupta - Laptop screen flickering, 2 yrs old, maybe just needs repair.
    Must ask diagnostic follow-up before deciding repair vs replace.
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-13")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.NEEDS_CLARIFICATION
    assert res.category == CategoryEnum.LAPTOP_REPLACEMENT
    assert res.follow_up_question is not None

def test_req14_browser_extension_productivity():
    """REQ-14: Tanya Chopra - Browser extension (productivity tracking).
    Must treat as non-catalog software + flag privacy/monitoring sensitivity (KB-04).
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-14")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.PENDING_APPROVAL
    assert res.category == CategoryEnum.SOFTWARE_INSTALLATION
    assert "KB-04" in res.matched_kb_ids
    assert "3–5 business days" in res.sla_if_any or "3-5" in res.sla_if_any
    assert "privacy" in res.reasoning_summary.lower() or "monitoring" in res.reasoning_summary.lower()

def test_req15_vague_request_clarification():
    """REQ-15: Rahul Menon - 'hey can you help, its not working'.
    Must ask clarifying question without guessing.
    """
    req = next(r for r in SEED_REQUESTS if r.id == "REQ-15")
    res = decision_engine.evaluate(
        text=req.request,
        employee_name=req.employee,
        employee_email=req.email,
        request_id=req.id
    )
    assert res.decision == DecisionType.NEEDS_CLARIFICATION
    assert res.category == CategoryEnum.UNCLEAR_INSUFFICIENT
    assert res.follow_up_question is not None

def test_ticket_id_auto_increment():
    """Verifies that new tickets start at TK-1052 and increment properly."""
    res1 = response_builder.process_request(ProcessRequestPayload(
        text="Guest Wi-Fi for client",
        employee_name="Alice Test",
        employee_email="alice@veridiancorp.example"
    ))
    assert res1.ticket.ticket_id == "TK-1052"

    res2 = response_builder.process_request(ProcessRequestPayload(
        text="Locked out after 6 attempts",
        employee_name="Bob Test",
        employee_email="bob@veridiancorp.example"
    ))
    assert res2.ticket.ticket_id == "TK-1053"
