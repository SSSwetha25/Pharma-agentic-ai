from typing import Dict, Any

def run_market_agent(user_query: str) -> Dict[str, Any]:
    """
    Simulates a Market & Competition Intelligence agent that parses the query,
    estimates global market sizes, growth trajectories, and forecasts.
    """
    query_lower = user_query.lower()
    
    # Default variables
    category = "General Pharma"
    size = "USD 3.2B"
    cagr = "5.4%"
    competition = "Medium"
    drivers = ["Growth in emerging markets", "Introduction of generic alternatives"]
    
    # 2026-2031 projections (in Millions USD)
    base_val = 3200
    growth_rate = 0.054
    
    if any(k in query_lower for k in ["oncology", "cancer", "tumor", "nsclc", "leukemia"]):
        category = "Oncology"
        size = "USD 185.4B"
        cagr = "11.2%"
        competition = "High"
        drivers = [
            "Approval of next-generation immune checkpoints",
            "Strong demand for precision targeted oncology therapies",
            "Expanding patient access and early cancer screening programs"
        ]
        base_val = 185400
        growth_rate = 0.112
    elif any(k in query_lower for k in ["cardio", "heart", "hypertension", "stroke", "atherosclerosis"]):
        category = "Cardiovascular"
        size = "USD 62.8B"
        cagr = "4.2%"
        competition = "Medium"
        drivers = [
            "Rising prevalence of chronic hypertension globally",
            "Launch of long-acting lipid-lowering therapies (siRNA)",
            "Expanding geriatric demographics in developed economies"
        ]
        base_val = 62800
        growth_rate = 0.042
    elif any(k in query_lower for k in ["diabetes", "obesity", "glp", "insulin", "nash", "mld"]):
        category = "Metabolic / Obesity"
        size = "USD 88.5B"
        cagr = "14.6%"
        competition = "Very High"
        drivers = [
            "Explosive adoption of anti-obesity and dual GLP-1/GIP therapies",
            "Widening reimbursement coverage policies by public payers",
            "Expanding clinical indications for metabolic syndrome"
        ]
        base_val = 88500
        growth_rate = 0.146
    elif any(k in query_lower for k in ["alzheimer", "dementia", "neurology", "parkinson", "ms", "als"]):
        category = "Neurology"
        size = "USD 48.2B"
        cagr = "8.8%"
        competition = "Medium"
        drivers = [
            "Approval of amyloid-clearing monoclonal antibody therapies",
            "Massive unmet need in neurodegenerative disease categories",
            "Increased public/private funding for brain health initiatives"
        ]
        base_val = 48200
        growth_rate = 0.088
    elif any(k in query_lower for k in ["immunology", "arthritis", "lupus", "autoimmune", "psoriasis", "crohn"]):
        category = "Immunology"
        size = "USD 95.3B"
        cagr = "7.1%"
        competition = "High"
        drivers = [
            "Increasing uptake of selective biologics (IL-17/IL-23)",
            "Expansion of oral JAK inhibitor medications",
            "Rising diagnoses of auto-inflammatory conditions globally"
        ]
        base_val = 95300
        growth_rate = 0.071

    # Generate annual revenue projections list (2026 to 2031)
    projections = []
    current_val = base_val
    for year in range(2026, 2032):
        projections.append({
            "Year": str(year),
            "Market Size ($M)": round(current_val, 1)
        })
        current_val *= (1 + growth_rate)

    summary = (
        f"The {category} therapeutic market represents a major commercial segment with an estimated "
        f"market value of {size} growing at a CAGR of {cagr}. Commercialization success requires addressing "
        f"high competitive pressure (evaluated as {competition}) and gaining regulatory approvals with favorable "
        f"reimbursement coverage. Key growth engines include: {', '.join(drivers)}."
    )

    market_data = {
        "estimated_size": size,
        "cagr": cagr,
        "competition_level": competition,
        "key_drivers": drivers,
        "projections": projections
    }

    return {
        "summary": summary,
        "market_data": market_data,
    }
