from typing import Dict, Any
import pandas as pd


def run_clinical_trials_agent(user_query: str) -> Dict[str, Any]:
    """
    Placeholder clinical trials agent.

    In a real implementation this would query clinical trial registries.
    For now we return simple, illustrative data so the UI works end-to-end.
    """
    trials_df = pd.DataFrame(
        [
            {"trial_id": "CT-001", "phase": "Phase II", "status": "Recruiting"},
            {"trial_id": "CT-002", "phase": "Phase III", "status": "Completed"},
        ]
    )

    return {
        "summary": f"Prototype clinical insights generated for: {user_query}",
        "trials": trials_df,
    }

def run_clinical_trials_agent(query):
    return {
        "summary": "Identified 3 ongoing clinical trials relevant to the query.",
        "trials": [
            {"drug": "Compound A", "phase": "Phase II", "status": "Recruiting"},
            {"drug": "Compound B", "phase": "Phase III", "status": "Completed"},
            {"drug": "Compound C", "phase": "Phase I", "status": "Recruiting"}
        ]
    }
