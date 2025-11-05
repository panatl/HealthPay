import pytest
from datetime import datetime, timedelta
from app.models.claim import Claim, ClaimType, ClaimStatus, ServiceCode, ClaimAnalysisResult, PaymentIntegrityIssue
from app.services.analytics import AnalyticsService


@pytest.fixture
def analytics_service():
    """Create analytics service instance"""
    return AnalyticsService()


@pytest.fixture
def sample_claims():
    """Create sample claims for analytics"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    claims = []
    
    # Claim 1: Approved
    claim1 = Claim(
        claim_id="CLM001",
        patient_id="PAT001",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00)],
        claimed_amount=150.00,
        allowed_amount=150.00,
        paid_amount=150.00,
        status=ClaimStatus.APPROVED,
        diagnosis_codes=["I10"]
    )
    
    # Claim 2: Approved
    claim2 = Claim(
        claim_id="CLM002",
        patient_id="PAT002",
        provider_id="PRV002",
        claim_type=ClaimType.INPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[ServiceCode(code="99285", description="Emergency visit", units=1, unit_price=500.00)],
        claimed_amount=500.00,
        allowed_amount=450.00,
        paid_amount=450.00,
        status=ClaimStatus.APPROVED,
        diagnosis_codes=["I10"]
    )
    
    # Claim 3: Rejected
    claim3 = Claim(
        claim_id="CLM003",
        patient_id="PAT003",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[ServiceCode(code="99214", description="Complex visit", units=1, unit_price=200.00)],
        claimed_amount=200.00,
        status=ClaimStatus.REJECTED,
        diagnosis_codes=["I10"]
    )
    
    # Claim 4: Approved (PRV001)
    claim4 = Claim(
        claim_id="CLM004",
        patient_id="PAT004",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00)],
        claimed_amount=150.00,
        allowed_amount=150.00,
        paid_amount=150.00,
        status=ClaimStatus.APPROVED,
        diagnosis_codes=["I10"]
    )
    
    claims.extend([claim1, claim2, claim3, claim4])
    return claims


def test_generate_summary(analytics_service, sample_claims):
    """Test generation of analytics summary"""
    summary = analytics_service.generate_summary(sample_claims)
    
    assert summary.total_claims == 4
    assert summary.total_claimed_amount == 1000.00
    assert summary.total_paid_amount == 750.00
    assert summary.claims_by_status[ClaimStatus.APPROVED.value] == 3
    assert summary.claims_by_status[ClaimStatus.REJECTED.value] == 1


def test_generate_summary_with_analysis(analytics_service, sample_claims):
    """Test generation of summary with analysis results"""
    # Create mock analysis results
    analysis_results = [
        ClaimAnalysisResult(
            claim_id="CLM001",
            is_valid=True,
            issues=[],
            total_estimated_impact=0.0,
            risk_score=10.0
        ),
        ClaimAnalysisResult(
            claim_id="CLM002",
            is_valid=False,
            issues=[
                PaymentIntegrityIssue(
                    issue_type="overpayment",
                    severity="high",
                    description="Test overpayment",
                    estimated_impact=50.00,
                    recommendation="Test"
                )
            ],
            total_estimated_impact=50.0,
            risk_score=75.0
        )
    ]
    
    summary = analytics_service.generate_summary(sample_claims[:2], analysis_results)
    
    assert summary.total_claims == 2
    assert summary.total_issues_found == 1
    assert summary.estimated_overpayment == 50.00
    assert summary.average_risk_score == 42.5  # (10 + 75) / 2


def test_generate_summary_empty_claims(analytics_service):
    """Test generation of summary with empty claims list"""
    summary = analytics_service.generate_summary([])
    
    assert summary.total_claims == 0
    assert summary.total_claimed_amount == 0.0
    assert summary.total_paid_amount == 0.0


def test_get_top_providers_by_amount(analytics_service, sample_claims):
    """Test getting top providers by amount"""
    top_providers = analytics_service.get_top_providers_by_amount(sample_claims, limit=2)
    
    assert len(top_providers) == 2
    # PRV001 has 3 claims totaling 500.00, PRV002 has 1 claim of 500.00
    assert top_providers[0]['provider_id'] in ['PRV001', 'PRV002']
    assert top_providers[0]['total_amount'] > 0


def test_get_top_service_codes(analytics_service, sample_claims):
    """Test getting most frequently billed service codes"""
    top_services = analytics_service.get_top_service_codes(sample_claims, limit=3)
    
    assert len(top_services) <= 3
    # 99213 appears twice
    service_codes = [s['code'] for s in top_services]
    assert '99213' in service_codes


def test_calculate_payment_accuracy_rate(analytics_service, sample_claims):
    """Test calculation of payment accuracy rate"""
    accuracy = analytics_service.calculate_payment_accuracy_rate(sample_claims)
    
    # 2 out of 3 applicable claims paid correctly
    assert accuracy > 0
    assert accuracy <= 100


def test_calculate_payment_accuracy_empty(analytics_service):
    """Test payment accuracy with no claims"""
    accuracy = analytics_service.calculate_payment_accuracy_rate([])
    assert accuracy == 0.0


def test_calculate_cost_efficiency(analytics_service, sample_claims):
    """Test calculation of cost efficiency metrics"""
    efficiency = analytics_service.calculate_cost_efficiency(sample_claims)
    
    assert 'total_claimed' in efficiency
    assert 'total_paid' in efficiency
    assert 'total_savings' in efficiency
    assert 'savings_rate_percent' in efficiency
    
    assert efficiency['total_claimed'] == 1000.00
    assert efficiency['total_paid'] == 750.00
    assert efficiency['total_savings'] == 250.00
    assert efficiency['savings_rate_percent'] == 25.0


def test_claims_by_type_summary(analytics_service, sample_claims):
    """Test claims breakdown by type in summary"""
    summary = analytics_service.generate_summary(sample_claims)
    
    assert ClaimType.OUTPATIENT.value in summary.claims_by_type
    assert ClaimType.INPATIENT.value in summary.claims_by_type
    assert summary.claims_by_type[ClaimType.OUTPATIENT.value] == 3
    assert summary.claims_by_type[ClaimType.INPATIENT.value] == 1
