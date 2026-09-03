from typing import Dict, Any, List
from backend.app.config.settings import settings

def get_saptarshi_masid_case_study() -> Dict[str, Any]:
    """
    Returns the real-world Kolkata case study of Mr. Saptarshi Masid,
    documented by Debtkart (SETTLEND LEGAL ADVISORS LLP).
    """
    return {
        "client_name": "Mr. Saptarshi Masid",
        "location": "Kolkata, West Bengal (Diamond Harbour Road corridor)",
        "total_exposure_amount": 2530760.0,
        "final_settlement_amount": 635600.0,
        "liability_reduction_amount": 1895160.0,
        "savings_percentage": 74.88,
        "hardship_background": (
            "Mr. Saptarshi Masid, a resident of Kolkata with a previously flawless repayment track record, "
            "was plunged into severe financial distress due to involuntary employment loss (complete elimination "
            "of primary income) combined with ongoing heavy medical expenses for himself and dependent family members. "
            "He held active liabilities across three major financial institutions: HDFC Bank, Standard Chartered Bank, "
            "and RBL Bank, totaling Rs. 25,30,760."
        ),
        "creditor_breakdown": [
            {
                "lender_name": "HDFC Bank",
                "liability_type": "Personal Loan & Credit Facility",
                "original_dues": 1050000.0,
                "settled_amount": 260000.0,
                "reduction_percent": 75.24,
                "status": "Settlement Letter Received"
            },
            {
                "lender_name": "Standard Chartered Bank",
                "liability_type": "Credit Card & Overdraft Balance",
                "original_dues": 820760.0,
                "settled_amount": 205600.0,
                "reduction_percent": 74.95,
                "status": "Settlement Letter Received"
            },
            {
                "lender_name": "RBL Bank",
                "liability_type": "Credit Card Liability (Aggressive Recovery)",
                "original_dues": 660000.0,
                "settled_amount": 170000.0,
                "reduction_percent": 74.24,
                "status": "Settlement Letter Received"
            }
        ],
        "harassment_challenges": [
            "Persistent, non-stop abusive and coercive recovery calls throughout the day and night",
            "Intimidatory recovery tactics specifically deployed by recovery agents representing RBL Bank",
            "Unauthorized contact attempts and character defamation to references, employers, and personal contact lists",
            "Severe psychological and emotional distress leading to breakdown of family well-being",
            "Fragmented partial payments: client attempted small payments that only sank into interest penalties without lowering principal"
        ],
        "legal_strategy_actions": [
            "Immediate issuance of formal legal notices from Settlend Legal Advisors LLP to HDFC, Standard Chartered, and RBL Bank",
            "Formal documentation establishing that default was involuntary, genuine, and devoid of dishonest or wilful intent",
            "Assertion of core constitutional and legal distinction: Civil contractual default CANNOT be criminalized as fraud",
            "Enforcement of Reserve Bank of India (RBI) Fair Practices Code and statutory borrower privacy mandates",
            "Strict prohibition on calling third parties, references, or relatives under threat of regulatory escalation",
            "Demanded an enforceable 4 to 6-month financial stabilization moratorium",
            "Channelized all communication strictly through Debtkart as authorized legal representatives"
        ],
        "moratorium_details": {
            "period_granted": "6 Months Moratorium",
            "harassment_reduction": "100% cease of unauthorized agent visits and calls",
            "legal_standing": "Full regulatory compliance under RBI Master Directions"
        },
        "legal_counsel": {
            "firm_name": settings.DEBTKART_LEGAL_ENTITY,
            "trading_as": settings.DEBTKART_BRAND,
            "primary_phone": settings.DEBTKART_PHONE,
            "alternate_phones": settings.DEBTKART_ALT_PHONES,
            "primary_email": settings.DEBTKART_EMAIL,
            "operations_email": settings.DEBTKART_OPS_EMAIL,
            "registered_address": settings.DEBTKART_ADDRESS,
            "duns_number": settings.DEBTKART_DUNS,
            "working_hours": settings.DEBTKART_HOURS
        },
        "outcomes": [
            "Total debt exposure of Rs. 25,30,760 successfully resolved for Rs. 6,35,600",
            "Massive savings of Rs. 18,95,160 (74.88% liability reduction)",
            "Complete cessation of recovery harassment and restoration of borrower peace of mind",
            "Formal No Dues / Settlement Certificates issued by all three banking institutions"
        ],
        "key_learnings": [
            "Partial payments without a coordinated legal strategy only burn capital on fees and penalties without solving multi-lender distress",
            "Loss of employment and medical hardship require structured legal positioning early to preempt unlawful escalation",
            "Borrowers have statutory protections: coercive recovery tactics violate RBI guidelines and can be challenged legally",
            "Consolidating negotiations through authorized legal counsel balances leverage against institutional lenders"
        ]
    }

def generate_debtkart_legal_notice(
    client_name: str,
    lender_name: str,
    account_number: str,
    outstanding_amount: float,
    hardship_reason: str,
    moratorium_months: int = 6
) -> Dict[str, Any]:
    """
    Generates structured formal legal notice under RBI Fair Practices Code
    on behalf of Debtkart (Settlend Legal Advisors LLP).
    """
    notice_text = f"""
FORMAL LEGAL NOTICE & REBUTTAL UNDER RBI FAIR PRACTICES CODE
Issued by: {settings.DEBTKART_LEGAL_ENTITY} (T/A "{settings.DEBTKART_BRAND}")
Address: {settings.DEBTKART_ADDRESS}
Contact: {settings.DEBTKART_PHONE} | Email: {settings.DEBTKART_EMAIL}

TO:
The Authorized Officer / Grievance Redressal Officer
{lender_name}

IN RE: LOAN / CREDIT ACCOUNT NO: {account_number}
CLIENT NAME: {client_name}
TOTAL STATED OUTSTANDING: INR {outstanding_amount:,.2f}

SIR/MADAM,

Under instructions and on behalf of our client, {client_name}, we hereby address this formal notice to place the following critical facts and legal assertions upon your institutional record:

1. BONA FIDE DISTRESS & INVOLUNTARY DEFAULT:
Our client has maintained a consistent and honorable repayment history. The inability to sustain the current repayment schedule arises strictly from involuntary, catastrophic hardship—namely: {hardship_reason}. Our client retains bona fide intent to resolve all legitimate obligations in a fair and lawful manner.

2. REBUTTAL AGAINST COERCIVE PRACTICES & CRIMINAL ALLEGATIONS:
Any imputation of fraudulent intent or criminal liability is vehemently rejected. In accordance with settled jurisprudence of the Hon'ble Supreme Court of India, a breach of loan agreement is purely a civil contractual dispute. Any threat to initiate criminal proceedings or police complaints constitutes actionable intimidation.

3. IMMEDIATE CEASE & DESIST ON UNLAWFUL RECOVERY:
Recovery agents acting on your behalf must immediately cease and desist from:
(a) Placing persistent calls outside RBI-mandated hours (08:00 to 19:00 hrs).
(b) Contacting unauthorized third parties, family members, workplace colleagues, or reference contact lists.
(c) Utilizing intimidating, abusive, or coercive language.

4. DEMAND FOR FINANCIAL STABILIZATION MORATORIUM:
We formally demand a temporary moratorium of {moratorium_months} months to enable financial stabilization, during which all coercive actions, interest compounding, and penal levies shall remain suspended.

5. EXCLUSIVE LEGAL CHANNEL:
Take notice that all future correspondence, settlement proposals, and communications concerning this account MUST be routed exclusively through our office at {settings.DEBTKART_EMAIL} or contact {settings.DEBTKART_PHONE}.

Yours faithfully,
For {settings.DEBTKART_LEGAL_ENTITY}
Authorized Legal Counsel
"""
    return {
        "status": "generated",
        "client_name": client_name,
        "lender_name": lender_name,
        "account_number": account_number,
        "moratorium_months": moratorium_months,
        "notice_content": notice_text.strip()
    }
