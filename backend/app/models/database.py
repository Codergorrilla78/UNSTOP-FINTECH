import uuid
import datetime
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, Date, DateTime, 
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from ..config.settings import settings

Base = declarative_base()

# Database Engine initialization (PostgreSQL with SQLite fallback for resilient execution)
try:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    # Test connection
    with engine.connect() as conn:
        pass
except Exception as e:
    # If postgres is not yet initialized or port not open, fallback gracefully to sqlite
    sqlite_url = "sqlite:///./finshield.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# Models
# =============================================================================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    date_of_birth = Column(Date, nullable=True)
    
    employment_status = Column(String(50), default="employed")  # employed, self_employed, unemployed, medical_leave
    employer_name = Column(String(200), nullable=True)
    occupation = Column(String(100), nullable=True)
    monthly_income = Column(Float, default=0.0)
    
    pan_number = Column(String(20), nullable=True)
    aadhar_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), default="Kolkata")
    state = Column(String(100), default="West Bengal")
    pin_code = Column(String(20), default="700023")
    
    status = Column(String(20), default="active")  # active, distressed, under_moratorium, settled
    customer_since = Column(Date, default=datetime.date.today)
    assigned_officer_id = Column(String(36), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    accounts = relationship("Account", back_populates="customer", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="customer", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="customer", cascade="all, delete-orphan")
    financial_snapshots = relationship("FinancialSnapshot", back_populates="customer", cascade="all, delete-orphan")
    cashflow_forecasts = relationship("CashflowForecast", back_populates="customer", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="customer", cascade="all, delete-orphan")
    overdraft_offers = relationship("OverdraftOffer", back_populates="customer", cascade="all, delete-orphan")
    legal_interventions = relationship("LegalIntervention", back_populates="customer", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    account_number = Column(String(50), unique=True, nullable=False)
    account_type = Column(String(50), nullable=False)  # savings, salary, current
    account_name = Column(String(200), nullable=False)
    
    current_balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    status = Column(String(20), default="active")
    
    branch_code = Column(String(20), nullable=True)
    ifsc_code = Column(String(20), nullable=True)
    opened_date = Column(Date, default=datetime.date.today)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    transaction_date = Column(DateTime, default=datetime.datetime.utcnow)
    transaction_type = Column(String(20), nullable=False)  # credit, debit
    amount = Column(Float, nullable=False)
    
    category = Column(String(100), nullable=False)  # salary, rent, groceries, emi, medical, partial_payment
    sub_category = Column(String(100), nullable=True)
    is_recurring = Column(Boolean, default=False)
    
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)
    balance_after = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    account = relationship("Account", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")


class IncomeRecord(Base):
    __tablename__ = "income_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    income_date = Column(Date, nullable=False)
    income_type = Column(String(50), nullable=False)  # salary, freelance, business, severance
    amount = Column(Float, nullable=False)
    source = Column(String(200), nullable=True)
    is_regular = Column(Boolean, default=True)
    expected_next_date = Column(Date, nullable=True)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    expense_date = Column(Date, nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    is_essential = Column(Boolean, default=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_frequency = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Loan(Base):
    __tablename__ = "loans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    loan_number = Column(String(50), unique=True, nullable=False)
    loan_type = Column(String(50), nullable=False)  # personal, credit_card, auto, home
    lender_name = Column(String(200), nullable=False)  # HDFC Bank, Standard Chartered Bank, RBL Bank
    product_name = Column(String(200), nullable=True)
    
    principal_amount = Column(Float, nullable=False)
    sanctioned_amount = Column(Float, nullable=False)
    outstanding_principal = Column(Float, nullable=False)
    
    interest_rate = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    emi_amount = Column(Float, nullable=False)
    
    disbursement_date = Column(Date, nullable=True)
    first_emi_date = Column(Date, nullable=True)
    last_emi_date = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)
    
    processing_fee = Column(Float, default=0.0)
    prepayment_charges_percent = Column(Float, default=0.0)
    status = Column(String(20), default="active")  # active, defaulted, settled, closed, restructured
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="loans")
    payments = relationship("LoanPayment", back_populates="loan", cascade="all, delete-orphan")


class LoanPayment(Base):
    __tablename__ = "loan_payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_id = Column(String(36), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=True)
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    
    principal_component = Column(Float, default=0.0)
    interest_component = Column(Float, default=0.0)
    status = Column(String(20), default="pending")  # paid, pending, overdue, partial, missed
    days_overdue = Column(Integer, default=0)
    late_fee = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    loan = relationship("Loan", back_populates="payments")


class FinancialSnapshot(Base):
    __tablename__ = "financial_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    snapshot_date = Column(Date, default=datetime.date.today)
    monthly_income = Column(Float, default=0.0)
    income_stability_score = Column(Float, default=0.0)
    
    total_balance = Column(Float, default=0.0)
    average_balance = Column(Float, default=0.0)
    minimum_balance = Column(Float, default=0.0)
    
    total_debt = Column(Float, default=0.0)
    total_emi = Column(Float, default=0.0)
    debt_to_income_ratio = Column(Float, default=0.0)
    emi_to_income_ratio = Column(Float, default=0.0)
    
    monthly_expenses = Column(Float, default=0.0)
    essential_expenses = Column(Float, default=0.0)
    discretionary_expenses = Column(Float, default=0.0)
    
    savings_rate = Column(Float, default=0.0)
    emergency_fund_months = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="financial_snapshots")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    assessment_date = Column(DateTime, default=datetime.datetime.utcnow)
    risk_score = Column(Float, nullable=False)  # 0 to 100
    risk_category = Column(String(20), nullable=False)  # critical, at_risk, watch, healthy
    
    income_stability_score = Column(Float, default=0.0)
    liquidity_score = Column(Float, default=0.0)
    debt_burden_score = Column(Float, default=0.0)
    payment_behavior_score = Column(Float, default=0.0)
    credit_utilization_score = Column(Float, default=0.0)
    
    weights = Column(JSON, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    ml_distress_probability = Column(Float, default=0.0)
    ml_features = Column(JSON, nullable=True)
    
    previous_score = Column(Float, nullable=True)
    score_change = Column(Float, nullable=True)
    trend = Column(String(20), default="stable")  # improving, stable, declining
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="risk_assessments")


class CashflowForecast(Base):
    __tablename__ = "cashflow_forecasts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    forecast_generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    forecast_start_date = Column(Date, nullable=False)
    forecast_end_date = Column(Date, nullable=False)
    
    current_balance = Column(Float, default=0.0)
    daily_projections = Column(JSON, nullable=False)  # List of {date, projected_balance, inflows, outflows, notes}
    low_balance_dates = Column(JSON, nullable=True)
    negative_balance_dates = Column(JSON, nullable=True)
    
    minimum_projected_balance = Column(Float, default=0.0)
    minimum_balance_date = Column(Date, nullable=True)
    average_projected_balance = Column(Float, default=0.0)
    confidence_level = Column(String(20), default="high")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="cashflow_forecasts")


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    intervention_type = Column(String(50), nullable=False)  # spending_adjustment, repayment_restructure, overdraft, loan, legal_settlement
    trigger_reason = Column(String(255), nullable=False)
    trigger_score = Column(Float, default=0.0)
    
    recommendation_text = Column(Text, nullable=False)
    expected_impact = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, accepted, rejected, actioned
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    
    recommended_date = Column(DateTime, default=datetime.datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    action_date = Column(DateTime, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="interventions")


class OverdraftOffer(Base):
    __tablename__ = "overdraft_offers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    intervention_id = Column(String(36), nullable=True)
    
    required_amount = Column(Float, nullable=False)
    approved_amount = Column(Float, nullable=True)
    daily_interest_rate = Column(Float, default=0.0005)
    processing_fee = Column(Float, default=100.0)
    duration_days = Column(Integer, default=30)
    
    expected_repayment_date = Column(Date, nullable=False)
    expected_income_date = Column(Date, nullable=True)
    expected_income_amount = Column(Float, default=0.0)
    
    total_interest = Column(Float, default=0.0)
    total_repayment = Column(Float, default=0.0)
    eligibility_check = Column(JSON, nullable=True)
    
    status = Column(String(20), default="offered")  # offered, accepted, rejected, repaid
    offered_date = Column(DateTime, default=datetime.datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    acceptance_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="overdraft_offers")


class Lender(Base):
    __tablename__ = "lenders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lender_name = Column(String(200), unique=True, nullable=False)
    lender_type = Column(String(50), default="bank")  # bank, nbfc, fintech
    website = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    loan_products = relationship("LoanProduct", back_populates="lender", cascade="all, delete-orphan")


class LoanProduct(Base):
    __tablename__ = "loan_products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lender_id = Column(String(36), ForeignKey("lenders.id", ondelete="CASCADE"), nullable=False)
    
    product_name = Column(String(200), nullable=False)
    product_code = Column(String(50), nullable=True)
    loan_type = Column(String(50), default="personal")
    
    min_loan_amount = Column(Float, default=10000.0)
    max_loan_amount = Column(Float, default=2000000.0)
    min_interest_rate = Column(Float, default=10.5)
    max_interest_rate = Column(Float, default=18.0)
    interest_type = Column(String(20), default="reducing")
    
    min_tenure_months = Column(Integer, default=12)
    max_tenure_months = Column(Integer, default=60)
    
    processing_fee_percent = Column(Float, default=1.0)
    processing_fee_fixed = Column(Float, default=0.0)
    prepayment_charges_percent = Column(Float, default=2.0)
    
    min_monthly_income = Column(Float, default=25000.0)
    min_credit_score = Column(Integer, default=650)
    features = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    lender = relationship("Lender", back_populates="loan_products")


class LoanComparison(Base):
    __tablename__ = "loan_comparisons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    loan_amount = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    purpose = Column(String(100), default="debt_consolidation")
    
    products_compared = Column(JSON, nullable=False)
    best_fit_product_id = Column(String(36), nullable=True)
    best_fit_reason = Column(Text, nullable=True)
    weights_used = Column(JSON, nullable=True)
    
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    intervention_id = Column(String(36), nullable=True)
    
    recommendation_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    current_risk_score = Column(Float, default=0.0)
    projected_risk_score = Column(Float, default=0.0)
    impact_summary = Column(Text, nullable=True)
    
    priority = Column(Integer, default=1)
    confidence = Column(Float, default=85.0)
    ai_explanation = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # active, dismissed, actioned
    recommended_at = Column(DateTime, default=datetime.datetime.utcnow)


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    simulation_type = Column(String(50), default="loan")
    parameters = Column(JSON, nullable=False)
    results = Column(JSON, nullable=False)
    
    impact_on_risk_score = Column(Float, default=0.0)
    impact_on_monthly_surplus = Column(Float, default=0.0)
    saved = Column(Boolean, default=False)
    simulation_name = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =============================================================================
# Debtkart Legal Intervention Models (Real-World Kolkata Case Study)
# =============================================================================

class LegalIntervention(Base):
    __tablename__ = "legal_interventions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    case_reference_id = Column(String(50), unique=True, default=lambda: f"DK-KOL-{uuid.uuid4().hex[:6].upper()}")
    legal_firm = Column(String(200), default="SETTLEND LEGAL ADVISORS LLP (Debtkart)")
    lead_counsel_contact = Column(String(50), default="+91 6293629300")
    counsel_email = Column(String(255), default="info@debtkart.in")
    registered_office = Column(Text, default="59, Diamond Harbour Rd, Ekbalpur, Khidirpur, Kolkata, West Bengal 700023")
    
    # Financial Distress Parameters
    total_exposure_amount = Column(Float, nullable=False, default=2530760.0)  # Rs. 25,30,760
    hardship_reason = Column(Text, default="Involuntary employment loss coupled with continuous medical emergency expenses")
    
    # Creditors Involved
    creditor_banks = Column(JSON, default=lambda: ["HDFC Bank", "Standard Chartered Bank", "RBL Bank"])
    
    # Legal Status
    rbi_fair_practices_invoked = Column(Boolean, default=True)
    third_party_harassment_restrained = Column(Boolean, default=True)
    civil_vs_criminal_rebuttal_issued = Column(Boolean, default=True)
    
    # Moratorium
    moratorium_granted_months = Column(Integer, default=6)
    moratorium_start_date = Column(Date, default=datetime.date.today)
    moratorium_end_date = Column(Date, nullable=True)
    
    # Settlement Outcome
    settlement_status = Column(String(50), default="negotiated_settlement")  # in_moratorium, under_negotiation, negotiated_settlement
    final_settlement_amount = Column(Float, default=635600.0)  # Rs. 6,35,600
    liability_reduction_amount = Column(Float, default=1895160.0)  # Rs. 18,95,160 saved
    savings_percentage = Column(Float, default=74.88)
    
    legal_notices_sent = Column(JSON, nullable=True)
    resolution_mode = Column(String(100), default="Structured multi-bank legal intervention and negotiated settlements")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="legal_interventions")


def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
