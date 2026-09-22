# agents/clinical_agent.py

import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from agents.clinical_query_parser import parse_clinical_query
from evidence.evidence_schema import create_evidence


# ============================================================
# Configuration
# ============================================================

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

DEFAULT_PAGE_SIZE = 10
REQUEST_TIMEOUT = 20


# ============================================================
# Helper: Phase Filter
# ============================================================

def _build_advanced_filter(parsed: Dict[str, Any]) -> Optional[str]:
    """
    Build a ClinicalTrials.gov advanced filter for study phase.
    """

    phase_map = {
        "PHASE1": "AREA[Phase]PHASE1",
        "PHASE2": "AREA[Phase]PHASE2",
        "PHASE3": "AREA[Phase]PHASE3",
        "PHASE4": "AREA[Phase]PHASE4",
    }

    filters = []

    phase = parsed.get("phase")

    if phase and phase in phase_map:
        filters.append(phase_map[phase])

    if not filters:
        return None

    return " AND ".join(filters)


# ============================================================
# Helper: Phase Validation
# ============================================================

def _matches_phase(
    trial: Dict[str, Any],
    requested_phase: Optional[str],
) -> bool:
    """
    Validate that a normalized trial actually belongs
    to the requested phase.
    """

    if not requested_phase:
        return True

    trial_phases = trial.get("phase", [])

    if not trial_phases:
        return False

    return requested_phase in trial_phases


# ============================================================
# Helper: Intervention Validation
# ============================================================

def _matches_intervention(
    trial: Dict[str, Any],
    requested_intervention: Optional[str],
) -> bool:
    """
    Validate that the requested intervention actually appears
    in the trial's intervention list.

    This prevents false positives where the drug name may appear
    somewhere in the study record but is not an actual intervention.
    """

    if not requested_intervention:
        return True

    requested = requested_intervention.lower().strip()

    interventions = trial.get("interventions", [])

    for intervention in interventions:

        if not intervention:
            continue

        if requested in intervention.lower():
            return True

    return False


# ============================================================
# Helper: Status Validation
# ============================================================

def _matches_status(
    trial: Dict[str, Any],
    requested_status: Optional[str],
) -> bool:
    """
    Validate trial recruitment status locally.
    """

    if not requested_status:
        return True

    return trial.get("status") == requested_status


# ============================================================
# Helper: Condition Validation
# ============================================================

def _matches_condition(
    trial: Dict[str, Any],
    requested_condition: Optional[str],
) -> bool:
    """
    Validate that the requested condition appears
    in the trial conditions.
    """

    if not requested_condition:
        return True

    requested = requested_condition.lower().strip()

    conditions = trial.get("conditions", [])

    for condition in conditions:

        if not condition:
            continue

        if requested in condition.lower():
            return True

    return False


# ============================================================
# Helper: Location Validation
# ============================================================

def _matches_location(
    trial: Dict[str, Any],
    requested_location: Optional[str],
) -> bool:
    """
    Validate that the requested location/country appears
    in the trial locations.
    """

    if not requested_location:
        return True

    requested = requested_location.lower().strip()

    locations = trial.get("locations", [])

    for location in locations:

        if not location:
            continue

        if requested in location.lower():
            return True

    return False


# ============================================================
# Helper: Normalize Trial
# ============================================================

def _normalize_trial(
    study: Dict[str, Any],
    parsed_query: Dict[str, Any],
    retrieved_at: str,
) -> Dict[str, Any]:
    """
    Convert the nested ClinicalTrials.gov API response
    into a clean structure used by the rest of the system.
    """

    protocol = study.get("protocolSection", {})

    # --------------------------------------------------------
    # Identification
    # --------------------------------------------------------

    identification = protocol.get(
        "identificationModule",
        {}
    )

    nct_id = identification.get(
        "nctId"
    )

    title = identification.get(
        "briefTitle"
    )

    official_title = identification.get(
        "officialTitle"
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status_module = protocol.get(
        "statusModule",
        {}
    )

    status = status_module.get(
        "overallStatus"
    )

    start_date = (
        status_module
        .get("startDateStruct", {})
        .get("date")
    )

    completion_date = (
        status_module
        .get("completionDateStruct", {})
        .get("date")
    )

    # --------------------------------------------------------
    # Design / Phase
    # --------------------------------------------------------

    design_module = protocol.get(
        "designModule",
        {}
    )

    phases = design_module.get(
        "phases",
        []
    )

    study_type = design_module.get(
        "studyType"
    )

    enrollment_info = design_module.get(
        "enrollmentInfo",
        {}
    )

    enrollment = enrollment_info.get(
        "count"
    )

    # --------------------------------------------------------
    # Conditions
    # --------------------------------------------------------

    conditions_module = protocol.get(
        "conditionsModule",
        {}
    )

    conditions = conditions_module.get(
        "conditions",
        []
    )

    # --------------------------------------------------------
    # Interventions
    # --------------------------------------------------------

    arms_module = protocol.get(
        "armsInterventionsModule",
        {}
    )

    intervention_objects = arms_module.get(
        "interventions",
        []
    )

    interventions = []

    for intervention in intervention_objects:

        name = intervention.get(
            "name"
        )

        if name:
            interventions.append(name)

    # --------------------------------------------------------
    # Sponsor
    # --------------------------------------------------------

    sponsor_module = protocol.get(
        "sponsorCollaboratorsModule",
        {}
    )

    lead_sponsor = sponsor_module.get(
        "leadSponsor",
        {}
    )

    sponsor = lead_sponsor.get(
        "name"
    )

    # --------------------------------------------------------
    # Locations
    # --------------------------------------------------------

    contacts_locations_module = protocol.get(
        "contactsLocationsModule",
        {}
    )

    location_objects = contacts_locations_module.get(
        "locations",
        []
    )

    locations = []

    for location in location_objects:

        city = location.get(
            "city"
        )

        state = location.get(
            "state"
        )

        country = location.get(
            "country"
        )

        parts = [
            part
            for part in [
                city,
                state,
                country,
            ]
            if part
        ]

        if parts:
            locations.append(
                ", ".join(parts)
            )

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    source_url = None

    if nct_id:
        source_url = (
            f"https://clinicaltrials.gov/study/{nct_id}"
        )

    # --------------------------------------------------------
    # Final normalized object
    # --------------------------------------------------------

    return {
        "nct_id": nct_id,
        "title": title,
        "official_title": official_title,
        "status": status,
        "phase": phases,
        "study_type": study_type,
        "conditions": conditions,
        "interventions": interventions,
        "enrollment": enrollment,
        "sponsor": sponsor,
        "start_date": start_date,
        "completion_date": completion_date,
        "locations": locations,

        "source": {
            "name": "ClinicalTrials.gov",
            "url": source_url,
            "retrieved_at": retrieved_at,
        },

        "search_context": {
            "condition": parsed_query.get("condition"),
            "intervention": parsed_query.get("intervention"),
            "phase": parsed_query.get("phase"),
            "status": parsed_query.get("status"),
            "location": parsed_query.get("location"),
        },
    }


# ============================================================
# Main Clinical Trial Search
# ============================================================

def search_clinical_trials(
    query: str,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """
    Search ClinicalTrials.gov using a natural-language query.

    Example:

        Find recruiting Phase 3 obesity trials
        involving semaglutide in the US
    """

    # --------------------------------------------------------
    # Parse natural-language query
    # --------------------------------------------------------

    parsed = parse_clinical_query(query)

    # --------------------------------------------------------
    # API Parameters
    # --------------------------------------------------------

    params = {
        "pageSize": page_size,
        "format": "json",
    }

    # --------------------------------------------------------
    # Condition
    # --------------------------------------------------------

    if parsed.get("condition"):
        params["query.cond"] = parsed["condition"]

    # --------------------------------------------------------
    # Intervention
    # --------------------------------------------------------

    if parsed.get("intervention"):
        params["query.intr"] = parsed["intervention"]

    # --------------------------------------------------------
    # Recruitment Status
    # --------------------------------------------------------

    if parsed.get("status"):
        params["filter.overallStatus"] = parsed["status"]

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    if parsed.get("location"):
        params["query.locn"] = parsed["location"]

    # --------------------------------------------------------
    # Phase
    # --------------------------------------------------------

    advanced_filter = _build_advanced_filter(
        parsed
    )

    if advanced_filter:
        params["filter.advanced"] = advanced_filter

    # --------------------------------------------------------
    # Retrieval timestamp
    # --------------------------------------------------------

    retrieved_at = datetime.now(
        timezone.utc
    ).isoformat()

    # --------------------------------------------------------
    # API Request
    # --------------------------------------------------------

    try:

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.Timeout:

        return {
            "agent": "clinical",
            "query": query,
            "parsed_query": parsed,
            "source": "ClinicalTrials.gov",
            "trial_count": 0,
            "trials": [],
            "retrieved_at": retrieved_at,
            "error": "ClinicalTrials.gov request timed out.",
        }

    except requests.exceptions.RequestException as exc:

        return {
            "agent": "clinical",
            "query": query,
            "parsed_query": parsed,
            "source": "ClinicalTrials.gov",
            "trial_count": 0,
            "trials": [],
            "retrieved_at": retrieved_at,
            "error": f"ClinicalTrials.gov request failed: {exc}",
        }

    except ValueError:

        return {
            "agent": "clinical",
            "query": query,
            "parsed_query": parsed,
            "source": "ClinicalTrials.gov",
            "trial_count": 0,
            "trials": [],
            "retrieved_at": retrieved_at,
            "error": "ClinicalTrials.gov returned invalid JSON.",
        }

    # --------------------------------------------------------
    # Extract studies
    # --------------------------------------------------------

    studies = data.get(
        "studies",
        []
    )

    # --------------------------------------------------------
    # Normalize studies
    # --------------------------------------------------------

    trials: List[Dict[str, Any]] = []

    for study in studies:

        normalized_trial = _normalize_trial(
            study,
            parsed,
            retrieved_at,
        )

        trials.append(
            normalized_trial
        )

    # --------------------------------------------------------
    # Local Phase Validation
    # --------------------------------------------------------

    if parsed.get("phase"):

        trials = [
            trial
            for trial in trials
            if _matches_phase(
                trial,
                parsed["phase"],
            )
        ]

    # --------------------------------------------------------
    # Local Intervention Validation
    # --------------------------------------------------------

    if parsed.get("intervention"):

        trials = [
            trial
            for trial in trials
            if _matches_intervention(
                trial,
                parsed["intervention"],
            )
        ]

    # --------------------------------------------------------
    # Local Status Validation
    # --------------------------------------------------------

    if parsed.get("status"):

        trials = [
            trial
            for trial in trials
            if _matches_status(
                trial,
                parsed["status"],
            )
        ]

    # --------------------------------------------------------
    # Local Condition Validation
    # --------------------------------------------------------

    if parsed.get("condition"):

        trials = [
            trial
            for trial in trials
            if _matches_condition(
                trial,
                parsed["condition"],
            )
        ]

    # --------------------------------------------------------
    # Local Location Validation
    # --------------------------------------------------------

    if parsed.get("location"):

        trials = [
            trial
            for trial in trials
            if _matches_location(
                trial,
                parsed["location"],
            )
        ]
        # --------------------------------------------------------
    # Build standardized evidence records
    # --------------------------------------------------------

    evidence_records = []

    for trial in trials:

        evidence_text = (
            f"Clinical trial {trial.get('nct_id')} matched the requested "
            f"criteria. Status: {trial.get('status')}. "
            f"Phase: {trial.get('phase')}. "
            f"Condition(s): {trial.get('conditions')}. "
            f"Intervention(s): {trial.get('interventions')}."
        )

        evidence_record = create_evidence(
            source="ClinicalTrials.gov",
            source_type="clinical_registry",
            claim=(
                f"Trial {trial.get('nct_id')} matches the requested "
                f"clinical research criteria."
            ),
            evidence=evidence_text,
            url=trial.get("source", {}).get("url"),
            status="validated",
            confidence="high",
            agent="Clinical Agent",
            record_id=trial.get("nct_id"),
        )

        evidence_records.append(
            evidence_record.to_dict()
        )
            # --------------------------------------------------------
    # Aggregate clinical evidence
    # --------------------------------------------------------

    if trials:
        trial_ids = [
            trial.get("nct_id")
            for trial in trials
            if trial.get("nct_id")
        ]

        aggregate_evidence = create_evidence(
            source="ClinicalTrials.gov",
            source_type="clinical_registry",
            claim=f"{len(trials)} matching clinical trials identified.",
            evidence=(
                f"The Clinical Agent retrieved and locally validated "
                f"{len(trials)} ClinicalTrials.gov records matching "
                f"the requested clinical criteria."
            ),
            url="https://clinicaltrials.gov/",
            status="validated",
            confidence="high",
            agent="Clinical Agent",
            record_id=";".join(trial_ids),
        )

        evidence_records.insert(
            0,
            aggregate_evidence.to_dict()
        )
    # --------------------------------------------------------
    # Return structured result
    # --------------------------------------------------------

    return {
    "agent": "clinical",
    "query": query,
    "parsed_query": parsed,
    "source": "ClinicalTrials.gov",
    "retrieved_at": retrieved_at,
    "api_parameters": params,
    "trial_count": len(trials),
    "trials": trials,
    "evidence": evidence_records,
}


# ============================================================
# Agent Entry Point
# ============================================================

def run_clinical_agent(
    query: str,
) -> Dict[str, Any]:
    """
    Public entry point used by the Master Agent.
    """

    return search_clinical_trials(
        query
    )


# ============================================================
# Standalone Test
# ============================================================

if __name__ == "__main__":

    test_query = (
        "Find recruiting Phase 3 obesity trials "
        "involving semaglutide in the US"
    )

    result = run_clinical_agent(
        test_query
    )

    print("\n" + "=" * 70)
    print("CLINICAL AGENT TEST")
    print("=" * 70)

    print("\nQUERY:")
    print(result["query"])

    print("\nPARSED QUERY:")
    print(result["parsed_query"])

    print("\nAPI PARAMETERS:")
    print(result.get("api_parameters"))

    print("\nSOURCE:")
    print(result["source"])

    print("\nRETRIEVED AT:")
    print(result["retrieved_at"])

    print("\nTRIALS FOUND:")
    print(result["trial_count"])

    print("\n" + "-" * 70)

    for index, trial in enumerate(
        result["trials"],
        start=1,
    ):

        print(f"\nTRIAL {index}")

        print(
            f"NCT ID: {trial['nct_id']}"
        )

        print(
            f"Title: {trial['title']}"
        )

        print(
            f"Status: {trial['status']}"
        )

        print(
            f"Phase: {trial['phase']}"
        )

        print(
            f"Conditions: "
            f"{trial['conditions']}"
        )

        print(
            f"Interventions: "
            f"{trial['interventions']}"
        )

        print(
            f"Sponsor: "
            f"{trial['sponsor']}"
        )

        print(
            f"Enrollment: "
            f"{trial['enrollment']}"
        )

        print(
            f"Locations: "
            f"{trial['locations']}"
        )

        print(
            f"Source URL: "
            f"{trial['source']['url']}"
        )

        print("-" * 70)