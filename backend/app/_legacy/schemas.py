from pydantic import BaseModel, EmailStr
from typing import Optional


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr

    monthly_income: float
    monthly_expenses: float

    monthly_debt_payment: float = 0
    savings: float = 0
    existing_debt: float = 0


class CustomerResponse(CustomerCreate):
    id: int

    class Config:
        from_attributes = True


class FinancialAnalysisResponse(BaseModel):
    customer_id: int

    resilience_score: float

    monthly_surplus: float
    debt_to_income: float
    emergency_months: float

    risk_level: str
    recommendation: str