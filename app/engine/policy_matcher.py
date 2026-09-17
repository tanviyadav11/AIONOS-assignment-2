"""
Policy Matcher & Precedent Resolver for Veridian Corp.
Deterministically links classified requests to corresponding Knowledge Base articles,
Asset Management Policies, and historical precedent tickets.
Surfaces policy tensions (e.g. KB-03 3-yr vs Asset Management Policy 4-yr).
"""

from typing import List, Dict, Any, Tuple
from app.models.schemas import CategoryEnum, KnowledgeBaseArticle, PrecedentTicket
from app.data.seed_data import KNOWLEDGE_BASE, HISTORICAL_PRECEDENTS

class PolicyMatcher:
    def __init__(self):
        self.category_to_kb: Dict[CategoryEnum, List[str]] = {
            CategoryEnum.PASSWORD_RESET: ["KB-01"],
            CategoryEnum.VPN_ACCESS: ["KB-02"],
            CategoryEnum.LAPTOP_REPLACEMENT: ["KB-03", "ASSET-POLICY"],
            CategoryEnum.SOFTWARE_INSTALLATION: ["KB-04"],
            CategoryEnum.PRINTER_TROUBLESHOOTING: ["KB-05"],
            CategoryEnum.EMAIL_MAILBOX_QUOTA: ["KB-06"],
            CategoryEnum.GUEST_WIFI: ["KB-07"],
            CategoryEnum.EXPENSE_SOFTWARE_ACCESS: ["KB-08"],
            CategoryEnum.SECURITY_INCIDENT_REPORTING: ["KB-09"],
            CategoryEnum.WFH_EQUIPMENT: ["KB-10"],
            CategoryEnum.ADMIN_ACCESS: ["KB-08", "ASSET-POLICY"],
            CategoryEnum.UNCLEAR_INSUFFICIENT: [],
        }

        self.category_to_precedents: Dict[CategoryEnum, List[str]] = {
            CategoryEnum.PASSWORD_RESET: ["TK-1049"],
            CategoryEnum.VPN_ACCESS: ["TK-1042"],
            CategoryEnum.LAPTOP_REPLACEMENT: ["TK-1043"],
            CategoryEnum.SOFTWARE_INSTALLATION: ["TK-1044"],
            CategoryEnum.PRINTER_TROUBLESHOOTING: ["TK-1046"],
            CategoryEnum.EMAIL_MAILBOX_QUOTA: ["TK-1045"],
            CategoryEnum.GUEST_WIFI: ["TK-1051"],
            CategoryEnum.EXPENSE_SOFTWARE_ACCESS: [],
            CategoryEnum.SECURITY_INCIDENT_REPORTING: ["TK-1048"],
            CategoryEnum.WFH_EQUIPMENT: ["TK-1047"],
            CategoryEnum.ADMIN_ACCESS: ["TK-1050"],
            CategoryEnum.UNCLEAR_INSUFFICIENT: [],
        }

    def match_policies(self, category: CategoryEnum, entities: Dict[str, Any]) -> Tuple[List[str], List[str], bool, str]:
        """
        Retrieves relevant KB IDs, Precedent Ticket IDs, and evaluates policy tensions.
        Returns: (kb_ids, precedent_ids, conflict_detected, conflict_summary)
        """
        kb_ids = list(self.category_to_kb.get(category, []))
        precedent_ids = list(self.category_to_precedents.get(category, []))
        conflict_detected = False
        conflict_summary = ""

        # Evaluate Known Policy Tension: KB-03 vs Asset Management Policy (Q2 2026)
        if category == CategoryEnum.LAPTOP_REPLACEMENT:
            age = entities.get("device_age_years")
            if age is not None and 3.0 <= age < 4.0:
                conflict_detected = True
                conflict_summary = (
                    f"⚠️ POLICY TENSION DETECTED: Device age is {age} years. "
                    "KB-03 establishes replacement eligibility after 3 years of service. "
                    "However, the Asset Management Policy (Finance & Assets, Q2 2026) dictates a 4-year standard refresh cycle, "
                    "requiring Finance sign-off for any early replacement outside 4 years. "
                    "Precedent TK-1043 (S. Iyer, 3.2 yrs old) confirms that early replacements within the 3–4 year window "
                    "require dual authorization: IT Department approval AND a Finance sign-off flag."
                )
            elif age is not None and age < 3.0:
                conflict_summary = (
                    f"Device age is {age} years (under both the 3-year KB-03 threshold and 4-year Asset Policy cycle). "
                    "Replacement requires verified catastrophic hardware failure. Diagnostic evaluation needed."
                )

        return kb_ids, precedent_ids, conflict_detected, conflict_summary

    def get_kb_article(self, kb_id: str) -> KnowledgeBaseArticle:
        return KNOWLEDGE_BASE.get(kb_id)

    def get_precedent(self, ticket_id: str) -> PrecedentTicket:
        for p in HISTORICAL_PRECEDENTS:
            if p.ticket_id == ticket_id:
                return p
        return None

policy_matcher = PolicyMatcher()
