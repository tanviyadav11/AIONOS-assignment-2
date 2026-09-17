"""
In-memory and thread-safe data store for Tickets, Audit Logs, and Requests.
Seeds initial tickets (TK-1042..TK-1051) and allows auto-incrementing from TK-1052.
"""

import threading
from typing import Dict, List, Optional
from app.models.schemas import Ticket, DecisionType, AuditStep, SeedRequest
from app.data.seed_data import HISTORICAL_PRECEDENTS, SEED_REQUESTS

class DataStore:
    def __init__(self):
        self._lock = threading.RLock()
        self.tickets: Dict[str, Ticket] = {}
        self.audit_logs: Dict[str, List[AuditStep]] = {}
        self.requests: Dict[str, SeedRequest] = {}
        self._next_ticket_number = 1052
        self.reset_to_seed()

    def reset_to_seed(self):
        with self._lock:
            self.tickets.clear()
            self.audit_logs.clear()
            self.requests.clear()
            self._next_ticket_number = 1052

            # Seed requests
            for req in SEED_REQUESTS:
                self.requests[req.id] = req

            # Seed historical precedent tickets (TK-1042..TK-1051)
            for prec in HISTORICAL_PRECEDENTS:
                category_map = {
                    "TK-1042": ("VPN Access", ["KB-02"], DecisionType.RESOLVED_WITH_INSTRUCTIONS, None, "Immediate self-service"),
                    "TK-1043": ("Laptop Replacement", ["KB-03", "ASSET-POLICY"], DecisionType.PENDING_APPROVAL, "IT Approval + Finance Sign-off", "Standard cycle (2-week advance)"),
                    "TK-1044": ("Software Installation", ["KB-04"], DecisionType.PENDING_APPROVAL, "IT Security", "3–5 business days"),
                    "TK-1045": ("Email Mailbox Quota", ["KB-06"], DecisionType.RESOLVED_WITH_INSTRUCTIONS, "Manager approval", "Standard SLA"),
                    "TK-1046": ("Printer Troubleshooting", ["KB-05"], DecisionType.RESOLVED_WITH_INSTRUCTIONS, None, "Technician dispatched"),
                    "TK-1047": ("WFH Equipment", ["KB-10"], DecisionType.PENDING_APPROVAL, "Manager + Finance", "Procurement dependent"),
                    "TK-1048": ("Security Incident Reporting", ["KB-09"], DecisionType.ESCALATED_SECURITY, "IT Security Incident Response", "Immediate / High Priority"),
                    "TK-1049": ("Password Reset", ["KB-01"], DecisionType.RESOLVED_WITH_INSTRUCTIONS, None, "Operational queue"),
                    "TK-1050": ("Admin / Server Access", ["KB-08", "Access Policy"], DecisionType.PENDING_APPROVAL, "Finance / Manager Sign-off", "Rejected - Ineligible"),
                    "TK-1051": ("Guest Wi-Fi", ["KB-07"], DecisionType.AUTO_RESOLVED, None, "Immediate Kiosk"),
                }
                meta = category_map.get(prec.ticket_id, ("General IT", ["KB-01"], DecisionType.RESOLVED_WITH_INSTRUCTIONS, None, "N/A"))
                
                initial_audit = [
                    AuditStep(
                        step_num=1,
                        step_name="Historical Seeding",
                        timestamp="2026-09-21T09:00:00Z",
                        input_summary=f"Historical precedent ticket {prec.ticket_id}",
                        output_summary=f"Precedent recorded: {prec.status}",
                        details={"employee": prec.employee, "issue": prec.issue},
                        rationale=prec.relevance_notes or "Historical ticket for precedent matching."
                    )
                ]
                
                ticket = Ticket(
                    ticket_id=prec.ticket_id,
                    employee=prec.employee,
                    employee_email=f"{prec.employee.lower().replace(' ', '.').replace('.', '')}@veridiancorp.example",
                    category=meta[0],
                    kb_sources=meta[1],
                    decision=meta[2],
                    approver_if_any=meta[3],
                    sla_if_any=meta[4],
                    status=prec.status,
                    created_at="Mon 21 Sep 2026 09:00",
                    reasoning_summary=prec.relevance_notes or prec.issue,
                    original_request=prec.issue,
                    is_precedent=True,
                    audit_trail=initial_audit
                )
                self.tickets[ticket.ticket_id] = ticket
                self.audit_logs[ticket.ticket_id] = initial_audit

    def get_next_ticket_id(self) -> str:
        with self._lock:
            tid = f"TK-{self._next_ticket_number}"
            self._next_ticket_number += 1
            return tid

    def save_ticket(self, ticket: Ticket) -> Ticket:
        with self._lock:
            self.tickets[ticket.ticket_id] = ticket
            self.audit_logs[ticket.ticket_id] = ticket.audit_trail
            return ticket

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        with self._lock:
            return self.tickets.get(ticket_id)

    def list_tickets(self, status_filter: Optional[str] = None, category_filter: Optional[str] = None, search: Optional[str] = None) -> List[Ticket]:
        with self._lock:
            results = list(self.tickets.values())
            if status_filter:
                status_lower = status_filter.lower()
                if status_lower == "active":
                    results = [t for t in results if "closed" not in t.status.lower()]
                elif status_lower == "closed":
                    results = [t for t in results if "closed" in t.status.lower()]
                elif status_lower != "all":
                    results = [t for t in results if status_lower in t.status.lower()]

            if category_filter and category_filter != "All":
                results = [t for t in results if category_filter.lower() in t.category.lower()]

            if search:
                query = search.lower()
                results = [
                    t for t in results
                    if query in t.ticket_id.lower()
                    or query in t.employee.lower()
                    or query in t.original_request.lower()
                    or query in t.category.lower()
                    or query in t.reasoning_summary.lower()
                ]

            # Sort: Newest generated tickets first, then precedents
            return sorted(results, key=lambda t: t.ticket_id, reverse=True)

    def get_audit_trail(self, ticket_id: str) -> List[AuditStep]:
        with self._lock:
            return self.audit_logs.get(ticket_id, [])

    def list_requests(self) -> List[SeedRequest]:
        with self._lock:
            return list(self.requests.values())

    def get_request(self, req_id: str) -> Optional[SeedRequest]:
        with self._lock:
            return self.requests.get(req_id)

store = DataStore()
