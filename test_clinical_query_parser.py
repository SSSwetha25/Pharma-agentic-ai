from agents.clinical_query_parser import parse_clinical_query


queries = [
    "Find recruiting Phase 3 breast cancer trials in the US",

    "Show Phase III Alzheimer's trials",

    "Find completed Phase 2 lung cancer studies",

    "Recruiting obesity trials in India",

    "Phase 4 diabetes trials in the United Kingdom",

    "Find Phase 3 obesity trials involving semaglutide",

    "Find recruiting Phase 3 obesity trials involving semaglutide in the US",

    "Find Phase 2 breast cancer trials with pembrolizumab",

    "Find diabetes trials using tirzepatide",
]


for query in queries:

    print("\nQUERY:")
    print(query)

    result = parse_clinical_query(query)

    print("\nPARSED:")
    print(result)