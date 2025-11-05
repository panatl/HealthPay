from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ClaimStatus(str, Enum):
    """Status of a healthcare claim"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"


class ClaimType(str, Enum):
    """Type of healthcare claim"""
    INPATIENT = "inpatient"
    OUTPATIENT = "outpatient"
    PHARMACY = "pharmacy"
    PROFESSIONAL = "professional"
    DENTAL = "dental"


class ServiceCode(BaseModel):
    """Medical service or procedure code"""
    code: str = Field(..., description="CPT/HCPCS code")
    description: str = Field(..., description="Service description")
    units: int = Field(default=1, ge=1, description="Number of units")
    unit_price: float = Field(..., ge=0, description="Price per unit")


class Claim(BaseModel):
    """Healthcare claim model"""
    claim_id: str = Field(..., description="Unique claim identifier")
    patient_id: str = Field(..., description="Patient identifier")
    provider_id: str = Field(..., description="Healthcare provider identifier")
    claim_type: ClaimType = Field(..., description="Type of claim")
    service_date: datetime = Field(..., description="Date of service")
    submission_date: datetime = Field(..., description="Date claim was submitted")
    services: List[ServiceCode] = Field(..., description="Services provided")
    claimed_amount: float = Field(..., ge=0, description="Total claimed amount")
    allowed_amount: Optional[float] = Field(None, ge=0, description="Allowed amount per policy")
    paid_amount: Optional[float] = Field(None, ge=0, description="Amount actually paid")
    status: ClaimStatus = Field(default=ClaimStatus.PENDING)
    diagnosis_codes: List[str] = Field(default_factory=list, description="ICD diagnosis codes")
    
    @field_validator('submission_date')
    @classmethod
    def submission_after_service(cls, v: datetime, info) -> datetime:
        if 'service_date' in info.data and v < info.data['service_date']:
            raise ValueError("Submission date must be after service date")
        return v


class PaymentIntegrityIssue(BaseModel):
    """Payment integrity issue detected in a claim"""
    issue_type: str = Field(..., description="Type of issue detected")
    severity: str = Field(..., description="Severity level: low, medium, high, critical")
    description: str = Field(..., description="Description of the issue")
    estimated_impact: float = Field(..., description="Estimated financial impact")
    recommendation: str = Field(..., description="Recommended action")


class ClaimAnalysisResult(BaseModel):
    """Result of claim analysis"""
    claim_id: str
    is_valid: bool
    issues: List[PaymentIntegrityIssue] = Field(default_factory=list)
    total_estimated_impact: float = Field(default=0.0)
    risk_score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class FraudAlert(BaseModel):
    """Fraud, waste, or abuse alert"""
    alert_id: str
    claim_ids: List[str]
    alert_type: str = Field(..., description="Type of fraud/waste/abuse")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    pattern_description: str
    flagged_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="open")


class AnalyticsSummary(BaseModel):
    """Analytics summary for claims"""
    total_claims: int
    total_claimed_amount: float
    total_paid_amount: float
    total_issues_found: int
    estimated_overpayment: float
    estimated_underpayment: float
    fraud_alerts_count: int
    average_risk_score: float
    claims_by_status: dict
    claims_by_type: dict
