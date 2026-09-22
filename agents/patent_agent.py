# agents/patent_agent.py

import re
import requests
import pandas as pd

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus
from evidence.evidence_schema import create_evidence


# ============================================================
# Configuration
# ============================================================

GOOGLE_PATENTS_URL = "https://patents.google.com"

REQUEST_TIMEOUT = 20

DEFAULT_RESULT_LIMIT = 10


# ============================================================
# Query Extraction
# ============================================================

def _extract_geography(user_query: str) -> str:
    """
    Extract the requested patent jurisdiction from the
    natural-language query.
    """

    query = user_query.lower()

    if (
        "united states" in query
        or "us" in query
        or "usa" in query
        or "u.s." in query
        or "america" in query
    ):
        return "US"

    if (
        "europe" in query
        or "eu" in query
        or "european" in query
    ):
        return "EP"

    if (
        "japan" in query
        or "jp" in query
    ):
        return "JP"

    if (
        "india" in query
        or "indian" in query
    ):
        return "IN"

    if (
        "china" in query
        or "chinese" in query
    ):
        return "CN"

    return "US"


# ============================================================
# Query Extraction: Intervention / Drug
# ============================================================

def _extract_intervention(
    user_query: str
) -> Optional[str]:
    """
    Extract a likely pharmaceutical intervention from the query.

    This is intentionally conservative.

    Examples:

        involving semaglutide
        with pembrolizumab
        using tirzepatide
        for semaglutide
    """

    patterns = [
        r"involving\s+([a-zA-Z0-9\-]+)",
        r"involve\s+([a-zA-Z0-9\-]+)",
        r"with\s+([a-zA-Z0-9\-]+)",
        r"using\s+([a-zA-Z0-9\-]+)",
    ]

    query = user_query.lower()

    for pattern in patterns:

        match = re.search(
            pattern,
            query,
        )

        if match:

            value = match.group(
                1
            ).strip()

            if value:

                return value

    # --------------------------------------------------------
    # Known pharmaceutical names
    # --------------------------------------------------------

    known_drugs = [
        "semaglutide",
        "tirzepatide",
        "pembrolizumab",
        "nivolumab",
        "trastuzumab",
        "adalimumab",
        "infliximab",
        "dulaglutide",
        "liraglutide",
        "empagliflozin",
        "dapagliflozin",
        "metformin",
        "osimertinib",
        "sotorasib",
    ]

    for drug in known_drugs:

        if drug in query:
            return drug

    return None


# ============================================================
# Query Extraction: Condition
# ============================================================

def _extract_condition(
    user_query: str
) -> Optional[str]:
    """
    Extract a likely disease/therapeutic condition.

    This is a lightweight extraction layer. The Clinical Agent
    already has a stronger domain-specific parser; eventually
    both agents can share a common query planner.
    """

    query = user_query.lower()

    known_conditions = [
        "obesity",
        "diabetes",
        "type 2 diabetes",
        "breast cancer",
        "lung cancer",
        "prostate cancer",
        "colorectal cancer",
        "alzheimer's disease",
        "alzheimers disease",
        "atrial fibrillation",
        "heart failure",
        "hypertension",
        "asthma",
        "rheumatoid arthritis",
        "psoriasis",
        "multiple sclerosis",
    ]

    # Prefer longer phrases first.
    known_conditions.sort(
        key=len,
        reverse=True,
    )

    for condition in known_conditions:

        if condition in query:
            return condition

    return None


# ============================================================
# Search Query Construction
# ============================================================

def _build_patent_query(
    user_query: str,
) -> Dict[str, Any]:
    """
    Convert the natural-language user query into a patent
    search query.
    """

    geography = _extract_geography(
        user_query
    )

    intervention = _extract_intervention(
        user_query
    )

    condition = _extract_condition(
        user_query
    )

    # --------------------------------------------------------
    # Build search terms
    # --------------------------------------------------------

    search_terms = []

    if intervention:
        search_terms.append(
            intervention
        )

    elif condition:
        search_terms.append(
            condition
        )

    else:
        # Remove common instruction words.
        cleaned = user_query.lower()

        stop_words = [
            "find",
            "show",
            "search",
            "patents",
            "patent",
            "related",
            "relevant",
            "active",
            "status",
            "landscape",
            "ip",
            "intellectual",
            "property",
        ]

        for word in stop_words:

            cleaned = re.sub(
                rf"\b{re.escape(word)}\b",
                " ",
                cleaned,
            )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        ).strip()

        if cleaned:
            search_terms.append(
                cleaned
            )

    search_query = " ".join(
        search_terms
    )

    return {
        "geography": geography,
        "intervention": intervention,
        "condition": condition,
        "search_query": search_query,
    }


# ============================================================
# Google Patents Search
# ============================================================

def _search_google_patents(
    search_query: str,
    geography: str,
    limit: int = DEFAULT_RESULT_LIMIT,
) -> List[Dict[str, Any]]:
    """
    Search Google Patents public search pages.

    Google Patents supports free-text searches and country
    restrictions.

    This function extracts basic bibliographic information
    from search result HTML.
    """

    if not search_query:
        return []

    encoded_query = quote_plus(
        search_query
    )

    # Google Patents search URL.
    search_url = (
        f"{GOOGLE_PATENTS_URL}/"
        f"?q={encoded_query}"
        f"&country={geography}"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0 Safari/537.36"
        )
    }

    try:

        response = requests.get(
            search_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:

        raise RuntimeError(
            "Google Patents request timed out."
        )

    except requests.exceptions.RequestException as exc:

        raise RuntimeError(
            f"Google Patents request failed: {exc}"
        )

    html = response.text

    # --------------------------------------------------------
    # Extract patent result links
    # --------------------------------------------------------

    patent_pattern = re.compile(
        r'href="(/patent/[^"]+)"',
        re.IGNORECASE,
    )

    links = patent_pattern.findall(
        html
    )

    # --------------------------------------------------------
    # Deduplicate links
    # --------------------------------------------------------

    unique_links = []

    seen = set()

    for link in links:

        if link in seen:
            continue

        seen.add(link)

        unique_links.append(
            link
        )

    # --------------------------------------------------------
    # Extract individual patent pages
    # --------------------------------------------------------

    results = []

    for link in unique_links[:limit]:

        patent_url = (
            GOOGLE_PATENTS_URL
            + link
        )

        try:

            patent_response = requests.get(
                patent_url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            if patent_response.status_code != 200:
                continue

            patent_html = (
                patent_response.text
            )

        except requests.exceptions.RequestException:

            continue

        patent_data = (
            _parse_patent_page(
                patent_html,
                patent_url,
            )
        )

        if patent_data:

            results.append(
                patent_data
            )

    return results


# ============================================================
# Patent Page Parser
# ============================================================

def _extract_meta_content(
    html: str,
    name: str,
) -> Optional[str]:
    """
    Extract content from a meta tag.
    """

    pattern = re.compile(
        rf'<meta[^>]+'
        rf'(?:name|scheme|property)="'
        rf'{re.escape(name)}"'
        rf'[^>]+content="([^"]*)"',
        re.IGNORECASE,
    )

    match = pattern.search(
        html
    )

    if match:
        return match.group(1).strip()

    return None


def _extract_title(
    html: str
) -> Optional[str]:
    """
    Extract the patent title from the HTML.
    """

    # Google Patents uses DC.title in many pages.
    title = _extract_meta_content(
        html,
        "DC.title",
    )

    if title:
        return title

    # Fallback to HTML title.
    match = re.search(
        r"<title>(.*?)</title>",
        html,
        re.IGNORECASE | re.DOTALL,
    )

    if match:

        title = re.sub(
            r"\s+",
            " ",
            match.group(1),
        ).strip()

        return title

    return None


def _extract_patent_number(
    html: str,
) -> Optional[str]:
    """
    Extract a patent/publication number.
    """

    patterns = [
        r'<dd itemprop="publicationNumber">'
        r'\s*([^<]+)',

        r'"publicationNumber"\s*:\s*"([^"]+)"',

        r'Publication number'
        r'.{0,300}?'
        r'(US\d+[A-Z]\d)',
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            re.IGNORECASE | re.DOTALL,
        )

        if match:

            value = (
                match.group(1)
                .strip()
            )

            if value:
                return value

    return None


def _extract_assignee(
    html: str,
) -> Optional[str]:
    """
    Extract current/primary assignee.
    """

    patterns = [
        r'<dd itemprop="assigneeOriginal">'
        r'\s*([^<]+)',

        r'<dd itemprop="assignee">'
        r'\s*([^<]+)',
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            re.IGNORECASE,
        )

        if match:

            value = (
                match.group(1)
                .strip()
            )

            if value:
                return value

    return None


def _extract_date(
    html: str,
    property_name: str,
) -> Optional[str]:
    """
    Extract a patent date from an itemprop field.
    """

    pattern = re.compile(
        rf'<time[^>]+'
        rf'itemprop="{re.escape(property_name)}"'
        rf'[^>]*>(.*?)</time>',
        re.IGNORECASE | re.DOTALL,
    )

    match = pattern.search(
        html
    )

    if match:

        value = re.sub(
            r"<[^>]+>",
            "",
            match.group(1),
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

        return value

    return None


def _extract_status(
    html: str,
) -> str:
    """
    Extract legal status when available.

    Google Patents labels legal status as an assumption,
    so this should be treated as research metadata rather
    than a legal conclusion.
    """

    patterns = [
        r'<meta[^>]+'
        r'itemprop="status"'
        r'[^>]+content="([^"]+)"',

        r'<dd[^>]+'
        r'itemprop="legalStatus"'
        r'[^>]*>(.*?)</dd>',
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            re.IGNORECASE | re.DOTALL,
        )

        if match:

            value = re.sub(
                r"<[^>]+>",
                "",
                match.group(1),
            )

            value = re.sub(
                r"\s+",
                " ",
                value,
            ).strip()

            if value:
                return value

    return "Unknown"


def _parse_patent_page(
    html: str,
    patent_url: str,
) -> Optional[Dict[str, Any]]:
    """
    Parse basic bibliographic information from a Google
    Patents page.
    """

    patent_number = (
        _extract_patent_number(
            html
        )
    )

    title = _extract_title(
        html
    )

    if not patent_number and not title:
        return None

    assignee = _extract_assignee(
        html
    )

    filing_date = _extract_date(
        html,
        "filingDate",
    )

    publication_date = _extract_date(
        html,
        "publicationDate",
    )

    grant_date = _extract_date(
        html,
        "grantDate",
    )

    priority_date = _extract_date(
        html,
        "priorityDate",
    )

    status = _extract_status(
        html
    )

    return {
        "Patent ID": patent_number or "Unknown",
        "Title": title or "Unknown",
        "Assignee": assignee or "Unknown",
        "Status": status,
        "Filing Date": filing_date,
        "Publication Date": publication_date,
        "Grant Date": grant_date,
        "Priority Date": priority_date,
        "Source URL": patent_url,
    }


# ============================================================
# Relevance Scoring
# ============================================================

def _calculate_relevance(
    patent: Dict[str, Any],
    search_query: str,
) -> float:
    """
    Calculate a simple research relevance score.

    This is NOT an ML model and NOT a legal determination.
    """

    title = (
        patent.get(
            "Title",
            "",
        )
        or ""
    ).lower()

    query_terms = [
        term
        for term in search_query.lower().split()
        if len(term) > 2
    ]

    if not query_terms:
        return 0.0

    matches = 0

    for term in query_terms:

        if term in title:
            matches += 1

    score = (
        matches / len(query_terms)
    )

    return round(
        score,
        2,
    )


# ============================================================
# Risk Classification
# ============================================================

def _classify_risk(
    patent: Dict[str, Any],
    relevance_score: float,
) -> str:
    """
    Assign a research-oriented IP risk category.

    Important:
    This does NOT establish legal FTO.
    """

    status = (
        patent.get(
            "Status",
            "",
        )
        or ""
    ).lower()

    # --------------------------------------------------------
    # Expired
    # --------------------------------------------------------

    if (
        "expired" in status
        or "ceased" in status
    ):
        return "Low"

    # --------------------------------------------------------
    # Active / Granted
    # --------------------------------------------------------

    if (
        "active" in status
        or "granted" in status
    ):

        if relevance_score >= 0.8:
            return "High"

        if relevance_score >= 0.4:
            return "Moderate"

        return "Low"

    # --------------------------------------------------------
    # Pending / Application
    # --------------------------------------------------------

    if (
        "pending" in status
        or "application" in status
    ):

        if relevance_score >= 0.8:
            return "Moderate"

        return "Low"

    # --------------------------------------------------------
    # Unknown
    # --------------------------------------------------------

    if relevance_score >= 0.8:
        return "Moderate"

    return "Unknown"


# ============================================================
# Main Patent Agent
# ============================================================

def run_patent_agent(
    user_query: str,
) -> Dict[str, Any]:
    """
    Search and analyze the patent landscape for the
    requested pharmaceutical opportunity.

    Returns a structure compatible with the existing
    Master Agent.
    """

    retrieved_at = datetime.now(
        timezone.utc
    ).isoformat()

    # --------------------------------------------------------
    # Parse query
    # --------------------------------------------------------

    search_context = _build_patent_query(
        user_query
    )

    geography = search_context[
        "geography"
    ]

    intervention = search_context[
        "intervention"
    ]

    condition = search_context[
        "condition"
    ]

    search_query = search_context[
        "search_query"
    ]

    # --------------------------------------------------------
    # Search patents
    # --------------------------------------------------------

    try:

        patent_records = (
            _search_google_patents(
                search_query=search_query,
                geography=geography,
                limit=DEFAULT_RESULT_LIMIT,
            )
        )

    except RuntimeError as exc:

        empty_df = pd.DataFrame(
            columns=[
                "Patent ID",
                "Title",
                "Assignee",
                "Status",
                "Filing Date",
                "Publication Date",
                "Grant Date",
                "Priority Date",
                "Source URL",
                "Relevance Score",
                "Risk Level",
            ]
        )
        evidence_records = [
            create_evidence(
                source="Google Patents",
                source_type="patent_database",
                claim=(
                    f"Patent/IP evidence could not be retrieved for "
                    f"{intervention or condition or search_query} "
                    f"in the {geography} jurisdiction."
                ),
                evidence=(
                    f"The currently implemented Google Patents retrieval "
                    f"operation failed: {exc}"
                ),
                url=GOOGLE_PATENTS_URL,
                status="unavailable",
                confidence="unknown",
                agent="Patent Agent",
                record_id="patent_search",
            ).to_dict()
        ]
        return {
            "agent": "patent",
            "query": user_query,
            "geography": geography,
            "search_context": search_context,
            "source": "Google Patents",
            "retrieved_at": retrieved_at,
            "patent_count": 0,
            "summary": (
                "Patent search could not be completed: "
                f"{exc}"
            ),
            "patents": empty_df,
            "error": str(exc),
            "evidence": evidence_records,
        }

    # --------------------------------------------------------
    # Score patents
    # --------------------------------------------------------

    processed_patents = []

    for patent in patent_records:

        relevance_score = (
            _calculate_relevance(
                patent,
                search_query,
            )
        )

        risk_level = (
            _classify_risk(
                patent,
                relevance_score,
            )
        )

        patent[
            "Relevance Score"
        ] = relevance_score

        patent[
            "Risk Level"
        ] = risk_level

        patent[
            "Geography"
        ] = geography

        patent[
            "Retrieved At"
        ] = retrieved_at

        processed_patents.append(
            patent
        )

    # --------------------------------------------------------
    # DataFrame
    # --------------------------------------------------------

    patents_df = pd.DataFrame(
        processed_patents
    )

    # --------------------------------------------------------
    # Determine maximum risk
    # --------------------------------------------------------

    max_risk = "Unknown"

    risk_levels = (
        patents_df[
            "Risk Level"
        ].tolist()
        if not patents_df.empty
        else []
    )

    if "High" in risk_levels:

        max_risk = "High"

    elif "Moderate" in risk_levels:

        max_risk = "Moderate"

    elif "Low" in risk_levels:

        max_risk = "Low"

        # --------------------------------------------------------
    # Build standardized patent evidence records
    # --------------------------------------------------------

    evidence_records = []

    if patent_records:

        for patent in processed_patents:

            evidence_records.append(
                create_evidence(
                    source="Google Patents",
                    source_type="patent_database",
                    claim=(
                        f"Potentially relevant patent record "
                        f"{patent.get('Patent ID', 'Unknown')} "
                        f"was retrieved."
                    ),
                    evidence=(
                        f"Patent title: {patent.get('Title', 'Unknown')}. "
                        f"Assignee: {patent.get('Assignee', 'Unknown')}. "
                        f"Status: {patent.get('Status', 'Unknown')}. "
                        f"Research relevance score: "
                        f"{patent.get('Relevance Score', 0)}. "
                        f"Research risk classification: "
                        f"{patent.get('Risk Level', 'Unknown')}."
                    ),
                    url=patent.get("Source URL"),
                    status="retrieved",
                    confidence="moderate",
                    agent="Patent Agent",
                    record_id=patent.get(
                        "Patent ID",
                        "Unknown"
                    ),
                ).to_dict()
            )

    else:

        evidence_records.append(
            create_evidence(
                source="Google Patents",
                source_type="patent_database",
                claim=(
                    f"No patent records were retrieved by the "
                    f"currently implemented search for "
                    f"'{search_query}' in {geography}."
                ),
                evidence=(
                    "The search completed without returning "
                    "patent records. This does not establish "
                    "that no relevant patents exist."
                ),
                url=(
                    f"{GOOGLE_PATENTS_URL}/"
                ),
                status="no_records_returned",
                confidence="unknown",
                agent="Patent Agent",
                record_id="patent_search",
            ).to_dict()
        )

    # --------------------------------------------------------
    # Generate summary
    # --------------------------------------------------------

    if not patent_records:

        summary = (
            f"No relevant patent records were retrieved "
            f"for '{search_query}' in the {geography} "
            f"jurisdiction."
        )

    else:

        summary = (
            f"Retrieved {len(patent_records)} potentially "
            f"relevant patent records for "
            f"'{search_query}' in {geography}. "
            f"The highest research-oriented IP risk "
            f"identified was {max_risk}. "
            f"This is a preliminary patent-landscape "
            f"assessment and does not constitute a legal "
            f"Freedom-to-Operate opinion."
        )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "agent": "patent",

        "query": user_query,

        "geography": geography,

        "search_context": search_context,

        "source": "Google Patents",

        "source_url": GOOGLE_PATENTS_URL,

        "retrieved_at": retrieved_at,

        "patent_count": len(
            patent_records
        ),

        "max_risk": max_risk,

        "summary": summary,

        "patents": patents_df,

        "evidence": evidence_records,
    }


# ============================================================
# Standalone Test
# ============================================================

if __name__ == "__main__":

    test_query = (
        "Find patents related to semaglutide "
        "for obesity in the US"
    )

    result = run_patent_agent(
        test_query
    )

    print("\n" + "=" * 70)
    print("PATENT AGENT TEST")
    print("=" * 70)

    print("\nQUERY:")
    print(
        result["query"]
    )

    print("\nSEARCH CONTEXT:")
    print(
        result["search_context"]
    )

    print("\nSOURCE:")
    print(
        result["source"]
    )

    print("\nRETRIEVED AT:")
    print(
        result["retrieved_at"]
    )

    print("\nPATENTS FOUND:")
    print(
        result["patent_count"]
    )

    print("\nMAX RESEARCH RISK:")
    print(
        result["max_risk"]
    )

    print("\nSUMMARY:")
    print(
        result["summary"]
    )

    patents = result[
        "patents"
    ]

    if not patents.empty:

        print(
            "\n" + "-" * 70
        )

        for _, row in patents.iterrows():

            print(
                f"\nPatent: "
                f"{row.get('Patent ID', 'Unknown')}"
            )

            print(
                f"Title: "
                f"{row.get('Title', 'Unknown')}"
            )

            print(
                f"Assignee: "
                f"{row.get('Assignee', 'Unknown')}"
            )

            print(
                f"Status: "
                f"{row.get('Status', 'Unknown')}"
            )

            print(
                f"Relevance: "
                f"{row.get('Relevance Score', 0)}"
            )

            print(
                f"Risk: "
                f"{row.get('Risk Level', 'Unknown')}"
            )

            print(
                f"Source: "
                f"{row.get('Source URL', 'Unknown')}"
            )

            print(
                "-" * 70
            )