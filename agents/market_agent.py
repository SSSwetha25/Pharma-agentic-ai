# agents/market_agent.py

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import re


# ============================================================
# Configuration
# ============================================================

DEFAULT_PROJECTION_YEARS = 6


# ============================================================
# Source-backed Market Database
# ============================================================

MARKET_SOURCES = {
    "obesity": {
        "category": "Obesity / Anti-Obesity Medicines",

        # Source-reported values
        "market_size_2026": 92.0,
        "market_size_unit": "USD billion",
        "market_size_year": 2026,
        "cagr": "13–15%",
        "forecast_year": 2034,
        "forecast_market_size": 130.0,
        "competition_level": "Very High",

        "key_drivers": [
            "Rapid adoption of GLP-1 and GLP-1/GIP therapies",
            "Increasing global obesity prevalence",
            "Expansion of treatment access and reimbursement",
            "New oral and next-generation obesity therapies",
            "Expansion of clinical indications for metabolic therapies",
        ],

        "source": {
            "name": "IQVIA",
            "title": (
                "IQVIA Early Bird: 2025 Revealed - "
                "The Trends Shaping Pharma's Future"
            ),
            "url": (
                "https://www.iqvia.com/blogs/2026/03/"
                "iqvia-early-bird-2025-revealed"
            ),
        },

        "secondary_source": {
            "name": "World Health Organization",
            "title": "Obesity and overweight",
            "url": (
                "https://www.who.int/news-room/fact-sheets/"
                "detail/obesity-and-overweight"
            ),
        },

        # Used only for the separate derived projection series.
        "projection_growth_rate": 0.14,
        "projection_growth_rate_label": (
            "14% midpoint of reported 13–15% range"
        ),
    },
}


# ============================================================
# Query Parsing
# ============================================================

def _contains_keyword(query: str, keyword: str) -> bool:
    """Match a keyword/phrase without accidental substring matches."""
    query = query.lower().strip()
    keyword = keyword.lower().strip()

    pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
    return re.search(pattern, query) is not None


def _extract_market_category(
    user_query: str,
) -> Optional[str]:
    """Determine the most relevant market category from the query."""

    query = user_query.lower()

    obesity_keywords = [
        "obesity",
        "obese",
        "weight loss",
        "weight management",
        "anti-obesity",
        "anti obesity",
        "glp-1",
        "glp1",
        "glp",
        "semaglutide",
        "tirzepatide",
        "liraglutide",
        "dulaglutide",
        "cagrilintide",
    ]

    if any(
        _contains_keyword(query, keyword)
        for keyword in obesity_keywords
    ):
        return "obesity"

    oncology_keywords = [
        "oncology",
        "cancer",
        "tumor",
        "nsclc",
        "leukemia",
    ]

    if any(
        _contains_keyword(query, keyword)
        for keyword in oncology_keywords
    ):
        return "oncology"

    cardiovascular_keywords = [
        "cardio",
        "cardiovascular",
        "heart",
        "hypertension",
        "stroke",
        "atherosclerosis",
    ]

    if any(
        _contains_keyword(query, keyword)
        for keyword in cardiovascular_keywords
    ):
        return "cardiovascular"

    neurology_keywords = [
        "alzheimer",
        "alzheimer's",
        "dementia",
        "neurology",
        "parkinson",
        "multiple sclerosis",
        "ms",
        "als",
    ]

    if any(
        _contains_keyword(query, keyword)
        for keyword in neurology_keywords
    ):
        return "neurology"

    immunology_keywords = [
        "immunology",
        "arthritis",
        "lupus",
        "autoimmune",
        "psoriasis",
        "crohn",
    ]

    if any(
        _contains_keyword(query, keyword)
        for keyword in immunology_keywords
    ):
        return "immunology"

    if _contains_keyword(query, "diabetes"):
        return "diabetes"

    return None


# ============================================================
# Projection Generator
# ============================================================

def _generate_projections(
    base_value: float,
    growth_rate: float,
    start_year: int,
    number_of_years: int,
) -> List[Dict[str, Any]]:
    """
    Generate model-derived projections.

    These are NOT source-reported forecast values.
    """

    projections = []
    current_value = base_value

    for year in range(
        start_year,
        start_year + number_of_years,
    ):
        projections.append(
            {
                "Year": str(year),
                "Market Size ($B)": round(current_value, 2),
                "Data Type": (
                    "Source baseline"
                    if year == start_year
                    else "Derived projection"
                ),
            }
        )

        current_value *= 1 + growth_rate

    return projections


# ============================================================
# Strategic Signal Extraction
# ============================================================

def _build_strategic_signals(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert source-backed market facts into structured
    strategic signals.

    These are interpretations of the supplied evidence,
    not independently sourced market facts.
    """

    competition = data["competition_level"]
    cagr = data["cagr"]

    if competition == "Very High":
        competitive_intensity = {
            "level": "Very High",
            "assessment": (
                "The market is highly competitive, so entry "
                "would likely require meaningful differentiation."
            ),
        }
    else:
        competitive_intensity = {
            "level": competition,
            "assessment": (
                "Competitive intensity should be assessed "
                "alongside the available market evidence."
            ),
        }

    growth_outlook = {
        "reported_range": cagr,
        "assessment": (
            "The reported growth range indicates strong "
            "market expansion potential."
        ),
    }

    opportunity = {
        "level": "Strong market potential",
        "rationale": (
            f"Large reported market size combined with a "
            f"{cagr} growth range indicates substantial "
            "commercial activity."
        ),
    }

    risks = [
        "Very high competitive intensity",
        "Market-size estimates depend on the cited source's methodology",
        "The derived projection series is not the source's official forecast",
        "Patent and regulatory evidence must be assessed separately",
    ]

    limitations = [
        "Current market figures are source-backed rather than live API retrieval",
        "Only selected therapeutic categories currently have source-backed data",
        "Market attractiveness does not by itself establish investment feasibility",
    ]

    next_step = (
        "Combine market evidence with validated clinical, patent/IP, "
        "regulatory, and competitive evidence before making an investment decision."
    )

    return {
        "opportunity": opportunity,
        "competitive_intensity": competitive_intensity,
        "growth_outlook": growth_outlook,
        "key_drivers": data["key_drivers"],
        "risks": risks,
        "evidence_limitations": limitations,
        "recommended_next_step": next_step,
    }


# ============================================================
# Main Market Agent
# ============================================================

def run_market_agent(
    user_query: str,
) -> Dict[str, Any]:
    """
    Market & Competition Intelligence Agent.

    Returns source-backed market information where reliable
    public data is available, plus structured strategic
    interpretations of that evidence.

    Unsupported markets return an explicit unavailable state
    instead of fabricated numbers.
    """

    retrieved_at = datetime.now(
        timezone.utc
    ).isoformat()

    category_key = _extract_market_category(
        user_query
    )

    # --------------------------------------------------------
    # Unsupported category
    # --------------------------------------------------------

    if category_key is None:
        return {
            "agent": "market",
            "query": user_query,
            "category": "Unknown",
            "status": "UNAVAILABLE",
            "retrieved_at": retrieved_at,
            "source": None,
            "secondary_source": None,
            "summary": (
                "A reliable source-backed market estimate "
                "could not be identified for the requested "
                "therapeutic area."
            ),
            "market_data": {
                "estimated_size": "Unavailable",
                "cagr": "Unavailable",
                "competition_level": "Unavailable",
                "key_drivers": [],
                "source_reported": {},
                "derived_projection": [],
                "projections": [],
                "strategic_signals": {},
                "data_quality": "Insufficient",
            },
        }

    # --------------------------------------------------------
    # Recognized category but data unavailable
    # --------------------------------------------------------

    if category_key not in MARKET_SOURCES:
        readable_category = category_key.title()

        return {
            "agent": "market",
            "query": user_query,
            "category": readable_category,
            "status": "UNAVAILABLE",
            "retrieved_at": retrieved_at,
            "source": None,
            "secondary_source": None,
            "summary": (
                f"The {readable_category} market was identified, "
                "but the current implementation does not have "
                "a sufficiently reliable source-backed "
                "market-size estimate for it."
            ),
            "market_data": {
                "estimated_size": "Unavailable",
                "cagr": "Unavailable",
                "competition_level": "Unavailable",
                "key_drivers": [],
                "source_reported": {},
                "derived_projection": [],
                "projections": [],
                "strategic_signals": {},
                "data_quality": "Insufficient",
            },
        }

    data = MARKET_SOURCES[category_key]

    base_value = data["market_size_2026"]
    growth_rate = data["projection_growth_rate"]

    # --------------------------------------------------------
    # Derived projections
    # --------------------------------------------------------

    derived_projections = _generate_projections(
        base_value=base_value,
        growth_rate=growth_rate,
        start_year=data["market_size_year"],
        number_of_years=DEFAULT_PROJECTION_YEARS,
    )

    # --------------------------------------------------------
    # Source-reported evidence
    # --------------------------------------------------------

    source_reported = {
        "market_size": f"USD {base_value:.1f}B",
        "market_size_numeric": base_value,
        "market_size_year": data["market_size_year"],
        "market_size_unit": data["market_size_unit"],
        "cagr": data["cagr"],
        "forecast_year": data["forecast_year"],
        "forecast_market_size": (
            f"USD {data['forecast_market_size']:.1f}B"
        ),
        "competition_level": data["competition_level"],
    }

    strategic_signals = _build_strategic_signals(data)

    summary = (
        f"The {data['category']} market is estimated at "
        f"approximately USD {base_value:.1f}B in "
        f"{data['market_size_year']} according to "
        f"{data['source']['name']}. The source reports a "
        f"{data['cagr']} growth range and a "
        f"USD {data['forecast_market_size']:.1f}B market "
        f"forecast for {data['forecast_year']}. "
        f"The segment currently faces "
        f"{data['competition_level'].lower()} "
        f"competitive pressure."
    )

    return {
        "agent": "market",
        "query": user_query,
        "category": data["category"],
        "status": "SUCCESS",
        "retrieved_at": retrieved_at,
        "source": data["source"],
        "secondary_source": data["secondary_source"],
        "summary": summary,

        "market_data": {
            # Backward-compatible fields
            "estimated_size": f"USD {base_value:.1f}B",
            "estimated_size_numeric": base_value,
            "estimated_size_year": data["market_size_year"],
            "cagr": data["cagr"],
            "forecast_year": data["forecast_year"],
            "forecast_market_size": (
                f"USD {data['forecast_market_size']:.1f}B"
            ),
            "competition_level": data["competition_level"],
            "key_drivers": data["key_drivers"],

            # Evidence separation
            "source_reported": source_reported,
            "derived_projection": derived_projections,
            "projections": derived_projections,

            # New strategic layer
            "strategic_signals": strategic_signals,

            "projection_method": (
                "Derived using the 14% midpoint of the "
                "source-reported 13–15% growth range."
            ),

            "data_quality": (
                "Source-backed market size, growth range, "
                "and source forecast; derived projections "
                "and strategic signals are calculated or "
                "interpreted separately."
            ),
        },
    }


# ============================================================
# Standalone Test
# ============================================================

if __name__ == "__main__":

    test_query = (
        "Find recruiting Phase 3 obesity trials "
        "involving semaglutide in the US"
    )

    result = run_market_agent(test_query)

    print("\n" + "=" * 70)
    print("MARKET AGENT TEST")
    print("=" * 70)

    print("\nQUERY:")
    print(result["query"])

    print("\nCATEGORY:")
    print(result["category"])

    print("\nSTATUS:")
    print(result["status"])

    print("\nSOURCE:")
    print(result.get("source"))

    print("\nRETRIEVED AT:")
    print(result["retrieved_at"])

    print("\nSUMMARY:")
    print(result["summary"])

    print("\nSOURCE-REPORTED DATA:")
    print(result["market_data"]["source_reported"])

    print("\nSTRATEGIC SIGNALS:")
    for key, value in result["market_data"]["strategic_signals"].items():
        print(f"\n{key.upper()}:")
        print(value)

    print("\nDERIVED PROJECTIONS:")
    for projection in result["market_data"]["derived_projection"]:
        print(
            f"{projection['Year']}: "
            f"{projection['Market Size ($B)']}B "
            f"({projection['Data Type']})"
        )

    print("\nDATA QUALITY:")
    print(result["market_data"]["data_quality"])
