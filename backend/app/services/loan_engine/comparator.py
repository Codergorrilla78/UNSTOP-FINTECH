from typing import List, Dict, Any
from backend.app.config.settings import settings
from backend.app.services.financial_engine.emi import calculate_emi

def compare_and_rank_loans(
    loan_amount: float,
    tenure_months: int,
    monthly_income: float,
    current_total_emi: float,
    current_resilience_score: float,
    available_products: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates and ranks multi-lender loan options using composite Best-Fit scoring.
    Compliant with FR-006.
    """
    analyzed_products = []
    
    for product in available_products:
        lender_name = product.get("lender_name", "Bank")
        product_name = product.get("product_name", "Personal Loan")
        interest_rate = product.get("interest_rate", 12.0)
        proc_fee_pct = product.get("processing_fee_percent", 1.0)
        proc_fee_fixed = product.get("processing_fee_fixed", 0.0)
        
        # EMI and costs
        emi = calculate_emi(loan_amount, interest_rate, tenure_months)
        total_interest = round((emi * tenure_months) - loan_amount, 2)
        total_repayment = round(emi * tenure_months, 2)
        processing_fee = round((loan_amount * proc_fee_pct / 100.0) + proc_fee_fixed, 2)
        total_cost = round(total_repayment + processing_fee, 2)
        
        # Affordability
        new_total_emi = current_total_emi + emi
        new_foir = round(new_total_emi / monthly_income, 3) if monthly_income > 0 else 1.0
        monthly_surplus = round(monthly_income - new_total_emi, 2)
        is_affordable = new_foir <= 0.50 and monthly_surplus > 0
        
        # Risk impact
        projected_score = max(5.0, round(current_resilience_score - (new_foir * 15.0), 1))
        score_change = round(projected_score - current_resilience_score, 1)
        
        # Multi-attribute scoring (0 to 100)
        cost_score = max(10.0, 100.0 - ((interest_rate - 9.0) * 8.0))
        affordability_score = max(10.0, 100.0 - (new_foir * 120.0)) if new_foir <= 0.8 else 10.0
        resilience_score = max(10.0, projected_score)
        tenure_score = 85.0 if 12 <= tenure_months <= 36 else 70.0
        fee_score = max(20.0, 100.0 - (proc_fee_pct * 30.0))
        flexibility_score = 80.0 if product.get("prepayment_charges_percent", 2.0) <= 1.0 else 65.0
        
        w = {
            "cost": settings.LOAN_WEIGHT_TOTAL_COST,
            "affordability": settings.LOAN_WEIGHT_EMI_AFFORDABILITY,
            "resilience": settings.LOAN_WEIGHT_RESILIENCE_IMPACT,
            "tenure": settings.LOAN_WEIGHT_TENURE_SUITABILITY,
            "fees": settings.LOAN_WEIGHT_FEES,
            "flexibility": settings.LOAN_WEIGHT_FLEXIBILITY
        }
        
        composite_score = round(
            (cost_score * w["cost"]) +
            (affordability_score * w["affordability"]) +
            (resilience_score * w["resilience"]) +
            (tenure_score * w["tenure"]) +
            (fee_score * w["fees"]) +
            (flexibility_score * w["flexibility"]),
            1
        )
        
        analyzed_products.append({
            "product_id": product.get("id"),
            "lender_name": lender_name,
            "product_name": product_name,
            "interest_rate": interest_rate,
            "emi": emi,
            "total_interest": total_interest,
            "total_repayment": total_repayment,
            "processing_fee": processing_fee,
            "total_cost": total_cost,
            "affordability": {
                "emi_to_income_ratio": new_foir,
                "monthly_surplus_after_emi": monthly_surplus,
                "affordable": is_affordable
            },
            "impact": {
                "projected_risk_score": projected_score,
                "risk_score_change": score_change
            },
            "scores": {
                "total_cost_score": round(cost_score, 1),
                "affordability_score": round(affordability_score, 1),
                "resilience_impact_score": round(resilience_score, 1),
                "tenure_score": round(tenure_score, 1),
                "fees_score": round(fee_score, 1),
                "flexibility_score": round(flexibility_score, 1),
                "composite_score": composite_score
            },
            "is_best_fit": False,
            "recommendation_reason": ""
        })
        
    # Rank descending by composite score
    analyzed_products.sort(key=lambda x: x["scores"]["composite_score"], reverse=True)
    
    # Set best-fit and rankings
    for idx, item in enumerate(analyzed_products):
        item["rank"] = idx + 1
        if idx == 0:
            item["is_best_fit"] = True
            item["recommendation_reason"] = (
                f"Selected as the Best-Fit loan because it provides the optimal balance of "
                f"manageable monthly EMI (₹{item['emi']:,.0f}), competitive rate ({item['interest_rate']}%), "
                f"and least adverse impact on financial resilience."
            )
        else:
            item["recommendation_reason"] = f"Rank {idx + 1} option based on multi-factor affordability and cost trade-offs."
            
    best_product = analyzed_products[0] if analyzed_products else None
    
    return {
        "loan_amount": loan_amount,
        "tenure_months": tenure_months,
        "products": analyzed_products,
        "best_fit_product_id": best_product["product_id"] if best_product else None,
        "best_fit_reason": best_product["recommendation_reason"] if best_product else None,
        "weights_used": {
            "total_cost": settings.LOAN_WEIGHT_TOTAL_COST,
            "affordability": settings.LOAN_WEIGHT_EMI_AFFORDABILITY,
            "resilience_impact": settings.LOAN_WEIGHT_RESILIENCE_IMPACT,
            "tenure": settings.LOAN_WEIGHT_TENURE_SUITABILITY,
            "fees": settings.LOAN_WEIGHT_FEES,
            "flexibility": settings.LOAN_WEIGHT_FLEXIBILITY
        }
    }
