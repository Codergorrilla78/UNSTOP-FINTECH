from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    monthly_income = Column(Float, nullable=False)

    monthly_expenses = Column(Float, nullable=False)
    monthly_debt_payment = Column(Float, default=0)

    savings = Column(Float, default=0)
    existing_debt = Column(Float, default=0)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class FinancialAnalysis(Base):
    __tablename__ = "financial_analysis"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, nullable=False)

    resilience_score = Column(Float, nullable=False)

    monthly_surplus = Column(Float)
    debt_to_income = Column(Float)
    emergency_months = Column(Float)

    risk_level = Column(String)

    recommendation = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )