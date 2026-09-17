"""
Intake & Classification Engine for Veridian Corp IT Support.
Parses natural language requests, extracts operational entities (e.g. device age, failed attempts, contractor status, forwarding),
and categorizes them into KB categories or flags insufficient information.
"""

import re
from typing import Dict, Any, Tuple
from app.models.schemas import CategoryEnum

class RequestClassifier:
    def __init__(self):
        # Weighted keyword profiles for high-precision category classification
        self.category_keywords = {
            CategoryEnum.PASSWORD_RESET: [
                "password", "passcode", "locked out", "lock out", "failed attempt", "login attempt", 
                "unlock", "reset password", "forgot password", "cant login", "can't log in", "credentials"
            ],
            CategoryEnum.VPN_ACCESS: [
                "vpn", "virtual private network", "cisco anyconnect", "globalprotect", "remote access", 
                "contractor vpn", "credentials expired", "renew vpn", "vpn stopped"
            ],
            CategoryEnum.LAPTOP_REPLACEMENT: [
                "laptop", "macbook", "thinkpad", "computer", "dead laptop", "screen flickering", 
                "hardware failure", "replace laptop", "laptop replacement", "yrs old", "years old", 
                "motherboard", "hinge", "battery swollen", "laptop broken"
            ],
            CategoryEnum.SOFTWARE_INSTALLATION: [
                "install", "software", "application", "tool", "extension", "chrome extension", 
                "browser extension", "non-catalog", "catalog", "data-analysis tool", "python", "rstudio",
                "productivity tracking", "timetracker", "download app"
            ],
            CategoryEnum.PRINTER_TROUBLESHOOTING: [
                "printer", "print", "printing", "paper jam", "spooler", "print queue", "toner", 
                "cartridge", "scanner", "printer offline", "floor printer"
            ],
            CategoryEnum.EMAIL_MAILBOX_QUOTA: [
                "mailbox", "quota", "mailbox full", "outlook storage", "email storage", "cant send email", 
                "can't send", "archive email", "25gb", "50gb", "increase quota", "storage limit"
            ],
            CategoryEnum.GUEST_WIFI: [
                "guest wifi", "guest wi-fi", "visitor wifi", "visitor", "kiosk", "wifi pass", 
                "guest internet", "wifi code", "front-desk", "guest network"
            ],
            CategoryEnum.EXPENSE_SOFTWARE_ACCESS: [
                "expense", "expense tool", "concur", "expensify", "reimbursement", "expense report", 
                "expense login", "saml token", "expense account", "finance tool"
            ],
            CategoryEnum.SECURITY_INCIDENT_REPORTING: [
                "phishing", "suspicious email", "malware", "virus", "ransomware", "unauthorized access", 
                "security alert", "hacked", "spam email", "forwarded to team", "forwarded to teammates", "scam"
            ],
            CategoryEnum.WFH_EQUIPMENT: [
                "wfh", "work from home", "home office", "monitor", "ergonomic chair", "desk", 
                "remote equipment", "remote allowance", "days/week", "shipping address"
            ],
            CategoryEnum.ADMIN_ACCESS: [
                "admin access", "root access", "server access", "finance reporting server", 
                "database access", "sudo", "elevated permissions", "system administration", "production server"
            ],
        }

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract key structural metadata from request text."""
        text_lower = text.lower()
        entities = {
            "device_age_years": None,
            "failed_attempts": None,
            "is_contractor": False,
            "forwarded_to_others": False,
            "urgent": False,
            "wfh_days_per_week": None,
            "hardware_failure_indicated": False,
            "monitoring_tool_indicated": False,
            "account_exists_indicated": None,
        }

        # Extract device age (e.g. "~3.5 yrs old", "2 yrs old", "3.2 years")
        age_match = re.search(r"(\d+(\.\d+)?)\s*(?:yrs|years|yr|year)", text_lower)
        if age_match:
            try:
                entities["device_age_years"] = float(age_match.group(1))
            except ValueError:
                pass

        # Extract failed attempts (e.g. "6 failed attempts", "5 attempts")
        attempt_match = re.search(r"(\d+)\s*(?:failed\s+)?attempts?", text_lower)
        if attempt_match:
            try:
                entities["failed_attempts"] = int(attempt_match.group(1))
            except ValueError:
                pass

        # Contractor check
        if "contractor" in text_lower or "vendor" in text_lower or "external" in text_lower:
            entities["is_contractor"] = True

        # Forwarding check (critical for KB-09 violation)
        if (
            "forwarded to teammates" in text_lower 
            or "forwarded to team" in text_lower 
            or "forwarded to others" in text_lower 
            or "forwarded it to" in text_lower
            or "shared with my team" in text_lower
        ):
            entities["forwarded_to_others"] = True

        # Urgent flag
        if "urgent" in text_lower or "asap" in text_lower or "emergency" in text_lower:
            entities["urgent"] = True

        # WFH days
        wfh_match = re.search(r"(\d+)\s*days?\s*/\s*week", text_lower)
        if wfh_match:
            try:
                entities["wfh_days_per_week"] = int(wfh_match.group(1))
            except ValueError:
                pass

        # Hardware failure indicator
        if any(term in text_lower for term in ["dead", "completely dead", "unbootable", "won't turn on", "smoke", "broken screen"]):
            entities["hardware_failure_indicated"] = True

        # Monitoring / Productivity tracking indicator
        if any(term in text_lower for term in ["productivity tracking", "monitoring", "keystroke", "timetracker", "activity log"]):
            entities["monitoring_tool_indicated"] = True

        return entities

    def classify(self, text: str) -> Tuple[CategoryEnum, float, Dict[str, Any]]:
        """
        Classifies input text into a CategoryEnum with confidence and extracted entities.
        Flags vague / insufficient requests if information is too sparse to take action.
        """
        cleaned = text.strip()
        entities = self.extract_entities(cleaned)
        cleaned_lower = cleaned.lower()

        # Check for vague / insufficient info (e.g. "hey can you help, its not working")
        vague_patterns = [
            r"^hey\s+can\s+you\s+help",
            r"^its?\s+not\s+working$",
            r"^help\s*me$",
            r"^nothing\s+is\s+working$",
            r"^please\s+help$",
            r"^issue\s+with\s+my\s+computer$"
        ]
        if len(cleaned.split()) <= 8 and (
            any(re.search(p, cleaned_lower) for p in vague_patterns)
            or (len(cleaned.split()) <= 4 and not any(kw in cleaned_lower for kws in self.category_keywords.values() for kw in kws))
        ):
            return CategoryEnum.UNCLEAR_INSUFFICIENT, 0.95, entities

        # Specific disambiguation rules
        if "guest" in cleaned_lower and ("wifi" in cleaned_lower or "wi-fi" in cleaned_lower or "visitor" in cleaned_lower):
            return CategoryEnum.GUEST_WIFI, 0.99, entities

        if "phishing" in cleaned_lower or "suspicious email" in cleaned_lower or "malware" in cleaned_lower:
            return CategoryEnum.SECURITY_INCIDENT_REPORTING, 0.99, entities

        if "admin access" in cleaned_lower or "finance reporting server" in cleaned_lower or "root access" in cleaned_lower:
            return CategoryEnum.ADMIN_ACCESS, 0.98, entities

        if "expense" in cleaned_lower or "concur" in cleaned_lower or "expense tool" in cleaned_lower:
            return CategoryEnum.EXPENSE_SOFTWARE_ACCESS, 0.95, entities

        if "wfh" in cleaned_lower or "work from home" in cleaned_lower or "home office" in cleaned_lower:
            return CategoryEnum.WFH_EQUIPMENT, 0.98, entities

        if "mailbox" in cleaned_lower or ("quota" in cleaned_lower and "email" in cleaned_lower) or ("mail" in cleaned_lower and "full" in cleaned_lower):
            return CategoryEnum.EMAIL_MAILBOX_QUOTA, 0.98, entities

        if "printer" in cleaned_lower or "paper-jam" in cleaned_lower or "paper jam" in cleaned_lower or "spooler" in cleaned_lower:
            return CategoryEnum.PRINTER_TROUBLESHOOTING, 0.98, entities

        if "laptop" in cleaned_lower or "thinkpad" in cleaned_lower or "macbook" in cleaned_lower:
            return CategoryEnum.LAPTOP_REPLACEMENT, 0.96, entities

        if "vpn" in cleaned_lower:
            return CategoryEnum.VPN_ACCESS, 0.98, entities

        if "install" in cleaned_lower or "extension" in cleaned_lower or "software" in cleaned_lower or "tool" in cleaned_lower:
            return CategoryEnum.SOFTWARE_INSTALLATION, 0.95, entities

        if "locked out" in cleaned_lower or "password" in cleaned_lower or "failed attempt" in cleaned_lower:
            return CategoryEnum.PASSWORD_RESET, 0.96, entities

        # Score matching for arbitrary queries
        scores: Dict[CategoryEnum, int] = {}
        for category, keywords in self.category_keywords.items():
            score = 0
            for kw in keywords:
                if kw in cleaned_lower:
                    score += 2 if len(kw) > 6 else 1
            if score > 0:
                scores[category] = score

        if scores:
            best_cat = max(scores, key=scores.get)
            confidence = min(0.95, 0.5 + (scores[best_cat] * 0.15))
            return best_cat, confidence, entities

        return CategoryEnum.UNCLEAR_INSUFFICIENT, 0.40, entities

classifier = RequestClassifier()
