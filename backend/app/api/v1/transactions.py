from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models.database import get_db, Transaction, Account, Customer
from backend.app.schemas.schemas import TransactionCreate, ApiResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=ApiResponse)
def get_transactions(
    customer_id: Optional[str] = None,
    account_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Lists transactions with pagination and category filtering."""
    query = db.query(Transaction)
    if customer_id:
        query = query.filter(Transaction.customer_id == customer_id)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if category:
        query = query.filter(Transaction.category == category)
        
    total_count = query.count()
    txs = query.order_by(Transaction.transaction_date.desc()).offset(offset).limit(limit).all()
    
    results = [
        {
            "id": t.id,
            "account_id": t.account_id,
            "customer_id": t.customer_id,
            "transaction_date": t.transaction_date.isoformat(),
            "transaction_type": t.transaction_type,
            "amount": t.amount,
            "category": t.category,
            "sub_category": t.sub_category,
            "description": t.description,
            "balance_after": t.balance_after
        }
        for t in txs
    ]
    return ApiResponse(data={"transactions": results, "total_count": total_count, "limit": limit, "offset": offset})

@router.post("", response_model=ApiResponse)
def create_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == tx_in.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    # Update account balance
    if tx_in.transaction_type == "credit":
        account.current_balance += tx_in.amount
        account.available_balance += tx_in.amount
    else:
        account.current_balance -= tx_in.amount
        account.available_balance -= tx_in.amount
        
    tx = Transaction(
        account_id=account.id,
        customer_id=account.customer_id,
        transaction_type=tx_in.transaction_type,
        amount=tx_in.amount,
        category=tx_in.category,
        description=tx_in.description,
        balance_after=account.current_balance
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    
    return ApiResponse(
        message="Transaction recorded successfully",
        data={
            "id": tx.id,
            "amount": tx.amount,
            "balance_after": tx.balance_after,
            "category": tx.category
        }
    )
