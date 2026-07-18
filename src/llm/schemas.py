"""Pydantic schemas for structured LLM outputs."""

from pydantic import BaseModel, Field


class OperatorRecommendation(BaseModel):
    locomotive_id: str
    severity: str = Field(description="low, medium, or high")
    summary: str = Field(description="Brief situation summary for the operator")
    recommended_action: str = Field(description="Action the operator should take")
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence 0-1")
