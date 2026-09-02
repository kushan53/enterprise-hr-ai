import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from app.main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_dashboard_summary(self):
        response = self.client.get("/api/v1/dashboard/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_employees", data)
        self.assertIn("average_engagement", data)

    def test_department_attrition_metrics(self):
        response = self.client.get("/api/v1/dashboard/attrition-by-department")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_single_attrition_prediction(self):
        payload = {
            "EmployeeID": 101,
            "Age": 32,
            "Department": "Sales",
            "JobRole": "Sales Executive",
            "EducationLevel": 3,
            "MonthlySalary": 55000.0,
            "OvertimeHoursPerMonth": 25.0,
            "LeavesTaken": 5,
            "ProjectsHandled": 7,
            "TrainingHours": 20,
            "YearsAtCompany": 5,
            "WorkLifeBalanceScore": 2.5,
            "PerformanceRating": 3,
            "LastPromotionYear": 2021
        }
        response = self.client.post("/api/v1/attrition/predict?model_version=v2", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("AttritionProbability", data)
        self.assertIn(data["RiskCategory"], ["Low", "Medium", "High"])

    def test_skill_gap_endpoint(self):
        payload = {
            "CurrentRole": "Developer",
            "TargetRole": "Engineer",
            "CurrentSkills": ["Python", "SQL"]
        }
        response = self.client.post("/api/v1/skills/gap-analysis", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ReadinessScoreToday", data)
        self.assertGreater(len(data["RecommendedCourses"]), 0)

    def test_policy_rag_endpoint(self):
        response = self.client.get("/api/v1/agent/policy-rag?query=What is our PTO policy?")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["found"])

if __name__ == "__main__":
    unittest.main()
