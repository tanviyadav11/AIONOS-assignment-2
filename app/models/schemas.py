from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DecisionType(str, Enum):
    AUTO_RESOLVED = "AUTO_RESOLVED"
    RESOLVED_WITH_INSTRUCTIONS = "RESOLVED_WITH_INSTRUCTIONS"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ESCALATED_SECURITY = "ESCALATED_SECURITY"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"

class CategoryEnum(str, Enum):
    PASSWORD_RESET = "Password Reset"
    VPN_ACCESS = "VPN Access"
    LAPTOP_REPLACEMENT = "Laptop Replacement"
    SOFTWARE_INSTALLATION = "Software Installation"
    PRINTER_TROUBLESHOOTING = "Printer Troubleshooting"
    EMAIL_MAILBOX_QUOTA = "Email Mailbox Quota"
    GUEST_WIFI = "Guest Wi-Fi"
    EXPENSE_SOFTWARE_ACCESS = "Expense Software Access"
    SECURITY_INCIDENT_REPORTING = "Security Incident Reporting"
    WFH_EQUIPMENT = "WFH Equipment"
    ADMIN_ACCESS = "Admin / Server Access"
    UNCLEAR_INSUFFICIENT = "Unclear / Insufficient Info"

class AuditStep(BaseModel):
    step_num: int
    step_name: str
    timestamp: str
    input_summary: str
    output_summary: str
    details: Dict[str, Any] = Field(default_factory=dict)
    rationale: str

class KnowledgeBaseArticle(BaseModel):
    kb_id: str
    title: str
    summary: str
    full_text: str
    category: str
    approvals_required: Optional[str] = None
    sla: Optional[str] = None
    self_service: bool = False
    special_notes: Optional[str] = None

class PrecedentTicket(BaseModel):
    ticket_id: str
    employee: str
    issue: str
    status: str
    category: Optional[str] = None
    relevance_notes: Optional[str] = None

class SeedRequest(BaseModel):
    id: str
    employee: str
    email: str
    date: str
    request: str
    status_so_far: str
    simulated_follow_up_answer: Optional[str] = None

class AgentReasoning(BaseModel):
    category: CategoryEnum
    confidence: float
    matched_kb_ids: List[str]
    matched_precedents: List[str]
    policy_conflict_detected: bool = False
    policy_conflict_summary: Optional[str] = None
    decision: DecisionType
    approver_if_any: Optional[str] = None
    sla_if_any: Optional[str] = None
    security_violation_flag: bool = False
    security_violation_details: Optional[str] = None
    follow_up_question: Optional[str] = None
    simulated_employee_response: Optional[str] = None
    employee_response_text: str
    sources_cited: List[str]
    reasoning_summary: str
    audit_trail: List[AuditStep]

class Ticket(BaseModel):
    ticket_id: str
    employee: str
    employee_email: Optional[str] = None
    category: str
    kb_sources: List[str]
    decision: DecisionType
    approver_if_any: Optional[str] = None
    sla_if_any: Optional[str] = None
    status: str
    created_at: str
    reasoning_summary: str
    original_request: str
    is_precedent: bool = False
    audit_trail: List[AuditStep] = Field(default_factory=list)

class ProcessRequestPayload(BaseModel):
    text: str
    employee_name: Optional[str] = "Employee"
    employee_email: Optional[str] = "employee@veridiancorp.example"
    request_id: Optional[str] = None
    follow_up_answer: Optional[str] = None
    interactive: Optional[bool] = False

class ProcessResponse(BaseModel):
    ticket: Optional[Ticket] = None
    reasoning: AgentReasoning
    needs_follow_up: bool
    follow_up_question: Optional[str] = None
    status: str
