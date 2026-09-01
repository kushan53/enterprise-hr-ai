import os
import pandas as pd
from app.utils.config import settings

class EngagementService:
    def __init__(self):
        self.eng_file = os.path.join(settings.DATA_PROCESSED_DIR, "engagement_data.csv")
        self.intel_file = os.path.join(settings.DATA_PROCESSED_DIR, "employee_intelligence.csv")

    def get_overview_metrics(self) -> dict:
        if not os.path.exists(self.intel_file):
            return {
                "total_employees": 0,
                "high_risk_count": 0,
                "average_engagement": 0.0,
                "avg_work_life_balance": 0.0
            }
        df = pd.read_csv(self.intel_file)
        return {
            "total_employees": int(len(df)),
            "high_risk_count": int((df['AttritionRiskCategory'] == 'High').sum()),
            "medium_risk_count": int((df['AttritionRiskCategory'] == 'Medium').sum()),
            "low_risk_count": int((df['AttritionRiskCategory'] == 'Low').sum()),
            "average_engagement": round(float(df['EngagementScore'].mean()), 1),
            "avg_work_life_balance": round(float(df['WorkLifeBalanceScore'].mean()), 2),
            "avg_monthly_salary": round(float(df['MonthlySalary'].mean()), 0),
            "avg_overtime_hours": round(float(df['OvertimeHoursPerMonth'].mean()), 1)
        }

    def get_burnout_hotspots(self) -> list:
        if not os.path.exists(self.intel_file):
            return []
        df = pd.read_csv(self.intel_file)
        hotspots = df[df['WorkLifeBalanceScore'] < 2.0].sort_values('OvertimeHoursPerMonth', ascending=False)
        return hotspots[['EmployeeID', 'Name', 'Department', 'JobRole', 'OvertimeHoursPerMonth', 'WorkLifeBalanceScore', 'EngagementScore']].head(30).to_dict(orient='records')

engagement_service = EngagementService()
