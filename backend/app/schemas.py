from pydantic import BaseModel, Field


class ProjectInput(BaseModel):
    project_type: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    district: str = Field(..., min_length=1)
    land_area_acres: float = Field(..., ge=0)
    affected_families: int = Field(..., ge=0)
    approval_days: int = Field(..., ge=0)
    pending_approvals: int = Field(..., ge=0)
    legal_disputes: int = Field(..., ge=0)
    compensation_paid_pct: float = Field(..., ge=0, le=100)
    documentation_complete_pct: float = Field(..., ge=0, le=100)
    notifications_pending: int = Field(..., ge=0)
    ownership_conflicts: int = Field(..., ge=0)
    rehabilitation_progress_pct: float = Field(..., ge=0, le=100)
    possession_progress_pct: float = Field(..., ge=0, le=100)
    stakeholder_response_days: int = Field(..., ge=0)
    inter_departmental_issues: int = Field(..., ge=0)
    historical_delay_rate_pct: float = Field(..., ge=0, le=100)


class PredictionResponse(BaseModel):
    delay_probability: float
    risk_level: str
    expected_delay: str
    top_drivers: list[dict]
    recommendations: list[str]
