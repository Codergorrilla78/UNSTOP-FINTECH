from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config.settings import settings
from backend.app.models.database import Base, engine, SessionLocal
from backend.app.seed.seeder import seed_database
from backend.app.api.v1 import api_v1_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed database with initial data on startup
try:
    with SessionLocal() as db:
        seed_database(db)
except Exception as e:
    print(f"[FinShield] Seeder notice: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Banking Financial-Resilience Platform & Responsible Lending API",
    version=settings.VERSION
)

# CORS middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 routes
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health_check():
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "database": "postgresql (with sqlite fallback resilience)",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "engines": [
                "financial_engine",
                "risk_engine",
                "forecast_engine",
                "ml_engine",
                "overdraft_engine",
                "loan_engine",
                "simulator_engine",
                "intervention_engine",
                "debtkart_service",
                "ai_service"
            ]
        }
    }


@app.get("/")
def root():
    return {
        "success": True,
        "message": f"{settings.PROJECT_NAME} is running",
        "data": {
            "partner": f"{settings.DEBTKART_BRAND} ({settings.DEBTKART_LEGAL_ENTITY})",
            "helpline": settings.DEBTKART_PHONE,
            "version": settings.VERSION,
            "docs": "/docs",
            "api_prefix": settings.API_V1_PREFIX
        }
    }