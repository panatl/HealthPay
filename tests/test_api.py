import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_analyze_claim():
    """Test claim analysis endpoint"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    claim_data = {
        "claim_id": "TEST_CLM001",
        "patient_id": "TEST_PAT001",
        "provider_id": "TEST_PRV001",
        "claim_type": "outpatient",
        "service_date": service_date.isoformat(),
        "submission_date": submission_date.isoformat(),
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
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/claims/analyze", json=claim_data)
        assert response.status_code == 200
        data = response.json()
        assert data["claim_id"] == "TEST_CLM001"
        assert "risk_score" in data
        assert "issues" in data


@pytest.mark.asyncio
async def test_analyze_overpayment():
    """Test overpayment detection"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    claim_data = {
        "claim_id": "TEST_OVER",
        "patient_id": "TEST_PAT002",
        "provider_id": "TEST_PRV002",
        "claim_type": "outpatient",
        "service_date": service_date.isoformat(),
        "submission_date": submission_date.isoformat(),
        "services": [
            {
                "code": "99213",
                "description": "Office visit",
                "units": 1,
                "unit_price": 150.00
            }
        ],
        "claimed_amount": 150.00,
        "allowed_amount": 100.00,
        "paid_amount": 150.00,
        "status": "approved",
        "diagnosis_codes": ["I10"]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/claims/analyze", json=claim_data)
        assert response.status_code == 200
        data = response.json()
        
        # Should detect overpayment
        overpayment_issues = [i for i in data["issues"] if i["issue_type"] == "overpayment"]
        assert len(overpayment_issues) > 0


@pytest.mark.asyncio
async def test_batch_analyze():
    """Test batch claim analysis"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    claims_data = [
        {
            "claim_id": f"TEST_BATCH{i}",
            "patient_id": f"TEST_PAT{i}",
            "provider_id": "TEST_PRV001",
            "claim_type": "outpatient",
            "service_date": service_date.isoformat(),
            "submission_date": submission_date.isoformat(),
            "services": [
                {
                    "code": "99213",
                    "description": "Office visit",
                    "units": 1,
                    "unit_price": 150.00
                }
            ],
            "claimed_amount": 150.00,
            "diagnosis_codes": ["I10"]
        }
        for i in range(3)
    ]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/claims/batch-analyze", json=claims_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


@pytest.mark.asyncio
async def test_check_duplicates():
    """Test duplicate claims detection"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create duplicate claims
    claims_data = [
        {
            "claim_id": "TEST_DUP1",
            "patient_id": "TEST_PAT_DUP",
            "provider_id": "TEST_PRV_DUP",
            "claim_type": "outpatient",
            "service_date": service_date.isoformat(),
            "submission_date": submission_date.isoformat(),
            "services": [
                {
                    "code": "99213",
                    "description": "Office visit",
                    "units": 1,
                    "unit_price": 150.00
                }
            ],
            "claimed_amount": 150.00,
            "diagnosis_codes": ["I10"]
        },
        {
            "claim_id": "TEST_DUP2",
            "patient_id": "TEST_PAT_DUP",
            "provider_id": "TEST_PRV_DUP",
            "claim_type": "outpatient",
            "service_date": service_date.isoformat(),
            "submission_date": submission_date.isoformat(),
            "services": [
                {
                    "code": "99213",
                    "description": "Office visit",
                    "units": 1,
                    "unit_price": 150.00
                }
            ],
            "claimed_amount": 150.00,
            "diagnosis_codes": ["I10"]
        }
    ]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/claims/check-duplicates", json=claims_data)
        assert response.status_code == 200
        data = response.json()
        assert "duplicate_groups" in data
        assert data["total_claims_checked"] == 2


@pytest.mark.asyncio
async def test_fraud_analysis():
    """Test fraud detection endpoint"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    # Create claims that should trigger fraud alert
    claims_data = [
        {
            "claim_id": f"TEST_FRAUD{i}",
            "patient_id": f"TEST_PAT_FRAUD{i}",
            "provider_id": "TEST_PRV_FRAUD",
            "claim_type": "outpatient",
            "service_date": service_date.isoformat(),
            "submission_date": submission_date.isoformat(),
            "services": [
                {
                    "code": "99215",
                    "description": "Complex visit",
                    "units": 1,
                    "unit_price": 300.00
                }
            ],
            "claimed_amount": 300.00,
            "diagnosis_codes": ["I10"]
        }
        for i in range(60)  # High volume to trigger alert
    ]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/fraud/analyze", json=claims_data)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_analytics_summary():
    """Test analytics summary endpoint"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    claims_data = [
        {
            "claim_id": "TEST_ANALYTICS1",
            "patient_id": "TEST_PAT_A1",
            "provider_id": "TEST_PRV_A1",
            "claim_type": "outpatient",
            "service_date": service_date.isoformat(),
            "submission_date": submission_date.isoformat(),
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
        }
    ]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/analytics/summary", json=claims_data)
        assert response.status_code == 200
        data = response.json()
        assert data["total_claims"] == 1
        assert "total_claimed_amount" in data
        assert "claims_by_status" in data


@pytest.mark.asyncio
async def test_get_claim():
    """Test get claim by ID"""
    service_date = datetime.utcnow() - timedelta(days=5)
    submission_date = datetime.utcnow()
    
    claim_data = {
        "claim_id": "TEST_GET_CLM",
        "patient_id": "TEST_PAT_GET",
        "provider_id": "TEST_PRV_GET",
        "claim_type": "outpatient",
        "service_date": service_date.isoformat(),
        "submission_date": submission_date.isoformat(),
        "services": [
            {
                "code": "99213",
                "description": "Office visit",
                "units": 1,
                "unit_price": 150.00
            }
        ],
        "claimed_amount": 150.00,
        "diagnosis_codes": ["I10"]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First analyze to store the claim
        await client.post("/api/v1/claims/analyze", json=claim_data)
        
        # Then retrieve it
        response = await client.get("/api/v1/claims/TEST_GET_CLM")
        assert response.status_code == 200
        data = response.json()
        assert data["claim_id"] == "TEST_GET_CLM"
