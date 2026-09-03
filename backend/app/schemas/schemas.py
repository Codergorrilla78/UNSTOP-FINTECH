from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime

# Generic response wrapper
class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: str = "Operation successful"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Customer schemas
class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    employment_status: Optional[str] = "employed"
    monthly_income: Optional[float] = 0.0
    city: Optional[str] = "Kolkata"
    state: Optional[str] = "West Bengal"
    pin_code: Optional[str] = "700023"

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    phone: Optional[str] = None
    monthly_income: Optional[float] = None
    employment_status: Optional[str] = None
    address: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: str
    status: str
    customer_since: Optional[date] = None
    created_at: datetime
    class Config:
        from_attributes = True

# Account schemas
class AccountResponse(BaseModel):
    id: str
    customer_id: str
    account_number: str
    account_type: str
    account_name: str
    current_balance: float
    available_balance: float
    status: str
    branch_code: Optional[str] = None
    ifsc_code: Optional[str] = None
    class Config:
        from_attributes = True

# Transaction schemas
class TransactionCreate(BaseModel):
    account_id: str
    transaction_type: str  # credit or debit
    amount: float
    category: str
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    customer_id: str
    transaction_date: datetime
    transaction_type: str
    amount: float
    category: str
    sub_category: Optional[str] = None
    is_recurring: bool = False
    description: Optional[str] = None
    balance_after: Optional[float] = None
    class Config:
        from_attributes = True

# Financial Health Schema
class FinancialHealthData(BaseModel):
    snapshot_date: date
    monthly_income: float
    total_balance: float
    average_balance: float
    total_debt: float
    total_emi: float
    debt_to_income_ratio: float
    emi_to_income_ratio: float
    monthly_expenses: float
    essential_expenses: float
    discretionary_expenses: float
    savings_rate: float
    emergency_fund_months: float

# Risk Assessment Schemas
class RiskFactors(BaseModel):
    income_stability_score: float
    liquidity_score: float
    debt_burden_score: float
    payment_behavior_score: float
    credit_utilization_score: float

class RiskScoreData(BaseModel):
    assessment_date: datetime
    risk_score: float
    risk_category: str  # critical, at_risk, watch, healthy
    previous_score: Optional[float] = None
    score_change: Optional[float] = None
    trend: str
    factors: RiskFactors
    weights: Dict[str, float]
    risk_factors: List[Dict[str, Any]]
    explanation: Optional[str] = None

# Forecast Schemas
class DailyProjection(BaseModel):
    date: str
    projected_balance: float
    inflows: float
    outflows: float
    notes: Optional[str] = None

class ForecastSummary(BaseModel):
    minimum_balance: float
    minimum_balance_date: Optional[str] = None
    average_balance: float
    negative_balance_days: int
    low_balance_alerts: List[Dict[str, Any]]

class ForecastData(BaseModel):
    forecast_generated_at: datetime
    forecast_period: Dict[str, str]
    current_balance: float
    daily_projections: List[DailyProjection]
    summary: ForecastSummary
    confidence_level: str

# Intervention Schemas
class InterventionResponse(BaseModel):
    id: str
    customer_id: str
    intervention_type: str
    trigger_reason: str
    trigger_score: float
    recommendation_text: str
    expected_impact: Optional[str] = None
    status: str
    priority: str
    recommended_date: datetime
    expiry_date: Optional[datetime] = None
    class Config:
        from_attributes = True

class InterventionRejectRequest(BaseModel):
    reason: Optional[str] = None

# Overdraft Schemas
class OverdraftCalculateRequest(BaseModel):
    required_amount: float
    expected_repayment_date: str

class OverdraftCalculateResponse(BaseModel):
    eligible: bool
    required_amount: float
    approved_amount: float
    duration_days: int
    daily_interest_rate: float
    processing_fee: float
    total_interest: float
    total_repayment: float
    expected_repayment_date: str
    eligibility_check: Dict[str, bool]
    impact: Dict[str, Any]

# Loan Schemas
class LoanResponse(BaseModel):
    id: str
    loan_number: str
    loan_type: str
    lender_name: str
    principal_amount: float
    outstanding_principal: float
    interest_rate: float
    tenure_months: int
    emi_amount: float
    status: str
    next_emi_date: Optional[date] = None
    class Config:
        from_attributes = True

class LoanCompareRequest(BaseModel):
    loan_amount: float
    tenure_months: int
    loan_type: Optional[str] = "personal"
    purpose: Optional[str] = "debt_consolidation"

# Simulator Schemas
class LoanSimulateRequest(BaseModel):
    loan_amount: float
    interest_rate: float
    tenure_months: int
    processing_fee: Optional[float] = 0.0

class EMISimulateRequest(BaseModel):
    principal: float
    interest_rate: float
    tenure_months: int

# AI Explanation Schemas
class AIExplainRequest(BaseModel):
    context_type: str  # risk_score, forecast, intervention, debtkart
    context_data: Dict[str, Any]

class AIExplainResponse(BaseModel):
    explanation: str
    advisory_recommendation: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Debtkart Real-World Case Study Schemas
class DebtkartCaseStudyResponse(BaseModel):
    client_name: str = "Mr. Saptarshi Masid"
    location: str = "Kolkata, West Bengal"
    total_exposure_amount: float = 2530760.0  # Rs. 25,30,760
    final_settlement_amount: float = 635600.0  # Rs. 6,35,600
    liability_reduction_amount: float = 1895160.0
    savings_percentage: float = 74.88
    hardship_background: str
    creditor_breakdown: List[Dict[str, Any]]
    harassment_challenges: List[str]
    legal_strategy_actions: List[str]
    moratorium_details: Dict[str, Any]
    legal_counsel: Dict[str, Any]
    outcomes: List[str]
    key_learnings: List[str]

class DebtkartNoticeRequest(BaseModel):
    customer_id: str
    lender_name: str
    account_number: str
    outstanding_amount: float
    hardship_details: str
    request_moratorium_months: int = 6
