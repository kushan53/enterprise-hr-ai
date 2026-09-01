"""
Agentic Workflow & HR Policy RAG Service.
Implements specialized agent behaviors:
1. Workforce Intelligence Agent
2. Upskilling Agent
3. Policy RAG Agent (Grounded Q&A over company handbook & leave rules)
4. Career Simulation Agent
"""

import os
import pandas as pd
from app.utils.config import settings

# HR Knowledge Base for Policy RAG
HR_POLICY_KNOWLEDGE = [
    {
        "topic": "Parental & Maternity Leave Policy",
        "keywords": ["parental", "maternity", "paternity", "child", "birth", "adoption"],
        "weight": 3,
        "content": "All full-time employees are eligible for 16 weeks of fully paid parental leave for primary caregivers following the birth or adoption of a child. Secondary caregivers receive 6 weeks of fully paid leave."
    },
    {
        "topic": "Paid Time Off & Annual Leave",
        "keywords": ["pto", "vacation", "holiday", "time off", "annual leave"],
        "weight": 2,
        "content": "Employees accrue 20 days of Paid Time Off (PTO) annually. Unused PTO up to 5 days can roll over to the subsequent calendar year. Leave requests exceeding 3 consecutive days require manager approval via HR portal."
    },
    {
        "topic": "Professional Development & Training Stipend",
        "keywords": ["stipend", "upskilling", "certification", "tuition", "budget", "course reimbursement"],
        "weight": 3,
        "content": "Each employee is allocated an annual $2,500 continuous learning and certification budget. Approved courses on Coursera, LinkedIn Learning, and vendor certifications (AWS, GCP, Scrum) are 100% reimbursable."
    },
    {
        "topic": "Flexible Work & Remote Policy",
        "keywords": ["remote", "work from home", "wfh", "hybrid", "flexible hours", "telecommute"],
        "weight": 3,
        "content": "Our organization operates a hybrid-first model: employees are permitted up to 3 days of remote work per week. Full remote contracts can be granted based on performance and departmental executive review."
    },
    {
        "topic": "Promotion & Compensation Review Cycle",
        "keywords": ["promotion", "salary hike", "raise", "compensation review", "appraisal", "bonus"],
        "weight": 3,
        "content": "Formal performance reviews occur bi-annually in June and December. Promotion eligibility requires meeting or exceeding performance benchmarks for at least 12 months with demonstrated competency progression."
    },
    {
        "topic": "Mental Health & Wellness Benefits",
        "keywords": ["mental health", "wellness", "burnout", "counseling", "therapy", "eap", "stress"],
        "weight": 3,
        "content": "The Employee Assistance Program (EAP) provides 24/7 confidential psychological counseling (up to 8 free sessions per year), dedicated wellness days, and subscription to mindfulness apps."
    }
]

class AgentService:
    def __init__(self):
        self.intel_file = os.path.join(settings.DATA_PROCESSED_DIR, "employee_intelligence.csv")

    def query_policy_rag(self, query: str) -> dict:
        q_lower = query.lower()
        best_match = None
        highest_score = 0
        
        for doc in HR_POLICY_KNOWLEDGE:
            score = sum(doc.get("weight", 1) for kw in doc["keywords"] if kw in q_lower)
            if score > highest_score:
                highest_score = score
                best_match = doc
                
        if best_match and highest_score > 0:
            return {
                "query": query,
                "found": True,
                "topic": best_match["topic"],
                "answer": best_match["content"],
                "source": "Enterprise HR Policy Handbook 2026"
            }
        else:
            return {
                "query": query,
                "found": False,
                "topic": "General Inquiries",
                "answer": "For custom HR policy requests not covered in standard handbooks, please raise a ticket with People Operations or consult your designated HR Business Partner.",
                "source": "Enterprise HR Operations Directory"
            }

    def dispatch_agent_workflow(self, agent_type: str, query: str, context: dict = None) -> dict:
        context = context or {}
        agent_type = agent_type.lower()
        
        if "policy" in agent_type:
            return self.query_policy_rag(query)
            
        elif "workforce" in agent_type or "attrition" in agent_type:
            emp_id = context.get("employee_id")
            if emp_id and os.path.exists(self.intel_file):
                df = pd.read_csv(self.intel_file)
                match = df[df['EmployeeID'] == int(emp_id)]
                if not match.empty:
                    row = match.iloc[0]
                    return {
                        "agent": "Workforce Intelligence Agent",
                        "employee_id": emp_id,
                        "name": row['Name'],
                        "flight_risk": f"{row['AttritionRiskCategory']} ({row['AttritionProbability']*100:.1f}%)",
                        "work_life_balance": row['WorkLifeBalanceScore'],
                        "overtime": f"{row['OvertimeHoursPerMonth']} hrs/mo",
                        "summary": f"{row['Name']} is currently at {row['AttritionRiskCategory']} attrition risk. Primary drivers relate to overtime and work-life balance."
                    }
            return {
                "agent": "Workforce Intelligence Agent",
                "summary": "Workforce flight-risk monitoring active. 11% average attrition across departments."
            }

        elif "upskill" in agent_type or "skill" in agent_type:
            emp_id = context.get("employee_id")
            if emp_id and os.path.exists(self.intel_file):
                df = pd.read_csv(self.intel_file)
                match = df[df['EmployeeID'] == int(emp_id)]
                if not match.empty:
                    row = match.iloc[0]
                    return {
                        "agent": "Upskilling Agent",
                        "employee_id": emp_id,
                        "name": row['Name'],
                        "missing_skills": row['MissingSkills'],
                        "recommended_course": row['PrimaryRecommendation'],
                        "readiness_trajectory": f"{row['ReadinessScoreToday']}% -> {row['ProjectedReadinessAfterTraining']}%"
                    }
            return {
                "agent": "Upskilling Agent",
                "summary": "Identified critical organizational gaps in Cloud Infrastructure, MLOps, and Data Governance."
            }

        else:
            rag_res = self.query_policy_rag(query)
            if rag_res["found"]:
                return {
                    "agent": "Orchestrator Agent (Routed to Policy RAG)",
                    **rag_res
                }
            return {
                "agent": "Orchestrator Agent",
                "answer": f"Processed query: '{query}'. Automated tools ready for flight-risk diagnosis, career simulations, and upskilling pathways.",
                "tools_available": ["get_employee_profile", "calculate_skill_gap", "recommend_courses", "query_policy_rag"]
            }

agent_service = AgentService()
