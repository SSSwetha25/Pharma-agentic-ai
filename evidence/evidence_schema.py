from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Evidence:
    """
    Standard evidence record used by all research agents.

    This schema does not determine whether evidence is correct.
    Agents are responsible for retrieval and validation.
    """

    source: str
    source_type: str

    claim: str
    evidence: str

    url: Optional[str] = None

    retrieved_at: Optional[str] = None

    status: str = "unverified"
    confidence: str = "unknown"

    agent: Optional[str] = None
    record_id: Optional[str] = None

    def __post_init__(self):
        if self.retrieved_at is None:
            self.retrieved_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        """Convert the evidence record into a normal dictionary."""
        return asdict(self)


def create_evidence(
    source: str,
    source_type: str,
    claim: str,
    evidence: str,
    url: Optional[str] = None,
    status: str = "unverified",
    confidence: str = "unknown",
    agent: Optional[str] = None,
    record_id: Optional[str] = None,
):
    """
    Convenience function for creating a standardized evidence record.
    """

    return Evidence(
        source=source,
        source_type=source_type,
        claim=claim,
        evidence=evidence,
        url=url,
        status=status,
        confidence=confidence,
        agent=agent,
        record_id=record_id,
    )