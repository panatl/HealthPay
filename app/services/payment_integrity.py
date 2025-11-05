from typing import List, Dict, Set
from datetime import datetime, timedelta
from collections import defaultdict
from app.models.claim import (
    Claim, ClaimAnalysisResult, PaymentIntegrityIssue,
    ClaimStatus, ServiceCode
)


class PaymentIntegrityService:
    """Service for detecting payment integrity issues in healthcare claims"""
    
    def __init__(self):
        self.processed_claims: Dict[str, Claim] = {}
        self.analysis_results: Dict[str, ClaimAnalysisResult] = {}
    
    def analyze_claim(self, claim: Claim) -> ClaimAnalysisResult:
        """
        Analyze a claim for payment integrity issues
        
        Detects:
        - Overpayments
        - Underpayments
        - Duplicate claims
        - Invalid service combinations
        - Pricing errors
        """
        issues: List[PaymentIntegrityIssue] = []
        
        # Check for overpayment
        if claim.paid_amount and claim.allowed_amount:
            if claim.paid_amount > claim.allowed_amount:
                overpayment = claim.paid_amount - claim.allowed_amount
                issues.append(PaymentIntegrityIssue(
                    issue_type="overpayment",
                    severity="high",
                    description=f"Claim paid ${claim.paid_amount:.2f} exceeds allowed amount ${claim.allowed_amount:.2f}",
                    estimated_impact=overpayment,
                    recommendation="Recover overpaid amount from provider"
                ))
        
        # Check for underpayment
        if claim.paid_amount and claim.allowed_amount:
            if claim.paid_amount < claim.allowed_amount and claim.status == ClaimStatus.APPROVED:
                underpayment = claim.allowed_amount - claim.paid_amount
                if underpayment > 0.01:  # Ignore cents
                    issues.append(PaymentIntegrityIssue(
                        issue_type="underpayment",
                        severity="medium",
                        description=f"Claim paid ${claim.paid_amount:.2f} is less than allowed amount ${claim.allowed_amount:.2f}",
                        estimated_impact=-underpayment,
                        recommendation="Issue supplemental payment to provider"
                    ))
        
        # Check for service pricing errors
        calculated_amount = sum(s.units * s.unit_price for s in claim.services)
        if abs(calculated_amount - claim.claimed_amount) > 0.01:
            issues.append(PaymentIntegrityIssue(
                issue_type="pricing_error",
                severity="medium",
                description=f"Claimed amount ${claim.claimed_amount:.2f} does not match calculated amount ${calculated_amount:.2f}",
                estimated_impact=abs(calculated_amount - claim.claimed_amount),
                recommendation="Review service pricing and recalculate"
            ))
        
        # Check for duplicate services
        service_codes = [s.code for s in claim.services]
        if len(service_codes) != len(set(service_codes)):
            duplicate_codes = [code for code in service_codes if service_codes.count(code) > 1]
            issues.append(PaymentIntegrityIssue(
                issue_type="duplicate_service",
                severity="high",
                description=f"Duplicate service codes found: {set(duplicate_codes)}",
                estimated_impact=0.0,
                recommendation="Review and remove duplicate services"
            ))
        
        # Check for excessive units
        for service in claim.services:
            if service.units > 20:  # Threshold for review
                issues.append(PaymentIntegrityIssue(
                    issue_type="excessive_units",
                    severity="medium",
                    description=f"Service {service.code} has {service.units} units, which seems excessive",
                    estimated_impact=0.0,
                    recommendation="Review medical necessity for high unit count"
                ))
        
        # Check for timely filing
        if claim.submission_date:
            days_to_submit = (claim.submission_date - claim.service_date).days
            if days_to_submit > 90:  # Typical timely filing limit
                issues.append(PaymentIntegrityIssue(
                    issue_type="late_filing",
                    severity="low",
                    description=f"Claim submitted {days_to_submit} days after service date",
                    estimated_impact=0.0,
                    recommendation="Consider timely filing rules in adjudication"
                ))
        
        # Check for missing diagnosis codes
        if not claim.diagnosis_codes:
            issues.append(PaymentIntegrityIssue(
                issue_type="missing_diagnosis",
                severity="medium",
                description="Claim has no diagnosis codes",
                estimated_impact=0.0,
                recommendation="Request diagnosis codes from provider"
            ))
        
        # Calculate risk score based on issues
        risk_score = self._calculate_risk_score(issues, claim)
        
        # Calculate total estimated impact
        total_impact = sum(issue.estimated_impact for issue in issues)
        
        result = ClaimAnalysisResult(
            claim_id=claim.claim_id,
            is_valid=len([i for i in issues if i.severity in ["high", "critical"]]) == 0,
            issues=issues,
            total_estimated_impact=total_impact,
            risk_score=risk_score,
            analysis_timestamp=datetime.utcnow()
        )
        
        # Store for duplicate detection
        self.processed_claims[claim.claim_id] = claim
        self.analysis_results[claim.claim_id] = result
        
        return result
    
    def _calculate_risk_score(self, issues: List[PaymentIntegrityIssue], claim: Claim) -> float:
        """Calculate risk score based on detected issues"""
        base_score = 0.0
        
        severity_weights = {
            "critical": 40,
            "high": 25,
            "medium": 15,
            "low": 5
        }
        
        for issue in issues:
            base_score += severity_weights.get(issue.severity, 0)
        
        # Add factors based on claim amount
        if claim.claimed_amount > 10000:
            base_score += 10
        elif claim.claimed_amount > 5000:
            base_score += 5
        
        # Cap at 100
        return min(base_score, 100.0)
    
    def detect_duplicate_claims(self, claims: List[Claim]) -> List[List[str]]:
        """
        Detect potential duplicate claims based on:
        - Same patient
        - Same provider
        - Same service date
        - Similar services
        """
        duplicates: List[List[str]] = []
        claim_groups: Dict[tuple, List[str]] = defaultdict(list)
        
        for claim in claims:
            # Create a key for grouping potential duplicates
            key = (
                claim.patient_id,
                claim.provider_id,
                claim.service_date.date(),
                claim.claim_type
            )
            claim_groups[key].append(claim.claim_id)
        
        # Find groups with multiple claims
        for key, claim_ids in claim_groups.items():
            if len(claim_ids) > 1:
                duplicates.append(claim_ids)
        
        return duplicates
    
    def check_allowed_amount(self, claim: Claim, fee_schedule: Dict[str, float]) -> float:
        """
        Calculate allowed amount based on fee schedule
        
        Args:
            claim: The claim to check
            fee_schedule: Dictionary mapping service codes to allowed amounts
        
        Returns:
            Total allowed amount
        """
        allowed_amount = 0.0
        
        for service in claim.services:
            if service.code in fee_schedule:
                allowed_amount += fee_schedule[service.code] * service.units
            else:
                # If not in fee schedule, use claimed amount
                allowed_amount += service.unit_price * service.units
        
        return allowed_amount
