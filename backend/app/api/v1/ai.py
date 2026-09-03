from fastapi import APIRouter
from backend.app.schemas.schemas import ApiResponse, AIExplainRequest
from backend.app.services.ai_service.explainer import generate_ai_explanation

router = APIRouter(prefix="/ai", tags=["AI Explanations"])

@router.post("/explain", response_model=ApiResponse)
def explain_financial_context(req: AIExplainRequest):
    """Generates context-aware, explainable natural language financial and legal insights."""
    result = generate_ai_explanation(req.context_type, req.context_data)
    return ApiResponse(data=result)
