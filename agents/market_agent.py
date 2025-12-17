from typing import Dict, Any


def run_market_agent(user_query: str) -> Dict[str, Any]:
    """
    Placeholder market agent.

    A real version would use market research / sales data APIs.
    For demo purposes we return a simple JSON-serialisable structure.
    """
    market_data = {
        "estimated_market_size": "5-7B USD",
        "key_regions": ["US", "EU5", "Japan"],
        "competition_level": "Moderate",
    }

    return {
        "summary": f"Prototype market overview generated for: {user_query}",
        "market_data": market_data,
    }

def run_market_agent(query):
    return {
        "summary": "Market shows moderate growth with unmet demand.",
        "market_data": {
            "estimated_size": "USD 450M",
            "cagr": "8.2%",
            "competition_level": "Medium"
        }
    }
