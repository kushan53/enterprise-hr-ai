from fastapi import APIRouter, HTTPException, Query
from app.validation.engagement_schema import SkillGapRequest, SkillGapResponse
from app.services.skill_gap_service import skill_gap_service
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/skills", tags=["Skills & Upskilling"])

@router.post("/gap-analysis", response_model=SkillGapResponse)
def evaluate_skill_gap(request: SkillGapRequest):
    """
    Computes individual skill gaps, current readiness, projected readiness, and matched upskilling courses.
    """
    try:
        res = skill_gap_service.calculate_employee_skill_gap(
            current_role=request.CurrentRole,
            target_role=request.TargetRole,
            current_skills=request.CurrentSkills,
            employee_id=request.EmployeeID
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/organization-gaps")
def get_org_wide_skill_gaps():
    """
    Returns enterprise-wide skill shortfalls, severity ratings, and hire-vs-reskill targets.
    """
    return skill_gap_service.get_organization_gaps()

@router.get("/courses")
def list_available_courses():
    """
    Returns the internal and external upskilling course catalog.
    """
    return recommendation_service.get_all_courses()

@router.get("/employee-recommendation/{employee_id}")
def get_single_employee_recommendation(employee_id: int):
    """
    Returns personalized recommendation card for a single employee ID.
    """
    res = recommendation_service.get_employee_recommendation(employee_id)
    if "message" in res and res["message"] == "Employee not found":
        raise HTTPException(status_code=404, detail="Employee record not found")
    return res
