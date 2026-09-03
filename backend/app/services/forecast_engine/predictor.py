import datetime
from typing import Dict, Any, List
from backend.app.config.settings import settings

def generate_90_day_cashflow_forecast(
    current_balance: float,
    monthly_income: float,
    salary_day_of_month: int,
    active_emis: List[Dict[str, Any]],  # List of {emi_amount, due_day, lender_name}
    monthly_essential_expenses: float,
    monthly_discretionary_expenses: float,
    forecast_days: int = 90
) -> Dict[str, Any]:
    """
    Simulates day-by-day cashflow over 90 days.
    Identifies liquidity cliffs, negative balance risks, and salary bridge intervals.
    """
    start_date = datetime.date.today()
    projections = []
    low_balance_alerts = []
    
    running_balance = current_balance
    min_balance = current_balance
    min_balance_date = start_date
    negative_balance_days = 0
    
    # Calculate daily baseline burn for non-EMI expenses
    daily_essential_burn = monthly_essential_expenses / 30.0
    daily_discretionary_burn = monthly_discretionary_expenses / 30.0
    
    for day_idx in range(forecast_days):
        current_date = start_date + datetime.timedelta(days=day_idx)
        day_of_month = current_date.day
        
        inflow = 0.0
        outflow = round(daily_essential_burn + daily_discretionary_burn, 2)
        notes = []
        
        # Salary Inflow (if employed / receiving income)
        if day_of_month == salary_day_of_month and monthly_income > 0:
            inflow += monthly_income
            notes.append(f"Salary credited: +₹{monthly_income:,.0f}")
            
        # EMI Outflows
        for emi_item in active_emis:
            if emi_item.get("due_day") == day_of_month:
                emi_amt = emi_item.get("emi_amount", 0.0)
                outflow += emi_amt
                lender = emi_item.get("lender_name", "Lender")
                notes.append(f"EMI due ({lender}): -₹{emi_amt:,.0f}")
                
        # Update running balance
        running_balance = round(running_balance + inflow - outflow, 2)
        
        if running_balance < min_balance:
            min_balance = running_balance
            min_balance_date = current_date
            
        if running_balance < 0:
            negative_balance_days += 1
            
        # Check low balance alert
        if running_balance <= settings.CRITICAL_LOW_BALANCE:
            alert_entry = {
                "date": current_date.isoformat(),
                "projected_balance": running_balance,
                "reason": "Balance below safe liquidity threshold (₹5,000)" if running_balance > 0 else "Negative liquidity deficit / Overdraft trigger"
            }
            if day_idx % 5 == 0 or running_balance < 0:  # Sample alerts
                low_balance_alerts.append(alert_entry)
                
        projections.append({
            "date": current_date.isoformat(),
            "projected_balance": running_balance,
            "inflows": round(inflow, 2),
            "outflows": round(outflow, 2),
            "notes": "; ".join(notes) if notes else "Routine daily expenses"
        })
        
    avg_balance = round(sum(p["projected_balance"] for p in projections) / len(projections), 2)
    confidence = "high" if monthly_income > 0 else "medium"
    
    return {
        "forecast_generated_at": datetime.datetime.utcnow().isoformat(),
        "forecast_period": {
            "start_date": start_date.isoformat(),
            "end_date": (start_date + datetime.timedelta(days=forecast_days)).isoformat()
        },
        "current_balance": current_balance,
        "daily_projections": projections,
        "summary": {
            "minimum_balance": min_balance,
            "minimum_balance_date": min_balance_date.isoformat(),
            "average_balance": avg_balance,
            "negative_balance_days": negative_balance_days,
            "low_balance_alerts": low_balance_alerts[:10]
        },
        "confidence_level": confidence
    }
