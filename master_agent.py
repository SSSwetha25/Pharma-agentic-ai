from agents.clinical_agent import run_clinical_trials_agent
from agents.patent_agent import run_patent_agent
from agents.market_agent import run_market_agent


def run_master_agent(user_query: str):
    """
    Orchestrate the domain-specific agents and aggregate their outputs.

    Returns a dict with clinical, patent, market, and a combined conclusion.
    """
    clinical_results = run_clinical_trials_agent(user_query)
    patent_results = run_patent_agent(user_query)
    market_results = run_market_agent(user_query)

    return {
        "clinical": clinical_results,
        "patent": patent_results,
        "market": market_results,
        "conclusion": (
            "Based on combined clinical, patent, and market analysis, "
            "the identified compounds show potential for further evaluation."
        ),
    }


