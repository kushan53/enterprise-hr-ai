import os
import pandas as pd
from app.utils.config import settings

class SkillGapService:
    def __init__(self):
        self.role_skills_file = os.path.join(settings.DATA_PROCESSED_DIR, "role_skills.csv")
        self.emp_skills_file = os.path.join(settings.DATA_PROCESSED_DIR, "employee_skills.csv")
        self.org_gaps_file = os.path.join(settings.DATA_PROCESSED_DIR, "organization_skill_gaps.csv")
        self.courses_file = os.path.join(settings.DATA_PROCESSED_DIR, "courses.csv")
        self.intel_file = os.path.join(settings.DATA_PROCESSED_DIR, "employee_intelligence.csv")

    def get_role_requirements(self, role_name: str) -> list:
        if not os.path.exists(self.role_skills_file):
            return []
        df = pd.read_csv(self.role_skills_file)
        matching = df[df['JobRole'].str.lower() == role_name.lower()]
        return matching['SkillName'].tolist()

    def calculate_employee_skill_gap(self, current_role: str, target_role: str, current_skills: list = None, employee_id: int = None) -> dict:
        req_skills = self.get_role_requirements(target_role)
        if not req_skills:
            req_skills = self.get_role_requirements(current_role) or ["Leadership", "Domain Problem Solving", "Technical Communication", "Project Delivery"]

        if current_skills is None and employee_id is not None and os.path.exists(self.emp_skills_file):
            df_s = pd.read_csv(self.emp_skills_file)
            user_s = df_s[df_s['EmployeeID'] == employee_id]
            current_skills = user_s['SkillName'].tolist()
        
        current_skills = current_skills or []
        
        # Semantic set difference (normalized lower)
        curr_set = {s.lower().strip(): s for s in current_skills}
        matched = []
        missing = []
        
        for req in req_skills:
            req_clean = req.lower().strip()
            # Direct or partial semantic matching
            if any(req_clean in c or c in req_clean for c in curr_set.keys()):
                matched.append(req)
            else:
                missing.append(req)

        total_req = max(1, len(req_skills))
        gap_ratio = len(missing) / total_req
        readiness_today = round((1.0 - gap_ratio) * 100, 1)
        readiness_projected = round(min(100.0, readiness_today + (gap_ratio * 80.0)), 1)
        
        # Course matches for missing skills
        df_courses = pd.read_csv(self.courses_file) if os.path.exists(self.courses_file) else pd.DataFrame()
        recs = []
        for m in missing:
            matched_c = df_courses[df_courses['TargetSkill'].str.lower() == m.lower()] if not df_courses.empty else pd.DataFrame()
            if not matched_c.empty:
                c = matched_c.iloc[0]
                recs.append({
                    "skill": m,
                    "course_id": c['CourseID'],
                    "course_title": c['CourseTitle'],
                    "duration": f"{c['DurationHours']} hrs",
                    "provider": c['Provider'],
                    "level": c['Level']
                })
            else:
                recs.append({
                    "skill": m,
                    "course_id": "EXT-01",
                    "course_title": f"Executive Masterclass: {m}",
                    "duration": "15 hrs",
                    "provider": "Enterprise Academy",
                    "level": "Intermediate"
                })

        return {
            "EmployeeID": employee_id,
            "CurrentRole": current_role,
            "TargetRole": target_role,
            "MatchedSkills": matched,
            "MissingSkills": missing,
            "ReadinessScoreToday": readiness_today,
            "ProjectedReadinessAfterPlan": readiness_projected,
            "RecommendedCourses": recs,
            "ActionPlan": f"Complete {len(recs)} targeted learning modules over the next 90 days to achieve {readiness_projected}% role readiness."
        }

    def get_organization_gaps(self) -> list:
        if not os.path.exists(self.org_gaps_file):
            return []
        df = pd.read_csv(self.org_gaps_file)
        return df.to_dict(orient='records')

skill_gap_service = SkillGapService()
