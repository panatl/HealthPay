from typing import List, Dict
from collections import Counter
from datetime import datetime
from app.models.claim import Claim, AnalyticsSummary, ClaimAnalysisResult


class AnalyticsService:
    """Service for generating analytics and reports on claims"""
    
    def __init__(self):
        self.claims_cache: List[Claim] = []
        self.analysis_cache: List[ClaimAnalysisResult] = []
    
    def generate_summary(
        self,
        claims: List[Claim],
        analysis_results: List[ClaimAnalysisResult] = None
    ) -> AnalyticsSummary:
        """Generate comprehensive analytics summary"""
        
        if not claims:
            return AnalyticsSummary(
                total_claims=0,
                total_claimed_amount=0.0,
                total_paid_amount=0.0,
                total_issues_found=0,
                estimated_overpayment=0.0,
                estimated_underpayment=0.0,
                fraud_alerts_count=0,
                average_risk_score=0.0,
                claims_by_status={},
                claims_by_type={}
            )
        
        # Calculate basic stats
        total_claims = len(claims)
        total_claimed = sum(c.claimed_amount for c in claims)
        total_paid = sum(c.paid_amount or 0 for c in claims)
        
        # Count claims by status
        status_counter = Counter(c.status.value for c in claims)
        claims_by_status = dict(status_counter)
        
        # Count claims by type
        type_counter = Counter(c.claim_type.value for c in claims)
        claims_by_type = dict(type_counter)
        
        # Analyze issues if results provided
        total_issues = 0
        estimated_overpayment = 0.0
        estimated_underpayment = 0.0
        total_risk_score = 0.0
        
        if analysis_results:
            for result in analysis_results:
                total_issues += len(result.issues)
                total_risk_score += result.risk_score
                
                for issue in result.issues:
                    if issue.issue_type == "overpayment":
                        estimated_overpayment += issue.estimated_impact
                    elif issue.issue_type == "underpayment":
                        estimated_underpayment += abs(issue.estimated_impact)
        
        avg_risk_score = total_risk_score / len(analysis_results) if analysis_results else 0.0
        
        return AnalyticsSummary(
            total_claims=total_claims,
            total_claimed_amount=total_claimed,
            total_paid_amount=total_paid,
            total_issues_found=total_issues,
            estimated_overpayment=estimated_overpayment,
            estimated_underpayment=estimated_underpayment,
            fraud_alerts_count=0,  # Will be updated by fraud service
            average_risk_score=avg_risk_score,
            claims_by_status=claims_by_status,
            claims_by_type=claims_by_type
        )
    
    def get_top_providers_by_amount(self, claims: List[Claim], limit: int = 10) -> List[Dict]:
        """Get top providers by total claimed amount"""
        provider_stats: Dict[str, float] = {}
        
        for claim in claims:
            if claim.provider_id not in provider_stats:
                provider_stats[claim.provider_id] = 0.0
            provider_stats[claim.provider_id] += claim.claimed_amount
        
        sorted_providers = sorted(
            provider_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {"provider_id": provider_id, "total_amount": amount}
            for provider_id, amount in sorted_providers
        ]
    
    def get_top_service_codes(self, claims: List[Claim], limit: int = 10) -> List[Dict]:
        """Get most frequently billed service codes"""
        code_counter: Counter = Counter()
        
        for claim in claims:
            for service in claim.services:
                code_counter[service.code] += service.units
        
        return [
            {"code": code, "count": count}
            for code, count in code_counter.most_common(limit)
        ]
    
    def calculate_payment_accuracy_rate(self, claims: List[Claim]) -> float:
        """Calculate percentage of claims paid correctly"""
        if not claims:
            return 0.0
        
        correct_payments = 0
        total_applicable = 0
        
        for claim in claims:
            if claim.paid_amount is not None and claim.allowed_amount is not None:
                total_applicable += 1
                if abs(claim.paid_amount - claim.allowed_amount) < 0.01:
                    correct_payments += 1
        
        if total_applicable == 0:
            return 0.0
        
        return (correct_payments / total_applicable) * 100.0
    
    def calculate_cost_efficiency(self, claims: List[Claim]) -> Dict:
        """Calculate cost efficiency metrics"""
        total_claimed = sum(c.claimed_amount for c in claims)
        total_paid = sum(c.paid_amount or 0 for c in claims)
        total_allowed = sum(c.allowed_amount or 0 for c in claims if c.allowed_amount)
        
        savings = total_claimed - total_paid
        savings_rate = (savings / total_claimed * 100) if total_claimed > 0 else 0.0
        
        return {
            "total_claimed": total_claimed,
            "total_paid": total_paid,
            "total_allowed": total_allowed,
            "total_savings": savings,
            "savings_rate_percent": savings_rate
        }
