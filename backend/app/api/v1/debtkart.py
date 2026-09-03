from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.database import get_db, Customer, LegalIntervention
from backend.app.schemas.schemas import ApiResponse, DebtkartNoticeRequest
from backend.app.services.debtkart_service.service import (
    get_saptarshi_masid_case_study, generate_debtkart_legal_notice
)
from backend.app.config.settings import settings

router = APIRouter(prefix="/debtkart", tags=["Debtkart Legal Intervention (Real-World Case Study)"])

@router.get("/case-study/saptarshi-masid", response_model=ApiResponse)
def get_case_study():
    """
    Returns the real-world Kolkata case study of Mr. Saptarshi Masid:
    - Total Loan Exposure: Rs. 25,30,760
    - Multi-Lender Breakdown: HDFC Bank, Standard Chartered Bank, RBL Bank
    - Hardship: Employment loss + family medical emergency
    - Final Negotiated Settlement: Rs. 6,35,600 (74.88% / Rs. 18,95,160 saved!)
    """
    data = get_saptarshi_masid_case_study()
    return ApiResponse(
        message="Debtkart Real-World Kolkata Case Study: Mr. Saptarshi Masid",
        data=data
    )

@router.get("/info", response_model=ApiResponse)
def get_debtkart_info():
    """Returns official contact and credentials for Debtkart (Settlend Legal Advisors LLP)."""
    return ApiResponse(
        data={
            "legal_entity": settings.DEBTKART_LEGAL_ENTITY,
            "brand": settings.DEBTKART_BRAND,
            "primary_phone": settings.DEBTKART_PHONE,
            "alternate_phones": settings.DEBTKART_ALT_PHONES,
            "primary_email": settings.DEBTKART_EMAIL,
            "operations_email": settings.DEBTKART_OPS_EMAIL,
            "address": settings.DEBTKART_ADDRESS,
            "duns_number": settings.DEBTKART_DUNS,
            "operating_hours": settings.DEBTKART_HOURS,
            "practice_areas": [
                "Loan Settlement & Negotiation",
                "RBI Fair Practices Code Enforcement",
                "Recovery Agent Harassment Injunction",
                "Alternate Dispute Resolution (ADR) & Mediation",
                "Virtual Court & Regulatory Representation",
                "Credit Repair Advisory"
            ]
        }
    )

@router.post("/generate-notice", response_model=ApiResponse)
def generate_legal_notice(req: DebtkartNoticeRequest, db: Session = Depends(get_db)):
    """Generates formal multi-bank legal notice asserting RBI Fair Practices Code and moratorium."""
    customer = db.query(Customer).filter(Customer.id == req.customer_id).first()
    client_name = f"{customer.first_name} {customer.last_name}" if customer else "Mr. Saptarshi Masid"
    
    notice_result = generate_debtkart_legal_notice(
        client_name=client_name,
        lender_name=req.lender_name,
        account_number=req.account_number,
        outstanding_amount=req.outstanding_amount,
        hardship_reason=req.hardship_details,
        moratorium_months=req.request_moratorium_months
    )
    return ApiResponse(message="Formal legal notice prepared successfully", data=notice_result)

@router.get("/settlement-status/{customer_id}", response_model=ApiResponse)
def get_customer_settlement_status(customer_id: str, db: Session = Depends(get_db)):
    """Retrieves legal intervention record and bank-wise settlement ledger."""
    legal_record = db.query(LegalIntervention).filter(LegalIntervention.customer_id == customer_id).first()
    if not legal_record:
        # Check if first customer
        legal_record = db.query(LegalIntervention).first()
        
    if not legal_record:
        raise HTTPException(status_code=404, detail="No legal intervention record found")
        
    return ApiResponse(
        data={
            "case_reference_id": legal_record.case_reference_id,
            "legal_firm": legal_record.legal_firm,
            "total_exposure": legal_record.total_exposure_amount,
            "final_settlement": legal_record.final_settlement_amount,
            "liability_reduction": legal_record.liability_reduction_amount,
            "savings_percentage": legal_record.savings_percentage,
            "settlement_status": legal_record.settlement_status,
            "moratorium_months": legal_record.moratorium_granted_months,
            "moratorium_dates": {
                "start": str(legal_record.moratorium_start_date),
                "end": str(legal_record.moratorium_end_date) if legal_record.moratorium_end_date else None
            },
            "creditor_banks": legal_record.creditor_banks,
            "legal_notices": legal_record.legal_notices_sent,
            "lead_counsel_contact": legal_record.lead_counsel_contact,
            "counsel_email": legal_record.counsel_email
        }
    )
