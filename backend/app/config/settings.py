import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # App Information
    PROJECT_NAME: str = "FinShield — Intelligent Banking Financial-Resilience Platform"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # PostgreSQL Database Configuration
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "finshield"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    
    # Primary PostgreSQL Database URL
    DATABASE_URL: str = "postgresql://postgres@127.0.0.1:5432/finshield"

    # Security & Auth
    JWT_SECRET: str = "finshield-secret-key-development-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        return ["*"]

    # Resilience Scoring Weights (must sum to 1.0)
    WEIGHT_INCOME_STABILITY: float = 0.20
    WEIGHT_LIQUIDITY: float = 0.25
    WEIGHT_DEBT_BURDEN: float = 0.25
    WEIGHT_PAYMENT_BEHAVIOR: float = 0.15
    WEIGHT_CREDIT_UTILIZATION: float = 0.15

    # Risk Categories Thresholds
    THRESHOLD_CRITICAL: float = 30.0
    THRESHOLD_AT_RISK: float = 50.0
    THRESHOLD_WATCH: float = 70.0
    THRESHOLD_HEALTHY: float = 100.0

    # Cash Flow & Liquidity
    FORECAST_DAYS: int = 90
    CRITICAL_LOW_BALANCE: float = 5000.0

    # Overdraft Limits
    OVERDRAFT_MIN_INCOME: float = 20000.0
    OVERDRAFT_MAX_LIMIT: float = 50000.0
    OVERDRAFT_DAILY_INTEREST_RATE: float = 0.0005
    OVERDRAFT_PROCESSING_FEE: float = 100.0

    # Loan Comparison Weights
    LOAN_WEIGHT_TOTAL_COST: float = 0.30
    LOAN_WEIGHT_EMI_AFFORDABILITY: float = 0.25
    LOAN_WEIGHT_RESILIENCE_IMPACT: float = 0.20
    LOAN_WEIGHT_TENURE_SUITABILITY: float = 0.10
    LOAN_WEIGHT_FEES: float = 0.05
    LOAN_WEIGHT_FLEXIBILITY: float = 0.10

    # Debtkart Legal Advisor Partner Configuration
    DEBTKART_LEGAL_ENTITY: str = "SETTLEND LEGAL ADVISORS LLP"
    DEBTKART_BRAND: str = "Debtkart"
    DEBTKART_PHONE: str = "+91 6293629300"
    DEBTKART_ALT_PHONES: List[str] = ["+91 6293000456", "+91 6293889388"]
    DEBTKART_EMAIL: str = "info@debtkart.in"
    DEBTKART_OPS_EMAIL: str = "operations@debtkart.in"
    DEBTKART_ADDRESS: str = "59, Diamond Harbour Rd, Ekbalpur, Khidirpur, Kolkata, West Bengal 700023"
    DEBTKART_DUNS: str = "644953151"
    DEBTKART_HOURS: str = "Mon - Fri: 10:30 AM - 7:00 PM, Saturday: 10:30 AM - 4:00 PM"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
