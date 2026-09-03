import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.database import (
    Base, Customer, Account, Transaction, IncomeRecord, Expense,
    Loan, LoanPayment, FinancialSnapshot, RiskAssessment,
    CashflowForecast, Intervention, OverdraftOffer,
    Lender, LoanProduct, LoanComparison, Recommendation,
    Simulation, LegalIntervention
)

# Use in-memory SQLite database for isolated model tests
@pytest.fixture(scope="function")
def db_session():
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# =============================================================================
# Database & Model Layer Tests
# =============================================================================

def test_customer_creation_and_defaults(db_session):
    customer = Customer(
        first_name="Anita",
        last_name="Roy",
        email="anita.roy@example.com",
        phone="+91-9876543210",
        monthly_income=65000.0,
        city="Kolkata"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    assert customer.id is not None
    assert customer.status == "active"
    assert customer.state == "West Bengal"
    assert customer.monthly_income == 65000.0

def test_account_relation_and_balance(db_session):
    customer = Customer(first_name="Rohan", last_name="Sharma", email="rohan@example.com")
    db_session.add(customer)
    db_session.commit()

    account = Account(
        customer_id=customer.id,
        account_number="ACC-1001",
        account_type="savings",
        account_name="Primary Savings",
        current_balance=45000.0,
        available_balance=45000.0
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)

    assert account.customer_id == customer.id
    assert account.customer.email == "rohan@example.com"
    assert len(customer.accounts) == 1
    assert customer.accounts[0].account_number == "ACC-1001"

def test_transaction_creation(db_session):
    customer = Customer(first_name="Deb", last_name="Sen", email="deb@example.com")
    db_session.add(customer)
    db_session.commit()

    account = Account(
        customer_id=customer.id,
        account_number="ACC-2002",
        account_type="salary",
        account_name="Salary Account",
        current_balance=10000.0,
        available_balance=10000.0
    )
    db_session.add(account)
    db_session.commit()

    tx = Transaction(
        account_id=account.id,
        customer_id=customer.id,
        transaction_type="debit",
        amount=2500.0,
        category="groceries",
        description="Weekly grocery shopping"
    )
    db_session.add(tx)
    db_session.commit()
    db_session.refresh(tx)

    assert tx.id is not None
    assert tx.amount == 2500.0
    assert tx.account.account_number == "ACC-2002"

def test_loan_and_loan_payment(db_session):
    customer = Customer(first_name="Pooja", last_name="Das", email="pooja@example.com")
    db_session.add(customer)
    db_session.commit()

    loan = Loan(
        customer_id=customer.id,
        loan_number="LN-9901",
        loan_type="personal",
        lender_name="HDFC Bank",
        principal_amount=500000.0,
        sanctioned_amount=500000.0,
        outstanding_principal=420000.0,
        interest_rate=11.5,
        tenure_months=36,
        emi_amount=16480.0
    )
    db_session.add(loan)
    db_session.commit()

    payment = LoanPayment(
        loan_id=loan.id,
        customer_id=customer.id,
        due_date=datetime.date(2026, 9, 5),
        amount_due=16480.0,
        amount_paid=16480.0,
        status="paid"
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(loan)

    assert len(loan.payments) == 1
    assert loan.payments[0].status == "paid"
    assert loan.outstanding_principal == 420000.0

def test_lender_and_loan_products(db_session):
    lender = Lender(
        lender_name="State Bank of India",
        lender_type="bank",
        website="https://sbi.co.in"
    )
    db_session.add(lender)
    db_session.commit()

    product = LoanProduct(
        lender_id=lender.id,
        product_name="SBI Xpress Credit",
        loan_type="personal",
        min_loan_amount=50000.0,
        max_loan_amount=2500000.0,
        min_interest_rate=9.80,
        max_interest_rate=13.50,
        min_tenure_months=12,
        max_tenure_months=72
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(lender)

    assert len(lender.loan_products) == 1
    assert lender.loan_products[0].min_interest_rate == 9.80

def test_risk_assessment_model(db_session):
    customer = Customer(first_name="Kunal", last_name="Basu", email="kunal@example.com")
    db_session.add(customer)
    db_session.commit()

    risk = RiskAssessment(
        customer_id=customer.id,
        risk_score=28.5,
        risk_category="critical",
        liquidity_score=15.0,
        debt_burden_score=20.0,
        ml_distress_probability=0.88,
        trend="declining"
    )
    db_session.add(risk)
    db_session.commit()
    db_session.refresh(risk)

    assert risk.risk_category == "critical"
    assert risk.ml_distress_probability == 0.88
    assert risk.customer.email == "kunal@example.com"

def test_legal_intervention_saptarshi_case(db_session):
    customer = Customer(
        first_name="Saptarshi",
        last_name="Masid",
        email="saptarshi.masid@kolkata.debtkart.in",
        status="distressed"
    )
    db_session.add(customer)
    db_session.commit()

    legal = LegalIntervention(
        customer_id=customer.id,
        legal_firm="SETTLEND LEGAL ADVISORS LLP (Debtkart)",
        lead_counsel_contact="+91 6293629300",
        total_exposure_amount=2530760.0,
        final_settlement_amount=635600.0,
        liability_reduction_amount=1895160.0,
        savings_percentage=74.88,
        settlement_status="negotiated_settlement"
    )
    db_session.add(legal)
    db_session.commit()
    db_session.refresh(legal)

    assert legal.total_exposure_amount == 2530760.0
    assert legal.savings_percentage == 74.88
    assert legal.liability_reduction_amount == 1895160.0
    assert legal.legal_firm == "SETTLEND LEGAL ADVISORS LLP (Debtkart)"

def test_customer_cascade_deletion(db_session):
    customer = Customer(first_name="Temp", last_name="User", email="temp@example.com")
    db_session.add(customer)
    db_session.commit()

    account = Account(
        customer_id=customer.id,
        account_number="TEMP-11",
        account_type="savings",
        account_name="Temp Savings"
    )
    db_session.add(account)
    db_session.commit()

    cust_id = customer.id
    db_session.delete(customer)
    db_session.commit()

    # Verify accounts are deleted via cascade
    remaining_accounts = db_session.query(Account).filter(Account.customer_id == cust_id).all()
    assert len(remaining_accounts) == 0
