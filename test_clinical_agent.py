from agents.clinical_agent import run_clinical_agent


result = run_clinical_agent(
    "Find recruiting Phase 3 obesity trials involving semaglutide in the US"
)

print("Agent:", result["agent"])
print("Source:", result["source"])
print("Trials found:", result["trial_count"])

for trial in result["trials"][:3]:

    print("\n--------------------")

    print("NCT ID:", trial["nct_id"])
    print("Title:", trial["title"])
    print("Status:", trial["status"])
    print("Phase:", trial["phase"])
    print("Conditions:", trial["conditions"])
    print("Interventions:", trial["interventions"])
    print("Sponsor:", trial["sponsor"])
    print("Enrollment:", trial["enrollment"])