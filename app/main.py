from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router

app = FastAPI(
    title="HealthPay Payment Integrity Platform",
    description="""
    Healthcare Payment Integrity & Analytics platform services to ensure claims are paid correctly.
    
    ## Features
    
    * **Payment Integrity Analysis**: Identify overpayments, underpayments, and payment errors
    * **Fraud Detection**: Detect fraud, waste, and abuse patterns in claims
    * **Duplicate Detection**: Find duplicate claims across submissions
    * **Analytics & Reporting**: Generate comprehensive analytics summaries
    * **Cost Efficiency**: Calculate savings and payment accuracy rates
    
    ## Key Capabilities
    
    - Analyze individual or batch claims for payment integrity issues
    - Detect overpayments and underpayments
    - Identify duplicate billing and services
    - Flag fraud, waste, and abuse patterns
    - Calculate provider risk scores
    - Generate analytics summaries and reports
    - Track top providers and service codes
    - Measure payment accuracy and cost efficiency
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with platform information"""
    return {
        "service": "HealthPay Payment Integrity Platform",
        "version": "1.0.0",
        "description": "Healthcare Payment Integrity & Analytics platform",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
