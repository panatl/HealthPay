import pytest
from datetime import datetime, timedelta
from app.models.claim import Claim, ClaimType, ClaimStatus, ServiceCode
from app.services.fraud_detection import FraudDetectionService


@pytest.fixture
def fraud_service():
    """Create fraud detection service instance"""
    return FraudDetectionService()


@pytest.fixture
def sample_service():
    """Create a sample service code"""
    return ServiceCode(
        code="99213",
        description="Office visit",
        units=1,
        unit_price=150.00
    )


def test_detect_duplicate_billing(fraud_service):
    """Test detection of duplicate billing"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create identical claims (duplicate billing)
    service = ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00)
    
    claim1 = Claim(
        claim_id="CLM001",
        patient_id="PAT001",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[service],
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
        services=[service],
        claimed_amount=150.00,
        diagnosis_codes=["I10"]
    )
    
    alerts = fraud_service.analyze_for_fraud([claim1, claim2])
    
    # Should detect duplicate billing
    duplicate_alerts = [a for a in alerts if a.alert_type == "duplicate_billing"]
    assert len(duplicate_alerts) > 0
    assert duplicate_alerts[0].confidence_score >= 0.9


def test_detect_high_volume_billing(fraud_service):
    """Test detection of high volume billing"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create many claims for same provider on same day
    claims = []
    for i in range(60):  # Exceeds threshold
        claim = Claim(
            claim_id=f"CLM{i:03d}",
            patient_id=f"PAT{i:03d}",
            provider_id="PRV_HIGHVOL",
            claim_type=ClaimType.OUTPATIENT,
            service_date=service_date,
            submission_date=submission_date,
            services=[ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00)],
            claimed_amount=150.00,
            diagnosis_codes=["I10"]
        )
        claims.append(claim)
    
    alerts = fraud_service.analyze_for_fraud(claims)
    
    # Should detect high volume billing
    high_volume_alerts = [a for a in alerts if a.alert_type == "high_volume_billing"]
    assert len(high_volume_alerts) > 0


def test_detect_high_average_claims(fraud_service):
    """Test detection of high average claim amounts"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create multiple high-value claims
    claims = []
    for i in range(15):
        claim = Claim(
            claim_id=f"CLM_HIGH{i:03d}",
            patient_id=f"PAT{i:03d}",
            provider_id="PRV_HIGHAVG",
            claim_type=ClaimType.INPATIENT,
            service_date=service_date,
            submission_date=submission_date,
            services=[ServiceCode(code="99285", description="Emergency visit", units=1, unit_price=8000.00)],
            claimed_amount=8000.00,
            diagnosis_codes=["I10"]
        )
        claims.append(claim)
    
    alerts = fraud_service.analyze_for_fraud(claims)
    
    # Should detect high average claims
    high_avg_alerts = [a for a in alerts if a.alert_type == "high_average_claims"]
    assert len(high_avg_alerts) > 0


def test_detect_service_code_concentration(fraud_service):
    """Test detection of excessive use of specific service codes"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create many claims with same service code (upcoding pattern)
    claims = []
    for i in range(30):
        claim = Claim(
            claim_id=f"CLM_UPCODE{i:03d}",
            patient_id=f"PAT{i:03d}",
            provider_id="PRV_UPCODE",
            claim_type=ClaimType.OUTPATIENT,
            service_date=service_date,
            submission_date=submission_date,
            services=[ServiceCode(code="99215", description="High complexity visit", units=1, unit_price=300.00)],
            claimed_amount=300.00,
            diagnosis_codes=["I10"]
        )
        claims.append(claim)
    
    alerts = fraud_service.analyze_for_fraud(claims)
    
    # Should detect service code concentration
    concentration_alerts = [a for a in alerts if a.alert_type == "service_code_concentration"]
    assert len(concentration_alerts) > 0


def test_detect_doctor_shopping(fraud_service):
    """Test detection of doctor shopping (patient seeing many providers)"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create claims for same patient with many different providers
    claims = []
    for i in range(15):
        claim = Claim(
            claim_id=f"CLM_SHOP{i:03d}",
            patient_id="PAT_SHOPPER",
            provider_id=f"PRV{i:03d}",
            claim_type=ClaimType.PHARMACY,
            service_date=service_date,
            submission_date=submission_date,
            services=[ServiceCode(code="J2001", description="Medication", units=1, unit_price=50.00)],
            claimed_amount=50.00,
            diagnosis_codes=["M79.3"]
        )
        claims.append(claim)
    
    alerts = fraud_service.analyze_for_fraud(claims)
    
    # Should detect doctor shopping
    shopping_alerts = [a for a in alerts if a.alert_type == "doctor_shopping"]
    assert len(shopping_alerts) > 0


def test_detect_multiple_services_same_day(fraud_service):
    """Test detection of multiple services on same day"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create multiple claims for same patient on same day
    claims = []
    for i in range(5):
        claim = Claim(
            claim_id=f"CLM_SAMEDAY{i:03d}",
            patient_id="PAT_BUSY",
            provider_id=f"PRV{i:03d}",
            claim_type=ClaimType.OUTPATIENT,
            service_date=service_date,
            submission_date=submission_date,
            services=[ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00)],
            claimed_amount=150.00,
            diagnosis_codes=["I10"]
        )
        claims.append(claim)
    
    alerts = fraud_service.analyze_for_fraud(claims)
    
    # Should detect multiple services same day
    same_day_alerts = [a for a in alerts if a.alert_type == "multiple_services_same_day"]
    assert len(same_day_alerts) > 0


def test_calculate_provider_fraud_risk_score(fraud_service):
    """Test calculation of provider fraud risk score"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create claims for provider
    claims = []
    for i in range(25):
        claim = Claim(
            claim_id=f"CLM_RISK{i:03d}",
            patient_id=f"PAT{i:03d}",
            provider_id="PRV_RISK",
            claim_type=ClaimType.OUTPATIENT,
            service_date=service_date,
            submission_date=submission_date,
            services=[ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00)],
            claimed_amount=150.00,
            diagnosis_codes=["I10"]
        )
        claims.append(claim)
    
    # Analyze to build history
    fraud_service.analyze_for_fraud(claims)
    
    # Calculate risk score
    risk_score = fraud_service.calculate_fraud_risk_score("PRV_RISK")
    
    assert risk_score >= 0
    assert risk_score <= 100


def test_fraud_alert_structure(fraud_service):
    """Test structure of fraud alerts"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create duplicate claims
    service = ServiceCode(code="99213", description="Office visit", units=1, unit_price=150.00)
    
    claim1 = Claim(
        claim_id="CLM_A",
        patient_id="PAT001",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[service],
        claimed_amount=150.00,
        diagnosis_codes=["I10"]
    )
    
    claim2 = Claim(
        claim_id="CLM_B",
        patient_id="PAT001",
        provider_id="PRV001",
        claim_type=ClaimType.OUTPATIENT,
        service_date=service_date,
        submission_date=submission_date,
        services=[service],
        claimed_amount=150.00,
        diagnosis_codes=["I10"]
    )
    
    alerts = fraud_service.analyze_for_fraud([claim1, claim2])
    
    if alerts:
        alert = alerts[0]
        assert hasattr(alert, 'alert_id')
        assert hasattr(alert, 'claim_ids')
        assert hasattr(alert, 'alert_type')
        assert hasattr(alert, 'confidence_score')
        assert hasattr(alert, 'pattern_description')
        assert hasattr(alert, 'status')
        assert 0 <= alert.confidence_score <= 1
