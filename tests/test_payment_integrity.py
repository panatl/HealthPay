import pytest
from datetime import datetime, timedelta
from app.models.claim import Claim, ClaimType, ClaimStatus, ServiceCode
from app.services.payment_integrity import PaymentIntegrityService


@pytest.fixture
def payment_service():
    """Create payment integrity service instance"""
    return PaymentIntegrityService()


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
def overpayment_claim(sample_service):
    """Create a claim with overpayment"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    return Claim(
        claim_id="CLM_OVER",
        patient_id="PAT001",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[sample_service],
        claimed_amount=150.00,
        allowed_amount=100.00,
        paid_amount=150.00,  # Overpaid by $50
        status=ClaimStatus.APPROVED,
        diagnosis_codes=["I10"]
    )


@pytest.fixture
def underpayment_claim(sample_service):
    """Create a claim with underpayment"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    return Claim(
        claim_id="CLM_UNDER",
        patient_id="PAT002",
        provider_id="PRV002",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[sample_service],
        claimed_amount=150.00,
        allowed_amount=150.00,
        paid_amount=100.00,  # Underpaid by $50
        status=ClaimStatus.APPROVED,
        diagnosis_codes=["I10"]
    )


def test_analyze_overpayment(payment_service, overpayment_claim):
    """Test detection of overpayment"""
    result = payment_service.analyze_claim(overpayment_claim)
    
    assert result.claim_id == "CLM_OVER"
    assert len(result.issues) > 0
    
    # Check for overpayment issue
    overpayment_issues = [i for i in result.issues if i.issue_type == "overpayment"]
    assert len(overpayment_issues) == 1
    assert overpayment_issues[0].severity == "high"
    assert overpayment_issues[0].estimated_impact == 50.00


def test_analyze_underpayment(payment_service, underpayment_claim):
    """Test detection of underpayment"""
    result = payment_service.analyze_claim(underpayment_claim)
    
    assert result.claim_id == "CLM_UNDER"
    assert len(result.issues) > 0
    
    # Check for underpayment issue
    underpayment_issues = [i for i in result.issues if i.issue_type == "underpayment"]
    assert len(underpayment_issues) == 1
    assert underpayment_issues[0].severity == "medium"
    assert underpayment_issues[0].estimated_impact == -50.00


def test_detect_duplicate_services(payment_service):
    """Test detection of duplicate services within a claim"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create claim with duplicate service codes
    duplicate_claim = Claim(
        claim_id="CLM_DUP",
        patient_id="PAT003",
        provider_id="PRV003",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[
            ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00),
            ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00),
        ],
        claimed_amount=300.00,
        diagnosis_codes=["I10"]
    )
    
    result = payment_service.analyze_claim(duplicate_claim)
    
    # Check for duplicate service issue
    duplicate_issues = [i for i in result.issues if i.issue_type == "duplicate_service"]
    assert len(duplicate_issues) == 1


def test_detect_pricing_error(payment_service):
    """Test detection of pricing errors"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create claim with pricing error
    pricing_error_claim = Claim(
        claim_id="CLM_PRICE",
        patient_id="PAT004",
        provider_id="PRV004",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[
            ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00),
        ],
        claimed_amount=200.00,  # Incorrect: should be 150.00
        diagnosis_codes=["I10"]
    )
    
    result = payment_service.analyze_claim(pricing_error_claim)
    
    # Check for pricing error issue
    pricing_issues = [i for i in result.issues if i.issue_type == "pricing_error"]
    assert len(pricing_issues) == 1


def test_detect_missing_diagnosis(payment_service, sample_service):
    """Test detection of missing diagnosis codes"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create claim without diagnosis codes
    no_diagnosis_claim = Claim(
        claim_id="CLM_NODIAG",
        patient_id="PAT005",
        provider_id="PRV005",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[sample_service],
        claimed_amount=150.00,
        diagnosis_codes=[]  # Missing diagnosis codes
    )
    
    result = payment_service.analyze_claim(no_diagnosis_claim)
    
    # Check for missing diagnosis issue
    diagnosis_issues = [i for i in result.issues if i.issue_type == "missing_diagnosis"]
    assert len(diagnosis_issues) == 1


def test_detect_duplicate_claims(payment_service):
    """Test detection of duplicate claims"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create two identical claims
    claim1 = Claim(
        claim_id="CLM001",
        patient_id="PAT001",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00)],
        claimed_amount=150.00,
        diagnosis_codes=["I10"]
    )
    
    claim2 = Claim(
        claim_id="CLM002",
        patient_id="PAT001",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00)],
        claimed_amount=150.00,
        diagnosis_codes=["I10"]
    )
    
    duplicates = payment_service.detect_duplicate_claims([claim1, claim2])
    
    assert len(duplicates) == 1
    assert len(duplicates[0]) == 2
    assert "CLM001" in duplicates[0]
    assert "CLM002" in duplicates[0]


def test_calculate_allowed_amount(payment_service, sample_service):
    """Test calculation of allowed amount based on fee schedule"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    claim = Claim(
        claim_id="CLM_ALLOW",
        patient_id="PAT006",
        provider_id="PRV006",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[sample_service],
        claimed_amount=150.00,
        diagnosis_codes=["I10"]
    )
    
    fee_schedule = {
        "99213": 120.00  # Allowed amount less than charged
    }
    
    allowed = payment_service.check_allowed_amount(claim, fee_schedule)
    assert allowed == 120.00


def test_risk_score_calculation(payment_service, overpayment_claim):
    """Test risk score calculation"""
    result = payment_service.analyze_claim(overpayment_claim)
    
    # Should have a risk score
    assert result.risk_score >= 0
    assert result.risk_score <= 100
    
    # Claim with high severity issues should have higher risk score
    assert result.risk_score > 0
