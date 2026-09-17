"""
Ground Truth Data Pack for Veridian Corp (Mon 21 Sep 2026 – Fri 25 Sep 2026).
Contains exact policies, historical precedent tickets, and seed employee requests.
"""

from typing import Dict, List
from app.models.schemas import KnowledgeBaseArticle, PrecedentTicket, SeedRequest

KNOWLEDGE_BASE: Dict[str, KnowledgeBaseArticle] = {
    "KB-01": KnowledgeBaseArticle(
        kb_id="KB-01",
        title="Password Reset & Account Lockout",
        category="Password Reset",
        summary="Self-service reset anytime. Locked out after 5 failed attempts -> contact IT to unlock manually. No approval required.",
        full_text=(
            "Employees can perform a self-service password reset anytime via the identity portal. "
            "If an account is locked out after 5 consecutive failed login attempts, the employee must contact IT "
            "to unlock the account manually. No approval is required for password resets or manual unlocks."
        ),
        approvals_required="None",
        sla="Not stated in policy (Standard operational queue)",
        self_service=True,
        special_notes="Locked out accounts (>5 attempts) require IT manual unlock without approval."
    ),
    "KB-02": KnowledgeBaseArticle(
        kb_id="KB-02",
        title="VPN Access & Credential Expiration",
        category="VPN Access",
        summary="Auto-granted to full-time employees. Contractors need manager approval via access request form. Credentials expire every 90 days, employee must renew.",
        full_text=(
            "VPN access is automatically granted to all full-time employees (FTE). "
            "Contractors require explicit manager approval submitted via the formal access request form. "
            "All VPN credentials expire every 90 days, and employees must renew them self-service."
        ),
        approvals_required="Contractors: Manager approval via Access Request Form. Full-Time Employees: None (Auto-granted).",
        sla="Self-renewal: Instant. Contractor approval: Depends on manager sign-off.",
        self_service=True,
        special_notes="Full-time employees self-renew expired 90-day credentials. Contractors must not be auto-granted access."
    ),
    "KB-03": KnowledgeBaseArticle(
        kb_id="KB-03",
        title="Laptop Replacement & Refresh",
        category="Laptop Replacement",
        summary="Eligible after 3 years of service, or earlier with verified hardware failure. Must be raised >=2 weeks in advance of intended replacement.",
        full_text=(
            "Laptops are eligible for replacement after 3 years of service, or earlier in the event of a verified hardware failure. "
            "Requests must be raised at least 2 weeks in advance of intended replacement date."
        ),
        approvals_required="IT Department approval (and Finance sign-off if in 3–4 year window under Asset Management Policy)",
        sla="Request must be raised >=2 weeks in advance; procurement fulfillment SLA not stated in policy.",
        self_service=False,
        special_notes="Known policy tension with Asset Management Policy (4-year standard cycle). Early replacement requires Finance sign-off."
    ),
    "KB-04": KnowledgeBaseArticle(
        kb_id="KB-04",
        title="Software Installation & Catalog",
        category="Software Installation",
        summary="Catalog software = self-install. Non-catalog = IT Security review, 3–5 business days.",
        full_text=(
            "Standard catalog software is available in the Company Software Center for self-installation without IT assistance. "
            "Non-catalog software requires an IT Security review and risk evaluation. Expected turnaround is 3–5 business days."
        ),
        approvals_required="IT Security",
        sla="3–5 business days",
        self_service=False,
        special_notes="Browser extensions and monitoring/productivity tools fall under non-catalog and carry elevated privacy/security review requirements."
    ),
    "KB-05": KnowledgeBaseArticle(
        kb_id="KB-05",
        title="Printer Troubleshooting",
        category="Printer Troubleshooting",
        summary="Check queue + restart spooler first. If unresolved, log ticket with asset tag.",
        full_text=(
            "For printing issues or false error messages (e.g. false paper jam), employees must first check the local print queue "
            "and restart the print spooler service. If the issue remains unresolved, log an IT support ticket including the printer asset tag."
        ),
        approvals_required="None",
        sla="Not stated in policy",
        self_service=True,
        special_notes="Spooler restart instructions provided first; on-site technician dispatched if unresolved."
    ),
    "KB-06": KnowledgeBaseArticle(
        kb_id="KB-06",
        title="Email Mailbox Quota",
        category="Email Mailbox Quota",
        summary="Default 25GB. Increases need manager approval, capped at 50GB.",
        full_text=(
            "Default email mailbox quota is 25GB. Employees reaching quota should archive or clean up older emails. "
            "Mailbox quota increases require direct manager approval and are strictly capped at a maximum of 50GB."
        ),
        approvals_required="Manager approval",
        sla="Not stated in policy",
        self_service=False,
        special_notes="Hard ceiling of 50GB cannot be exceeded under any circumstances."
    ),
    "KB-07": KnowledgeBaseArticle(
        kb_id="KB-07",
        title="Guest Wi-Fi Provisioning",
        category="Guest Wi-Fi",
        summary="Valid 24h, self-generated at front-desk kiosk by any employee. No IT ticket required.",
        full_text=(
            "Guest Wi-Fi network credentials are valid for 24 hours. Any employee can self-generate visitor access codes "
            "directly at the front-desk touchscreen kiosk. No IT support ticket or approval is required."
        ),
        approvals_required="None",
        sla="Immediate / Self-service",
        self_service=True,
        special_notes="Auto-resolved directly. Direct employee to front-desk kiosk."
    ),
    "KB-08": KnowledgeBaseArticle(
        kb_id="KB-08",
        title="Expense Software Access & Troubleshooting",
        category="Expense Software Access",
        summary="Granted by Finance, not IT. IT only helps with login/technical issues on an existing account.",
        full_text=(
            "Access provisioning and permissions for the corporate expense software are granted exclusively by the Finance department, not IT. "
            "IT Support only provides technical assistance with login failures, browser errors, or password issues for existing active accounts."
        ),
        approvals_required="Finance (for new access/accounts). None for IT login troubleshooting on existing accounts.",
        sla="Not stated in policy",
        self_service=False,
        special_notes="Clarify if the employee already has an account before routing."
    ),
    "KB-09": KnowledgeBaseArticle(
        kb_id="KB-09",
        title="Security Incident Reporting & Phishing",
        category="Security Incident Reporting",
        summary="Suspected phishing/malware/unauthorized access -> report to security@veridian-corp.example immediately. Must NOT be forwarded to other employees.",
        full_text=(
            "Employees encountering suspected phishing emails, malware alerts, or unauthorized system access must report the incident "
            "immediately to security@veridian-corp.example. CRITICAL RULE: Suspicious emails must NOT be forwarded to other employees or distribution lists under any circumstances."
        ),
        approvals_required="Immediate escalation to IT Security Incident Response",
        sla="Immediate / High Priority",
        self_service=False,
        special_notes="If employee forwarded phishing email to teammates, explicitly flag this as a direct policy violation."
    ),
    "KB-10": KnowledgeBaseArticle(
        kb_id="KB-10",
        title="WFH Equipment & Remote Allowance",
        category="WFH Equipment",
        summary="Remote >3 days/week -> one-time allowance (chair, monitor). Needs manager sign-off + Finance processing. IT only handles shipping once approved.",
        full_text=(
            "Employees working remotely more than 3 days per week qualify for a one-time WFH ergonomic allowance (e.g. ergonomic chair, external monitor). "
            "Requests require direct manager sign-off and subsequent Finance processing. IT Support's role is strictly limited to hardware procurement and shipping once all approvals are completed."
        ),
        approvals_required="Manager sign-off + Finance processing",
        sla="Fulfillment SLA not stated in policy (Pending Finance/Manager approval)",
        self_service=False,
        special_notes="Ticket is parked in 'Pending Finance/Manager'. IT does not approve the budget."
    ),
    "ASSET-POLICY": KnowledgeBaseArticle(
        kb_id="ASSET-POLICY",
        title="Asset Management Policy (Finance & Assets, Q2 2026)",
        category="Laptop Replacement",
        summary="All company hardware follows a 4-year standard refresh cycle from date of issue. Early replacement outside this cycle requires Finance sign-off in addition to IT approval.",
        full_text=(
            "Asset Management Policy (Finance & Assets Department, Q2 2026): "
            "All company-owned hardware follows a mandatory 4-year standard refresh cycle from the initial date of issue. "
            "Any early replacement outside this 4-year lifecycle requires explicit Finance sign-off in addition to standard IT approval."
        ),
        approvals_required="IT Approval AND Finance Sign-off (for any hardware <4 years old)",
        sla="Procurement cycle dependent",
        self_service=False,
        special_notes="Tension with KB-03: Laptops between 3.0 and 4.0 years old are eligible under KB-03 but classified as early replacement under Asset Management Policy, requiring Finance sign-off flag."
    ),
}

HISTORICAL_PRECEDENTS: List[PrecedentTicket] = [
    PrecedentTicket(
        ticket_id="TK-1042",
        employee="R. Verma",
        issue="VPN credential expired",
        status="Resolved (closed)",
        category="VPN Access",
        relevance_notes="FTE self-service credential renewal standard resolution."
    ),
    PrecedentTicket(
        ticket_id="TK-1043",
        employee="S. Iyer",
        issue="Laptop replacement (3.2 yrs old)",
        status="Approved — pending fulfillment (active)",
        category="Laptop Replacement",
        relevance_notes="Critical precedent: Laptop replaced at 3.2 years old was approved under the 3–4 year window requiring IT approval + Finance sign-off."
    ),
    PrecedentTicket(
        ticket_id="TK-1044",
        employee="A. Khan",
        issue="Non-catalog software request",
        status="Pending Security review (active)",
        category="Software Installation",
        relevance_notes="Standard non-catalog routing to IT Security review (3–5 business days SLA)."
    ),
    PrecedentTicket(
        ticket_id="TK-1045",
        employee="P. Joshi",
        issue="Mailbox quota increase",
        status="Approved at 35GB (closed)",
        category="Email Mailbox Quota",
        relevance_notes="Manager approved quota increase within the 50GB maximum ceiling."
    ),
    PrecedentTicket(
        ticket_id="TK-1046",
        employee="M. Das",
        issue="Printer paper jam, floor 2",
        status="Resolved (closed)",
        category="Printer Troubleshooting",
        relevance_notes="Spooler and queue cleared; technician assigned when hardware check was required."
    ),
    PrecedentTicket(
        ticket_id="TK-1047",
        employee="K. Singh",
        issue="Home office equipment request",
        status="Pending Finance (active)",
        category="WFH Equipment",
        relevance_notes="WFH monitor/chair request routed to Finance for budget sign-off."
    ),
    PrecedentTicket(
        ticket_id="TK-1048",
        employee="T. Rao",
        issue="Phishing email reported",
        status="Escalated to Security — under investigation (active)",
        category="Security Incident Reporting",
        relevance_notes="Direct report to security@veridian-corp.example without unauthorized forwarding."
    ),
    PrecedentTicket(
        ticket_id="TK-1049",
        employee="V. Nambiar",
        issue="Password reset",
        status="Resolved (closed)",
        category="Password Reset",
        relevance_notes="Standard self-service or IT unlock without approval."
    ),
    PrecedentTicket(
        ticket_id="TK-1050",
        employee="J. Fernandes",
        issue="Admin access request",
        status="Rejected — no business justification provided (closed)",
        category="Admin / Server Access",
        relevance_notes="Critical precedent: Direct admin access requests without documented business justification and manager/Finance authorization are rejected."
    ),
    PrecedentTicket(
        ticket_id="TK-1051",
        employee="L. Menon",
        issue="Guest Wi-Fi issued",
        status="Resolved (closed)",
        category="Guest Wi-Fi",
        relevance_notes="Directed to front-desk kiosk for 24h pass; closed immediately."
    ),
]

SEED_REQUESTS: List[SeedRequest] = [
    SeedRequest(
        id="REQ-01",
        employee="Aditi Sharma",
        email="aditi.sharma@veridiancorp.example",
        date="Mon 21 Sep",
        request="Laptop completely dead, ~3.5 yrs old",
        status_so_far="Not started",
        simulated_follow_up_answer="Hardware diagnostic confirms motherboard failure. Device is completely unbootable."
    ),
    SeedRequest(
        id="REQ-02",
        employee="Vikram Chawla",
        email="vikram.chawla@veridiancorp.example",
        date="Mon 21 Sep",
        request="Guest Wi-Fi for visitor tomorrow",
        status_so_far="Not started",
        simulated_follow_up_answer="Visitor will be arriving at 10 AM for client meetings."
    ),
    SeedRequest(
        id="REQ-03",
        employee="Karan Mehta",
        email="karan.mehta@veridiancorp.example",
        date="Mon 21 Sep",
        request="Locked out, 6 failed attempts",
        status_so_far="In progress — reset queued",
        simulated_follow_up_answer="Account is karan.mehta@veridiancorp.example, locked out on workstation."
    ),
    SeedRequest(
        id="REQ-04",
        employee="Ritu Bhatia",
        email="ritu.bhatia@veridiancorp.example",
        date="Tue 22 Sep",
        request="Install non-catalog data-analysis tool",
        status_so_far="Waiting on Security review",
        simulated_follow_up_answer="Tool is Orange Data Mining v3.36 for statistical modeling."
    ),
    SeedRequest(
        id="REQ-05",
        employee="Sanjay Oberoi",
        email="sanjay.oberoi@veridiancorp.example",
        date="Tue 22 Sep",
        request="VPN stopped, credentials expired",
        status_so_far="Not started",
        simulated_follow_up_answer="Full-time employee in Marketing. Last renewed 90 days ago."
    ),
    SeedRequest(
        id="REQ-06",
        employee="Meera Iyer",
        email="meera.iyer@veridiancorp.example",
        date="Tue 22 Sep",
        request="3rd floor printer false paper-jam",
        status_so_far="Investigating — technician assigned",
        simulated_follow_up_answer="Printer Asset Tag is PRN-FL3-08. Spooler restarted but error remains."
    ),
    SeedRequest(
        id="REQ-07",
        employee="Farhan Ali",
        email="farhan.ali@veridiancorp.example",
        date="Wed 23 Sep",
        request="WFH 4 days/week, needs monitor",
        status_so_far="Not started",
        simulated_follow_up_answer="Manager is Sarah Jenkins. Working remote Mon-Thu."
    ),
    SeedRequest(
        id="REQ-08",
        employee="Ananya Reddy",
        email="ananya.reddy@veridiancorp.example",
        date="Wed 23 Sep",
        request="Possible phishing email, forwarded to teammates",
        status_so_far="Escalated to Security (auto-flagged)",
        simulated_follow_up_answer="Email subject was 'Urgent Invoice Payment' with a suspicious zip attachment. Forwarded to team of 6."
    ),
    SeedRequest(
        id="REQ-09",
        employee="Rohit Desai",
        email="rohit.desai@veridiancorp.example",
        date="Wed 23 Sep",
        request="Mailbox full, can't send",
        status_so_far="Not started",
        simulated_follow_up_answer="Current mailbox is at 24.8GB / 25GB quota. Need 10GB more."
    ),
    SeedRequest(
        id="REQ-10",
        employee="Kavya Pillai",
        email="kavya.pillai@veridiancorp.example",
        date="Wed 23 Sep",
        request="Wants admin access to finance reporting server, urgent",
        status_so_far="Not started",
        simulated_follow_up_answer="Need root/admin access to production finance database for ad-hoc quarterly reporting."
    ),
    SeedRequest(
        id="REQ-11",
        employee="Nikhil Bansal",
        email="nikhil.bansal@veridiancorp.example",
        date="Thu 24 Sep",
        request="New contractor needs VPN access",
        status_so_far="Not started",
        simulated_follow_up_answer="Contractor is Alex Reed (contractor ID CON-8821), reporting to Nikhil Bansal."
    ),
    SeedRequest(
        id="REQ-12",
        employee="Sneha Kulkarni",
        email="sneha.kulkarni@veridiancorp.example",
        date="Thu 24 Sep",
        request="Can't log into expense tool",
        status_so_far="Waiting on employee response (screenshot requested, no reply)",
        simulated_follow_up_answer="Yes, I have an existing approved Concur account, getting error 'Invalid SAML token' today."
    ),
    SeedRequest(
        id="REQ-13",
        employee="Aman Gupta",
        email="aman.gupta@veridiancorp.example",
        date="Thu 24 Sep",
        request="Laptop screen flickering, 2 yrs old, maybe just needs repair",
        status_so_far="Not started",
        simulated_follow_up_answer="Flickering occurs when adjusting hinge. External monitor works fine. No physical drops."
    ),
    SeedRequest(
        id="REQ-14",
        employee="Tanya Chopra",
        email="tanya.chopra@veridiancorp.example",
        date="Fri 25 Sep",
        request="Approval to install browser extension (productivity tracking)",
        status_so_far="Not started",
        simulated_follow_up_answer="Extension is 'TimeTracker Pro' Chrome extension that logs keystrokes and active URLs."
    ),
    SeedRequest(
        id="REQ-15",
        employee="Rahul Menon",
        email="rahul.menon@veridiancorp.example",
        date="Fri 25 Sep",
        request="hey can you help, its not working",
        status_so_far="Not started",
        simulated_follow_up_answer="My Outlook desktop app crashes immediately upon opening on Windows 11."
    ),
]
