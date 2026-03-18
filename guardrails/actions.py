"""
Custom NeMo Guardrails actions for Scientific Grounding Protocol enforcement.

Actions use deterministic keyword/regex matching rather than LLM-based self-check
to ensure reproducibility across experimental runs. Two actions are exported:

    check_domain_relevance  — INPUT rail: validates question is in-scope
    check_sgp_compliance    — OUTPUT rail: validates response meets SGP criteria

NeMo Guardrails auto-discovers this file because it lives alongside config.yml
in the guardrails/ config directory.

Author: Monica Guimaraes
"""

import re
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Domain keyword registry
# ---------------------------------------------------------------------------

_DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "cog_sci": [
        "cognitive load", "cognitive science", "learning theory", "memory",
        "schema", "attention", "working memory", "instructional design",
        "pedagogy", "e-learning", "online learning", "educational",
    ],
    "ml_factuality": [
        "language model", "llm", "large language", "factual", "hallucination",
        "machine learning", "neural network", "transformer", "retrieval",
        "grounding", "factuality", "accuracy", "techniques",
    ],
    "hci": [
        "human-computer", "hci", "user interface", "decision-making",
        "ai assistant", "workplace", "automation bias", "cognitive",
        "reliance", "over-reliance", "trust in ai",
    ],
    "health_tech": [
        "clinical", "medical", "health", "patient", "diagnosis", "treatment",
        "generative ai", "clinical decision", "ehr", "radiology", "triage",
        "safely used",
    ],
    "policy_eu": [
        "regulation", "policy", "eu ", "european union", "governance",
        "compliance", "ai act", "risk assessment", "legislation", "legal",
        "regulating",
    ],
}

_ALL_DOMAIN_KEYWORDS: List[str] = [
    kw for keywords in _DOMAIN_KEYWORDS.values() for kw in keywords
]


# ---------------------------------------------------------------------------
# Evidence marker registry
# ---------------------------------------------------------------------------

_EVIDENCE_MARKERS: List[str] = [
    "research", "study", "studies", "evidence", "findings", "paper",
    "published", "found that", "showed that", "demonstrated", "meta-analysis",
    "systematic review", "et al", "doi:", "journal", "peer-reviewed",
    "(20", "results suggest", "data indicate", "literature",
]

_UNCERTAINTY_MARKERS: List[str] = [
    "limitation", "caveat", "uncertain", "unclear", "may ", "might ",
    "could ", "however", "although", "it is important to note",
    "further research", "evidence is mixed", "not conclusive",
    "context-dependent", "varies", "depends on", "note that",
    "caution", "lack of", "insufficient", "unknown", "emerging",
]

# Regex patterns for unqualified absolute claims.
# Each pattern uses a negative lookahead to avoid flagging benign uses
# (e.g., "always note" or "never before").
_ABSOLUTE_CLAIM_PATTERNS: List[str] = [
    r"\balways\b(?! note| keep| consider| remember)",
    r"\bnever\b(?! before| mind| been| studied)",
    r"\bdefinitively proves?\b",
    r"\bconclusively shows?\b",
    r"\bproven fact\b",
    r"\bundeniably\b",
    r"\bwithout (any )?doubt\b",
    r"\bit is (a )?fact that\b",
    r"\bguarantees?\b(?! no| that)",
]


# ---------------------------------------------------------------------------
# Input rail action
# ---------------------------------------------------------------------------

async def check_domain_relevance(context: Optional[dict] = None) -> bool:
    """
    Verify that the user message is within a supported research domain.

    Matches the user message against vocabulary for five domains:
    cog_sci, ml_factuality, hci, health_tech, policy_eu.

    Args:
        context: NeMo Guardrails runtime context. Reads 'user_message' or
                 'last_user_message' key.

    Returns:
        True if the message matches at least one domain keyword; False otherwise.
        Defaults to True when context is unavailable (fail-open for safety).
    """
    ctx = context or {}
    user_message = (
        ctx.get("user_message") or ctx.get("last_user_message") or ""
    ).lower()

    if not user_message:
        return True  # Fail-open: do not block when message is unreadable

    return any(kw in user_message for kw in _ALL_DOMAIN_KEYWORDS)


# ---------------------------------------------------------------------------
# Output rail action
# ---------------------------------------------------------------------------

async def check_sgp_compliance(context: Optional[dict] = None) -> bool:
    """
    Verify that the bot response satisfies all SGP output constraints.

    Applies three deterministic checks:

        1. Evidence     — response references research, studies, or findings.
        2. Uncertainty  — response discloses limitations or hedges claims.
        3. Transparency — response avoids unqualified absolute claims.

    All three must pass for the function to return True.

    Args:
        context: NeMo Guardrails runtime context. Reads 'bot_message' or
                 'last_bot_message' key.

    Returns:
        True if all three SGP criteria are satisfied; False if any fail.
        Defaults to True when context is unavailable (fail-open for safety).
    """
    ctx = context or {}
    bot_message = (
        ctx.get("bot_message") or ctx.get("last_bot_message") or ""
    )

    if not bot_message:
        return True  # Fail-open: do not block when response is unreadable

    bot_lower = bot_message.lower()

    has_evidence = any(marker in bot_lower for marker in _EVIDENCE_MARKERS)
    has_uncertainty = any(marker in bot_lower for marker in _UNCERTAINTY_MARKERS)
    no_absolute_claims = not any(
        re.search(pattern, bot_lower) for pattern in _ABSOLUTE_CLAIM_PATTERNS
    )

    return has_evidence and has_uncertainty and no_absolute_claims
