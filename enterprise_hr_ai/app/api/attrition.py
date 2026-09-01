from fastapi import APIRouter, HTTPException, Query
from app.validation.employee_schema import EmployeeInputSchema, AttritionPredictionResponse, BatchAttritionRequest
from app.services.attrition_service import attrition_service
from typing import List, Dict, Any

router = APIRouter(prefix="/attrition", tags=["Attrition Prediction"])

@router.post("/predict", response_model=AttritionPredictionResponse)
def predict_employee_attrition(
    employee: EmployeeInputSchema,
    model_version: str = Query(default="v2", description="Model version: v1 or v2")
):
    """
    Predicts single employee attrition probability and identifies top contributing flight-risk drivers.
    """
    try:
        res = attrition_service.predict_attrition(employee.model_dump(), model_version=model_version)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch-predict")
def batch_predict_attrition(
    request: BatchAttritionRequest,
    model_version: str = Query(default="v2")
):
    """
    Batch prediction endpoint for workforce rosters.
    """
    results = []
    for emp in request.employees:
        res = attrition_service.predict_attrition(emp.model_dump(), model_version=model_version)
        results.append(res)
    return {"total_evaluated": len(results), "predictions": results}

@router.get("/high-risk-roster", response_model=List[Dict[str, Any]])
def get_high_risk_employees(limit: int = Query(default=30, ge=1, le=200)):
    """
    Returns list of highest flight-risk personnel requiring HR intervention.
    """
    return attrition_service.get_high_risk_roster(limit=limit)
