import os
import pandas as pd
from app.utils.config import settings

class RecommendationService:
    def __init__(self):
        self.courses_file = os.path.join(settings.DATA_PROCESSED_DIR, "courses.csv")
        self.intel_file = os.path.join(settings.DATA_PROCESSED_DIR, "employee_intelligence.csv")

    def get_all_courses(self) -> list:
        if not os.path.exists(self.courses_file):
            return []
        df = pd.read_csv(self.courses_file)
        return df.to_dict(orient='records')

    def get_employee_recommendation(self, employee_id: int) -> dict:
        if not os.path.exists(self.intel_file):
            return {}
        df = pd.read_csv(self.intel_file)
        emp = df[df['EmployeeID'] == employee_id]
        if emp.empty:
            return {"message": "Employee not found"}
        
        row = emp.iloc[0]
        return {
            "EmployeeID": int(row['EmployeeID']),
            "Name": row['Name'],
            "CurrentRole": row['JobRole'],
            "Department": row['Department'],
            "MissingSkills": row['MissingSkills'],
            "PrimaryRecommendation": row['PrimaryRecommendation'],
            "ReadinessToday": float(row['ReadinessScoreToday']),
            "ProjectedReadiness": float(row['ProjectedReadinessAfterTraining'])
        }

recommendation_service = RecommendationService()
