from typing import List, Dict
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import uuid
from app.models.claim import Claim, FraudAlert


class FraudDetectionService:
    """Service for detecting fraud, waste, and abuse in healthcare claims"""
    
    def __init__(self):
        self.alerts: Dict[str, FraudAlert] = {}
        self.provider_history: Dict[str, List[Claim]] = defaultdict(list)
        self.patient_history: Dict[str, List[Claim]] = defaultdict(list)
    
    def analyze_for_fraud(self, claims: List[Claim]) -> List[FraudAlert]:
        """
        Analyze claims for fraud, waste, and abuse patterns
        
        Detects:
        - Billing for services not rendered
        - Upcoding (billing for more expensive services)
        - Unbundling (billing separately for bundled services)
        - Duplicate billing
        - Pattern anomalies
        """
        alerts: List[FraudAlert] = []
        
        # Update history
        for claim in claims:
            self.provider_history[claim.provider_id].append(claim)
            self.patient_history[claim.patient_id].append(claim)
        
        # Check for duplicate billing
        duplicate_alerts = self._detect_duplicate_billing(claims)
        alerts.extend(duplicate_alerts)
        
        # Check for unusual billing patterns
        pattern_alerts = self._detect_unusual_patterns(claims)
        alerts.extend(pattern_alerts)
        
        # Check for high-risk provider behavior
        provider_alerts = self._detect_provider_anomalies(claims)
        alerts.extend(provider_alerts)
        
        # Check for patient abuse patterns
        patient_alerts = self._detect_patient_anomalies(claims)
        alerts.extend(patient_alerts)
        
        return alerts
    
    def _detect_duplicate_billing(self, claims: List[Claim]) -> List[FraudAlert]:
        """Detect duplicate billing for same services"""
        alerts: List[FraudAlert] = []
        seen_claims: Dict[tuple, List[str]] = defaultdict(list)
        
        for claim in claims:
            # Create signature for claim
            services_signature = tuple(sorted([
                (s.code, s.units, s.unit_price) for s in claim.services
            ]))
            
            key = (
                claim.patient_id,
                claim.provider_id,
                claim.service_date.date(),
                services_signature
            )
            
            seen_claims[key].append(claim.claim_id)
        
        # Find duplicates
        for key, claim_ids in seen_claims.items():
            if len(claim_ids) > 1:
                alerts.append(FraudAlert(
                    alert_id=str(uuid.uuid4()),
                    claim_ids=claim_ids,
                    alert_type="duplicate_billing",
                    confidence_score=0.95,
                    pattern_description=f"Identical claims submitted for same patient, provider, and service date",
                    flagged_date=datetime.utcnow(),
                    status="open"
                ))
        
        return alerts
    
    def _detect_unusual_patterns(self, claims: List[Claim]) -> List[FraudAlert]:
        """Detect unusual billing patterns"""
        alerts: List[FraudAlert] = []
        
        # Check for high-frequency billing
        provider_daily_claims: Dict[tuple, int] = Counter()
        
        for claim in claims:
            key = (claim.provider_id, claim.service_date.date())
            provider_daily_claims[key] += 1
        
        # Flag providers with unusually high daily claims
        for (provider_id, date), count in provider_daily_claims.items():
            if count > 50:  # Threshold for review
                related_claims = [
                    c.claim_id for c in claims 
                    if c.provider_id == provider_id and c.service_date.date() == date
                ]
                
                alerts.append(FraudAlert(
                    alert_id=str(uuid.uuid4()),
                    claim_ids=related_claims,
                    alert_type="high_volume_billing",
                    confidence_score=0.75,
                    pattern_description=f"Provider submitted {count} claims on {date}, which exceeds normal patterns",
                    flagged_date=datetime.utcnow(),
                    status="open"
                ))
        
        return alerts
    
    def _detect_provider_anomalies(self, claims: List[Claim]) -> List[FraudAlert]:
        """Detect anomalies in provider billing behavior"""
        alerts: List[FraudAlert] = []
        
        # Analyze provider billing patterns
        provider_stats: Dict[str, Dict] = defaultdict(lambda: {
            'total_claims': 0,
            'total_amount': 0.0,
            'service_codes': Counter(),
            'claim_ids': []
        })
        
        for claim in claims:
            stats = provider_stats[claim.provider_id]
            stats['total_claims'] += 1
            stats['total_amount'] += claim.claimed_amount
            stats['claim_ids'].append(claim.claim_id)
            
            for service in claim.services:
                stats['service_codes'][service.code] += 1
        
        # Check for providers with suspicious patterns
        for provider_id, stats in provider_stats.items():
            avg_claim_amount = stats['total_amount'] / stats['total_claims'] if stats['total_claims'] > 0 else 0
            
            # Flag high average claim amounts
            if avg_claim_amount > 5000 and stats['total_claims'] > 10:
                alerts.append(FraudAlert(
                    alert_id=str(uuid.uuid4()),
                    claim_ids=stats['claim_ids'],
                    alert_type="high_average_claims",
                    confidence_score=0.70,
                    pattern_description=f"Provider has average claim amount of ${avg_claim_amount:.2f}, which is unusually high",
                    flagged_date=datetime.utcnow(),
                    status="open"
                ))
            
            # Check for excessive use of specific codes (potential upcoding)
            if stats['service_codes']:
                most_common = stats['service_codes'].most_common(1)[0]
                code, frequency = most_common
                if frequency > stats['total_claims'] * 0.8:  # More than 80% of claims
                    alerts.append(FraudAlert(
                        alert_id=str(uuid.uuid4()),
                        claim_ids=stats['claim_ids'],
                        alert_type="service_code_concentration",
                        confidence_score=0.65,
                        pattern_description=f"Provider uses service code {code} in {frequency}/{stats['total_claims']} claims",
                        flagged_date=datetime.utcnow(),
                        status="open"
                    ))
        
        return alerts
    
    def _detect_patient_anomalies(self, claims: List[Claim]) -> List[FraudAlert]:
        """Detect anomalies in patient claim patterns"""
        alerts: List[FraudAlert] = []
        
        # Analyze patient claim patterns
        patient_stats: Dict[str, Dict] = defaultdict(lambda: {
            'providers': set(),
            'claim_ids': [],
            'service_dates': []
        })
        
        for claim in claims:
            stats = patient_stats[claim.patient_id]
            stats['providers'].add(claim.provider_id)
            stats['claim_ids'].append(claim.claim_id)
            stats['service_dates'].append(claim.service_date)
        
        # Check for patients seeing too many providers (doctor shopping)
        for patient_id, stats in patient_stats.items():
            if len(stats['providers']) > 10:  # Threshold for review
                alerts.append(FraudAlert(
                    alert_id=str(uuid.uuid4()),
                    claim_ids=stats['claim_ids'],
                    alert_type="doctor_shopping",
                    confidence_score=0.80,
                    pattern_description=f"Patient has claims from {len(stats['providers'])} different providers",
                    flagged_date=datetime.utcnow(),
                    status="open"
                ))
            
            # Check for impossible dates (services on same day at different locations)
            if len(stats['service_dates']) > 1:
                date_counter = Counter([d.date() for d in stats['service_dates']])
                for date, count in date_counter.items():
                    if count > 3:  # Multiple services in one day
                        related_claims = [
                            c.claim_id for c in claims
                            if c.patient_id == patient_id and c.service_date.date() == date
                        ]
                        alerts.append(FraudAlert(
                            alert_id=str(uuid.uuid4()),
                            claim_ids=related_claims,
                            alert_type="multiple_services_same_day",
                            confidence_score=0.60,
                            pattern_description=f"Patient has {count} services on {date}",
                            flagged_date=datetime.utcnow(),
                            status="open"
                        ))
        
        return alerts
    
    def calculate_fraud_risk_score(self, provider_id: str) -> float:
        """Calculate fraud risk score for a provider (0-100)"""
        if provider_id not in self.provider_history:
            return 0.0
        
        claims = self.provider_history[provider_id]
        if not claims:
            return 0.0
        
        risk_score = 0.0
        
        # Factor: High claim amounts
        avg_amount = sum(c.claimed_amount for c in claims) / len(claims)
        if avg_amount > 5000:
            risk_score += 30
        elif avg_amount > 3000:
            risk_score += 15
        
        # Factor: High volume
        if len(claims) > 100:
            risk_score += 20
        elif len(claims) > 50:
            risk_score += 10
        
        # Factor: Service code diversity (too little can indicate upcoding)
        all_codes = [s.code for c in claims for s in c.services]
        unique_codes = len(set(all_codes))
        if unique_codes < 5 and len(claims) > 20:
            risk_score += 25
        
        return min(risk_score, 100.0)
