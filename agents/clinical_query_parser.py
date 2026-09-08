import re
from typing import Dict, Optional


PHASE_PATTERNS = {
    "PHASE1": [
        r"\bphase\s*1\b",
        r"\bphase\s*i\b",
    ],
    "PHASE2": [
        r"\bphase\s*2\b",
        r"\bphase\s*ii\b",
    ],
    "PHASE3": [
        r"\bphase\s*3\b",
        r"\bphase\s*iii\b",
    ],
    "PHASE4": [
        r"\bphase\s*4\b",
        r"\bphase\s*iv\b",
    ],
}


STATUS_PATTERNS = {
    "RECRUITING": [
        r"\brecruiting\b",
        r"\bcurrently recruiting\b",
    ],
    "NOT_YET_RECRUITING": [
        r"\bnot yet recruiting\b",
    ],
    "ACTIVE_NOT_RECRUITING": [
        r"\bactive but not recruiting\b",
        r"\bactive not recruiting\b",
    ],
    "COMPLETED": [
        r"\bcompleted\b",
    ],
}


LOCATION_PATTERNS = {
    "United States": [
        r"\bin the us\b",
        r"\bin us\b",
        r"\bin usa\b",
        r"\bin the usa\b",
        r"\bunited states\b",
        r"\bunited states of america\b",
    ],
    "India": [
        r"\bin india\b",
        r"\bindia\b",
    ],
    "United Kingdom": [
        r"\bin the uk\b",
        r"\bin uk\b",
        r"\bunited kingdom\b",
    ],
}


def parse_clinical_query(query: str) -> Dict[str, Optional[str]]:
    query_lower = query.lower()

    phase = _extract_phase(query_lower)
    status = _extract_status(query_lower)
    location = _extract_location(query_lower)
    intervention = _extract_intervention(query)

    condition = _extract_condition(
        query,
        phase,
        status,
        location,
        intervention,
    )

    return {
        "original_query": query,
        "condition": condition,
        "intervention": intervention,
        "phase": phase,
        "status": status,
        "location": location,
    }


def _extract_phase(query: str) -> Optional[str]:
    for phase, patterns in PHASE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query):
                return phase

    return None


def _extract_status(query: str) -> Optional[str]:
    for status, patterns in STATUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query):
                return status

    return None


def _extract_location(query: str) -> Optional[str]:
    for location, patterns in LOCATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query):
                return location

    return None


def _extract_intervention(query: str) -> Optional[str]:
    """
    Extract a likely drug/intervention from common user phrasings.
    """

    patterns = [
        r"\binvolving\s+(.+?)(?=\s+in\s+the\s+|\s+in\s+|\s+for\s+|\s*$)",
        r"\bwith\s+(.+?)(?=\s+in\s+the\s+|\s+in\s+|\s+for\s+|\s*$)",
        r"\busing\s+(.+?)(?=\s+in\s+the\s+|\s+in\s+|\s+for\s+|\s*$)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            query,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return None


def _extract_condition(
    original_query: str,
    phase: Optional[str],
    status: Optional[str],
    location: Optional[str],
    intervention: Optional[str],
) -> str:
    condition = original_query

    # Remove common query-intent phrases
    intent_patterns = [
        r"\bfind\b",
        r"\bshow me\b",
        r"\bshow\b",
        r"\bsearch for\b",
        r"\blook for\b",
        r"\bget\b",
    ]

    for pattern in intent_patterns:
        condition = re.sub(
            pattern,
            " ",
            condition,
            flags=re.IGNORECASE,
        )

    # Remove phase expressions
    condition = re.sub(
        r"\bphase\s*(?:1|2|3|4|i|ii|iii|iv)\b",
        " ",
        condition,
        flags=re.IGNORECASE,
    )

    # Remove status expressions
    for patterns in STATUS_PATTERNS.values():
        for pattern in patterns:
            condition = re.sub(
                pattern,
                " ",
                condition,
                flags=re.IGNORECASE,
            )

    # Remove location expressions
    for patterns in LOCATION_PATTERNS.values():
        for pattern in patterns:
            condition = re.sub(
                pattern,
                " ",
                condition,
                flags=re.IGNORECASE,
            )

    # Remove intervention text itself
    if intervention:
        condition = re.sub(
            re.escape(intervention),
            " ",
            condition,
            flags=re.IGNORECASE,
        )

    # Remove intervention trigger words
    intervention_words = [
        r"\binvolving\b",
        r"\busing\b",
        r"\bwith\b",
    ]

    for pattern in intervention_words:
        condition = re.sub(
            pattern,
            " ",
            condition,
            flags=re.IGNORECASE,
        )

    # Remove trial-related words
    trial_terms = [
        r"\bclinical trials?\b",
        r"\btrials?\b",
        r"\bstudies\b",
        r"\bstudy\b",
    ]

    for pattern in trial_terms:
        condition = re.sub(
            pattern,
            " ",
            condition,
            flags=re.IGNORECASE,
        )

    # Remove leftover filler words
    filler_words = [
        r"\bin\b",
        r"\bthe\b",
        r"\bfor\b",
        r"\bon\b",
        r"\bof\b",
    ]

    for pattern in filler_words:
        condition = re.sub(
            pattern,
            " ",
            condition,
            flags=re.IGNORECASE,
        )

    condition = re.sub(
        r"\s+",
        " ",
        condition,
    ).strip()

    return condition