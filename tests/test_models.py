import pytest
from datetime import datetime, timedelta
from app.models.claim import (
    Claim, ClaimType, ClaimStatus, ServiceCode,
    PaymentIntegrityIssue, ClaimAnalysisResult
)


@pytest.fixture
def sample_service():
    """Create a sample service code"""
    return ServiceCode(
        code="99213",
        description="Office visit",
        units=1,
        unit_price=150.00
    )


@pytest.fixture
def sample_claim(sample_service):
    """Create a sample claim"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    return Claim(
        claim_id="CLM001",
        patient_id="PAT001",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[sample_service],
        claimed_amount=150.00,
        allowed_amount=150.00,
        paid_amount=150.00,
        status=ClaimStatus.APPROVED,
        diagnosis_codes=["I10"]
    )


def test_service_code_creation(sample_service):
    """Test service code model creation"""
    assert sample_service.code == "99213"
    assert sample_service.description == "Office visit"
    assert sample_service.units == 1
    assert sample_service.unit_price == 150.00


def test_claim_creation(sample_claim):
    """Test claim model creation"""
    assert sample_claim.claim_id == "CLM001"
    assert sample_claim.patient_id == "PAT001"
    assert sample_claim.provider_id == "PRV001"
    assert sample_claim.claim_type == ClaimType.OUTPATIENT
    assert sample_claim.claimed_amount == 150.00
    assert len(sample_claim.services) == 1
    assert len(sample_claim.diagnosis_codes) == 1


def test_claim_validation_submission_date():
    """Test claim validation for submission date"""
    service_date = datetime.utcnow()
    submission_date = service_date - timedelta(days=1)  # Invalid: before service
    
    with pytest.raises(ValueError):
        Claim(
            claim_id="CLM002",
            patient_id="PAT001",
            provider_id="PRV001",
            claim_type=ClaimType.OUTPATIENT,
            service_date=service_date,
            submission_date=submission_date,
            services=[],
            claimed_amount=100.00
        )


def test_payment_integrity_issue_creation():
    """Test payment integrity issue creation"""
    issue = PaymentIntegrityIssue(
        issue_type="overpayment",
        severity="high",
        description="Payment exceeds allowed amount",
        estimated_impact=50.00,
        recommendation="Recover overpaid amount"
    )
    
    assert issue.issue_type == "overpayment"
    assert issue.severity == "high"
    assert issue.estimated_impact == 50.00


def test_claim_analysis_result():
    """Test claim analysis result model"""
    issues = [
        PaymentIntegrityIssue(
            issue_type="overpayment",
            severity="high",
            description="Test issue",
            estimated_impact=50.00,
            recommendation="Test"
        )
    ]
    
    result = ClaimAnalysisResult(
        claim_id="CLM001",
        is_valid=False,
        issues=issues,
        total_estimated_impact=50.00,
        risk_score=75.0
    )
    
    assert result.claim_id == "CLM001"
    assert result.is_valid is False
    assert len(result.issues) == 1
    assert result.total_estimated_impact == 50.00
    assert result.risk_score == 75.0
