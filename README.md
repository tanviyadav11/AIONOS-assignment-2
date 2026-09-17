# Veridian Corp - Internal IT Support Service Agent
AIONOS Agentic AI Factory - Timed Take-Home Assignment 2

An enterprise-grade, rules-first LLM-assisted Internal IT Support Service Agent built for Veridian Corp (Exercise Week: Mon 21 Sep 2026 – Fri 25 Sep 2026).

The system implements deterministic policy matching, identifies multi-policy conflicts, enforces dual-approval requirements, asks targeted follow-up questions, generates sequential tickets starting at TK-1052, cites exact KB and precedent sources, and maintains an append-only audit trail without inventing unstated facts.

## Grading Rubric Compliance

Understand Employee's Issue
Implementation: Entity extraction identifies details such as device age, failed lockout attempts, contractor status, forwarding actions, and system names.
File: app/engine/classifier.py

Find Relevant Policy / Resolution
Implementation: Deterministic lookup maps request categories to KB-01 to KB-10, the Asset Management Policy, and relevant historical tickets.
File: app/engine/policy_matcher.py

Ask Sensible Follow-up Questions
Implementation: The agent asks targeted questions for vague requests such as REQ-15, screen diagnostics for REQ-13, and account status for REQ-12.
File: app/engine/decision_engine.py

Resolve Simple Requests
Implementation: Direct resolution for Guest Wi-Fi (REQ-02), self-service guidance for password unlock (REQ-03), and VPN credential renewal (REQ-05).
Test: test_req02_guest_wifi_auto_resolved

Escalate Risky or Unclear Requests
Implementation: Security issues such as phishing forwarding (REQ-08) are escalated. Non-catalog software requests (REQ-04 and REQ-14) are routed for Security review. WFH and admin access requests are placed in the required approval queues.
Test: test_req08_phishing_forward_security_violation

Surface Policy Tensions
Implementation: REQ-01 identifies the conflict between KB-03, which allows laptop replacement after 3 years, and the Asset Management Policy, which specifies a 4-year refresh cycle. The system requires IT and Finance approval and cites TK-1043.
Test: test_req01_laptop_replacement_policy_conflict

Show Sources Used
Implementation: Agent responses include the KB, Asset Policy, and relevant precedent ticket used for the decision.
File: app/engine/response_builder.py

Maintain Audit Trail
Implementation: Timestamped append-only audit records are maintained for classification, policy matching, rule evaluation, and response generation.
File: app/data/store.py

No Hallucinated Data
Implementation: When a policy does not specify an SLA or approval detail, the system states that the information is not provided instead of inventing it.

## Solution Architecture

The application operates as a four-stage sequential pipeline.

1. Intake and Classification Engine
File: app/engine/classifier.py
- The classifier extracts information such as device age, failed login attempts, contractor status, and forwarding indicators.
- It checks whether the request contains enough information and identifies vague or incomplete requests.
- It categorizes requests across the ten Knowledge Base domains.

2. Deterministic Policy and Precedent Matcher
File: app/engine/policy_matcher.py
- The matcher looks up KB-01 through KB-10 and the Asset Management Policy.
- It also retrieves relevant historical tickets from TK-1042 through TK-1051.
- The system detects policy tensions, such as the 3-year laptop replacement condition in KB-03 compared with the 4-year hardware refresh cycle in the Asset Management Policy.

3. Rule and Decision Engine
File: app/engine/decision_engine.py
The decision engine uses five decision states:
- AUTO_RESOLVED
- RESOLVED_WITH_INSTRUCTIONS
- PENDING_APPROVAL
- ESCALATED_SECURITY
- NEEDS_CLARIFICATION
- It applies the required approval rules for hardware cases involving policy conflicts.
- It identifies security policy violations such as forwarding phishing emails.
- It also states when an SLA is not specified in the provided policies.

4. Ticketing and Audit Log Service
Files: app/engine/response_builder.py and app/data/store.py
- The system generates sequential ticket IDs starting at TK-1052.
- It generates employee-facing responses with the relevant sources.
- It records the steps taken during classification, policy matching, decision-making, and response generation.

## AI Tools Used and Code vs. LLM Boundary

Intent Categorization and Entity Extraction
Handled by: Hybrid approach using Claude / GPT for semantic understanding and Regex for structured entities
Used for extracting details such as device age, lockout counts, contractor status, and forwarding indicators.

Policy Matching and Conflict Detection
Handled by: Deterministic code in policy_matcher.py
This ensures that the provided KB and Asset Management Policy rules are applied consistently without probabilistic drift.

Decision State Assignment
Handled by: Deterministic code in decision_engine.py
This controls the decision states and approval requirements mathematically.

Response Phrasing and Tone
Handled by: Claude and GPT / Grounded LLM Layer
Used to generate clear, polite employee-facing responses strictly constrained by the evaluated decision and policy information.

Source Citation and Audit Trail
Handled by: Deterministic code in response_builder.py
This ensures that only validated KB and precedent identifiers are included in responses without hallucination.

## Known Limitations and Anti-Hallucination Boundaries

Policy Tensions
KB-03 allows laptop replacement after 3 years of service, while the Asset Management Policy specifies a 4-year hardware refresh cycle.
For devices between 3 and 4 years old, such as REQ-01 and REQ-13, the system identifies the policy tension and routes the request for the required approvals rather than selecting one policy without explanation.

Unstated SLAs
Some policies do not provide turnaround times. For example, manual password unlocks, printer technician visits, and mailbox quota adjustments do not have a stated SLA.
The system explicitly tells the user when an SLA is not provided in the available policy information.

Enterprise Access Boundaries
IT Support does not directly provision server administrator privileges or create new expense software accounts.
These requests are routed according to the relevant ownership and approval requirements.

## Quickstart

### Prerequisites
Python 3.10 or higher

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Application
```bash
python run.py
```
Open http://localhost:8000 in a browser to access the application.

### Run Automated Tests
```bash
python -m pytest tests/ -v
```

## Data Pack Test Coverage

REQ-01
Employee: Aditi Sharma
Request: Laptop dead, approximately 3.5 years old
Decision: PENDING_APPROVAL
Sources: KB-03, Asset Policy, TK-1043
Handling: Identifies the 3-year versus 4-year policy tension and requires the relevant approvals.

REQ-02
Employee: Vikram Chawla
Request: Guest Wi-Fi for visitor tomorrow
Decision: AUTO_RESOLVED
Sources: KB-07, TK-1051
Handling: Directs the employee to the front-desk kiosk. No IT ticket is required.

REQ-03
Employee: Karan Mehta
Request: Locked out after 6 failed attempts
Decision: RESOLVED_WITH_INSTRUCTIONS
Sources: KB-01, TK-1049
Handling: The request exceeds the 5-attempt threshold and requires manual IT unlock. The SLA is not stated.

REQ-04
Employee: Ritu Bhatia
Request: Non-catalog data analysis tool
Decision: PENDING_APPROVAL
Sources: KB-04, TK-1044
Handling: Routes the request to IT Security for review. The stated review time is 3–5 business days.

REQ-05
Employee: Sanjay Oberoi
Request: VPN stopped working because credentials expired
Decision: RESOLVED_WITH_INSTRUCTIONS
Sources: KB-02, TK-1042
Handling: Provides instructions for renewing the 90-day VPN credentials.

REQ-06
Employee: Meera Iyer
Request: Printer showing a false paper-jam message
Decision: RESOLVED_WITH_INSTRUCTIONS
Sources: KB-05, TK-1046
Handling: Provides printer troubleshooting instructions and accounts for the technician already assigned.

REQ-07
Employee: Farhan Ali
Request: Working from home 4 days per week and needs a monitor
Decision: PENDING_APPROVAL
Sources: KB-10, TK-1047
Handling: Requires manager sign-off and Finance processing.

REQ-08
Employee: Ananya Reddy
Request: Phishing email forwarded to team members
Decision: ESCALATED_SECURITY
Sources: KB-09, TK-1048
Handling: Escalates the issue to Security and identifies the forwarding action as a policy violation.

REQ-09
Employee: Rohit Desai
Request: Mailbox full and unable to send emails
Decision: RESOLVED_WITH_INSTRUCTIONS
Sources: KB-06, TK-1045
Handling: Provides archiving guidance and explains the approval requirement for increasing the quota.

REQ-10
Employee: Kavya Pillai
Request: Urgent admin access to the finance reporting server
Decision: PENDING_APPROVAL
Sources: KB-08, TK-1050
Handling: Does not directly grant access and routes the request according to the required ownership and approval process.

REQ-11
Employee: Nikhil Bansal
Request: VPN access for a new contractor
Decision: PENDING_APPROVAL
Sources: KB-02
Handling: Requires manager approval through the access request form.

REQ-12
Employee: Sneha Kulkarni
Request: Unable to log into the expense tool
Decision: NEEDS_CLARIFICATION
Sources: KB-08
Handling: Asks whether an expense-tool account already exists. Finance handles account access, while IT handles login and technical issues.

REQ-13
Employee: Aman Gupta
Request: Laptop screen flickering, device is 2 years old
Decision: NEEDS_CLARIFICATION
Sources: KB-03, Asset Policy
Handling: Requests diagnostic information before deciding whether repair or replacement is appropriate.

REQ-14
Employee: Tanya Chopra
Request: Browser extension for productivity tracking
Decision: PENDING_APPROVAL
Sources: KB-04, TK-1044
Handling: Routes the non-catalog software request for Security review.

REQ-15
Employee: Rahul Menon
Request: "hey can you help, its not working"
Decision: NEEDS_CLARIFICATION
Sources: None
Handling: Asks for more information instead of guessing the issue.

## Repository Structure

```
veridian-it-support-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI REST API & web server
│   ├── config.py                # Application configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Data schemas (DecisionType, Ticket, AuditStep)
│   ├── data/
│   │   ├── __init__.py
│   │   ├── seed_data.py         # Data Pack fixtures (KB-01..10, Asset Policy, REQ-01..15, TK-1042..1051)
│   │   └── store.py             # In-memory ticket storage and audit logger
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── classifier.py        # Entity extraction and classification engine
│   │   ├── policy_matcher.py    # Policy matcher and conflict detector
│   │   ├── decision_engine.py   # Decision state machine and rule evaluator
│   │   └── response_builder.py  # Response generator with citations
│   └── static/
│       ├── index.html           # Web application user interface
│       ├── css/
│       │   └── style.css        # Application stylesheet
│       └── js/
│           └── app.js           # Client application logic
├── tests/
│   ├── __init__.py
│   ├── test_engine.py           # Unit tests for decision engine and citations
│   ├── test_api.py              # API endpoint tests
│   └── test_e2e_flow.py         # End-to-end integration tests
├── requirements.txt             # Project dependencies
├── .env.example                 # Environment configuration template
├── run.py                       # Application entry point
└── README.md                    # Project documentation
```

## License
MIT License
