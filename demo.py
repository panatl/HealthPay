#!/usr/bin/env python3
"""
Example script demonstrating the HealthPay Payment Integrity Platform usage
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"


def test_payment_integrity():
    """Test payment integrity analysis"""
    print("=" * 60)
    print("Testing Payment Integrity Analysis")
    print("=" * 60)
    
    # Create a sample claim with overpayment
    service_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
    submission_date = datetime.utcnow().isoformat()
    
    claim = {
        "claim_id": "DEMO_CLM001",
        "patient_id": "PAT12345",
        "provider_id": "PRV67890",
        "claim_type": "outpatient",
        "service_date": service_date,
        "submission_date": submission_date,
        "services": [
            {
                "code": "99213",
                "description": "Office visit - established patient",
                "units": 1,
                "unit_price": 150.00
            }
        ],
        "claimed_amount": 150.00,
        "allowed_amount": 100.00,
        "paid_amount": 150.00,  # Overpayment!
        "status": "approved",
        "diagnosis_codes": ["I10", "E11.9"]
    }
    
    response = requests.post(f"{BASE_URL}/claims/analyze", json=claim)
    result = response.json()
    
    print(f"\nClaim ID: {result['claim_id']}")
    print(f"Valid: {result['is_valid']}")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Total Issues: {len(result['issues'])}")
    print(f"Estimated Impact: ${result['total_estimated_impact']:.2f}")
    
    print("\nIssues Found:")
    for issue in result['issues']:
        print(f"  - {issue['issue_type'].upper()} ({issue['severity']})")
        print(f"    {issue['description']}")
        print(f"    Impact: ${issue['estimated_impact']:.2f}")
        print(f"    Recommendation: {issue['recommendation']}")
    
    return result


def test_fraud_detection():
    """Test fraud detection"""
    print("\n" + "=" * 60)
    print("Testing Fraud Detection")
    print("=" * 60)
    
    # Create multiple claims to test fraud patterns
    service_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
    submission_date = datetime.utcnow().isoformat()
    
    claims = []
    for i in range(5):
        claim = {
            "claim_id": f"DEMO_FRAUD{i:03d}",
            "patient_id": "PAT_SHOPPER",  # Same patient
            "provider_id": f"PRV{i:03d}",  # Different providers
            "claim_type": "pharmacy",
            "service_date": service_date,
            "submission_date": submission_date,
            "services": [
                {
                    "code": "J2001",
                    "description": "Medication",
                    "units": 1,
                    "unit_price": 150.00
                }
            ],
            "claimed_amount": 150.00,
            "diagnosis_codes": ["M79.3"]
        }
        claims.append(claim)
    
    response = requests.post(f"{BASE_URL}/fraud/analyze", json=claims)
    alerts = response.json()
    
    print(f"\nTotal Fraud Alerts: {len(alerts)}")
    for alert in alerts:
        print(f"\n  Alert Type: {alert['alert_type']}")
        print(f"  Confidence: {alert['confidence_score']:.2%}")
        print(f"  Pattern: {alert['pattern_description']}")
        print(f"  Status: {alert['status']}")
        print(f"  Claims Involved: {len(alert['claim_ids'])}")


def test_analytics():
    """Test analytics generation"""
    print("\n" + "=" * 60)
    print("Testing Analytics & Reporting")
    print("=" * 60)
    
    # Create sample claims for analytics
    service_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
    submission_date = datetime.utcnow().isoformat()
    
    claims = []
    for i in range(10):
        claim = {
            "claim_id": f"DEMO_ANALYTICS{i:03d}",
            "patient_id": f"PAT{i:03d}",
            "provider_id": f"PRV{i % 3:03d}",  # 3 providers
            "claim_type": "outpatient" if i % 2 == 0 else "inpatient",
            "service_date": service_date,
            "submission_date": submission_date,
            "services": [
                {
                    "code": "99213",
                    "description": "Office visit",
                    "units": 1,
                    "unit_price": 150.00 + (i * 10)
                }
            ],
            "claimed_amount": 150.00 + (i * 10),
            "allowed_amount": 150.00 + (i * 10),
            "paid_amount": 150.00 + (i * 10),
            "status": "approved" if i < 8 else "rejected",
            "diagnosis_codes": ["I10"]
        }
        claims.append(claim)
    
    response = requests.post(f"{BASE_URL}/analytics/summary", json=claims)
    summary = response.json()
    
    print(f"\nTotal Claims: {summary['total_claims']}")
    print(f"Total Claimed: ${summary['total_claimed_amount']:.2f}")
    print(f"Total Paid: ${summary['total_paid_amount']:.2f}")
    print(f"Average Risk Score: {summary['average_risk_score']:.2f}")
    
    print("\nClaims by Status:")
    for status, count in summary['claims_by_status'].items():
        print(f"  {status}: {count}")
    
    print("\nClaims by Type:")
    for claim_type, count in summary['claims_by_type'].items():
        print(f"  {claim_type}: {count}")
    
    # Get top providers
    response = requests.post(f"{BASE_URL}/analytics/top-providers", json=claims, params={"limit": 3})
    top_providers = response.json()
    
    print("\nTop Providers by Amount:")
    for provider in top_providers:
        print(f"  {provider['provider_id']}: ${provider['total_amount']:.2f}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("HealthPay Payment Integrity Platform - Demo")
    print("=" * 60)
    print("\nMake sure the server is running:")
    print("  python -m uvicorn app.main:app --reload")
    print()
    
    try:
        # Test health
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        health_data = response.json()
        print(f"Server Status: {health_data.get('status', 'unknown')}")
        
        # Run tests
        test_payment_integrity()
        test_fraud_detection()
        test_analytics()
        
        print("\n" + "=" * 60)
        print("All Demo Tests Completed Successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server.")
        print("Please start the server first with:")
        print("  python -m uvicorn app.main:app --reload")
    except requests.exceptions.Timeout:
        print("\nError: Server health check timed out.")
        print("Please ensure the server is running properly.")
    except requests.exceptions.RequestException as e:
        print(f"\nError: Failed to connect to server: {e}")
        print("Please ensure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\nError: {e}")
