import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.attrition_service import attrition_service
from app.services.engagement_service import engagement_service
from app.services.skill_gap_service import skill_gap_service
from app.services.recommendation_service import recommendation_service
from app.services.agent_service import agent_service

class TestServices(unittest.TestCase):
    def test_overview_metrics(self):
        metrics = engagement_service.get_overview_metrics()
        self.assertIn("total_employees", metrics)
        self.assertGreater(metrics["total_employees"], 0)
        self.assertIn("high_risk_count", metrics)
        self.assertIn("average_engagement", metrics)

    def test_attrition_prediction(self):
        payload = {
            "Age": 30,
            "Department": "IT",
            "JobRole": "Developer",
            "EducationLevel": 3,
            "MonthlySalary": 60000.0,
            "OvertimeHoursPerMonth": 35.0,
            "LeavesTaken": 8,
            "ProjectsHandled": 6,
            "TrainingHours": 10,
            "YearsAtCompany": 4,
            "WorkLifeBalanceScore": 1.2,
            "PerformanceRating": 2,
            "LastPromotionYear": 2019
        }
        pred = attrition_service.predict_attrition(payload, model_version="v2")
        self.assertIn("AttritionProbability", pred)
        self.assertTrue(0.0 <= pred["AttritionProbability"] <= 1.0)
        self.assertIn(pred["RiskCategory"], ["Low", "Medium", "High"])
        self.assertGreater(len(pred["TopRiskDrivers"]), 0)

    def test_skill_gap_calculation(self):
        res = skill_gap_service.calculate_employee_skill_gap(
            current_role="Developer",
            target_role="Engineer",
            current_skills=["Python", "SQL & Database Design"]
        )
        self.assertIn("MatchedSkills", res)
        self.assertIn("MissingSkills", res)
        self.assertIn("ReadinessScoreToday", res)
        self.assertIn("ProjectedReadinessAfterPlan", res)
        self.assertGreater(len(res["RecommendedCourses"]), 0)

    def test_policy_rag(self):
        res = agent_service.query_policy_rag("What is our parental leave policy?")
        self.assertTrue(res["found"])
        self.assertIn("parental", res["answer"].lower())

if __name__ == "__main__":
    unittest.main()
