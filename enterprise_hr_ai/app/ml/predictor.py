import pandas as pd
import numpy as np
from app.ml.model_loader import model_loader
from app.utils.logger import log_prediction, logger

class AttritionPredictor:
    def __init__(self):
        pass

    def prepare_features(self, data: dict or pd.DataFrame) -> pd.DataFrame:
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()

        # Engineered features
        last_promo = pd.to_numeric(df.get('LastPromotionYear', 2021), errors='coerce')
        if hasattr(last_promo, 'fillna'):
            last_promo = last_promo.fillna(2021)
        else:
            last_promo = 2021 if pd.isna(last_promo) else last_promo

        df['YearsSincePromotion'] = 2024 - last_promo
        df['SalaryPerYearAtCompany'] = df['MonthlySalary'] / (df['YearsAtCompany'] + 1)
        df['OvertimeRatio'] = df['OvertimeHoursPerMonth'] / 160.0
        df['BurnoutRiskIndex'] = (df['OvertimeHoursPerMonth'] * 0.4) - (df['WorkLifeBalanceScore'] * 10) + (df['ProjectsHandled'] * 2)
        
        feature_cols = [
            'Age', 'Department', 'JobRole', 'EducationLevel', 'MonthlySalary', 
            'OvertimeHoursPerMonth', 'LeavesTaken', 'ProjectsHandled', 'TrainingHours',
            'YearsAtCompany', 'WorkLifeBalanceScore', 'PerformanceRating',
            'YearsSincePromotion', 'SalaryPerYearAtCompany', 'OvertimeRatio', 'BurnoutRiskIndex'
        ]
        return df[feature_cols]

    def predict_single(self, employee_data: dict, model_version: str = "v2") -> dict:
        model = model_loader.get_model(model_version)
        if model is None:
            raise ValueError(f"Model version {model_version} is not available.")
            
        X = self.prepare_features(employee_data)
        
        probs = model.predict_proba(X)[0]
        attrition_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
        
        # Categorize Risk
        if attrition_prob >= 0.70:
            risk_cat = "High"
            intervention = "Immediate 1-on-1 retention review, workload adjustment, and compensation alignment."
        elif attrition_prob >= 0.35:
            risk_cat = "Medium"
            intervention = "Career development check-in, skill path assignment, and work-life balance monitoring."
        else:
            risk_cat = "Low"
            intervention = "Standard talent engagement & continuous learning path."

        # Compute top individual risk drivers
        drivers = []
        if employee_data.get('OvertimeHoursPerMonth', 0) > 20:
            drivers.append({"factor": "Excessive Overtime", "severity": "High", "impact": f"{employee_data.get('OvertimeHoursPerMonth')} hrs/month"})
        if employee_data.get('WorkLifeBalanceScore', 3) < 2.0:
            drivers.append({"factor": "Low Work-Life Balance", "severity": "High", "impact": f"Score: {employee_data.get('WorkLifeBalanceScore')}"})
        if employee_data.get('YearsAtCompany', 0) > 4 and (2024 - employee_data.get('LastPromotionYear', 2021)) >= 3:
            drivers.append({"factor": "Promotion Stagnation", "severity": "Medium", "impact": ">= 3 years since promotion"})
        if employee_data.get('MonthlySalary', 50000) < 45000:
            drivers.append({"factor": "Below Market Compensation", "severity": "Medium", "impact": f"${employee_data.get('MonthlySalary'):,.0f}/mo"})
        if not drivers:
            drivers.append({"factor": "Healthy Retention Profile", "severity": "Low", "impact": "No critical anomalies"})

        emp_id = employee_data.get('EmployeeID', 0)
        log_prediction(emp_id, model_version, round(attrition_prob, 4), risk_cat, employee_data)

        return {
            "EmployeeID": emp_id,
            "AttritionProbability": round(attrition_prob, 4),
            "RiskCategory": risk_cat,
            "TopRiskDrivers": drivers,
            "ModelVersion": model_version,
            "RecommendedIntervention": intervention
        }

predictor = AttritionPredictor()
