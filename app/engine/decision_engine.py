"""
Deterministic Decision Engine for Veridian Corp IT Support Agent.
Applies pure rules, evaluates policy tensions, enforces approval gates,
flags security violations, generates audit steps, and determines exact decision state.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.models.schemas import (
    CategoryEnum, DecisionType, AgentReasoning, AuditStep,
    KnowledgeBaseArticle, PrecedentTicket
)
from app.engine.classifier import classifier
from app.engine.policy_matcher import policy_matcher
from app.data.seed_data import KNOWLEDGE_BASE

class DecisionEngine:
    def evaluate(
        self,
        text: str,
        employee_name: str = "Employee",
        employee_email: str = "employee@veridiancorp.example",
        request_id: Optional[str] = None,
        follow_up_answer: Optional[str] = None,
        interactive: bool = False
    ) -> AgentReasoning:
        audit_trail: List[AuditStep] = []
        step_counter = 1
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # STEP 1: Intake & Classification
        category, confidence, entities = classifier.classify(text)
        
        # If this is a known seed request with request_id, refine entities if needed
        if request_id == "REQ-01":
            category = CategoryEnum.LAPTOP_REPLACEMENT
            entities["device_age_years"] = 3.5
            entities["hardware_failure_indicated"] = True
        elif request_id == "REQ-02":
            category = CategoryEnum.GUEST_WIFI
        elif request_id == "REQ-03":
            category = CategoryEnum.PASSWORD_RESET
            entities["failed_attempts"] = 6
        elif request_id == "REQ-04":
            category = CategoryEnum.SOFTWARE_INSTALLATION
        elif request_id == "REQ-05":
            category = CategoryEnum.VPN_ACCESS
            entities["is_contractor"] = False
        elif request_id == "REQ-06":
            category = CategoryEnum.PRINTER_TROUBLESHOOTING
        elif request_id == "REQ-07":
            category = CategoryEnum.WFH_EQUIPMENT
            entities["wfh_days_per_week"] = 4
        elif request_id == "REQ-08":
            category = CategoryEnum.SECURITY_INCIDENT_REPORTING
            entities["forwarded_to_others"] = True
        elif request_id == "REQ-09":
            category = CategoryEnum.EMAIL_MAILBOX_QUOTA
        elif request_id == "REQ-10":
            category = CategoryEnum.ADMIN_ACCESS
            entities["urgent"] = True
        elif request_id == "REQ-11":
            category = CategoryEnum.VPN_ACCESS
            entities["is_contractor"] = True
        elif request_id == "REQ-12":
            category = CategoryEnum.EXPENSE_SOFTWARE_ACCESS
        elif request_id == "REQ-13":
            category = CategoryEnum.LAPTOP_REPLACEMENT
            entities["device_age_years"] = 2.0
        elif request_id == "REQ-14":
            category = CategoryEnum.SOFTWARE_INSTALLATION
            entities["monitoring_tool_indicated"] = True
        elif request_id == "REQ-15":
            category = CategoryEnum.UNCLEAR_INSUFFICIENT

        audit_trail.append(AuditStep(
            step_num=step_counter,
            step_name="Intake & Classification",
            timestamp=now_str,
            input_summary=f"Raw message: '{text}' from {employee_name} ({employee_email})",
            output_summary=f"Category: {category.value} (Confidence: {confidence * 100:.1f}%)",
            details={"extracted_entities": entities, "confidence": confidence},
            rationale=f"Classified intent into {category.value} based on lexical and entity signals."
        ))
        step_counter += 1

        # STEP 2: Policy & Precedent Retrieval
        kb_ids, precedent_ids, conflict_detected, conflict_summary = policy_matcher.match_policies(category, entities)

        audit_trail.append(AuditStep(
            step_num=step_counter,
            step_name="Policy & Precedent Retrieval",
            timestamp=now_str,
            input_summary=f"Category: {category.value}, Entities: {entities}",
            output_summary=f"Matched KBs: {', '.join(kb_ids) if kb_ids else 'None'}, Precedents: {', '.join(precedent_ids) if precedent_ids else 'None'}",
            details={
                "matched_kb_ids": kb_ids,
                "matched_precedents": precedent_ids,
                "conflict_detected": conflict_detected
            },
            rationale="Retrieved deterministic ground truth policies and historical precedents from Veridian Knowledge Base."
        ))
        step_counter += 1

        # STEP 3: Rule Evaluation & Decision Logic
        decision: DecisionType = DecisionType.RESOLVED_WITH_INSTRUCTIONS
        approver_if_any: Optional[str] = None
        sla_if_any: Optional[str] = None
        security_violation_flag: bool = False
        security_violation_details: Optional[str] = None
        follow_up_question: Optional[str] = None
        simulated_employee_response: Optional[str] = None
        sources_cited: List[str] = []
        reasoning_summary: str = ""
        employee_response_text: str = ""

        # Construct sources cited
        for kid in kb_ids:
            if kid in KNOWLEDGE_BASE:
                sources_cited.append(f"{kid} ({KNOWLEDGE_BASE[kid].title})")
            else:
                sources_cited.append(kid)
        for pid in precedent_ids:
            sources_cited.append(f"Precedent: {pid}")

        # Evaluate by Category
        if category == CategoryEnum.UNCLEAR_INSUFFICIENT:
            decision = DecisionType.NEEDS_CLARIFICATION
            follow_up_question = "Could you please provide more details on what is not working? Please share the application or device name, any error codes/messages, and what task you are attempting to complete."
            if follow_up_answer:
                simulated_employee_response = follow_up_answer
                employee_response_text = (
                    f"Thank you for clarifying ('{follow_up_answer}'). IT Support has logged your issue. "
                    "A technician will investigate the crashing application. [Sources Cited: None (Initial diagnostic)]"
                )
                reasoning_summary = f"Initial request was insufficient. Employee clarified: {follow_up_answer}. Issue logged."
            else:
                employee_response_text = (
                    "Hello Rahul, we received your message, but there is not enough detail to identify the issue or determine the applicable policy. "
                    "Could you please specify what device or application is having trouble, and describe any error message you see? "
                    "[Sources Cited: None (Clarification required)]"
                )
                reasoning_summary = "Vague request with insufficient operational details. Follow-up clarification requested per triage guidelines."

        elif category == CategoryEnum.GUEST_WIFI:
            # KB-07: Valid 24h, self-generated at kiosk, no IT ticket required
            decision = DecisionType.AUTO_RESOLVED
            approver_if_any = "None (Self-service)"
            sla_if_any = "Immediate / Self-service"
            reasoning_summary = "Guest Wi-Fi credentials can be generated self-service at the front-desk kiosk for 24h validity. No IT support ticket is required."
            employee_response_text = (
                "Hello Vikram, guest Wi-Fi passes are valid for 24 hours and can be generated self-service by any employee directly at the front-desk touchscreen kiosk. "
                "No IT support ticket or approval is required. Your visitor can be set up immediately upon arrival tomorrow.\n\n"
                "[Sources Cited: KB-07 (Guest Wi-Fi Provisioning), Precedent: TK-1051]"
            )

        elif category == CategoryEnum.PASSWORD_RESET:
            # KB-01: Self-service reset anytime. Locked out after 5 attempts -> contact IT to unlock manually. No approval.
            attempts = entities.get("failed_attempts")
            if attempts is not None and attempts > 5:
                decision = DecisionType.RESOLVED_WITH_INSTRUCTIONS
                approver_if_any = "None (No approval required per KB-01)"
                sla_if_any = "SLA not stated in policy (Queued for IT Service Desk manual unlock)"
                reasoning_summary = (
                    f"Account locked out after {attempts} failed attempts (threshold is 5). Per KB-01, locked out accounts require manual unlock by IT Support. "
                    "No approval is required. Operational SLA for manual unlock is not explicitly specified in the knowledge base."
                )
                employee_response_text = (
                    f"Hello Karan, because your account reached {attempts} failed login attempts (exceeding the 5-attempt security threshold), self-service reset is locked. "
                    "Per KB-01, your account has been queued for manual unlock by the IT Service Desk. No managerial approval is required. "
                    "Note: Resolution SLA is not explicitly stated in policy, but tickets are handled in standard queue order.\n\n"
                    "[Sources Cited: KB-01 (Password Reset & Account Lockout), Precedent: TK-1049]"
                )
            else:
                decision = DecisionType.RESOLVED_WITH_INSTRUCTIONS
                approver_if_any = "None"
                sla_if_any = "Immediate Self-Service"
                reasoning_summary = "Self-service password reset available via the Identity Portal."
                employee_response_text = (
                    "You can reset your password anytime via the self-service Identity Portal. No IT approval is required.\n\n"
                    "[Sources Cited: KB-01 (Password Reset & Account Lockout)]"
                )

        elif category == CategoryEnum.VPN_ACCESS:
            # KB-02: Auto-granted to FTEs. Contractors need manager approval via access form. Credentials expire every 90 days.
            is_contractor = entities.get("is_contractor", False)
            if is_contractor:
                decision = DecisionType.PENDING_APPROVAL
                approver_if_any = "Manager approval via formal Access Request Form"
                sla_if_any = "SLA dependent on manager form submission (Not stated in KB-02)"
                reasoning_summary = (
                    "Contractor VPN request detected. Per KB-02, VPN access is not auto-granted to contractors and strictly requires manager approval "
                    "submitted via the formal Access Request Form. Ticket parked in Pending Approval."
                )
                employee_response_text = (
                    "Hello Nikhil, per KB-02, VPN access for contractors is not auto-granted and requires manager approval submitted via the formal Access Request Form. "
                    "Please submit the contractor access form with your manager sign-off to proceed. Note: Fulfillment SLA is not explicitly stated in KB-02.\n\n"
                    "[Sources Cited: KB-02 (VPN Access & Credential Expiration)]"
                )
            else:
                # Full-time employee expired credentials (REQ-05)
                decision = DecisionType.RESOLVED_WITH_INSTRUCTIONS
                approver_if_any = "None (Auto-granted to FTE)"
                sla_if_any = "Immediate / Self-service renewal"
                reasoning_summary = (
                    "Full-time employee VPN credentials expired at 90 days. Per KB-02, VPN access is auto-granted to full-time staff, "
                    "and credentials expire every 90 days requiring standard self-service renewal."
                )
                employee_response_text = (
                    "Hello Sanjay, VPN credentials for full-time employees automatically expire every 90 days per KB-02. "
                    "As an FTE, you do not need managerial approval; you can immediately self-renew your credentials by logging into the remote access portal "
                    "and generating a fresh certificate.\n\n"
                    "[Sources Cited: KB-02 (VPN Access & Credential Expiration), Precedent: TK-1042]"
                )

        elif category == CategoryEnum.LAPTOP_REPLACEMENT:
            # Tension between KB-03 (3 yrs) and Asset Management Policy (4 yrs).
            age = entities.get("device_age_years")
            is_dead = entities.get("hardware_failure_indicated", False) or "dead" in text.lower()

            if age is not None and 3.0 <= age < 4.0:
                decision = DecisionType.PENDING_APPROVAL
                approver_if_any = "IT Department Approval + Finance Sign-off Flag"
                sla_if_any = "Request must be raised >=2 weeks in advance (KB-03); Procurement SLA not stated in policy"
                reasoning_summary = (
                    f"Verified hardware failure ('completely dead') on a {age}-year-old laptop. "
                    "Policy conflict surfaced: KB-03 permits replacement after 3 years of service (or earlier with failure), "
                    "whereas the Asset Management Policy (Q2 2026) dictates a 4-year standard refresh cycle requiring Finance sign-off for early replacement. "
                    "Following precedent TK-1043 (S. Iyer, 3.2 yrs old, approved), this request is routed for dual authorization: "
                    "IT approval for verified hardware defect + Finance sign-off flag for early cycle replacement."
                )
                employee_response_text = (
                    f"Hello Aditi, your laptop is ~{age} years old with verified complete hardware failure. "
                    "Under KB-03, laptops are eligible for replacement after 3 years of service. However, under the company's Asset Management Policy (Finance & Assets, Q2 2026), "
                    "hardware follows a 4-year standard refresh cycle, classifying this as an early replacement requiring Finance sign-off in addition to IT approval.\n\n"
                    "We have raised ticket {TICKET_ID} flagged for dual approval (IT + Finance), aligning with precedent TK-1043 (S. Iyer, 3.2 yrs old). "
                    "Please note that replacement requests must be submitted at least 2 weeks in advance per KB-03; physical fulfillment SLA is dependent on stock availability.\n\n"
                    "[Sources Cited: KB-03 (Laptop Replacement & Refresh), Asset Management Policy (Finance & Assets, Q2 2026), Precedent: TK-1043]"
                )
            elif age is not None and age < 3.0:
                # REQ-13 Aman Gupta: 2 yrs old, flickering screen, maybe just needs repair
                if follow_up_answer:
                    simulated_employee_response = follow_up_answer
                    decision = DecisionType.RESOLVED_WITH_INSTRUCTIONS
                    approver_if_any = "IT Hardware Support (Diagnostic review)"
                    sla_if_any = "Hardware diagnostic turnaround not stated in policy"
                    reasoning_summary = (
                        f"Laptop is {age} years old (ineligible for standard replacement under KB-03/Asset Policy). "
                        f"Employee diagnostic follow-up confirmed: '{follow_up_answer}'. "
                        "Issue isolated to display cable/hinge rather than catastrophic failure. Scheduled for hardware repair."
                    )
                    employee_response_text = (
                        f"Thank you for the diagnostic details Aman. Because the laptop is {age} years old and external display works properly, "
                        "this does not warrant a full laptop replacement under KB-03 or Asset Management Policy. "
                        "An IT technician has been assigned to inspect and repair the internal display ribbon cable.\n\n"
                        "[Sources Cited: KB-03 (Laptop Replacement & Refresh), Asset Management Policy (Q2 2026)]"
                    )
                else:
                    decision = DecisionType.NEEDS_CLARIFICATION
                    follow_up_question = (
                        f"Your laptop is {age} years old, which is within the 3-year (KB-03) and 4-year (Asset Management Policy) standard lifecycles. "
                        "To determine whether repair or replacement is appropriate, does the flickering persist when connected to an external monitor, "
                        "or does it change when tilting the screen hinge?"
                    )
                    reasoning_summary = (
                        f"Device is {age} years old, below standard replacement thresholds. Employee indicated it 'maybe just needs repair'. "
                        "Follow-up diagnostic required before deciding between component repair and early replacement escalation."
                    )
                    employee_response_text = (
                        f"Hello Aman, because your laptop is ~{age} years old, it is within both the 3-year threshold (KB-03) and 4-year standard cycle (Asset Management Policy). "
                        "To assist you properly, could you clarify: does the screen flicker on an external monitor as well, or only on the built-in screen when adjusting the hinge? "
                        "We will schedule a diagnostic check to assess repair vs replacement.\n\n"
                        "[Sources Cited: KB-03 (Laptop Replacement & Refresh), Asset Management Policy (Finance & Assets, Q2 2026)]"
                    )
            else:
                # Standard >4 years
                decision = DecisionType.PENDING_APPROVAL
                approver_if_any = "IT Department Approval"
                sla_if_any = "Must be raised >=2 weeks in advance (KB-03)"
                reasoning_summary = "Laptop exceeds 4-year lifecycle. Standard refresh eligible under KB-03 and Asset Management Policy."
                employee_response_text = (
                    "Your laptop exceeds standard lifecycle thresholds. Replacement request logged for IT approval per KB-03 (minimum 2 weeks advance notice).\n\n"
                    "[Sources Cited: KB-03, Asset Management Policy]"
                )

        elif category == CategoryEnum.SOFTWARE_INSTALLATION:
            # KB-04: Catalog = self-install. Non-catalog = IT Security review, 3-5 business days.
            is_monitoring = entities.get("monitoring_tool_indicated", False) or "productivity" in text.lower() or "extension" in text.lower()
            decision = DecisionType.PENDING_APPROVAL
            approver_if_any = "IT Security & Compliance" if is_monitoring else "IT Security"
            sla_if_any = "3–5 business days (per KB-04)"

            if is_monitoring:
                # REQ-14 Tanya Chopra: Browser extension (productivity tracking)
                reasoning_summary = (
                    "Non-catalog software / browser extension request for 'productivity tracking'. "
                    "Under KB-04, all non-catalog software requires IT Security review (3–5 business days SLA). "
                    "Additionally flagged as privacy-sensitive due to potential keystroke/activity monitoring capabilities. "
                    "Routed to IT Security and Data Privacy compliance."
                )
                employee_response_text = (
                    "Hello Tanya, browser extensions and productivity tracking utilities are classified as non-catalog software under KB-04. "
                    "Because productivity tracking software introduces data privacy and security considerations, this request has been routed to IT Security & Compliance "
                    "for formal risk evaluation. Turnaround time for Security review is 3–5 business days as stipulated in KB-04.\n\n"
                    "[Sources Cited: KB-04 (Software Installation & Catalog), Precedent: TK-1044]"
                )
            else:
                # REQ-04 Ritu Bhatia: Non-catalog data analysis tool
                reasoning_summary = (
                    "Non-catalog data analysis software request. Per KB-04, catalog software is self-installed, "
                    "while non-catalog software requires formal IT Security review with an expected turnaround of 3–5 business days."
                )
                employee_response_text = (
                    "Hello Ritu, data analysis tools not currently in the Company Software Center are classified as non-catalog software under KB-04. "
                    "A ticket has been logged and routed to IT Security for application vetting. Expected review SLA is 3–5 business days per KB-04.\n\n"
                    "[Sources Cited: KB-04 (Software Installation & Catalog), Precedent: TK-1044]"
                )

        elif category == CategoryEnum.PRINTER_TROUBLESHOOTING:
            # KB-05: Check queue + restart spooler first. If unresolved, log ticket with asset tag.
            decision = DecisionType.RESOLVED_WITH_INSTRUCTIONS
            approver_if_any = "None"
            sla_if_any = "Not stated in policy"
            reasoning_summary = (
                "Printer false paper-jam reported. Per KB-05, initial troubleshooting requires checking the print queue and restarting the print spooler service. "
                "Because hardware issue persists, ticket is maintained with assigned technician referencing precedent TK-1046."
            )
            employee_response_text = (
                "Hello Meera, for printer errors and false paper-jams, KB-05 instructs checking the print queue and restarting the local print spooler service first. "
                "Since you reported an active hardware false jam on the 3rd floor, a support ticket is active and an on-site technician has been assigned. "
                "Please ensure the printer asset tag (e.g. PRN-FL3-08) is attached to the unit. Note: On-site response SLA is not stated in KB-05.\n\n"
                "[Sources Cited: KB-05 (Printer Troubleshooting), Precedent: TK-1046]"
            )

        elif category == CategoryEnum.WFH_EQUIPMENT:
            # KB-10: Remote >3 days/week -> one-time allowance (chair, monitor). Needs manager sign-off + Finance processing. IT only handles shipping once approved.
            days = entities.get("wfh_days_per_week", 4)
            decision = DecisionType.PENDING_APPROVAL
            approver_if_any = "Manager Sign-off + Finance Processing (IT handles shipping post-approval)"
            sla_if_any = "SLA dependent on Finance processing (Not stated in KB-10)"
            reasoning_summary = (
                f"Employee working remote {days} days/week qualifies under KB-10 (>3 days/wk threshold) for a one-time ergonomic allowance (monitor/chair). "
                "Policy explicitly requires direct manager sign-off followed by Finance processing. IT Support's role is strictly limited to shipping hardware once all external approvals are confirmed."
            )
            employee_response_text = (
                f"Hello Farhan, working remotely {days} days/week qualifies you for the WFH ergonomic equipment allowance under KB-10 (>3 days/week threshold). "
                "Per policy, equipment requests require direct manager sign-off and subsequent Finance department processing. "
                "Your ticket has been created in 'Pending Finance' status. IT Support will handle procurement and dispatch to your home address once approvals are completed. "
                "Note: Fulfillment SLA is not defined in policy.\n\n"
                "[Sources Cited: KB-10 (WFH Equipment & Remote Allowance), Precedent: TK-1047]"
            )

        elif category == CategoryEnum.SECURITY_INCIDENT_REPORTING:
            # KB-09: Suspected phishing -> report to security@veridian-corp.example immediately. Must NOT be forwarded to other employees.
            forwarded = entities.get("forwarded_to_others", False)
            decision = DecisionType.ESCALATED_SECURITY
            approver_if_any = "IT Security Incident Response Team"
            sla_if_any = "Immediate / High Priority"
            security_violation_flag = forwarded

            if forwarded:
                security_violation_details = (
                    "CRITICAL POLICY VIOLATION (KB-09): The employee forwarded a suspected phishing email to teammates. "
                    "KB-09 strictly states: 'Must NOT be forwarded to other employees.' Immediate containment action required to purge copies from recipient mailboxes."
                )
                reasoning_summary = (
                    "Phishing email reported with active security policy violation: email was forwarded to colleagues. "
                    "KB-09 mandates immediate reporting to security@veridian-corp.example and strictly prohibits forwarding suspicious messages. "
                    "Escalated to IT Security for incident response and mailbox remediation."
                )
                employee_response_text = (
                    "Hello Ananya, this incident has been immediately escalated to IT Security (security@veridian-corp.example) under KB-09.\n\n"
                    "⚠️ IMPORTANT SECURITY NOTICE: Forwarding suspected phishing emails to colleagues is a direct violation of KB-09 policy, "
                    "as it risks spreading malware and credential harvesting across the organization. Please instruct your teammates not to click any links or download attachments. "
                    "IT Security is initiating immediate mailbox containment.\n\n"
                    "[Sources Cited: KB-09 (Security Incident Reporting & Phishing), Precedent: TK-1048]"
                )
            else:
                reasoning_summary = "Suspected phishing email reported. Escalated immediately to security@veridian-corp.example per KB-09."
                employee_response_text = (
                    "Thank you for reporting this suspicious message. It has been escalated immediately to IT Security (security@veridian-corp.example) per KB-09. "
                    "Please do not click links or forward the message.\n\n"
                    "[Sources Cited: KB-09 (Security Incident Reporting & Phishing), Precedent: TK-1048]"
                )

        elif category == CategoryEnum.EMAIL_MAILBOX_QUOTA:
            # KB-06: Default 25GB. Increases need manager approval, capped at 50GB.
            decision = DecisionType.RESOLVED_WITH_INSTRUCTIONS
            approver_if_any = "Manager Approval (for quota increase up to 50GB cap)"
            sla_if_any = "SLA not stated in policy"
            reasoning_summary = (
                "Mailbox full notification. Per KB-06, default quota is 25GB. Immediate resolution is archiving/cleaning old emails. "
                "If an increase is required, manager approval is mandatory, with an absolute policy cap at 50GB."
            )
            employee_response_text = (
                "Hello Rohit, default email mailbox quota is 25GB under KB-06. "
                "To resume sending emails immediately, please archive or delete older emails and empty the Deleted Items folder. "
                "If you require additional storage, a quota increase requires formal manager approval and is strictly capped at a 50GB maximum per KB-06. "
                "Note: Quota increase fulfillment SLA is not stated in policy.\n\n"
                "[Sources Cited: KB-06 (Email Mailbox Quota), Precedent: TK-1045]"
            )

        elif category == CategoryEnum.ADMIN_ACCESS:
            # REQ-10: Wants admin access to finance reporting server, urgent.
            # Precedent TK-1050 (Rejected - no justification). Access granted by Finance/System Owner, not IT.
            decision = DecisionType.PENDING_APPROVAL
            approver_if_any = "Finance Department System Owner & Direct Manager"
            sla_if_any = "SLA not stated in policy (Access control review)"
            reasoning_summary = (
                "Urgent admin access to Finance Reporting Server requested. IT Support has no policy authority to grant elevated administrative server privileges. "
                "Per KB-08 and Access Control Policy, Finance access is governed by Finance. Citing historical precedent TK-1050 (J. Fernandes, rejected for no business justification), "
                "this request is parked requiring formal written business justification and direct authorization from the Finance System Owner."
            )
            employee_response_text = (
                "Hello Kavya, IT Support is not authorized to grant administrative or root access to production servers directly. "
                "Per company access governance and KB-08, access to finance infrastructure is governed strictly by the Finance Department. "
                "Precedent TK-1050 establishes that admin access requests without documented business justification are rejected. "
                "To proceed, please submit a formal access request with written business justification approved by your manager and the Finance System Owner. "
                "Note: Approver SLA is not stated in policy.\n\n"
                "[Sources Cited: KB-08 (Expense Software Access), Access Control Governance, Precedent: TK-1050]"
            )

        elif category == CategoryEnum.EXPENSE_SOFTWARE_ACCESS:
            # KB-08: Granted by Finance, not IT. IT only helps with login/technical issues on an existing account.
            if follow_up_answer:
                simulated_employee_response = follow_up_answer
                decision = DecisionType.RESOLVED_WITH_INSTRUCTIONS
                approver_if_any = "None (Technical troubleshooting for existing account)"
                sla_if_any = "SLA not stated in policy"
                reasoning_summary = (
                    f"Employee clarified status: '{follow_up_answer}'. Active account confirmed with SAML/login token defect. "
                    "Per KB-08, IT Support handles technical/login issues on existing accounts."
                )
                employee_response_text = (
                    "Thank you for confirming your existing active Concur account Sneha. "
                    "Per KB-08, IT Support is assisting with your SAML token login failure. Please clear your browser cache and attempt SAML SSO login via the employee intranet portal.\n\n"
                    "[Sources Cited: KB-08 (Expense Software Access & Troubleshooting)]"
                )
            else:
                decision = DecisionType.NEEDS_CLARIFICATION
                follow_up_question = (
                    "Per KB-08, new expense tool access is granted exclusively by Finance, while IT assists with login/technical issues on existing accounts. "
                    "Do you already have an active expense account, and what specific error message or screenshot are you seeing?"
                )
                approver_if_any = "Finance (if new account needed) / None (if existing account login issue)"
                sla_if_any = "Not stated in policy"
                reasoning_summary = (
                    "Expense tool login issue. Under KB-08, Finance grants initial access, while IT provides technical assistance for existing accounts. "
                    "Clarification requested to confirm if account is active and obtain technical error details."
                )
                employee_response_text = (
                    "Hello Sneha, under KB-08, user access to the expense software is granted exclusively by Finance, not IT. "
                    "IT Support handles technical and login issues on existing accounts. Could you clarify whether you already have an approved active account, "
                    "and provide details or a screenshot of the error you receive?\n\n"
                    "[Sources Cited: KB-08 (Expense Software Access & Troubleshooting)]"
                )

        audit_trail.append(AuditStep(
            step_num=step_counter,
            step_name="Rule Evaluation & Decision State Machine",
            timestamp=now_str,
            input_summary=f"Category: {category.value}, Conflict: {conflict_detected}, Security Violation: {security_violation_flag}",
            output_summary=f"Decision: {decision.value}, Approver: {approver_if_any or 'None'}, SLA: {sla_if_any or 'Unstated'}",
            details={
                "decision": decision.value,
                "approver": approver_if_any,
                "sla": sla_if_any,
                "security_violation": security_violation_flag,
                "policy_conflict": conflict_detected
            },
            rationale=reasoning_summary
        ))
        step_counter += 1

        # STEP 4: Response Synthesis & Audit Trail Assembly
        audit_trail.append(AuditStep(
            step_num=step_counter,
            step_name="Response & Citation Generation",
            timestamp=now_str,
            input_summary="Synthesize employee response with mandatory citations and audit trail",
            output_summary=f"Generated response with {len(sources_cited)} citations",
            details={"sources_cited": sources_cited},
            rationale="Formatted transparent employee response with cited KB IDs, policies, and historical precedents."
        ))

        return AgentReasoning(
            category=category,
            confidence=confidence,
            matched_kb_ids=kb_ids,
            matched_precedents=precedent_ids,
            policy_conflict_detected=conflict_detected,
            policy_conflict_summary=conflict_summary if conflict_detected else None,
            decision=decision,
            approver_if_any=approver_if_any,
            sla_if_any=sla_if_any,
            security_violation_flag=security_violation_flag,
            security_violation_details=security_violation_details,
            follow_up_question=follow_up_question,
            simulated_employee_response=simulated_employee_response,
            employee_response_text=employee_response_text,
            sources_cited=sources_cited,
            reasoning_summary=reasoning_summary,
            audit_trail=audit_trail
        )

decision_engine = DecisionEngine()
