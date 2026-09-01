from fastapi import APIRouter
from app.services.engagement_service import engagement_service
from app.services.attrition_service import attrition_service

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard"])

@router.get("/summary")
def get_executive_summary():
    """
    Returns enterprise-wide headcount, flight-risk count, and engagement KPIs.
    """
    return engagement_service.get_overview_metrics()

@router.get("/attrition-by-department")
def get_department_attrition_metrics():
    """
    Returns breakdown of headcount, high risk count, and avg risk percentage by department.
    """
    return attrition_service.get_department_risk_summary()

@router.get("/burnout-hotspots")
def get_burnout_hotspots():
    """
    Returns employees with elevated burnout indicators (high overtime & low work-life balance).
    """
    return engagement_service.get_burnout_hotspots()
