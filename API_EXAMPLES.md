# HealthPay API Examples

This document provides comprehensive examples for using the HealthPay Payment Integrity Platform API.

## Table of Contents
- [Authentication](#authentication)
- [Payment Integrity](#payment-integrity)
- [Fraud Detection](#fraud-detection)
- [Analytics](#analytics)
- [Error Handling](#error-handling)

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication. This should be implemented for production use.

## Payment Integrity

### Analyze a Single Claim

Analyze a claim for payment integrity issues including overpayments, underpayments, and errors.

**Endpoint:** `POST /claims/analyze`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/claims/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "CLM001",
    "patient_id": "PAT12345",
    "provider_id": "PRV67890",
    "claim_type": "outpatient",
    "service_date": "2024-01-15T10:00:00Z",
    "submission_date": "2024-01-20T10:00:00Z",
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
    "paid_amount": 150.00,
    "status": "approved",
    "diagnosis_codes": ["I10", "E11.9"]
  }'
```

**Example Response:**
```json
{
  "claim_id": "CLM001",
  "is_valid": false,
  "issues": [
    {
      "issue_type": "overpayment",
      "severity": "high",
      "description": "Claim paid $150.00 exceeds allowed amount $100.00",
      "estimated_impact": 50.00,
      "recommendation": "Recover overpaid amount from provider"
    }
  ],
  "total_estimated_impact": 50.00,
  "risk_score": 25.0,
  "analysis_timestamp": "2024-01-21T10:00:00Z"
}
```

### Batch Analyze Claims

Analyze multiple claims at once.

**Endpoint:** `POST /claims/batch-analyze`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/claims/batch-analyze" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "claim_id": "CLM001",
      "patient_id": "PAT001",
      ...
    },
    {
      "claim_id": "CLM002",
      "patient_id": "PAT002",
      ...
    }
  ]'
```

### Check for Duplicate Claims

Detect duplicate claims across submissions.

**Endpoint:** `POST /claims/check-duplicates`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/claims/check-duplicates" \
  -H "Content-Type: application/json" \
  -d '[...]'
```

**Example Response:**
```json
{
  "duplicate_groups": [
    ["CLM001", "CLM002"],
    ["CLM005", "CLM006", "CLM007"]
  ],
  "total_duplicate_groups": 2,
  "total_claims_checked": 10
}
```

### Calculate Allowed Amount

Calculate the allowed amount for a claim based on a fee schedule.

**Endpoint:** `POST /claims/calculate-allowed`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/claims/calculate-allowed" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": {
      "claim_id": "CLM001",
      "services": [
        {
          "code": "99213",
          "description": "Office visit",
          "units": 1,
          "unit_price": 150.00
        }
      ],
      ...
    },
    "fee_schedule": {
      "99213": 120.00,
      "99214": 180.00
    }
  }'
```

**Example Response:**
```json
{
  "claim_id": "CLM001",
  "claimed_amount": 150.00,
  "calculated_allowed_amount": 120.00,
  "difference": 30.00
}
```

## Fraud Detection

### Analyze Claims for Fraud

Detect fraud, waste, and abuse patterns in claims.

**Endpoint:** `POST /fraud/analyze`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/fraud/analyze" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "claim_id": "CLM001",
      "patient_id": "PAT001",
      ...
    },
    ...
  ]'
```

**Example Response:**
```json
[
  {
    "alert_id": "ALERT-123",
    "claim_ids": ["CLM001", "CLM002"],
    "alert_type": "duplicate_billing",
    "confidence_score": 0.95,
    "pattern_description": "Identical claims submitted for same patient, provider, and service date",
    "flagged_date": "2024-01-21T10:00:00Z",
    "status": "open"
  },
  {
    "alert_id": "ALERT-124",
    "claim_ids": ["CLM010", "CLM011", "..."],
    "alert_type": "high_volume_billing",
    "confidence_score": 0.75,
    "pattern_description": "Provider submitted 60 claims on 2024-01-15, which exceeds normal patterns",
    "flagged_date": "2024-01-21T10:00:00Z",
    "status": "open"
  }
]
```

### Get Provider Risk Score

Calculate fraud risk score for a specific provider.

**Endpoint:** `GET /fraud/provider-risk/{provider_id}`

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/fraud/provider-risk/PRV001"
```

**Example Response:**
```json
{
  "provider_id": "PRV001",
  "risk_score": 45.0,
  "risk_level": "medium"
}
```

### Get Fraud Alerts

Retrieve all fraud alerts, optionally filtered by status.

**Endpoint:** `GET /fraud/alerts?status=open`

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/fraud/alerts?status=open"
```

## Analytics

### Generate Analytics Summary

Generate comprehensive analytics for claims.

**Endpoint:** `POST /analytics/summary`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/summary" \
  -H "Content-Type: application/json" \
  -d '[...]'
```

**Example Response:**
```json
{
  "total_claims": 100,
  "total_claimed_amount": 50000.00,
  "total_paid_amount": 45000.00,
  "total_issues_found": 15,
  "estimated_overpayment": 2500.00,
  "estimated_underpayment": 1000.00,
  "fraud_alerts_count": 3,
  "average_risk_score": 25.5,
  "claims_by_status": {
    "approved": 85,
    "rejected": 10,
    "pending": 5
  },
  "claims_by_type": {
    "outpatient": 60,
    "inpatient": 30,
    "pharmacy": 10
  }
}
```

### Get Top Providers

Get top providers by total claimed amount.

**Endpoint:** `POST /analytics/top-providers?limit=10`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/top-providers?limit=10" \
  -H "Content-Type: application/json" \
  -d '[...]'
```

**Example Response:**
```json
[
  {
    "provider_id": "PRV001",
    "total_amount": 15000.00
  },
  {
    "provider_id": "PRV002",
    "total_amount": 12500.00
  }
]
```

### Get Top Service Codes

Get most frequently billed service codes.

**Endpoint:** `POST /analytics/top-services?limit=10`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/top-services?limit=10" \
  -H "Content-Type: application/json" \
  -d '[...]'
```

**Example Response:**
```json
[
  {
    "code": "99213",
    "count": 150
  },
  {
    "code": "99214",
    "count": 85
  }
]
```

### Calculate Payment Accuracy

Calculate the percentage of claims paid correctly.

**Endpoint:** `POST /analytics/payment-accuracy`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/payment-accuracy" \
  -H "Content-Type: application/json" \
  -d '[...]'
```

**Example Response:**
```json
{
  "payment_accuracy_rate": 92.5,
  "total_claims_evaluated": 100
}
```

### Calculate Cost Efficiency

Calculate cost efficiency metrics.

**Endpoint:** `POST /analytics/cost-efficiency`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/cost-efficiency" \
  -H "Content-Type: application/json" \
  -d '[...]'
```

**Example Response:**
```json
{
  "total_claimed": 50000.00,
  "total_paid": 45000.00,
  "total_allowed": 47000.00,
  "total_savings": 5000.00,
  "savings_rate_percent": 10.0
}
```

## Error Handling

All API endpoints return standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Interactive Documentation

For interactive API documentation, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Analyze a claim
claim = {
    "claim_id": "CLM001",
    "patient_id": "PAT001",
    # ... other claim data
}

response = requests.post(f"{BASE_URL}/claims/analyze", json=claim)
result = response.json()

print(f"Risk Score: {result['risk_score']}")
print(f"Issues Found: {len(result['issues'])}")
```

## JavaScript Client Example

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

async function analyzeClaim(claim) {
  const response = await fetch(`${BASE_URL}/claims/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(claim),
  });
  
  const result = await response.json();
  console.log('Risk Score:', result.risk_score);
  console.log('Issues Found:', result.issues.length);
}
```
