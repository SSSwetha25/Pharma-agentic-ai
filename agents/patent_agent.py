from typing import Dict, Any
import pandas as pd

def run_patent_agent(user_query: str) -> Dict[str, Any]:
    """
    Simulates a Patent and Intellectual Property (IP) agent that parses the query,
    analyzes FTO (Freedom to Operate) risks, and evaluates the patent landscape.
    """
    query_lower = user_query.lower()
    
    # Identify geography mentioned in the query
    geography = "US"
    if "eu" in query_lower or "europe" in query_lower:
        geography = "EP"
    elif "japan" in query_lower or "jp" in query_lower:
        geography = "JP"
        
    # Determine the molecule/risk characteristics
    is_biologic = any(k in query_lower for k in ["biologic", "antibody", "mab", "vaccine", "mrna", "car-t"])
    
    # Define patent data based on category and query details
    if is_biologic:
        summary = (
            f"The patent landscape for biologic molecules in {geography} is characterized by dense 'patent thickets' "
            "covering manufacturing processes, cell lines, and formulations rather than just core compound patents. "
            "While core patents may be nearing expiry, secondary formulation patents extend biosimilar defense. "
            "Overall FTO (Freedom to Operate) risk is evaluated as High due to active litigation from brand-name holders."
        )
        patents_data = [
            {
                "Patent ID": f"{geography}-7892113-B2",
                "Assignee": "BioGiant Corp",
                "Expiry Year": 2033,
                "Status": "Active",
                "Risk Level": "High",
                "Patent Type": "Manufacturing Process"
            },
            {
                "Patent ID": f"{geography}-8945622-B1",
                "Assignee": "Genentech Inc.",
                "Expiry Year": 2028,
                "Status": "Active",
                "Risk Level": "Moderate",
                "Patent Type": "Formulation & Dosage"
            },
            {
                "Patent ID": f"{geography}-6511204-B2",
                "Assignee": "Therapeutics PLC",
                "Expiry Year": 2024,
                "Status": "Expired",
                "Risk Level": "Low (Expired)",
                "Patent Type": "Composition of Matter"
            }
        ]
    else:
        # Small Molecule default / generic
        if "low patent risk" in query_lower or "generic" in query_lower:
            summary = (
                f"Low-risk patent landscape identified for small molecule target in {geography}. "
                "The primary Composition of Matter (COM) patents have either expired or are within 1-2 years of "
                "expiry, with minimal secondary patent blockades. Generics or value-added reformulations face "
                "minimal intellectual property barriers."
            )
            patents_data = [
                {
                    "Patent ID": f"{geography}-6123456-B1",
                    "Assignee": "PharmaClassic Ltd",
                    "Expiry Year": 2023,
                    "Status": "Expired",
                    "Risk Level": "Low (Expired)",
                    "Patent Type": "Composition of Matter"
                },
                {
                    "Patent ID": f"{geography}-6987654-B2",
                    "Assignee": "PharmaClassic Ltd",
                    "Expiry Year": 2026,
                    "Status": "Active",
                    "Risk Level": "Low",
                    "Patent Type": "Polymorph / Crystalline Form"
                }
            ]
        else:
            summary = (
                f"Moderate patent risk identified for small molecule compound in {geography}. "
                "Core Composition of Matter patents are active, shielding the market for another 5-8 years. "
                "Any formulation development will require careful design-around strategies or licensing negotiations "
                "to secure Freedom to Operate (FTO)."
            )
            patents_data = [
                {
                    "Patent ID": f"{geography}-8456123-B2",
                    "Assignee": "AstraZeneca PLC",
                    "Expiry Year": 2031,
                    "Status": "Active",
                    "Risk Level": "High",
                    "Patent Type": "Composition of Matter"
                },
                {
                    "Patent ID": f"{geography}-9102434-B1",
                    "Assignee": "Novartis AG",
                    "Expiry Year": 2029,
                    "Status": "Active",
                    "Risk Level": "Moderate",
                    "Patent Type": "Method of Use"
                }
            ]

    patents_df = pd.DataFrame(patents_data)

    return {
        "geography": geography,
        "summary": summary,
        "patents": patents_df,
    }
