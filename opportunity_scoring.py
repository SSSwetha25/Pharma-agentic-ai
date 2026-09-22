"""
Opportunity Scoring Engine

Calculates a transparent, evidence-based pharmaceutical
opportunity score from Clinical, Market, Competition, and IP data.

Evidence Confidence is reported separately from the Opportunity Score.

The engine does not invent missing evidence.
"""

from typing import Dict, Any


class OpportunityScorer:
    """Calculate pharmaceutical opportunity scores."""

    # ---------------------------------------------------------
    # Market Potential — 30 points
    # ---------------------------------------------------------

    def _score_market_growth(self, cagr: Any) -> int:
        """Score reported CAGR out of 15 points."""

        if cagr is None:
            return 0

        try:
            text = str(cagr).replace("%", "").strip()
            text = text.replace("–", "-")

            if "-" in text:
                parts = text.split("-")
                values = [float(x.strip()) for x in parts]
                growth = sum(values) / len(values)
            else:
                growth = float(text)

        except (ValueError, TypeError):
            return 0

        if growth >= 15:
            return 15
        elif growth >= 12:
            return 12
        elif growth >= 8:
            return 9
        elif growth >= 4:
            return 5
        else:
            return 2

    def _score_market_size(self, market_size: Any) -> int:
        """Score market size out of 15 points."""

        if market_size is None:
            return 0

        try:
            text = str(market_size)

            text = (
                text.replace("USD", "")
                .replace("$", "")
                .replace("B", "")
                .strip()
            )

            size = float(text)

        except (ValueError, TypeError):
            return 0

        if size >= 100:
            return 15
        elif size >= 50:
            return 12
        elif size >= 20:
            return 9
        elif size >= 5:
            return 6
        else:
            return 3

    def _score_market(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Market Potential score."""

        growth_score = self._score_market_growth(
            market.get("cagr")
        )

        size_score = self._score_market_size(
            market.get("estimated_size")
        )

        return {
            "score": growth_score + size_score,
            "maximum": 30,
            "growth_score": growth_score,
            "size_score": size_score,
        }

    # ---------------------------------------------------------
    # Clinical Activity — 25 points
    # ---------------------------------------------------------

    def _score_trial_count(self, trial_count: Any) -> int:
        """Score validated matching trials out of 15 points."""

        try:
            count = int(trial_count)
        except (ValueError, TypeError):
            return 0

        if count >= 20:
            return 15
        elif count >= 10:
            return 12
        elif count >= 5:
            return 9
        elif count >= 2:
            return 6
        elif count == 1:
            return 3
        else:
            return 0

    def _score_phase(self, phase: Any) -> int:
        """Score highest relevant clinical phase out of 10 points."""

        if not phase:
            return 0

        phase = str(phase).upper()

        if "PHASE3" in phase or "PHASE 3" in phase:
            return 10
        elif "PHASE2" in phase or "PHASE 2" in phase:
            return 7
        elif "PHASE1" in phase or "PHASE 1" in phase:
            return 4

        return 0

    def _score_clinical(self, clinical: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Clinical Activity score."""

        trial_score = self._score_trial_count(
            clinical.get("trial_count", 0)
        )

        phase_score = self._score_phase(
            clinical.get("phase")
        )

        return {
            "score": trial_score + phase_score,
            "maximum": 25,
            "trial_score": trial_score,
            "phase_score": phase_score,
        }

    # ---------------------------------------------------------
    # Competition — 20 points
    # ---------------------------------------------------------

    def _score_competition(self, competition: Any) -> Dict[str, Any]:
        """
        Competition is a negative factor.

        Lower competition = higher opportunity score.
        """

        if not competition:
            return {
                "score": 10,
                "maximum": 20,
                "level": "Unknown",
            }

        level = str(competition).strip().lower()

        mapping = {
            "low": 20,
            "moderate": 13,
            "medium": 13,
            "high": 7,
            "very high": 3,
            "unknown": 10,
            "unavailable": 10,
        }

        score = mapping.get(level, 10)

        return {
            "score": score,
            "maximum": 20,
            "level": str(competition),
        }

    # ---------------------------------------------------------
    # IP Evidence — 15 points
    # ---------------------------------------------------------

    def _score_ip(self, ip: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score available IP evidence.

        Unknown/unavailable IP evidence is represented as None
        and excluded from the opportunity-score denominator.
        """

        risk = str(
            ip.get("risk_level", "Unknown")
        ).strip().lower()

        if risk == "low":
            return {
                "score": 15,
                "maximum": 15,
                "status": "Low risk",
                "available": True,
            }

        if risk in ("moderate", "medium"):
            return {
                "score": 10,
                "maximum": 15,
                "status": "Moderate risk",
                "available": True,
            }

        if risk == "high":
            return {
                "score": 3,
                "maximum": 15,
                "status": "High risk",
                "available": True,
            }

        return {
            "score": None,
            "maximum": 15,
            "status": "Unknown",
            "available": False,
        }

    # ---------------------------------------------------------
    # Evidence Confidence
    # ---------------------------------------------------------

    def _score_evidence_confidence(
        self,
        clinical: Dict[str, Any],
        market: Dict[str, Any],
        ip: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assess completeness of the available evidence."""

        clinical_available = (
            clinical.get("status") == "available"
        )

        market_available = (
            market.get("status") in ("SUCCESS", "available")
        )

        ip_available = (
            ip.get("available") is True
        )

        available_count = sum(
            [
                clinical_available,
                market_available,
                ip_available,
            ]
        )

        if available_count == 3:
            score = 10
            level = "Strong"

        elif available_count == 2:
            score = 7
            level = "Moderate"

        elif available_count == 1:
            score = 4
            level = "Limited"

        else:
            score = 0
            level = "Insufficient"

        return {
            "score": score,
            "maximum": 10,
            "level": level,
            "available_sources": available_count,
            "total_sources": 3,
        }

    # ---------------------------------------------------------
    # Public scoring method
    # ---------------------------------------------------------

    def calculate(
        self,
        evidence_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate the overall opportunity score.

        Opportunity Score consists only of:
            Market      = 30
            Clinical    = 25
            Competition = 20
            IP          = 15

        Maximum = 90 points.

        Missing IP evidence is excluded from the denominator
        rather than being treated as zero.

        Evidence Confidence is calculated separately.
        """

        clinical = evidence_summary.get(
            "clinical",
            {}
        )

        market = evidence_summary.get(
            "market",
            {}
        )

        patent = evidence_summary.get(
            "patent",
            {}
        )

        # -----------------------------------------------------
        # Calculate individual dimensions
        # -----------------------------------------------------

        market_result = self._score_market(
            market
        )

        clinical_result = self._score_clinical(
            clinical
        )

        competition_result = self._score_competition(
            market.get(
                "competition_level",
                "Unknown"
            )
        )

        ip_result = self._score_ip(
            patent
        )

        # Evidence confidence is NOT part of opportunity score
        evidence_result = self._score_evidence_confidence(
            clinical,
            market,
            ip_result,
        )

        # -----------------------------------------------------
        # Calculate available opportunity score
        # -----------------------------------------------------

        opportunity_dimensions = [
            market_result,
            clinical_result,
            competition_result,
        ]

        available_score = sum(
            item["score"]
            for item in opportunity_dimensions
        )

        available_maximum = sum(
            item["maximum"]
            for item in opportunity_dimensions
        )

        # Add IP only when evidence is actually available
        if ip_result["available"]:
            available_score += ip_result["score"]
            available_maximum += ip_result["maximum"]

        # -----------------------------------------------------
        # Normalize opportunity score to 100
        # -----------------------------------------------------

        if available_maximum > 0:
            overall_score = round(
                (available_score / available_maximum) * 100
            )
        else:
            overall_score = 0

        # -----------------------------------------------------
        # Opportunity classification
        # -----------------------------------------------------

        if overall_score >= 80:
            rating = "Strong Opportunity"

        elif overall_score >= 60:
            rating = "Moderate Opportunity"

        elif overall_score >= 40:
            rating = "Limited Opportunity"

        else:
            rating = "Weak Opportunity"

        # -----------------------------------------------------
        # Generate explanations
        # -----------------------------------------------------

        explanations = []

        if market_result["score"] >= 20:
            explanations.append(
                "Strong reported market potential."
            )

        elif market_result["score"] > 0:
            explanations.append(
                "Market evidence indicates measurable "
                "commercial potential."
            )

        else:
            explanations.append(
                "Market evidence is unavailable or insufficient."
            )

        if clinical_result["score"] >= 18:
            explanations.append(
                "Strong clinical development activity was identified."
            )

        elif clinical_result["score"] > 0:
            explanations.append(
                "Clinical development activity was identified."
            )

        else:
            explanations.append(
                "Relevant clinical activity evidence is unavailable."
            )

        if competition_result["level"].lower() == "very high":
            explanations.append(
                "Competitive intensity is Very High."
            )

        elif competition_result["level"].lower() == "high":
            explanations.append(
                "Competitive intensity is High."
            )

        elif competition_result["level"].lower() == "low":
            explanations.append(
                "Competitive intensity is Low."
            )

        if not ip_result["available"]:
            explanations.append(
                "Patent/IP evidence is currently unavailable; "
                "the opportunity score was normalized without "
                "this dimension."
            )

        elif ip_result["status"] == "High risk":
            explanations.append(
                "Available IP evidence indicates High risk."
            )

        elif ip_result["status"] == "Moderate risk":
            explanations.append(
                "Available IP evidence indicates Moderate risk."
            )

        elif ip_result["status"] == "Low risk":
            explanations.append(
                "Available IP evidence indicates Low risk."
            )

        # -----------------------------------------------------
        # Final result
        # -----------------------------------------------------

        return {
            "overall_score": overall_score,
            "rating": rating,

            # Separate from opportunity score
            "confidence": evidence_result["level"],

            "dimension_scores": {
                "market": market_result,
                "clinical": clinical_result,
                "competition": competition_result,
                "ip": ip_result,
            },

            "evidence_confidence": evidence_result,

            "available_score": available_score,
            "available_maximum": available_maximum,

            "explanations": explanations,

            "methodology": {
                "opportunity_score_maximum": 100,
                "market_weight": 30,
                "clinical_weight": 25,
                "competition_weight": 20,
                "ip_weight": 15,
                "missing_evidence_policy": (
                    "Unavailable evidence is excluded from "
                    "the denominator and the opportunity "
                    "score is normalized."
                ),
                "evidence_confidence": (
                    "Reported separately based on the number "
                    "of available evidence domains."
                ),
            },
        }


def calculate_opportunity_score(
    evidence_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convenience function for the Master Agent.
    """

    scorer = OpportunityScorer()

    return scorer.calculate(
        evidence_summary
    )


if __name__ == "__main__":
    print("Opportunity Scoring Engine")
    print("Module loaded successfully.")