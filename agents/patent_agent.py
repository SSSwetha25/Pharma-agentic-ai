from typing import Dict, Any
import pandas as pd


def run_patent_agent(user_query: str) -> Dict[str, Any]:
    """
    Placeholder patent agent.

    A real version would query patent databases and analyse claims/expiry.
    Here we return simple, static data for demonstration.
    """
    patents_df = pd.DataFrame(
        [
            {"patent_id": "US-123456", "status": "Active", "expiry_year": 2032},
            {"patent_id": "EP-654321", "status": "Expired", "expiry_year": 2020},
        ]
    )

    return {
        "summary": f"Prototype patent landscape generated for: {user_query}",
        "patents": patents_df,
    }

def run_patent_agent(query):
    return {
        "summary": "Low to moderate patent risk identified.",
        "patents": [
            {"compound": "Compound A", "expiry": 2026, "risk": "Low"},
            {"compound": "Compound B", "expiry": 2024, "risk": "Expired"},
            {"compound": "Compound C", "expiry": 2029, "risk": "Moderate"}
        ]
    }
