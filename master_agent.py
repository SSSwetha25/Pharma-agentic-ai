from agents.clinical_agent import run_clinical_trials_agent
from agents.patent_agent import run_patent_agent
from agents.market_agent import run_market_agent

def run_master_agent(user_query: str):
    """
    Orchestrates the domain-specific agents, collects their outputs, and
    performs a dynamic executive synthesis to generate recommendations.
    """
    # Create execution trace log
    trace = []
    trace.append(f"🧠 [Master Orchestrator]: Initialized analysis for query: '{user_query}'")
    
    # 1. Spin up Clinical Agent
    trace.append("🔬 [Orchestrator] -> Spawning Clinical Evidence Agent...")
    clinical_results = run_clinical_trials_agent(user_query)
    indication = clinical_results.get("indication", "General")
    num_trials = len(clinical_results.get("trials", []))
    trace.append(f"🧪 [Clinical Trials Agent]: Identified therapeutic category as '{indication}' and parsed {num_trials} representative trials.")
    
    # 2. Spin up Patent Agent
    trace.append("📄 [Orchestrator] -> Spawning Patent & IP Landscape Agent...")
    patent_results = run_patent_agent(user_query)
    geography = patent_results.get("geography", "Global")
    max_risk = "Low"
    if "patents" in patent_results and not patent_results["patents"].empty:
        risks = patent_results["patents"]["Risk Level"].tolist()
        if "High" in risks:
            max_risk = "High"
        elif "Moderate" in risks or "Medium" in risks:
            max_risk = "Moderate"
    trace.append(f"⚖️ [Patent & IP Agent]: Evaluated Freedom to Operate (FTO) in {geography} region. Peak risk evaluated as: {max_risk}.")
    
    # 3. Spin up Market Agent
    trace.append("📈 [Orchestrator] -> Spawning Market & Competition Agent...")
    market_results = run_market_agent(user_query)
    market_size = market_results.get("market_data", {}).get("estimated_size", "N/A")
    cagr = market_results.get("market_data", {}).get("cagr", "N/A")
    trace.append(f"📊 [Market Agent]: Assessed commercial market. Current segment value: {market_size} with projected CAGR of {cagr}.")
    
    # 4. Synthesize Conclusion
    trace.append("🤝 [Orchestrator]: Consolidating insights and synthesizing strategic conclusion...")
    
    # Custom synthesized report
    if max_risk == "High":
        recommendation = (
            f"The opportunity in the {indication} segment is commercially attractive ({market_size} growing at {cagr}), "
            f"but presents significant **HIGH intellectual property risks** in the {geography} region. "
            f"Active formulation or manufacturing blockades require immediate design-around research. "
            f"Clinical trial progression (Phase II/III) suggests a highly validated target, making licensing or "
            f"partnership a potential entry route rather than generic formulation."
        )
    elif max_risk == "Moderate":
        recommendation = (
            f"The {indication} landscape represents a balanced risk/reward profile. "
            f"With a market size of {market_size} and steady CAGR of {cagr}, moderate patent barriers exist. "
            f"Filing specialized patents (dosage, combinations) could carve out a unique niche. "
            f"Clinical trials suggest strong progress, presenting an optimal entry window for value-added products."
        )
    else:
        recommendation = (
            f"Strategic greenlight for entry into the {indication} therapeutic area. "
            f"Minimal patent blockades remain (Low/Expired risk) in {geography}. "
            f"Given the high market demand (currently sized at {market_size} with {cagr} growth), "
            f"this opportunity represents a low-barrier, high-potential entry path. "
            f"We recommend accelerating development and conducting detailed regulatory formulation plans."
        )
        
    trace.append("✨ [Master Orchestrator]: Strategic assessment compiled successfully.")
    
    return {
        "clinical": clinical_results,
        "patent": patent_results,
        "market": market_results,
        "conclusion": recommendation,
        "trace": trace
    }
