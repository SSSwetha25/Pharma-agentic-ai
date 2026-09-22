class EvidenceAggregator:
    """
    Normalizes outputs from the Clinical, Patent, and Market agents
    into a common evidence structure.

    The aggregator does not invent missing evidence.
    """

    def aggregate(
        self,
        clinical_data=None,
        patent_data=None,
        market_data=None,
    ):
        return {
            "clinical": self._build_clinical_evidence(clinical_data),
            "patent": self._build_patent_evidence(patent_data),
            "market": self._build_market_evidence(market_data),
        }

    def _build_clinical_evidence(self, data):
        data = data or {}

        trials = data.get("trials", [])
        trial_count = data.get(
            "trial_count",
            len(trials)
        )

        if data.get("error"):
            return {
                "status": "unavailable",
                "results": [],
                "validation": {},
                "source": data.get(
                    "source",
                    "ClinicalTrials.gov"
                ),
                "limitations": [
                    data["error"]
                ],
            }

        if not trials:
            return {
                "status": "unavailable",
                "results": [],
                "validation": {},
                "source": data.get(
                    "source",
                    "ClinicalTrials.gov"
                ),
                "limitations": [
                    "No clinical trials were returned."
                ],
            }

        return {
            "status": "available",
            "results": trials,
            "trial_count": trial_count,
            "validation": {
                "validated": True,
                "count": trial_count,
            },
            "parsed_query": data.get(
                "parsed_query",
                {}
            ),
            "source": data.get(
                "source",
                "ClinicalTrials.gov"
            ),
            "limitations": data.get(
                "limitations",
                []
            ),
        }

    def _build_patent_evidence(self, data):
        data = data or {}

        patents = data.get("patents")

        if patents is None:
            return {
                "status": "unavailable",
                "risk": "Unknown",
                "jurisdiction": data.get(
                    "geography",
                    "Unknown"
                ),
                "evidence": [],
                "limitations": [
                    "Patent evidence is currently unavailable."
                ],
            }

        try:
            if patents.empty:
                return {
                    "status": "unavailable",
                    "risk": "Unknown",
                    "jurisdiction": data.get(
                        "geography",
                        "Unknown"
                    ),
                    "evidence": [],
                    "limitations": [
                        "No patent records were returned."
                    ],
                }
        except AttributeError:
            pass

        return {
            "status": "available",
            "risk": "Unknown",
            "jurisdiction": data.get(
                "geography",
                "Unknown"
            ),
            "evidence": patents,
            "limitations": data.get(
                "limitations",
                []
            ),
        }

    def _build_market_evidence(self, data):
        data = data or {}

        market = data.get(
            "market_data",
            {}
        )

        if not market:
            return {
                "status": "unavailable",
                "source_reported": {},
                "derived_projection": [],
                "competition": "Unknown",
                "strategic_signals": {},
                "limitations": [
                    "Market evidence is currently unavailable."
                ],
            }

        return {
            "status": data.get(
                "status",
                "SUCCESS"
            ),
            "category": data.get(
                "category"
            ),
            "source_reported": market.get(
                "source_reported",
                {}
            ),
            "derived_projection": market.get(
                "derived_projection",
                []
            ),
            "competition": market.get(
                "competition_level",
                "Unknown"
            ),
            "strategic_signals": market.get(
                "strategic_signals",
                {}
            ),
            "projection_method": market.get(
                "projection_method"
            ),
            "data_quality": market.get(
                "data_quality",
                "Unknown"
            ),
            "source": data.get(
                "source"
            ),
            "secondary_source": data.get(
                "secondary_source"
            ),
            "limitations": market.get(
                "limitations",
                []
            ),
        }