# master_agent.py

from typing import Dict, Any

from agents.clinical_agent import run_clinical_agent
from agents.patent_agent import run_patent_agent
from agents.market_agent import run_market_agent


# ============================================================
# Helper Functions
# ============================================================

def _get_indication(clinical_results: Dict[str, Any]) -> str:
    """
    Extract the primary indication from the parsed clinical query.
    """

    parsed_query = clinical_results.get(
        "parsed_query",
        {}
    )

    condition = parsed_query.get(
        "condition"
    )

    if condition:
        return condition

    return "General"


def _get_geography(clinical_results: Dict[str, Any]) -> str:
    """
    Extract the requested geography from the clinical query.
    """

    parsed_query = clinical_results.get(
        "parsed_query",
        {}
    )

    location = parsed_query.get(
        "location"
    )

    if location:
        return location

    return "Global"


def _calculate_patent_risk(
    patent_results: Dict[str, Any]
) -> str:
    """
    Determine the highest patent risk returned by the
    Patent Agent.

    This remains compatible with the existing Patent Agent,
    which returns a pandas DataFrame.
    """

    patents = patent_results.get(
        "patents"
    )

    if patents is None:
        return "Unknown"

    try:

        if patents.empty:
            return "Unknown"

        risks = patents[
            "Risk Level"
        ].tolist()

    except (
        AttributeError,
        KeyError,
        TypeError,
    ):
        return "Unknown"

    if "High" in risks:
        return "High"

    if (
        "Moderate" in risks
        or "Medium" in risks
    ):
        return "Moderate"

    if "Low" in risks:
        return "Low"

    return "Unknown"


def _get_market_data(
    market_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Safely extract the structured market evidence produced
    by the Market Agent.

    Backward-compatible with the original market fields while
    preserving richer source and strategic information.
    """

    market_data = market_results.get(
        "market_data",
        {}
    )

    return {
        "estimated_size": market_data.get(
            "estimated_size",
            "N/A"
        ),
        "cagr": market_data.get(
            "cagr",
            "N/A"
        ),
        "forecast_year": market_data.get(
            "forecast_year",
        ),
        "forecast_market_size": market_data.get(
            "forecast_market_size",
        ),
        "competition_level": market_data.get(
            "competition_level",
            "Unavailable"
        ),
        "key_drivers": market_data.get(
            "key_drivers",
            []
        ),
        "source_reported": market_data.get(
            "source_reported",
            {}
        ),
        "derived_projection": market_data.get(
            "derived_projection",
            market_data.get("projections", [])
        ),
        "strategic_signals": market_data.get(
            "strategic_signals",
            {}
        ),
        "projection_method": market_data.get(
            "projection_method"
        ),
        "data_quality": market_data.get(
            "data_quality",
            "Unknown"
        ),
    }


# ============================================================
# Master Agent
# ============================================================

def run_master_agent(
    user_query: str
) -> Dict[str, Any]:
    """
    Master Orchestrator for the pharmaceutical research system.

    Pipeline:

        User Query
             ↓
        Clinical Agent
             ↓
        Patent Agent
             ↓
        Market Agent
             ↓
        Evidence Aggregation
             ↓
        Strategic Synthesis

    The current version uses sequential execution while
    maintaining structured outputs for future LangGraph
    orchestration.
    """

    # --------------------------------------------------------
    # Initialize execution trace
    # --------------------------------------------------------

    trace = []

    trace.append(
        "🧠 [Master Orchestrator]: "
        f"Initialized analysis for query: '{user_query}'"
    )

    # --------------------------------------------------------
    # 1. Clinical Agent
    # --------------------------------------------------------

    trace.append(
        "🔬 [Orchestrator] -> "
        "Spawning Clinical Evidence Agent..."
    )

    clinical_results = run_clinical_agent(
        user_query
    )

    indication = _get_indication(
        clinical_results
    )

    num_trials = clinical_results.get(
        "trial_count",
        len(
            clinical_results.get(
                "trials",
                []
            )
        )
    )

    parsed_query = clinical_results.get(
        "parsed_query",
        {}
    )

    trace.append(
        "🧪 [Clinical Trials Agent]: "
        f"Identified therapeutic category as "
        f"'{indication}' and retrieved "
        f"{num_trials} validated clinical trials."
    )

    # --------------------------------------------------------
    # Clinical query information
    # --------------------------------------------------------

    phase = parsed_query.get(
        "phase"
    )

    status = parsed_query.get(
        "status"
    )

    intervention = parsed_query.get(
        "intervention"
    )

    location = parsed_query.get(
        "location"
    )

    if phase:
        trace.append(
            f"🔎 [Clinical Agent]: "
            f"Phase constraint validated: {phase}"
        )

    if status:
        trace.append(
            f"🔎 [Clinical Agent]: "
            f"Recruitment status validated: {status}"
        )

    if intervention:
        trace.append(
            f"💊 [Clinical Agent]: "
            f"Intervention constraint validated: "
            f"{intervention}"
        )

    if location:
        trace.append(
            f"🌎 [Clinical Agent]: "
            f"Location constraint validated: "
            f"{location}"
        )

    # --------------------------------------------------------
    # 2. Patent Agent
    # --------------------------------------------------------

    trace.append(
        "📄 [Orchestrator] -> "
        "Spawning Patent & IP Landscape Agent..."
    )

    patent_results = run_patent_agent(
        user_query
    )

    geography = patent_results.get(
        "geography",
        _get_geography(
            clinical_results
        )
    )

    max_risk = _calculate_patent_risk(
        patent_results
    )

    trace.append(
        "⚖️ [Patent & IP Agent]: "
        f"Evaluated Freedom to Operate (FTO) "
        f"in {geography} region. "
        f"Peak risk evaluated as: {max_risk}."
    )

    # --------------------------------------------------------
    # 3. Market Agent
    # --------------------------------------------------------

    trace.append(
        "📈 [Orchestrator] -> "
        "Spawning Market & Competition Agent..."
    )

    market_results = run_market_agent(
        user_query
    )

    market = _get_market_data(
        market_results
    )

    market_size = market["estimated_size"]
    cagr = market["cagr"]

    trace.append(
        "📊 [Market Agent]: "
        f"Assessed commercial market. "
        f"Current segment value: {market_size} "
        f"with reported growth of {cagr}. "
        f"Competitive intensity: "
        f"{market['competition_level']}."
    )

    if market["source_reported"]:
        trace.append(
            "📚 [Market Agent]: "
            "Source-reported market evidence preserved "
            "separately from derived projections."
        )

    if market["strategic_signals"]:
        trace.append(
            "🧭 [Market Agent]: "
            "Structured strategic market signals "
            "added to evidence aggregation."
        )

    # --------------------------------------------------------
    # 4. Evidence Aggregation
    # --------------------------------------------------------

    trace.append(
        "🔗 [Orchestrator]: "
        "Aggregating evidence from domain agents..."
    )

    evidence_summary = {
        "clinical": {
            "trial_count": num_trials,
            "indication": indication,
            "intervention": intervention,
            "phase": phase,
            "status": status,
            "location": location,
            "source": clinical_results.get(
                "source",
                "ClinicalTrials.gov"
            ),
        },

        "patent": {
            "geography": geography,
            "risk_level": max_risk,
        },

        "market": {
            "estimated_size": market_size,
            "cagr": cagr,
            "forecast_year": market["forecast_year"],
            "forecast_market_size": market[
                "forecast_market_size"
            ],
            "competition_level": market[
                "competition_level"
            ],
            "key_drivers": market[
                "key_drivers"
            ],
            "source_reported": market[
                "source_reported"
            ],
            "derived_projection": market[
                "derived_projection"
            ],
            "strategic_signals": market[
                "strategic_signals"
            ],
            "projection_method": market[
                "projection_method"
            ],
            "data_quality": market[
                "data_quality"
            ],
            "source": market_results.get(
                "source"
            ),
            "secondary_source": market_results.get(
                "secondary_source"
            ),
            "status": market_results.get(
                "status",
                "UNKNOWN"
            ),
        },
    }

    # --------------------------------------------------------
    # 5. Strategic Synthesis
    # --------------------------------------------------------

    trace.append(
        "🤝 [Orchestrator]: "
        "Consolidating evidence and "
        "synthesizing strategic conclusion..."
    )

    market_signal = market["strategic_signals"]
    market_opportunity = market_signal.get(
        "opportunity",
        {}
    )

    market_competition = market_signal.get(
        "competitive_intensity",
        {}
    )

    # --------------------------------------------------------
    # High Patent Risk
    # --------------------------------------------------------

    if max_risk == "High":

        recommendation = (
            f"The {indication} landscape shows "
            f"{market_opportunity.get('level', 'meaningful market potential')} "
            f"with an estimated market size of "
            f"{market_size} and reported growth of "
            f"{cagr}. However, competitive intensity is "
            f"{market_competition.get('level', 'Unavailable')} "
            f"and the current patent landscape indicates "
            f"HIGH intellectual property risk in the "
            f"{geography} region. Clinical evidence includes "
            f"{num_trials} matching trial(s)"
        )

        if phase:
            recommendation += (
                f" at the requested {phase} stage"
            )

        if intervention:
            recommendation += (
                f" involving {intervention}"
            )

        recommendation += (
            ". Entry should therefore prioritize "
            "detailed freedom-to-operate analysis, "
            "design-around research, licensing, or "
            "strategic partnerships rather than "
            "immediate independent development."
        )

    # --------------------------------------------------------
    # Moderate Patent Risk
    # --------------------------------------------------------

    elif max_risk == "Moderate":

        recommendation = (
            f"The {indication} landscape shows "
            f"{market_opportunity.get('level', 'meaningful market potential')} "
            f"with an estimated market size of "
            f"{market_size} and reported growth of "
            f"{cagr}. Competitive intensity is "
            f"{market_competition.get('level', 'Unavailable')}. "
            f"The patent landscape presents MODERATE "
            f"intellectual property barriers in the "
            f"{geography} region. "
            f"{num_trials} matching clinical trial(s) "
            f"provide evidence of ongoing development "
            f"activity."
        )

        if intervention:
            recommendation += (
                f" The requested intervention, "
                f"{intervention}, is represented in "
                f"the validated clinical evidence."
            )

        recommendation += (
            " Potential entry strategies include "
            "specialized formulations, differentiated "
            "delivery mechanisms, combination products, "
            "licensing, or new patentable improvements."
        )

    # --------------------------------------------------------
    # Low Patent Risk
    # --------------------------------------------------------

    elif max_risk == "Low":

        recommendation = (
            f"The {indication} therapeutic area shows "
            f"{market_opportunity.get('level', 'meaningful market potential')} "
            f"with an estimated market size of "
            f"{market_size} and reported growth of "
            f"{cagr}. Competitive intensity is "
            f"{market_competition.get('level', 'Unavailable')}. "
            f"The identified patent landscape currently "
            f"indicates LOW risk in the {geography} region. "
            f"The Clinical Agent identified "
            f"{num_trials} matching trial(s), providing "
            f"evidence of active development in the "
            f"therapeutic area."
        )

        recommendation += (
            " The opportunity may justify further "
            "commercial, regulatory, and technical "
            "assessment before development investment."
        )

    # --------------------------------------------------------
    # Unknown Patent Risk
    # --------------------------------------------------------

    else:

        recommendation = (
            f"The {indication} opportunity requires "
            f"additional investigation before a reliable "
            f"strategic recommendation can be made. "
            f"Market evidence indicates "
            f"{market_opportunity.get('level', 'meaningful market potential')} "
            f"with a reported market size of {market_size} "
            f"and growth range of {cagr}. Competitive "
            f"intensity is "
            f"{market_competition.get('level', 'Unavailable')}. "
            f"The Clinical Agent identified "
            f"{num_trials} matching trial(s), while "
            f"patent risk could not be confidently "
            f"determined for the {geography} region."
        )

        recommendation += (
            " A detailed freedom-to-operate and "
            "commercial analysis should be completed "
            "before making an investment decision."
        )

    # --------------------------------------------------------
    # Completion
    # --------------------------------------------------------

    trace.append(
        "✨ [Master Orchestrator]: "
        "Strategic assessment compiled successfully."
    )

    # --------------------------------------------------------
    # Final structured response
    # --------------------------------------------------------

    return {
        "query": user_query,
        "clinical": clinical_results,
        "patent": patent_results,
        "market": market_results,
        "evidence_summary": evidence_summary,
        "conclusion": recommendation,
        "trace": trace,
    }


# ============================================================
# Standalone Test
# ============================================================

if __name__ == "__main__":

    query = (
        "Find recruiting Phase 3 obesity trials "
        "involving semaglutide in the US"
    )

    result = run_master_agent(
        query
    )

    print("\n" + "=" * 70)
    print("PHARMA AGENTIC AI - MASTER AGENT TEST")
    print("=" * 70)

    print("\nQUERY:")
    print(result["query"])

    print("\nCLINICAL TRIALS:")
    print(
        result["clinical"].get(
            "trial_count",
            0
        )
    )

    print("\nPATENT RISK:")

    patent_data = result.get(
        "evidence_summary",
        {}
    ).get(
        "patent",
        {}
    )

    print(
        patent_data.get(
            "risk_level",
            "Unknown"
        )
    )

    print("\nMARKET:")

    market_data = result.get(
        "evidence_summary",
        {}
    ).get(
        "market",
        {}
    )

    print(
        "Estimated Size:",
        market_data.get(
            "estimated_size",
            "N/A"
        )
    )

    print(
        "CAGR:",
        market_data.get(
            "cagr",
            "N/A"
        )
    )

    print(
        "Competition:",
        market_data.get(
            "competition_level",
            "Unavailable"
        )
    )

    print(
        "Forecast:",
        market_data.get(
            "forecast_market_size",
            "Unavailable"
        ),
        "by",
        market_data.get(
            "forecast_year",
            "N/A"
        )
    )

    print("\n" + "=" * 70)
    print("STRATEGIC CONCLUSION")
    print("=" * 70)

    print(
        result["conclusion"]
    )

    print("\n" + "=" * 70)
    print("AGENT EXECUTION TRACE")
    print("=" * 70)

    for entry in result["trace"]:
        print(entry)
