# HealthPay GraphQL API Examples

This document provides comprehensive examples for using the HealthPay Platform GraphQL API through Apollo Gateway.

## Base URL

```
http://localhost:4000/graphql
```

## Payment Integrity Examples

### 1. Analyze a Single Claim

Analyze a claim for payment integrity issues including overpayments and underpayments.

```graphql
mutation AnalyzeClaim {
  analyzeClaim(input: {
    claimId: "CLM001"
    patientId: "PAT12345"
    providerId: "PRV67890"
    claimType: OUTPATIENT
    serviceDate: "2024-01-15T10:00:00Z"
    submissionDate: "2024-01-20T10:00:00Z"
    services: [{
      code: "99213"
      description: "Office visit - established patient"
      units: 1
      unitPrice: 150.00
    }]
    claimedAmount: 150.00
    allowedAmount: 100.00
    paidAmount: 150.00
    status: APPROVED
    diagnosisCodes: ["I10", "E11.9"]
  }) {
    claimId
    isValid
    riskScore
    totalEstimatedImpact
    analysisTimestamp
    issues {
      issueType
      severity
      description
      estimatedImpact
      recommendation
    }
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "analyzeClaim": {
      "claimId": "CLM001",
      "isValid": false,
      "riskScore": 25.0,
      "totalEstimatedImpact": 50.0,
      "analysisTimestamp": "2024-01-21T10:00:00Z",
      "issues": [
        {
          "issueType": "overpayment",
          "severity": "HIGH",
          "description": "Claim paid $150.00 exceeds allowed amount $100.00",
          "estimatedImpact": 50.0,
          "recommendation": "Recover overpaid amount from provider"
        }
      ]
    }
  }
}
```

### 2. Batch Analyze Claims

```graphql
query BatchAnalyze {
  batchAnalyzeClaims(inputs: [
    {
      claimId: "CLM001"
      patientId: "PAT001"
      providerId: "PRV001"
      claimType: OUTPATIENT
      serviceDate: "2024-01-15T10:00:00Z"
      submissionDate: "2024-01-20T10:00:00Z"
      services: [{code: "99213", description: "Office visit", units: 1, unitPrice: 150.00}]
      claimedAmount: 150.00
      diagnosisCodes: ["I10"]
    },
    {
      claimId: "CLM002"
      patientId: "PAT002"
      providerId: "PRV002"
      claimType: INPATIENT
      serviceDate: "2024-01-16T10:00:00Z"
      submissionDate: "2024-01-21T10:00:00Z"
      services: [{code: "99285", description: "Emergency visit", units: 1, unitPrice: 500.00}]
      claimedAmount: 500.00
      diagnosisCodes: ["I10"]
    }
  ]) {
    claimId
    isValid
    riskScore
    totalEstimatedImpact
  }
}
```

### 3. Submit a New Claim

```graphql
mutation SubmitClaim {
  submitClaim(input: {
    claimId: "CLM003"
    patientId: "PAT003"
    providerId: "PRV003"
    claimType: PROFESSIONAL
    serviceDate: "2024-01-22T10:00:00Z"
    submissionDate: "2024-01-23T10:00:00Z"
    services: [{
      code: "99214"
      description: "Complex office visit"
      units: 1
      unitPrice: 200.00
    }]
    claimedAmount: 200.00
    status: PENDING
    diagnosisCodes: ["J06.9"]
  }) {
    claimId
    status
    claimedAmount
  }
}
```

### 4. Get Claim by ID

```graphql
query GetClaim {
  getClaim(claimId: "CLM001") {
    claimId
    patientId
    providerId
    claimType
    serviceDate
    services {
      code
      description
      units
      unitPrice
    }
    claimedAmount
    status
  }
}
```

## Fraud Detection Examples

### 1. Analyze for Fraud Patterns

```graphql
query AnalyzeFraud {
  analyzeFraud(claims: [
    {
      claimId: "CLM001"
      patientId: "PAT_SHOPPER"
      providerId: "PRV001"
      claimType: PHARMACY
      serviceDate: "2024-01-15T10:00:00Z"
      submissionDate: "2024-01-20T10:00:00Z"
      services: [{code: "J2001", description: "Medication", units: 1, unitPrice: 150.00}]
      claimedAmount: 150.00
      diagnosisCodes: ["M79.3"]
    },
    {
      claimId: "CLM002"
      patientId: "PAT_SHOPPER"
      providerId: "PRV002"
      claimType: PHARMACY
      serviceDate: "2024-01-15T10:00:00Z"
      submissionDate: "2024-01-20T10:00:00Z"
      services: [{code: "J2001", description: "Medication", units: 1, unitPrice: 150.00}]
      claimedAmount: 150.00
      diagnosisCodes: ["M79.3"]
    }
  ]) {
    alertId
    alertType
    confidenceScore
    patternDescription
    status
    claimIds
    flaggedDate
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "analyzeFraud": [
      {
        "alertId": "ALERT-12345",
        "alertType": "DOCTOR_SHOPPING",
        "confidenceScore": 0.80,
        "patternDescription": "Patient has claims from multiple providers",
        "status": "OPEN",
        "claimIds": ["CLM001", "CLM002"],
        "flaggedDate": "2024-01-21T10:00:00Z"
      }
    ]
  }
}
```

### 2. Get Provider Risk Score

```graphql
query GetProviderRisk {
  getProviderRiskScore(providerId: "PRV001") {
    providerId
    riskScore
    riskLevel
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "getProviderRiskScore": {
      "providerId": "PRV001",
      "riskScore": 45.0,
      "riskLevel": "MEDIUM"
    }
  }
}
```

### 3. Get Fraud Alerts by Status

```graphql
query GetFraudAlerts {
  getFraudAlerts(status: "OPEN") {
    alertId
    alertType
    confidenceScore
    patternDescription
    claimIds
    status
  }
}
```

## Analytics Examples

### 1. Generate Analytics Summary

```graphql
query GetAnalyticsSummary {
  getAnalyticsSummary(claims: [
    {
      claimId: "CLM001"
      patientId: "PAT001"
      providerId: "PRV001"
      claimType: OUTPATIENT
      claimedAmount: 150.00
      allowedAmount: 150.00
      paidAmount: 150.00
      status: APPROVED
    },
    {
      claimId: "CLM002"
      patientId: "PAT002"
      providerId: "PRV002"
      claimType: INPATIENT
      claimedAmount: 500.00
      allowedAmount: 450.00
      paidAmount: 450.00
      status: APPROVED
    },
    {
      claimId: "CLM003"
      patientId: "PAT003"
      providerId: "PRV001"
      claimType: OUTPATIENT
      claimedAmount: 200.00
      status: REJECTED
    }
  ]) {
    totalClaims
    totalClaimedAmount
    totalPaidAmount
    averageRiskScore
    claimsByStatus {
      status
      count
    }
    claimsByType {
      claimType
      count
    }
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "getAnalyticsSummary": {
      "totalClaims": 3,
      "totalClaimedAmount": 850.0,
      "totalPaidAmount": 600.0,
      "averageRiskScore": 12.5,
      "claimsByStatus": [
        {"status": "APPROVED", "count": 2},
        {"status": "REJECTED", "count": 1}
      ],
      "claimsByType": [
        {"claimType": "OUTPATIENT", "count": 2},
        {"claimType": "INPATIENT", "count": 1}
      ]
    }
  }
}
```

### 2. Get Top Providers

```graphql
query GetTopProviders {
  getTopProviders(
    claims: [
      {claimId: "CLM001", patientId: "PAT001", providerId: "PRV001", claimType: OUTPATIENT, claimedAmount: 150.00}
      {claimId: "CLM002", patientId: "PAT002", providerId: "PRV002", claimType: INPATIENT, claimedAmount: 500.00}
      {claimId: "CLM003", patientId: "PAT003", providerId: "PRV001", claimType: OUTPATIENT, claimedAmount: 200.00}
    ]
    limit: 2
  ) {
    providerId
    totalAmount
    claimCount
  }
}
```

### 3. Calculate Payment Accuracy

```graphql
query GetPaymentAccuracy {
  getPaymentAccuracy(claims: [
    {
      claimId: "CLM001"
      patientId: "PAT001"
      providerId: "PRV001"
      claimType: OUTPATIENT
      claimedAmount: 150.00
      allowedAmount: 150.00
      paidAmount: 150.00
      status: APPROVED
    }
  ]) {
    paymentAccuracyRate
    totalClaimsEvaluated
  }
}
```

### 4. Calculate Cost Efficiency

```graphql
query GetCostEfficiency {
  getCostEfficiency(claims: [
    {
      claimId: "CLM001"
      patientId: "PAT001"
      providerId: "PRV001"
      claimType: OUTPATIENT
      claimedAmount: 150.00
      allowedAmount: 150.00
      paidAmount: 150.00
    },
    {
      claimId: "CLM002"
      patientId: "PAT002"
      providerId: "PRV002"
      claimType: INPATIENT
      claimedAmount: 500.00
      allowedAmount: 450.00
      paidAmount: 450.00
    }
  ]) {
    totalClaimed
    totalPaid
    totalAllowed
    totalSavings
    savingsRatePercent
  }
}
```

## Federated Query Example

Query spanning multiple services:

```graphql
query CompleteClaimAnalysis {
  # From Claims Service
  analyzeClaim(input: {
    claimId: "CLM001"
    patientId: "PAT001"
    providerId: "PRV001"
    claimType: OUTPATIENT
    serviceDate: "2024-01-15T10:00:00Z"
    submissionDate: "2024-01-20T10:00:00Z"
    services: [{code: "99213", description: "Office visit", units: 1, unitPrice: 150.00}]
    claimedAmount: 150.00
    diagnosisCodes: ["I10"]
  }) {
    claimId
    isValid
    riskScore
    issues {
      issueType
      severity
    }
  }
  
  # From Fraud Detection Service
  getProviderRiskScore(providerId: "PRV001") {
    providerId
    riskScore
    riskLevel
  }
  
  # From Analytics Service
  getAnalyticsSummary(claims: [{
    claimId: "CLM001"
    patientId: "PAT001"
    providerId: "PRV001"
    claimType: OUTPATIENT
    claimedAmount: 150.00
  }]) {
    totalClaims
    totalClaimedAmount
  }
}
```

## Testing with cURL

### Analyze Claim with cURL

```bash
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { analyzeClaim(input: { claimId: \"CLM001\", patientId: \"PAT001\", providerId: \"PRV001\", claimType: OUTPATIENT, serviceDate: \"2024-01-15T10:00:00Z\", submissionDate: \"2024-01-20T10:00:00Z\", services: [{ code: \"99213\", description: \"Office visit\", units: 1, unitPrice: 150.00 }], claimedAmount: 150.00, diagnosisCodes: [\"I10\"] }) { claimId isValid riskScore } }"
  }'
```

## GraphQL Playground

Access the interactive GraphQL Playground at:
```
http://localhost:4000/graphql
```

The playground provides:
- Schema documentation
- Query autocompletion
- Real-time query validation
- Response formatting
- Query history

## Error Handling

GraphQL errors are returned in standard format:

```json
{
  "errors": [
    {
      "message": "Claim not found",
      "locations": [{"line": 2, "column": 3}],
      "path": ["getClaim"]
    }
  ],
  "data": null
}
```

## Best Practices

1. **Use Variables**: Pass dynamic values as variables instead of inline
2. **Request Only Needed Fields**: GraphQL allows precise field selection
3. **Handle Errors**: Check both `errors` and `data` in responses
4. **Batch Queries**: Combine multiple queries in a single request
5. **Use Fragments**: Reuse field selections with fragments

## Additional Resources

- GraphQL Schema: Available via introspection at the gateway
- Apollo Studio: Can be configured for enhanced monitoring
- Federation Documentation: https://www.apollographql.com/docs/federation/
