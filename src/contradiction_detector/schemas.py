from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

ValueType = Literal["date", "number", "string", "other"]
EntityType = Literal["person", "org", "location", "event", "other"]
ContradictionType = Literal[
    "attribute_conflict",
    "date_mismatch",
    "number_mismatch",
    "name_mismatch",
]


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceSpan(StrictBaseModel):
    start: int = Field(..., description="0-based start offset")
    end: int = Field(..., description="0-based end offset (exclusive)")
    text: str

    @model_validator(mode="after")
    def validate_span(self) -> "EvidenceSpan":
        if self.start < 0:
            raise ValueError("start must be >= 0")
        if self.end <= self.start:
            raise ValueError("end must be greater than start")
        return self


class Claim(StrictBaseModel):
    value_text: str
    value_type: ValueType
    value_normalized: str
    evidence: list[EvidenceSpan] = Field(min_length=1)


class Entity(StrictBaseModel):
    text: str
    normalized: Optional[str] = None
    entity_type: EntityType


class Contradiction(StrictBaseModel):
    id: str
    type: ContradictionType
    subject: Entity
    attribute: str
    claims: list[Claim] = Field(min_length=2)
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class ContradictionResult(StrictBaseModel):
    document_id: Optional[str] = None
    contradictions: list[Contradiction]
