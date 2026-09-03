from fastapi import APIRouter
from backend.app.api.v1.customers import router as customers_router
from backend.app.api.v1.accounts import router as accounts_router
from backend.app.api.v1.transactions import router as transactions_router
from backend.app.api.v1.financial_health import router as financial_health_router
from backend.app.api.v1.risk import router as risk_router
from backend.app.api.v1.forecast import router as forecast_router
from backend.app.api.v1.interventions import router as interventions_router
from backend.app.api.v1.overdraft import router as overdraft_router
from backend.app.api.v1.loans import router as loans_router
from backend.app.api.v1.simulator import router as simulator_router
from backend.app.api.v1.recommendations import router as recommendations_router
from backend.app.api.v1.ai import router as ai_router
from backend.app.api.v1.officer import router as officer_router
from backend.app.api.v1.debtkart import router as debtkart_router

api_v1_router = APIRouter()

api_v1_router.include_router(customers_router)
api_v1_router.include_router(accounts_router)
api_v1_router.include_router(transactions_router)
api_v1_router.include_router(financial_health_router)
api_v1_router.include_router(risk_router)
api_v1_router.include_router(forecast_router)
api_v1_router.include_router(interventions_router)
api_v1_router.include_router(overdraft_router)
api_v1_router.include_router(loans_router)
api_v1_router.include_router(simulator_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(officer_router)
api_v1_router.include_router(debtkart_router)

__all__ = ["api_v1_router"]
