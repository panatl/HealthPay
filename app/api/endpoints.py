from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict
from app.models.claim import (
    Claim, ClaimAnalysisResult, PaymentIntegrityIssue,
    FraudAlert, AnalyticsSummary
)
from app.services.payment_integrity import PaymentIntegrityService
from app.services.fraud_detection import FraudDetectionService
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/v1", tags=["Payment Integrity"])

# Initialize services
payment_integrity_service = PaymentIntegrityService()
fraud_detection_service = FraudDetectionService()
analytics_service = AnalyticsService()

# In-memory storage for demo purposes
claims_db: Dict[str, Claim] = {}
analysis_db: Dict[str, ClaimAnalysisResult] = {}
fraud_alerts_db: Dict[str, FraudAlert] = {}


@router.post("/claims/analyze", response_model=ClaimAnalysisResult)
async def analyze_claim(claim: Claim):
    """
    Analyze a single claim for payment integrity issues
    
    Detects:
    - Overpayments and underpayments
    - Pricing errors
    - Duplicate services
    - Missing information
    - Late filing issues
    """
    try:
        # Store claim
        claims_db[claim.claim_id] = claim
        
        # Analyze claim
        result = payment_integrity_service.analyze_claim(claim)
        analysis_db[claim.claim_id] = result
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/claims/batch-analyze", response_model=List[ClaimAnalysisResult])
async def batch_analyze_claims(claims: List[Claim]):
    """
    Analyze multiple claims for payment integrity issues
    """
    try:
        results = []
        for claim in claims:
            claims_db[claim.claim_id] = claim
            result = payment_integrity_service.analyze_claim(claim)
            analysis_db[claim.claim_id] = result
            results.append(result)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.post("/claims/check-duplicates", response_model=Dict)
async def check_duplicate_claims(claims: List[Claim]):
    """
    Check for duplicate claims across the provided set
    """
    try:
        duplicates = payment_integrity_service.detect_duplicate_claims(claims)
        return {
            "duplicate_groups": duplicates,
            "total_duplicate_groups": len(duplicates),
            "total_claims_checked": len(claims)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Duplicate check failed: {str(e)}")


@router.post("/claims/calculate-allowed", response_model=Dict)
async def calculate_allowed_amount(
    claim: Claim,
    fee_schedule: Dict[str, float] = Body(...)
):
    """
    Calculate allowed amount based on fee schedule
    
    Args:
        claim: The claim to evaluate
        fee_schedule: Dictionary mapping service codes to allowed amounts
    """
    try:
        allowed = payment_integrity_service.check_allowed_amount(claim, fee_schedule)
        return {
            "claim_id": claim.claim_id,
            "claimed_amount": claim.claimed_amount,
            "calculated_allowed_amount": allowed,
            "difference": claim.claimed_amount - allowed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")


@router.post("/fraud/analyze", response_model=List[FraudAlert])
async def analyze_fraud(claims: List[Claim]):
    """
    Analyze claims for fraud, waste, and abuse patterns
    
    Detects:
    - Duplicate billing
    - High-volume billing anomalies
    - Provider pattern anomalies
    - Doctor shopping
    - Multiple services same day
    """
    try:
        alerts = fraud_detection_service.analyze_for_fraud(claims)
        
        # Store alerts
        for alert in alerts:
            fraud_alerts_db[alert.alert_id] = alert
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fraud analysis failed: {str(e)}")


@router.get("/fraud/provider-risk/{provider_id}", response_model=Dict)
async def get_provider_risk_score(provider_id: str):
    """
    Calculate fraud risk score for a specific provider
    """
    try:
        risk_score = fraud_detection_service.calculate_fraud_risk_score(provider_id)
        return {
            "provider_id": provider_id,
            "risk_score": risk_score,
            "risk_level": "high" if risk_score > 70 else "medium" if risk_score > 40 else "low"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk calculation failed: {str(e)}")


@router.get("/fraud/alerts", response_model=List[FraudAlert])
async def get_fraud_alerts(status: str = None):
    """
    Get all fraud alerts, optionally filtered by status
    """
    alerts = list(fraud_alerts_db.values())
    
    if status:
        alerts = [a for a in alerts if a.status == status]
    
    return alerts


@router.post("/analytics/summary", response_model=AnalyticsSummary)
async def generate_analytics_summary(claims: List[Claim] = None):
    """
    Generate comprehensive analytics summary for claims
    """
    try:
        # Use provided claims or all claims in database
        claims_to_analyze = claims if claims else list(claims_db.values())
        
        # Get analysis results for these claims
        analysis_results = []
        if claims_to_analyze:
            for claim in claims_to_analyze:
                if claim.claim_id in analysis_db:
                    analysis_results.append(analysis_db[claim.claim_id])
                else:
                    # Analyze if not already analyzed
                    result = payment_integrity_service.analyze_claim(claim)
                    analysis_results.append(result)
        
        summary = analytics_service.generate_summary(claims_to_analyze, analysis_results)
        
        # Add fraud alerts count
        summary.fraud_alerts_count = len(fraud_alerts_db)
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@router.post("/analytics/top-providers", response_model=List[Dict])
async def get_top_providers(claims: List[Claim], limit: int = 10):
    """
    Get top providers by total claimed amount
    """
    try:
        return analytics_service.get_top_providers_by_amount(claims, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provider analysis failed: {str(e)}")


@router.post("/analytics/top-services", response_model=List[Dict])
async def get_top_services(claims: List[Claim], limit: int = 10):
    """
    Get most frequently billed service codes
    """
    try:
        return analytics_service.get_top_service_codes(claims, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service analysis failed: {str(e)}")


@router.post("/analytics/payment-accuracy", response_model=Dict)
async def calculate_payment_accuracy(claims: List[Claim]):
    """
    Calculate payment accuracy rate
    """
    try:
        accuracy = analytics_service.calculate_payment_accuracy_rate(claims)
        return {
            "payment_accuracy_rate": accuracy,
            "total_claims_evaluated": len(claims)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Accuracy calculation failed: {str(e)}")


@router.post("/analytics/cost-efficiency", response_model=Dict)
async def calculate_cost_efficiency(claims: List[Claim]):
    """
    Calculate cost efficiency metrics
    """
    try:
        return analytics_service.calculate_cost_efficiency(claims)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Efficiency calculation failed: {str(e)}")


@router.get("/claims/{claim_id}", response_model=Claim)
async def get_claim(claim_id: str):
    """
    Get a specific claim by ID
    """
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claims_db[claim_id]


@router.get("/claims/{claim_id}/analysis", response_model=ClaimAnalysisResult)
async def get_claim_analysis(claim_id: str):
    """
    Get analysis results for a specific claim
    """
    if claim_id not in analysis_db:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis_db[claim_id]


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "HealthPay Payment Integrity Platform",
        "version": "1.0.0"
    }
