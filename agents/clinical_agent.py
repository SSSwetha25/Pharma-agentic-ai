from typing import Dict, Any
import pandas as pd

def run_clinical_trials_agent(user_query: str) -> Dict[str, Any]:
    """
    Simulates a clinical trials agent that parses the user query and searches
    clinical trial databases (e.g., ClinicalTrials.gov) for relevant trials.
    """
    query_lower = user_query.lower()
    
    # 1. Determine therapeutic category
    if any(k in query_lower for k in ["oncology", "cancer", "tumor", "nsclc", "leukemia", "car-t"]):
        indication = "Oncology"
        summary = (
            "The clinical landscape for Oncology exhibits intensive activity, particularly "
            "focusing on combination regimens (immunotherapy + chemotherapy) and targeted small molecules "
            "(e.g., KRAS/EGFR inhibitors). We identified high phase III trial density with primary endpoints "
            "centered on Progression-Free Survival (PFS) and Overall Survival (OS). Recruitments are active, "
            "indicating robust patient participation and substantial clinical progression."
        )
        trials_data = [
            {
                "Trial ID": "NCT05423192",
                "Drug Name": "OncoShield-X (SM)",
                "Phase": "Phase III",
                "Status": "Recruiting",
                "Indication": "Metastatic NSCLC",
                "Enrollment": 450,
                "Primary Endpoint": "Progression-Free Survival (PFS)"
            },
            {
                "Trial ID": "NCT06109982",
                "Drug Name": "ImmuTarget-4 (mAb)",
                "Phase": "Phase II",
                "Status": "Active, not recruiting",
                "Indication": "Advanced Solid Tumors",
                "Enrollment": 180,
                "Primary Endpoint": "Objective Response Rate (ORR)"
            },
            {
                "Trial ID": "NCT05988123",
                "Drug Name": "LethalBlock-2 (SM)",
                "Phase": "Phase I",
                "Status": "Recruiting",
                "Indication": "Refractory AML",
                "Enrollment": 60,
                "Primary Endpoint": "Safety & Dose Escalation"
            }
        ]
    elif any(k in query_lower for k in ["cardio", "heart", "hypertension", "stroke", "atherosclerosis"]):
        indication = "Cardiovascular"
        summary = (
            "Cardiovascular drug development centers around novel lipid-lowering compounds (PCSK9/siRNA), "
            "heart failure medications (ARNI/SGLT2 inhibitors), and anti-thrombotic agents. Current trials focus "
            "heavily on Major Adverse Cardiovascular Events (MACE) as the primary endpoint. Major trials are "
            "currently in Phase III, showing high enrollment requirements (>1,000 patients) and completed statuses "
            "releasing promising safety data."
        )
        trials_data = [
            {
                "Trial ID": "NCT04891104",
                "Drug Name": "CardioFlow-Z (siRNA)",
                "Phase": "Phase III",
                "Status": "Completed",
                "Indication": "Hypercholesterolemia",
                "Enrollment": 1250,
                "Primary Endpoint": "LDL-C reduction % at 24 weeks"
            },
            {
                "Trial ID": "NCT05332219",
                "Drug Name": "VasoRelax-M (SM)",
                "Phase": "Phase II",
                "Status": "Recruiting",
                "Indication": "Pulmonary Hypertension",
                "Enrollment": 220,
                "Primary Endpoint": "6-Minute Walk Distance (6MWD)"
            }
        ]
    elif any(k in query_lower for k in ["diabetes", "obesity", "glp", "insulin", "nash", "mld"]):
        indication = "Metabolic / Obesity"
        summary = (
            "The metabolic sector is highly competitive, dominated by next-generation GLP-1/GIP/Glucagon "
            "triple agonists and oral peptide formulations. Development pipelines show strong progress in Phase III "
            "efficacy studies. Primary endpoints focus on mean percentage change in body weight and HbA1c levels. "
            "Results indicate high compliance and robust weight loss profiles."
        )
        trials_data = [
            {
                "Trial ID": "NCT05912440",
                "Drug Name": "SlimGlide-3 (Peptide)",
                "Phase": "Phase III",
                "Status": "Recruiting",
                "Indication": "Obesity & Type 2 Diabetes",
                "Enrollment": 850,
                "Primary Endpoint": "% Weight Change from Baseline"
            },
            {
                "Trial ID": "NCT06200114",
                "Drug Name": "MetaboReg-X (SM)",
                "Phase": "Phase II",
                "Status": "Completed",
                "Indication": "MASH / NASH Fibrosis",
                "Enrollment": 310,
                "Primary Endpoint": "Resolution of NASH with no worsening"
            }
        ]
    elif any(k in query_lower for k in ["alzheimer", "dementia", "neurology", "parkinson", "ms", "als"]):
        indication = "Neurology"
        summary = (
            "Neurology pipelines, particularly Alzheimer's and Parkinson's disease, focus heavily on disease-modifying "
            "therapies such as monoclonal antibodies clearing amyloid/tau and neuroprotective small molecules. "
            "Trial progression is challenging with long durations and strict enrollment criteria. Primary endpoints "
            "center on cognitive score scales (CDR-SB, ADAS-Cog13)."
        )
        trials_data = [
            {
                "Trial ID": "NCT04911228",
                "Drug Name": "CogniClear-A (mAb)",
                "Phase": "Phase III",
                "Status": "Active, not recruiting",
                "Indication": "Early Alzheimer's Disease",
                "Enrollment": 1500,
                "Primary Endpoint": "Change in CDR-SB at 18 months"
            },
            {
                "Trial ID": "NCT05662134",
                "Drug Name": "NeuroProtect-D (SM)",
                "Phase": "Phase II",
                "Status": "Recruiting",
                "Indication": "Parkinson's Disease Progression",
                "Enrollment": 280,
                "Primary Endpoint": "MDS-UPDRS Part III Score"
            }
        ]
    elif any(k in query_lower for k in ["immunology", "arthritis", "lupus", "autoimmune", "psoriasis", "crohn"]):
        indication = "Immunology"
        summary = (
            "Immunology and autoimmune pipelines are shifting towards highly targeted biologics (IL-23, IL-17 blockers) "
            "and selective oral JAK inhibitors. Clinical trials demonstrate rapid efficacy profiles with primary endpoints "
            "like ACR20/ACR50 or PASI-90 scores. Safety evaluation remains a critical component due to immunosuppressive profiles."
        )
        trials_data = [
            {
                "Trial ID": "NCT05221094",
                "Drug Name": "ArthroBlock-9 (SM)",
                "Phase": "Phase III",
                "Status": "Completed",
                "Indication": "Rheumatoid Arthritis",
                "Enrollment": 620,
                "Primary Endpoint": "ACR20 Response Rate at Week 12"
            },
            {
                "Trial ID": "NCT05776123",
                "Drug Name": "DermaCalm-2 (Biologic)",
                "Phase": "Phase II",
                "Status": "Recruiting",
                "Indication": "Moderate-to-Severe Psoriasis",
                "Enrollment": 190,
                "Primary Endpoint": "PASI-90 Response Rate"
            }
        ]
    else:
        indication = "General Therapeutic Area"
        summary = (
            f"Conducted clinical landscape assessment for general pharmaceutical search: '{user_query}'. "
            "Current clinical trial registries demonstrate a healthy split between small-molecule therapeutics "
            "and novel biologic modalities, primarily targeting unmet medical needs in early-to-mid phase development."
        )
        trials_data = [
            {
                "Trial ID": "NCT05001122",
                "Drug Name": "NovaMend-X (SM)",
                "Phase": "Phase II",
                "Status": "Recruiting",
                "Indication": "Targeted Orphan Indication",
                "Enrollment": 120,
                "Primary Endpoint": "Biomarker Clearance Rate"
            },
            {
                "Trial ID": "NCT05224466",
                "Drug Name": "GeneFix-Y (Biologic)",
                "Phase": "Phase I",
                "Status": "Active, not recruiting",
                "Indication": "Rare Genetic Condition",
                "Enrollment": 45,
                "Primary Endpoint": "Safety and Tolerability Profile"
            }
        ]
    
    trials_df = pd.DataFrame(trials_data)
    
    return {
        "indication": indication,
        "summary": summary,
        "trials": trials_df,
    }
