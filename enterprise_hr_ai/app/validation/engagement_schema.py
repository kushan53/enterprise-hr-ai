from pydantic import BaseModel, Field
from typing import Optional, List

class EngagementSurveyInput(BaseModel):
    EmployeeID: int
    EngagementScore: float = Field(..., ge=0, le=100)
    SatisfactionScore: float = Field(..., ge=1, le=5)
    WorkLifeBalanceScore: float = Field(..., ge=-5.0, le=10.0)

class SkillGapRequest(BaseModel):
    EmployeeID: Optional[int] = None
    CurrentRole: str
    TargetRole: str
    CurrentSkills: List[str] = []

class SkillGapResponse(BaseModel):
    EmployeeID: Optional[int]
    CurrentRole: str
    TargetRole: str
    MatchedSkills: List[str]
    MissingSkills: List[str]
    ReadinessScoreToday: float
    ProjectedReadinessAfterPlan: float
    RecommendedCourses: List[dict]
    ActionPlan: str
