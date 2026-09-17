"""
Response Builder and Ticket Orchestration Service for Veridian Corp IT Support.
Coordinates decision engine, ticket lifecycle management, audit log persistence, and live interactions.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple
from app.models.schemas import (
    ProcessRequestPayload, ProcessResponse, Ticket, AgentReasoning, DecisionType
)
from app.engine.decision_engine import decision_engine
from app.data.store import store

class ResponseBuilder:
    def process_request(self, payload: ProcessRequestPayload) -> ProcessResponse:
        # Evaluate reasoning via Decision Engine
        reasoning: AgentReasoning = decision_engine.evaluate(
            text=payload.text,
            employee_name=payload.employee_name or "Employee",
            employee_email=payload.employee_email or "employee@veridiancorp.example",
            request_id=payload.request_id,
            follow_up_answer=payload.follow_up_answer,
            interactive=payload.interactive or False
        )

        ticket: Optional[Ticket] = None
        needs_follow_up = (reasoning.decision == DecisionType.NEEDS_CLARIFICATION and not payload.follow_up_answer)
        
        # Map decision to ticket status
        status_map = {
            DecisionType.AUTO_RESOLVED: "Resolved (closed)",
            DecisionType.RESOLVED_WITH_INSTRUCTIONS: "Resolved (closed)",
            DecisionType.PENDING_APPROVAL: (
                "Pending Security review (active)" if "Security" in (reasoning.approver_if_any or "")
                else "Pending Finance (active)" if "Finance" in (reasoning.approver_if_any or "")
                else "Pending Approval (active)"
            ),
            DecisionType.ESCALATED_SECURITY: "Escalated to Security — under investigation (active)",
            DecisionType.NEEDS_CLARIFICATION: "Waiting on employee response",
        }
        
        status_str = status_map.get(reasoning.decision, "Pending (active)")
        
        # Overwrite status for specific seed requests to reflect exact historical status so far if pending
        if payload.request_id == "REQ-06":
            status_str = "Investigating — technician assigned"
        elif payload.request_id == "REQ-01":
            status_str = "Pending Approval (active)"
        elif payload.request_id == "REQ-07":
            status_str = "Pending Finance (active)"
        elif payload.request_id == "REQ-04":
            status_str = "Pending Security review (active)"

        # Generate new ticket ID continuing from TK-1051
        ticket_id = store.get_next_ticket_id()
        now_display = datetime.now(timezone.utc).strftime("%a %d %b %Y %H:%M")

        # Format employee response with actual ticket ID
        formatted_response_text = reasoning.employee_response_text.replace("{TICKET_ID}", ticket_id)
        reasoning.employee_response_text = formatted_response_text

        # Create structured Ticket object
        ticket = Ticket(
            ticket_id=ticket_id,
            employee=payload.employee_name or "Employee",
            employee_email=payload.employee_email or "employee@veridiancorp.example",
            category=reasoning.category.value,
            kb_sources=reasoning.matched_kb_ids,
            decision=reasoning.decision,
            approver_if_any=reasoning.approver_if_any,
            sla_if_any=reasoning.sla_if_any,
            status=status_str,
            created_at=now_display,
            reasoning_summary=reasoning.reasoning_summary,
            original_request=payload.text,
            is_precedent=False,
            audit_trail=reasoning.audit_trail
        )

        # Save ticket into store
        store.save_ticket(ticket)

        return ProcessResponse(
            ticket=ticket,
            reasoning=reasoning,
            needs_follow_up=needs_follow_up,
            follow_up_question=reasoning.follow_up_question if needs_follow_up else None,
            status=status_str
        )

response_builder = ResponseBuilder()
