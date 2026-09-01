"""
Master Data Processing Pipeline for Enterprise HR AI Platform.
Processes raw datasets and generates standardized relational tables in data/processed/.
"""

import os
import pandas as pd
import numpy as np
import json
import re

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
EXTERNAL_DIR = "data/external"
MODELS_DIR = "models"

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(EXTERNAL_DIR, exist_ok=True)
os.makedirs(os.path.join(MODELS_DIR, "v1"), exist_ok=True)
os.makedirs(os.path.join(MODELS_DIR, "v2"), exist_ok=True)

print("--- Step 1: Loading Raw Data ---")

# 1. Employee Attrition
attrition_file = os.path.join(RAW_DIR, "employee_attrition.csv")
df_attrition = pd.read_csv(attrition_file)
print(f"Loaded employee_attrition: {df_attrition.shape}")

# 2. Performance & Operations
perf_file = os.path.join(RAW_DIR, "Employee_Performance_Dataset.csv") if os.path.exists(os.path.join(RAW_DIR, "Employee_Performance_Dataset.csv")) else os.path.join(RAW_DIR, "hr_performance.csv")
df_perf = pd.read_csv(perf_file) if os.path.exists(perf_file) else None
print(f"Loaded hr_performance: {df_perf.shape if df_perf is not None else 'None'}")

# 3. Engagement & Training
eng_file = os.path.join(RAW_DIR, "Cleaned_HR_Data_Analysis.csv") if os.path.exists(os.path.join(RAW_DIR, "Cleaned_HR_Data_Analysis.csv")) else os.path.join(RAW_DIR, "engagement_training.csv")
df_eng = pd.read_csv(eng_file) if os.path.exists(eng_file) else None
print(f"Loaded engagement_training: {df_eng.shape if df_eng is not None else 'None'}")

# 4. Occupation Master
occ_file = os.path.join(RAW_DIR, "occupation_data.csv")
df_occ = pd.read_csv(occ_file) if os.path.exists(occ_file) else None
print(f"Loaded occupation_data: {df_occ.shape if df_occ is not None else 'None'}")

# 5. Essential Skills
ess_file = os.path.join(RAW_DIR, "essential_skills.csv")
df_ess = pd.read_csv(ess_file) if os.path.exists(ess_file) else None
print(f"Loaded essential_skills: {df_ess.shape if df_ess is not None else 'None'}")

# 6. Software Skills
soft_file = os.path.join(RAW_DIR, "software_skills.csv")
df_soft = pd.read_csv(soft_file) if os.path.exists(soft_file) else None
print(f"Loaded software_skills: {df_soft.shape if df_soft is not None else 'None'}")

print("\n--- Step 2: Processing Master Employees Dataset ---")
# Standardize employee_attrition.csv into employees.csv
df_employees = df_attrition.copy()
# Normalize columns
df_employees.columns = [c.strip() for c in df_employees.columns]
# Standardize target
if 'AttritionRisk' in df_employees.columns:
    df_employees['Attrition'] = df_employees['AttritionRisk'].apply(lambda x: 1 if str(x).lower() in ['yes', '1', 'true', 'high'] else 0)
elif 'Attrition' in df_employees.columns:
    df_employees['Attrition'] = df_employees['Attrition'].apply(lambda x: 1 if str(x).lower() in ['yes', '1', 'true', 'high'] else 0)

# Fill missing customer satisfaction with median if present
if 'CustomerSatisfaction' in df_employees.columns:
    df_employees['CustomerSatisfaction'] = df_employees['CustomerSatisfaction'].fillna(df_employees['CustomerSatisfaction'].median())

# Save clean employees
employees_processed_path = os.path.join(PROCESSED_DIR, "employees.csv")
df_employees.to_csv(employees_processed_path, index=False)
print(f"Saved {employees_processed_path} ({len(df_employees)} rows)")

print("\n--- Step 3: Processing Engagement & Performance Data ---")
if df_eng is not None:
    df_eng.columns = [c.strip() for c in df_eng.columns]
    eng_processed_path = os.path.join(PROCESSED_DIR, "engagement_data.csv")
    df_eng.to_csv(eng_processed_path, index=False)
    print(f"Saved {eng_processed_path} ({len(df_eng)} rows)")

if df_perf is not None:
    df_perf.columns = [c.strip() for c in df_perf.columns]
    perf_processed_path = os.path.join(PROCESSED_DIR, "performance_history.csv")
    df_perf.to_csv(perf_processed_path, index=False)
    print(f"Saved {perf_processed_path} ({len(df_perf)} rows)")

print("\n--- Step 4: Processing Role & Skills Taxonomies ---")
# Role Master mapping
unique_roles = df_employees['JobRole'].dropna().unique()

# Generate role_skills benchmark table using O*NET knowledge + core domains
role_skills_map = {
    "Auditor": ["Accounting", "Financial Auditing", "Risk Assessment", "Tax Compliance", "Internal Controls", "Excel & Financial Modeling", "Regulatory Reporting"],
    "Sales Executive": ["B2B Sales", "Client Negotiation", "CRM Management", "Pipeline Forecasting", "Lead Generation", "Market Analysis", "Relationship Management"],
    "Helpdesk": ["Technical Support", "Customer Troubleshooting", "ServiceNow / ITSM", "Hardware Diagnostics", "Network Basics", "SLA Management", "Active Directory"],
    "HR Executive": ["Talent Acquisition", "Employee Onboarding", "HR Policies & Compliance", "HRIS Management", "Conflict Resolution", "Performance Management", "Payroll Coordination"],
    "Account Manager": ["Key Account Management", "Customer Success", "Upselling & Cross-selling", "Contract Negotiation", "Client Retention", "Strategic Account Planning"],
    "Engineer": ["Systems Architecture", "Cloud Infrastructure (AWS/GCP)", "CI/CD Pipelines", "Linux Administration", "Python / Go", "Docker & Kubernetes", "Monitoring & Logging"],
    "Developer": ["Python", "JavaScript / React", "REST APIs", "SQL & Database Design", "Git Version Control", "Docker", "Microservices Architecture"],
    "Tester": ["QA Testing", "Selenium / Playwright", "Test Automation", "API Testing (Postman)", "Bug Lifecycle Management", "Performance Testing (JMeter)", "CI/CD Quality Gates"],
    "HR Manager": ["HR Strategy", "Executive Leadership", "Labor Law & Compliance", "Succession Planning", "Organizational Development", "Budgeting", "Employee Engagement"],
    "Content Lead": ["Content Strategy", "Copywriting & Editing", "SEO & Keyword Strategy", "Brand Storytelling", "Content Marketing", "Social Media Management", "Analytics & Reporting"],
    "SEO Analyst": ["Search Engine Optimization", "Google Analytics / Search Console", "Keyword Research", "Technical SEO Auditing", "Content Strategy", "Link Building", "Competitor SEO Analysis"],
    "Accountant": ["General Ledger", "Financial Statements", "Accounts Payable / Receivable", "Tax Preparation", "QuickBooks / SAP", "Payroll Management", "Reconciliation"],
    "Support Engineer": ["L2/L3 Technical Troubleshooting", "Log Analysis", "Database Querying (SQL)", "Incident Management", "Cloud Monitoring", "Scripting (Python/Bash)", "Customer Communication"]
}

role_skills_records = []
for role in unique_roles:
    skills = role_skills_map.get(role, ["Communication", "Problem Solving", "Domain Expertise", "Project Management", "Data Literacy"])
    for idx, skill in enumerate(skills):
        importance = "High" if idx < 3 else "Medium"
        required_level = 4 if idx < 3 else 3
        role_skills_records.append({
            "JobRole": role,
            "SkillName": skill,
            "Importance": importance,
            "RequiredProficiency": required_level,
            "Category": "Technical" if any(tech in skill for tech in ["Python", "SQL", "QA", "SEO", "Cloud", "AWS", "API", "Docker", "Linux", "ITSM", "Financial"]) else "Soft Skill"
        })

df_role_skills = pd.DataFrame(role_skills_records)
df_role_skills.to_csv(os.path.join(PROCESSED_DIR, "role_skills.csv"), index=False)
print(f"Saved role_skills.csv ({len(df_role_skills)} mappings)")

print("\n--- Step 5: Generating Course Catalog ---")
courses = [
    {"CourseID": "C101", "CourseTitle": "Advanced Financial Auditing & Risk Management", "TargetSkill": "Financial Auditing", "DurationHours": 20, "Level": "Advanced", "Provider": "Coursera Enterprise"},
    {"CourseID": "C102", "CourseTitle": "Mastering Risk Assessment in Modern Enterprises", "TargetSkill": "Risk Assessment", "DurationHours": 15, "Level": "Intermediate", "Provider": "LinkedIn Learning"},
    {"CourseID": "C103", "CourseTitle": "Corporate Tax Compliance & Reporting", "TargetSkill": "Tax Compliance", "DurationHours": 18, "Level": "Advanced", "Provider": "Udemy for Business"},
    {"CourseID": "C104", "CourseTitle": "High-Impact Enterprise B2B Sales & Negotiation", "TargetSkill": "B2B Sales", "DurationHours": 25, "Level": "Advanced", "Provider": "Harvard Online"},
    {"CourseID": "C105", "CourseTitle": "Modern CRM & Sales Pipeline Mastery", "TargetSkill": "CRM Management", "DurationHours": 12, "Level": "Intermediate", "Provider": "HubSpot Academy"},
    {"CourseID": "C106", "CourseTitle": "ITSM & ServiceNow Service Desk Leadership", "TargetSkill": "ServiceNow / ITSM", "DurationHours": 30, "Level": "Advanced", "Provider": "ServiceNow Learn"},
    {"CourseID": "C107", "CourseTitle": "Strategic Talent Acquisition & Sourcing", "TargetSkill": "Talent Acquisition", "DurationHours": 14, "Level": "Intermediate", "Provider": "SHRM Online"},
    {"CourseID": "C108", "CourseTitle": "Enterprise Labor Law & HR Compliance", "TargetSkill": "Labor Law & Compliance", "DurationHours": 22, "Level": "Advanced", "Provider": "Cornell Certificate"},
    {"CourseID": "C109", "CourseTitle": "Cloud Infrastructure on AWS & Kubernetes", "TargetSkill": "Cloud Infrastructure (AWS/GCP)", "DurationHours": 40, "Level": "Advanced", "Provider": "AWS Training"},
    {"CourseID": "C110", "CourseTitle": "Docker & Container Orchestration Bootcamp", "TargetSkill": "Docker & Kubernetes", "DurationHours": 25, "Level": "Intermediate", "Provider": "Pluralsight"},
    {"CourseID": "C111", "CourseTitle": "Production Python & REST API Engineering", "TargetSkill": "Python", "DurationHours": 35, "Level": "Intermediate", "Provider": "Udemy for Business"},
    {"CourseID": "C112", "CourseTitle": "Modern Microservices Architecture in Cloud", "TargetSkill": "Microservices Architecture", "DurationHours": 30, "Level": "Advanced", "Provider": "Coursera Enterprise"},
    {"CourseID": "C113", "CourseTitle": "Test Automation with Playwright & Selenium", "TargetSkill": "Test Automation", "DurationHours": 28, "Level": "Intermediate", "Provider": "TestAutomationU"},
    {"CourseID": "C114", "CourseTitle": "SEO Growth Masterclass: Technical & Keyword Auditing", "TargetSkill": "Search Engine Optimization", "DurationHours": 20, "Level": "Advanced", "Provider": "Semrush Academy"},
    {"CourseID": "C115", "CourseTitle": "Strategic Account Planning & Retention", "TargetSkill": "Key Account Management", "DurationHours": 16, "Level": "Intermediate", "Provider": "LinkedIn Learning"},
    {"CourseID": "C116", "CourseTitle": "Corporate Financial Statements & Reconciliation", "TargetSkill": "Financial Statements", "DurationHours": 20, "Level": "Intermediate", "Provider": "Wharton Online"},
    {"CourseID": "C117", "CourseTitle": "Full-Stack React & Next.js Development", "TargetSkill": "JavaScript / React", "DurationHours": 32, "Level": "Intermediate", "Provider": "Frontend Masters"},
    {"CourseID": "C118", "CourseTitle": "Data Literacy & SQL Analytics for Managers", "TargetSkill": "SQL & Database Design", "DurationHours": 18, "Level": "Beginner", "Provider": "DataCamp"}
]
df_courses = pd.DataFrame(courses)
df_courses.to_csv(os.path.join(PROCESSED_DIR, "courses.csv"), index=False)
print(f"Saved courses.csv ({len(df_courses)} courses)")

print("\n--- Step 6: Generating Employee Skills & Skill Gaps ---")
np.random.seed(42)
emp_skills = []
emp_intelligence = []

for _, emp in df_employees.iterrows():
    emp_id = emp['EmployeeID']
    role = emp['JobRole']
    dept = emp['Department']
    perf_rating = emp['PerformanceRating']
    wlb_score = emp['WorkLifeBalanceScore']
    attrition_flag = emp['Attrition']
    years_at_co = emp['YearsAtCompany']
    monthly_sal = emp['MonthlySalary']
    ot_hours = emp['OvertimeHoursPerMonth']
    
    # Skills required for this role
    req_skills = role_skills_map.get(role, ["Communication", "Problem Solving", "Domain Expertise"])
    
    # Simulate current skills: employee has a subset of required skills + random proficiency
    num_known = max(1, int(len(req_skills) * np.random.uniform(0.4, 0.9)))
    known_skills = np.random.choice(req_skills, size=num_known, replace=False).tolist()
    missing_skills = [s for s in req_skills if s not in known_skills]
    
    for s in known_skills:
        prof = np.random.choice([2, 3, 4, 5], p=[0.1, 0.4, 0.4, 0.1])
        emp_skills.append({
            "EmployeeID": emp_id,
            "SkillName": s,
            "CurrentProficiency": prof,
            "YearsExperience": round(max(0.5, years_at_co * np.random.uniform(0.3, 0.9)), 1)
        })
    
    # Skill Gap percentage
    gap_ratio = len(missing_skills) / len(req_skills) if req_skills else 0.0
    readiness_today = round((1.0 - gap_ratio) * 100, 1)
    readiness_after_plan = round(min(100.0, readiness_today + (gap_ratio * 75)), 1)
    
    # Recommendation
    rec_course = "None required"
    if missing_skills:
        top_missing = missing_skills[0]
        # Match course
        matched_c = df_courses[df_courses['TargetSkill'] == top_missing]
        if not matched_c.empty:
            rec_course = f"{matched_c.iloc[0]['CourseTitle']} ({matched_c.iloc[0]['Provider']})"
        else:
            rec_course = f"Upskill in {top_missing}"
    
    # Compute holistic Attrition Risk Probability (composite simulation baseline)
    # Higher overtime, low WLB, low salary, long tenure without promotion increase probability
    risk_score = 0.1
    if ot_hours > 25: risk_score += 0.25
    if wlb_score < 2.0: risk_score += 0.30
    if perf_rating <= 2: risk_score += 0.20
    if gap_ratio > 0.4: risk_score += 0.15
    if attrition_flag == 1: risk_score += 0.35
    risk_prob = round(min(0.98, max(0.04, risk_score + np.random.normal(0, 0.05))), 2)
    risk_category = "High" if risk_prob >= 0.7 else ("Medium" if risk_prob >= 0.35 else "Low")
    
    # Synthetic engagement index
    engagement_score = round(max(20, min(100, (wlb_score * 12) + (perf_rating * 10) + np.random.normal(25, 5))), 1)

    emp_intelligence.append({
        "EmployeeID": emp_id,
        "Name": emp['Name'],
        "Gender": emp.get('Gender', 'Other'),
        "Age": emp.get('Age', 35),
        "Department": dept,
        "JobRole": role,
        "YearsAtCompany": years_at_co,
        "MonthlySalary": monthly_sal,
        "OvertimeHoursPerMonth": ot_hours,
        "WorkLifeBalanceScore": wlb_score,
        "PerformanceRating": perf_rating,
        "EngagementScore": engagement_score,
        "AttritionProbability": risk_prob,
        "AttritionRiskCategory": risk_category,
        "ReadinessScoreToday": readiness_today,
        "ProjectedReadinessAfterTraining": readiness_after_plan,
        "SkillGapCount": len(missing_skills),
        "MissingSkills": ", ".join(missing_skills) if missing_skills else "None",
        "PrimaryRecommendation": rec_course
    })

df_emp_skills = pd.DataFrame(emp_skills)
df_emp_skills.to_csv(os.path.join(PROCESSED_DIR, "employee_skills.csv"), index=False)
print(f"Saved employee_skills.csv ({len(df_emp_skills)} skill records)")

df_emp_intel = pd.DataFrame(emp_intelligence)
df_emp_intel.to_csv(os.path.join(PROCESSED_DIR, "employee_intelligence.csv"), index=False)
print(f"Saved employee_intelligence.csv ({len(df_emp_intel)} rows)")

print("\n--- Step 7: Organization-Wide Skill Gap Matrix ---")
org_gap_list = []
for role in unique_roles:
    role_emps = df_emp_intel[df_emp_intel['JobRole'] == role]
    req_skills = role_skills_map.get(role, [])
    dept = role_emps['Department'].iloc[0] if not role_emps.empty else "General"
    
    for skill in req_skills:
        # Count how many employees in this role have this skill
        role_emp_ids = role_emps['EmployeeID'].tolist()
        emp_with_skill = df_emp_skills[(df_emp_skills['EmployeeID'].isin(role_emp_ids)) & (df_emp_skills['SkillName'] == skill)]
        available_count = len(emp_with_skill)
        required_count = len(role_emps)
        gap_count = max(0, required_count - available_count)
        
        severity = "High" if gap_count >= (required_count * 0.45) else ("Medium" if gap_count >= (required_count * 0.2) else "Low")
        
        # Recommendation
        reskill_target = int(gap_count * 0.7)
        hire_target = gap_count - reskill_target
        
        org_gap_list.append({
            "Department": dept,
            "JobRole": role,
            "Skill": skill,
            "TotalHeadcount": required_count,
            "AvailableHeadcount": available_count,
            "GapCount": gap_count,
            "Severity": severity,
            "ReskillTarget": reskill_target,
            "ExternalHireTarget": hire_target
        })

df_org_gaps = pd.DataFrame(org_gap_list)
df_org_gaps.to_csv(os.path.join(PROCESSED_DIR, "organization_skill_gaps.csv"), index=False)
print(f"Saved organization_skill_gaps.csv ({len(df_org_gaps)} gap records)")

print("\n=== Master Data Processing Completed Successfully! ===")
