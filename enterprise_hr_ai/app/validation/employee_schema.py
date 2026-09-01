from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class EmployeeInputSchema(BaseModel):
    EmployeeID: Optional[int] = Field(default=9999, description="Employee unique identifier")
    Age: int = Field(..., ge=18, le=99, description="Employee age (between 18 and 99)")
    Department: str = Field(..., description="Department name (e.g. Sales, IT, Finance, HR, Support, Marketing)")
    JobRole: str = Field(..., description="Current job role")
    EducationLevel: int = Field(default=3, ge=1, le=5, description="Education level (1-5)")
    MonthlySalary: float = Field(..., gt=0, description="Monthly salary")
    OvertimeHoursPerMonth: float = Field(default=0.0, ge=0, description="Average overtime hours per month")
    LeavesTaken: int = Field(default=5, ge=0, description="Leaves taken in past year")
    ProjectsHandled: int = Field(default=5, ge=0, description="Total projects handled")
    TrainingHours: int = Field(default=20, ge=0, description="Training hours completed")
    YearsAtCompany: int = Field(..., ge=0, description="Tenure at company in years")
    WorkLifeBalanceScore: float = Field(..., ge=-5.0, le=10.0, description="Work-Life Balance Score")
    PerformanceRating: int = Field(default=3, ge=1, le=5, description="Performance rating score (1-5)")
    LastPromotionYear: Optional[int] = Field(default=2021, description="Year of last promotion")

class AttritionPredictionResponse(BaseModel):
    EmployeeID: int
    AttritionProbability: float
    RiskCategory: str  # Low, Medium, High
    TopRiskDrivers: List[Dict[str, Any]]
    ModelVersion: str
    RecommendedIntervention: str

class BatchAttritionRequest(BaseModel):
    employees: List[EmployeeInputSchema]

class EmployeeProfileResponse(BaseModel):
    EmployeeID: int
    Name: str
    Department: str
    JobRole: str
    MonthlySalary: float
    OvertimeHoursPerMonth: float
    WorkLifeBalanceScore: float
    PerformanceRating: int
    EngagementScore: float
    AttritionProbability: float
    AttritionRiskCategory: str
    ReadinessScoreToday: float
    ProjectedReadinessAfterTraining: float
    SkillGapCount: int
    MissingSkills: str
    PrimaryRecommendation: str
