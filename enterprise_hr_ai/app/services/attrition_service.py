import os
import pandas as pd
from app.ml.predictor import predictor
from app.utils.config import settings

class AttritionService:
    def __init__(self):
        self.employees_file = os.path.join(settings.DATA_PROCESSED_DIR, "employees.csv")
        self.intel_file = os.path.join(settings.DATA_PROCESSED_DIR, "employee_intelligence.csv")

    def predict_attrition(self, employee_data: dict, model_version: str = "v2") -> dict:
        return predictor.predict_single(employee_data, model_version=model_version)

    def get_department_risk_summary(self) -> list:
        if not os.path.exists(self.intel_file):
            return []
        df = pd.read_csv(self.intel_file)
        
        summary = df.groupby('Department').agg(
            TotalEmployees=('EmployeeID', 'count'),
            HighRiskCount=('AttritionRiskCategory', lambda x: (x == 'High').sum()),
            AvgRisk=('AttritionProbability', 'mean'),
            AvgSalary=('MonthlySalary', 'mean'),
            AvgOvertime=('OvertimeHoursPerMonth', 'mean')
        ).reset_index()
        
        summary['HighRiskPct'] = (summary['HighRiskCount'] / summary['TotalEmployees'] * 100).round(1)
        summary['AvgRisk'] = (summary['AvgRisk'] * 100).round(1)
        summary['AvgSalary'] = summary['AvgSalary'].round(0)
        summary['AvgOvertime'] = summary['AvgOvertime'].round(1)
        
        return summary.to_dict(orient='records')

    def get_high_risk_roster(self, limit: int = 50) -> list:
        if not os.path.exists(self.intel_file):
            return []
        df = pd.read_csv(self.intel_file)
        high_risk = df[df['AttritionRiskCategory'] == 'High'].sort_values('AttritionProbability', ascending=False)
        return high_risk.head(limit).to_dict(orient='records')

attrition_service = AttritionService()
