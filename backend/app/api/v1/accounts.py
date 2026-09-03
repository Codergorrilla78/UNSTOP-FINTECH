from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models.database import get_db, Account, Customer
from backend.app.schemas.schemas import ApiResponse

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("", response_model=ApiResponse)
def get_accounts(
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves all accounts for current customer."""
    query = db.query(Account)
    if customer_id:
        query = query.filter(Account.customer_id == customer_id)
    else:
        # Default to first customer (Mr. Saptarshi Masid)
        first_cust = db.query(Customer).first()
        if first_cust:
            query = query.filter(Account.customer_id == first_cust.id)
            
    accounts = query.all()
    results = [
        {
            "id": a.id,
            "customer_id": a.customer_id,
            "account_number": a.account_number,
            "account_type": a.account_type,
            "account_name": a.account_name,
            "current_balance": a.current_balance,
            "available_balance": a.available_balance,
            "branch_code": a.branch_code,
            "ifsc_code": a.ifsc_code,
            "status": a.status
        }
        for a in accounts
    ]
    return ApiResponse(data={"accounts": results, "total_balance": sum(a["current_balance"] for a in results)})

@router.get("/{account_id}", response_model=ApiResponse)
def get_account_by_id(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return ApiResponse(
        data={
            "id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "account_name": account.account_name,
            "current_balance": account.current_balance,
            "available_balance": account.available_balance,
            "status": account.status
        }
    )
