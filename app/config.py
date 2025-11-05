"""
Configuration settings for HealthPay Payment Integrity Platform
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "HealthPay Payment Integrity Platform"
    api_version: str = "1.0.0"
    api_description: str = "Healthcare Payment Integrity & Analytics platform"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # CORS Settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # Payment Integrity Thresholds
    overpayment_threshold: float = 0.01  # Minimum amount to flag as overpayment
    excessive_units_threshold: int = 20  # Units threshold for review
    timely_filing_days: int = 90  # Days limit for timely filing
    
    # Fraud Detection Thresholds
    high_volume_claims_threshold: int = 50  # Daily claims per provider
    high_average_claim_amount: float = 5000.0  # Average claim amount threshold
    service_code_concentration_pct: float = 0.8  # 80% threshold
    doctor_shopping_threshold: int = 10  # Number of providers
    same_day_services_threshold: int = 3  # Services per day threshold
    
    # Risk Score Weights
    risk_critical_weight: int = 40
    risk_high_weight: int = 25
    risk_medium_weight: int = 15
    risk_low_weight: int = 5
    
    # Database Settings (for future use)
    database_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
