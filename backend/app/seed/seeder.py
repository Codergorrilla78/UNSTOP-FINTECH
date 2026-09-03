import datetime
from sqlalchemy.orm import Session
from backend.app.models.database import (
    Customer, Account, Transaction, Loan, LoanPayment,
    FinancialSnapshot, RiskAssessment, Intervention,
    Lender, LoanProduct, LegalIntervention
)
from backend.app.config.settings import settings

def seed_database(db: Session):
    """Populates PostgreSQL with benchmark customers, market lenders, and the real-world Kolkata case study."""
    
    # Check if already seeded
    existing_customer = db.query(Customer).filter(Customer.email == "saptarshi.masid@kolkata.debtkart.in").first()
    if existing_customer:
        print("[FinShield Seeder] Database already seeded.")
        return

    print("[FinShield Seeder] Seeding PostgreSQL database with authentic records...")

    # =========================================================================
    # 1. Market Lenders & Loan Products Catalog
    # =========================================================================
    lenders_data = [
        {"name": "HDFC Bank", "type": "bank", "website": "https://www.hdfcbank.com"},
        {"name": "State Bank of India", "type": "bank", "website": "https://sbi.co.in"},
        {"name": "ICICI Bank", "type": "bank", "website": "https://www.icicibank.com"},
        {"name": "Axis Bank", "type": "bank", "website": "https://www.axisbank.com"},
        {"name": "Standard Chartered Bank", "type": "bank", "website": "https://www.sc.com/in"},
        {"name": "RBL Bank", "type": "bank", "website": "https://www.rblbank.com"}
    ]

    lender_instances = {}
    for l_info in lenders_data:
        lender = Lender(
            lender_name=l_info["name"],
            lender_type=l_info["type"],
            website=l_info["website"],
            contact_email=f"loans@{l_info['name'].lower().replace(' ', '')}.com",
            contact_phone="+91-1800-202-000",
            is_active=True
        )
        db.add(lender)
        db.flush()
        lender_instances[l_info["name"]] = lender

    # Loan Products
    products_data = [
        {
            "lender": "State Bank of India",
            "name": "SBI Xpress Credit",
            "code": "SBI-XC-01",
            "min_amount": 50000.0,
            "max_amount": 2500000.0,
            "min_rate": 9.80,
            "max_rate": 13.50,
            "min_tenure": 12,
            "max_tenure": 72,
            "proc_fee_pct": 0.5,
            "prepay_pct": 0.0
        },
        {
            "lender": "HDFC Bank",
            "name": "HDFC Personal Loan Premium",
            "code": "HDFC-PLP-01",
            "min_amount": 50000.0,
            "max_amount": 4000000.0,
            "min_rate": 10.50,
            "max_rate": 15.00,
            "min_tenure": 12,
            "max_tenure": 60,
            "proc_fee_pct": 0.99,
            "prepay_pct": 2.0
        },
        {
            "lender": "ICICI Bank",
            "name": "ICICI QuickCash Personal Loan",
            "code": "ICICI-QC-01",
            "min_amount": 50000.0,
            "max_amount": 3000000.0,
            "min_rate": 10.85,
            "max_rate": 15.50,
            "min_tenure": 12,
            "max_tenure": 60,
            "proc_fee_pct": 1.25,
            "prepay_pct": 3.0
        },
        {
            "lender": "Axis Bank",
            "name": "Axis 24x7 Express Credit",
            "code": "AXIS-EXP-01",
            "min_amount": 50000.0,
            "max_amount": 2500000.0,
            "min_rate": 11.25,
            "max_rate": 16.00,
            "min_tenure": 12,
            "max_tenure": 60,
            "proc_fee_pct": 1.50,
            "prepay_pct": 2.0
        }
    ]

    for p in products_data:
        prod = LoanProduct(
            lender_id=lender_instances[p["lender"]].id,
            product_name=p["name"],
            product_code=p["code"],
            loan_type="personal",
            min_loan_amount=p["min_amount"],
            max_loan_amount=p["max_amount"],
            min_interest_rate=p["min_rate"],
            max_interest_rate=p["max_rate"],
            min_tenure_months=p["min_tenure"],
            max_tenure_months=p["max_tenure"],
            processing_fee_percent=p["proc_fee_pct"],
            prepayment_charges_percent=p["prepay_pct"],
            min_monthly_income=25000.0,
            is_active=True
        )
        db.add(prod)

    # =========================================================================
    # 2. REAL-WORLD CASE STUDY: Mr. Saptarshi Masid (Kolkata)
    # Total Loan Exposure: Rs. 25,30,760
    # =========================================================================
    saptarshi = Customer(
        first_name="Saptarshi",
        last_name="Masid",
        email="saptarshi.masid@kolkata.debtkart.in",
        phone="+91-9830012345",
        employment_status="unemployed",  # Sudden loss of employment
        employer_name="Ex-Tech Solutions Kolkata",
        occupation="Senior Operations Specialist",
        monthly_income=0.0,  # Zero active income following layoff
        address="59, Diamond Harbour Road corridor, Ekbalpur, Khidirpur",
        city="Kolkata",
        state="West Bengal",
        pin_code="700023",
        status="distressed"
    )
    db.add(saptarshi)
    db.flush()

    # Accounts for Mr. Saptarshi
    acc_hdfc = Account(
        customer_id=saptarshi.id,
        account_number="HDFC-0098471203",
        account_type="salary",
        account_name="HDFC Salary Account (Ex-Employer)",
        current_balance=1850.0,
        available_balance=1850.0,
        branch_code="HDFC-KOL-DH",
        ifsc_code="HDFC0000098"
    )
    acc_scb = Account(
        customer_id=saptarshi.id,
        account_number="SCB-7749102834",
        account_type="savings",
        account_name="Standard Chartered Savings Account",
        current_balance=920.0,
        available_balance=920.0,
        branch_code="SCB-KOL-BR",
        ifsc_code="SCBL0036001"
    )
    db.add_all([acc_hdfc, acc_scb])
    db.flush()

    # Three active institution liabilities totaling Rs. 25,30,760:
    # 1. HDFC Bank: Rs. 10,50,000
    loan_hdfc = Loan(
        customer_id=saptarshi.id,
        loan_number="HDFC-PL-982314",
        loan_type="personal",
        lender_name="HDFC Bank",
        product_name="HDFC Personal Loan Facility",
        principal_amount=1050000.0,
        sanctioned_amount=1050000.0,
        outstanding_principal=1050000.0,
        interest_rate=14.5,
        tenure_months=60,
        emi_amount=24700.0,
        status="defaulted"
    )
    # 2. Standard Chartered Bank: Rs. 8,20,760
    loan_scb = Loan(
        customer_id=saptarshi.id,
        loan_number="SCB-CC-552190",
        loan_type="credit_card",
        lender_name="Standard Chartered Bank",
        product_name="Platinum Credit & Overdraft Facility",
        principal_amount=820760.0,
        sanctioned_amount=820760.0,
        outstanding_principal=820760.0,
        interest_rate=36.0,
        tenure_months=36,
        emi_amount=28500.0,
        status="defaulted"
    )
    # 3. RBL Bank: Rs. 6,60,000 (Aggressive recovery agent calls)
    loan_rbl = Loan(
        customer_id=saptarshi.id,
        loan_number="RBL-CR-119834",
        loan_type="credit_card",
        lender_name="RBL Bank",
        product_name="RBL SuperCard Line",
        principal_amount=660000.0,
        sanctioned_amount=660000.0,
        outstanding_principal=660000.0,
        interest_rate=42.0,
        tenure_months=24,
        emi_amount=27500.0,
        status="defaulted"
    )
    db.add_all([loan_hdfc, loan_scb, loan_rbl])
    db.flush()

    # Medical expense transactions (hardship)
    tx1 = Transaction(
        account_id=acc_hdfc.id,
        customer_id=saptarshi.id,
        transaction_type="debit",
        amount=38500.0,
        category="medical",
        description="Emergency Hospitalization - Family Medical Crisis Kolkata",
        balance_after=2350.0
    )
    tx2 = Transaction(
        account_id=acc_hdfc.id,
        customer_id=saptarshi.id,
        transaction_type="debit",
        amount=500.0,
        category="partial_payment",
        description="Partial token payment to RBL recovery agent (unstructured)",
        balance_after=1850.0
    )
    db.add_all([tx1, tx2])

    # Financial Snapshot for Saptarshi
    snap_saptarshi = FinancialSnapshot(
        customer_id=saptarshi.id,
        monthly_income=0.0,
        income_stability_score=10.0,
        total_balance=2770.0,
        average_balance=3500.0,
        minimum_balance=1850.0,
        total_debt=2530760.0,  # EXACT Rs. 25,30,760
        total_emi=80700.0,
        debt_to_income_ratio=99.9,
        emi_to_income_ratio=99.9,
        monthly_expenses=25000.0,  # Ongoing medical bills
        essential_expenses=25000.0,
        discretionary_expenses=0.0,
        savings_rate=0.0,
        emergency_fund_months=0.11
    )
    db.add(snap_saptarshi)

    # Risk Assessment (Critical: 18.5/100)
    risk_saptarshi = RiskAssessment(
        customer_id=saptarshi.id,
        risk_score=18.5,
        risk_category="critical",
        income_stability_score=10.0,
        liquidity_score=5.0,
        debt_burden_score=5.0,
        payment_behavior_score=20.0,
        credit_utilization_score=15.0,
        previous_score=32.0,
        score_change=-13.5,
        trend="declining",
        weights={
            "income_stability": settings.WEIGHT_INCOME_STABILITY,
            "liquidity": settings.WEIGHT_LIQUIDITY,
            "debt_burden": settings.WEIGHT_DEBT_BURDEN,
            "payment_behavior": settings.WEIGHT_PAYMENT_BEHAVIOR,
            "credit_utilization": settings.WEIGHT_CREDIT_UTILIZATION
        },
        risk_factors=[
            {"factor": "income_stability", "impact": "critical", "description": "Loss of primary employment eliminated monthly cashflow."},
            {"factor": "debt_burden", "impact": "critical", "description": "Total multi-lender exposure of Rs. 25,30,760 across 3 banks."},
            {"factor": "recovery_harassment", "impact": "critical", "description": "Persistent intimidatory calls and third-party reference contact attempts by RBL Bank."},
            {"factor": "liquidity", "impact": "high", "description": "Liquid cash depleted to Rs. 2,770 amidst ongoing medical expenditures."}
        ],
        ml_distress_probability=0.9650
    )
    db.add(risk_saptarshi)

    # Debtkart Legal Intervention Entity
    legal_saptarshi = LegalIntervention(
        customer_id=saptarshi.id,
        case_reference_id="DK-KOL-253076",
        legal_firm=settings.DEBTKART_LEGAL_ENTITY,
        lead_counsel_contact=settings.DEBTKART_PHONE,
        counsel_email=settings.DEBTKART_EMAIL,
        registered_office=settings.DEBTKART_ADDRESS,
        total_exposure_amount=2530760.0,
        hardship_reason="Sudden involuntary employment termination coupled with ongoing family medical emergencies",
        creditor_banks=["HDFC Bank", "Standard Chartered Bank", "RBL Bank"],
        rbi_fair_practices_invoked=True,
        third_party_harassment_restrained=True,
        civil_vs_criminal_rebuttal_issued=True,
        moratorium_granted_months=6,
        moratorium_start_date=datetime.date.today() - datetime.timedelta(days=120),
        moratorium_end_date=datetime.date.today() + datetime.timedelta(days=60),
        settlement_status="negotiated_settlement",
        final_settlement_amount=635600.0,  # EXACT Rs. 6,35,600
        liability_reduction_amount=1895160.0,  # EXACT Rs. 18,95,160 SAVED
        savings_percentage=74.88,
        resolution_mode="Structured multi-bank legal intervention and negotiated settlements",
        legal_notices_sent=[
            {"bank": "HDFC Bank", "notice_ref": "DK/NTC/HDFC/2026/01", "date": "2026-05-10", "status": "Delivered & Settlement Executed"},
            {"bank": "Standard Chartered Bank", "notice_ref": "DK/NTC/SCB/2026/02", "date": "2026-05-12", "status": "Delivered & Settlement Executed"},
            {"bank": "RBL Bank", "notice_ref": "DK/NTC/RBL/2026/03", "date": "2026-05-14", "status": "Harassment Restrained & Settlement Executed"}
        ]
    )
    db.add(legal_saptarshi)

    # =========================================================================
    # 3. BENCHMARK HEALTHY CUSTOMER (Ananya Roy)
    # =========================================================================
    ananya = Customer(
        first_name="Ananya",
        last_name="Roy",
        email="ananya.roy@example.com",
        phone="+91-9876543210",
        employment_status="employed",
        employer_name="Tata Consultancy Services Kolkata",
        occupation="Lead Software Architect",
        monthly_income=95000.0,
        address="Sector V, Salt Lake",
        city="Kolkata",
        state="West Bengal",
        pin_code="700091",
        status="active"
    )
    db.add(ananya)
    db.flush()

    acc_ananya = Account(
        customer_id=ananya.id,
        account_number="HDFC-9918273645",
        account_type="salary",
        account_name="HDFC Preferred Salary Account",
        current_balance=245000.0,
        available_balance=245000.0
    )
    db.add(acc_ananya)
    db.flush()

    loan_ananya = Loan(
        customer_id=ananya.id,
        loan_number="SBI-HL-772819",
        loan_type="home",
        lender_name="State Bank of India",
        principal_amount=3200000.0,
        sanctioned_amount=3200000.0,
        outstanding_principal=2400000.0,
        interest_rate=8.5,
        tenure_months=240,
        emi_amount=22500.0,
        status="active"
    )
    db.add(loan_ananya)

    snap_ananya = FinancialSnapshot(
        customer_id=ananya.id,
        monthly_income=95000.0,
        total_balance=245000.0,
        average_balance=230000.0,
        minimum_balance=180000.0,
        total_debt=2400000.0,
        total_emi=22500.0,
        debt_to_income_ratio=2.1,
        emi_to_income_ratio=0.237,
        monthly_expenses=38000.0,
        essential_expenses=28000.0,
        discretionary_expenses=10000.0,
        savings_rate=0.363,
        emergency_fund_months=8.75
    )
    db.add(snap_ananya)

    risk_ananya = RiskAssessment(
        customer_id=ananya.id,
        risk_score=84.5,
        risk_category="healthy",
        income_stability_score=95.0,
        liquidity_score=92.0,
        debt_burden_score=80.0,
        payment_behavior_score=100.0,
        credit_utilization_score=85.0,
        trend="improving",
        risk_factors=[]
    )
    db.add(risk_ananya)

    # Commit all
    db.commit()
    print("[FinShield Seeder] Successfully seeded PostgreSQL with all benchmark customers and Debtkart Kolkata case study.")
