# HealthPay Payment Integrity Platform

A comprehensive Healthcare Payment Integrity & Analytics platform that ensures claims are paid correctly by identifying overpayments, underpayments, errors, fraud, waste, and abuse in healthcare claims.

## Features

### 🔍 Payment Integrity Analysis
- Detect overpayments and underpayments
- Identify pricing errors and calculation mistakes
- Flag duplicate services within claims
- Check for late filing and timely submission
- Validate required information (diagnosis codes, etc.)
- Calculate risk scores for claims

### 🚨 Fraud, Waste, and Abuse Detection
- Identify duplicate billing across claims
- Detect high-volume billing anomalies
- Flag provider pattern anomalies and upcoding
- Identify doctor shopping behavior
- Detect impossible service patterns
- Calculate provider fraud risk scores

### 📊 Analytics & Reporting
- Generate comprehensive analytics summaries
- Track top providers by claim amount
- Analyze most frequently billed service codes
- Calculate payment accuracy rates
- Measure cost efficiency and savings
- Monitor claims by status and type

### ⚙️ Key Capabilities
- Analyze individual or batch claims
- Detect duplicate claims across submissions
- Calculate allowed amounts based on fee schedules
- Real-time fraud alerts
- RESTful API with comprehensive documentation

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/panatl/HealthPay.git
cd HealthPay
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the server:
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Payment Integrity
- `POST /api/v1/claims/analyze` - Analyze a single claim
- `POST /api/v1/claims/batch-analyze` - Analyze multiple claims
- `POST /api/v1/claims/check-duplicates` - Check for duplicate claims
- `POST /api/v1/claims/calculate-allowed` - Calculate allowed amount

### Fraud Detection
- `POST /api/v1/fraud/analyze` - Analyze claims for fraud patterns
- `GET /api/v1/fraud/provider-risk/{provider_id}` - Get provider risk score
- `GET /api/v1/fraud/alerts` - Get fraud alerts

### Analytics
- `POST /api/v1/analytics/summary` - Generate analytics summary
- `POST /api/v1/analytics/top-providers` - Get top providers
- `POST /api/v1/analytics/top-services` - Get top service codes
- `POST /api/v1/analytics/payment-accuracy` - Calculate payment accuracy
- `POST /api/v1/analytics/cost-efficiency` - Calculate cost efficiency

### Claims Management
- `GET /api/v1/claims/{claim_id}` - Get claim by ID
- `GET /api/v1/claims/{claim_id}/analysis` - Get claim analysis results

## Usage Examples

### Analyze a Claim

```bash
curl -X POST "http://localhost:8000/api/v1/claims/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "CLM001",
    "patient_id": "PAT001",
    "provider_id": "PRV001",
    "claim_type": "outpatient",
    "service_date": "2024-01-15T10:00:00Z",
    "submission_date": "2024-01-20T10:00:00Z",
    "services": [
      {
        "code": "99213",
        "description": "Office visit",
        "units": 1,
        "unit_price": 150.00
      }
    ],
    "claimed_amount": 150.00,
    "allowed_amount": 150.00,
    "paid_amount": 150.00,
    "status": "approved",
    "diagnosis_codes": ["I10"]
  }'
```

### Detect Fraud Patterns

```bash
curl -X POST "http://localhost:8000/api/v1/fraud/analyze" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "claim_id": "CLM001",
      "patient_id": "PAT001",
      "provider_id": "PRV001",
      ...
    },
    {
      "claim_id": "CLM002",
      "patient_id": "PAT001",
      "provider_id": "PRV001",
      ...
    }
  ]'
```

### Generate Analytics Summary

```bash
curl -X POST "http://localhost:8000/api/v1/analytics/summary" \
  -H "Content-Type: application/json" \
  -d '[...]'
```

## Architecture

The platform consists of three main services:

1. **Payment Integrity Service** (`app/services/payment_integrity.py`)
   - Analyzes claims for payment accuracy
   - Detects overpayments, underpayments, and errors
   - Validates claim data and pricing

2. **Fraud Detection Service** (`app/services/fraud_detection.py`)
   - Identifies fraud, waste, and abuse patterns
   - Monitors provider and patient behavior
   - Generates fraud alerts with confidence scores

3. **Analytics Service** (`app/services/analytics.py`)
   - Generates comprehensive reports
   - Calculates key performance metrics
   - Provides insights on payment efficiency

## Data Models

### Claim
- `claim_id`: Unique identifier
- `patient_id`: Patient identifier
- `provider_id`: Healthcare provider identifier
- `claim_type`: Type of claim (inpatient, outpatient, etc.)
- `service_date`: Date of service
- `services`: List of medical services/procedures
- `claimed_amount`: Total amount claimed
- `allowed_amount`: Amount allowed per policy
- `paid_amount`: Amount actually paid
- `status`: Claim status
- `diagnosis_codes`: ICD diagnosis codes

### Payment Integrity Issue
- `issue_type`: Type of issue (overpayment, underpayment, etc.)
- `severity`: Severity level (low, medium, high, critical)
- `description`: Detailed description
- `estimated_impact`: Financial impact
- `recommendation`: Recommended action

### Fraud Alert
- `alert_id`: Unique alert identifier
- `claim_ids`: Related claims
- `alert_type`: Type of fraud/waste/abuse
- `confidence_score`: Confidence level (0-1)
- `pattern_description`: Description of pattern
- `status`: Alert status

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.