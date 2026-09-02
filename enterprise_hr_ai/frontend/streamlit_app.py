import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Ensure root directory is in python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.services.attrition_service import attrition_service
from app.services.engagement_service import engagement_service
from app.services.skill_gap_service import skill_gap_service
from app.services.recommendation_service import recommendation_service
from app.services.agent_service import agent_service
from app.ml.predictor import predictor

# -------------------------------------------------------------
# 1. PAGE SETUP
# -------------------------------------------------------------
st.set_page_config(
    page_title="Enterprise HR AI Platform",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 2. DATA LOADING
# -------------------------------------------------------------
@st.cache_data
def load_data():
    intel_path = os.path.join(BASE_DIR, "data", "processed", "employee_intelligence.csv")
    org_gaps_path = os.path.join(BASE_DIR, "data", "processed", "organization_skill_gaps.csv")
    courses_path = os.path.join(BASE_DIR, "data", "processed", "courses.csv")
    
    df_intel = pd.read_csv(intel_path) if os.path.exists(intel_path) else pd.DataFrame()
    df_gaps = pd.read_csv(org_gaps_path) if os.path.exists(org_gaps_path) else pd.DataFrame()
    df_courses = pd.read_csv(courses_path) if os.path.exists(courses_path) else pd.DataFrame()
    return df_intel, df_gaps, df_courses

df_intel, df_gaps, df_courses = load_data()

# -------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & SCOPE
# -------------------------------------------------------------
st.sidebar.title("👥 Enterprise HR AI")
st.sidebar.markdown("Workforce Intelligence & Upskilling System")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard Overview",
        "🎯 Attrition Risk Predictor",
        "🧠 Skill Gap & Upskilling",
        "👤 Employee 360 Profile",
        "🤖 HR Policy Assistant (RAG)",
        "ℹ️ About Project"
    ]
)

st.sidebar.markdown("---")
department_list = ["All Departments"] + sorted(df_intel['Department'].unique().tolist()) if not df_intel.empty else ["All Departments"]
selected_dept = st.sidebar.selectbox("Filter Department", department_list)

if selected_dept != "All Departments" and not df_intel.empty:
    filtered_df = df_intel[df_intel['Department'] == selected_dept]
else:
    filtered_df = df_intel

# -------------------------------------------------------------
# PAGE 1: DASHBOARD OVERVIEW
# -------------------------------------------------------------
if menu == "📊 Dashboard Overview":
    st.title("📊 Workforce Analytics & Key Metrics")
    st.caption(f"Showing data for: **{selected_dept}** ({len(filtered_df):,} employees)")
    
    # Key Summary Cards
    total_emp = len(filtered_df)
    high_risk = len(filtered_df[filtered_df['AttritionRiskCategory'] == 'High']) if not filtered_df.empty else 0
    avg_eng = round(filtered_df['EngagementScore'].mean(), 1) if not filtered_df.empty else 0
    avg_wlb = round(filtered_df['WorkLifeBalanceScore'].mean(), 2) if not filtered_df.empty else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Total Employees", value=f"{total_emp:,}")
    with c2:
        risk_pct = (high_risk / max(1, total_emp)) * 100
        st.metric(label="High Flight-Risk", value=f"{high_risk:,}", delta=f"{risk_pct:.1f}% of total", delta_color="inverse")
    with c3:
        st.metric(label="Avg Engagement Score", value=f"{avg_eng} / 100")
    with c4:
        st.metric(label="Avg Work-Life Balance", value=f"{avg_wlb} / 10.0")

    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏢 Attrition Risk by Department")
        if not df_intel.empty:
            dept_summary = df_intel.groupby(['Department', 'AttritionRiskCategory']).size().reset_index(name='Count')
            fig_dept = px.bar(
                dept_summary,
                x='Department',
                y='Count',
                color='AttritionRiskCategory',
                barmode='group',
                color_discrete_map={'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#10b981'},
                height=350
            )
            st.plotly_chart(fig_dept, use_container_width=True)
            
    with col2:
        st.subheader("⚖️ Overtime vs. Work-Life Balance")
        if not filtered_df.empty:
            fig_scatter = px.scatter(
                filtered_df,
                x='OvertimeHoursPerMonth',
                y='WorkLifeBalanceScore',
                color='AttritionRiskCategory',
                size='MonthlySalary',
                hover_data=['Name', 'JobRole', 'Department'],
                color_discrete_map={'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#10b981'},
                height=350
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    # Priority Watchlist Table
    st.subheader("🚨 High Flight-Risk Employee Watchlist")
    if not filtered_df.empty:
        high_risk_table = filtered_df[filtered_df['AttritionRiskCategory'] == 'High'][
            ['EmployeeID', 'Name', 'Department', 'JobRole', 'AttritionProbability', 'OvertimeHoursPerMonth', 'WorkLifeBalanceScore', 'PrimaryRecommendation']
        ].sort_values('AttritionProbability', ascending=False)
        
        st.dataframe(
            high_risk_table.style.format({'AttritionProbability': '{:.1%}', 'OvertimeHoursPerMonth': '{:.1f} hrs'}),
            use_container_width=True,
            height=250
        )

# -------------------------------------------------------------
# PAGE 2: ATTRITION RISK PREDICTOR
# -------------------------------------------------------------
elif menu == "🎯 Attrition Risk Predictor":
    st.title("🎯 Employee Attrition Risk Predictor")
    st.write("Enter employee parameters below to predict attrition probability using trained ML models.")
    
    col_input, col_output = st.columns([5, 6])
    
    with col_input:
        st.subheader("Employee Details")
        sim_name = st.text_input("Employee Name", "John Doe")
        sim_age = st.slider("Age", 18, 65, 32)
        sim_dept = st.selectbox("Department", ["Sales", "IT", "Finance", "HR", "Support", "Marketing"], index=1)
        sim_role = st.selectbox("Job Role", [
            "Auditor", "Sales Executive", "Helpdesk", "HR Executive", "Account Manager", 
            "Engineer", "Developer", "Tester", "HR Manager", "Content Lead", "SEO Analyst", 
            "Accountant", "Support Engineer"
        ], index=5)
        sim_salary = st.number_input("Monthly Salary ($)", min_value=10000, max_value=200000, value=65000, step=5000)
        sim_ot = st.slider("Overtime Hours / Month", 0, 50, 25)
        sim_wlb = st.slider("Work-Life Balance Score", 0.0, 10.0, 3.5, step=0.5)
        sim_tenure = st.slider("Years at Company", 0, 20, 4)
        sim_projects = st.slider("Projects Handled", 1, 15, 5)
        sim_perf = st.selectbox("Performance Rating (1 to 5)", [1, 2, 3, 4, 5], index=2)
        sim_model = st.radio("Select Model", ["v2 (Random Forest Ensemble)", "v1 (Logistic Regression)"], index=0)
        chosen_version = "v2" if "v2" in sim_model else "v1"

    with col_output:
        st.subheader("Model Prediction")
        
        sim_payload = {
            "EmployeeID": 1001,
            "Age": sim_age,
            "Department": sim_dept,
            "JobRole": sim_role,
            "EducationLevel": 3,
            "MonthlySalary": float(sim_salary),
            "OvertimeHoursPerMonth": float(sim_ot),
            "LeavesTaken": 6,
            "ProjectsHandled": int(sim_projects),
            "TrainingHours": 20,
            "YearsAtCompany": int(sim_tenure),
            "WorkLifeBalanceScore": float(sim_wlb),
            "PerformanceRating": int(sim_perf),
            "LastPromotionYear": 2020
        }
        
        res = predictor.predict_single(sim_payload, model_version=chosen_version)
        prob = res["AttritionProbability"]
        cat = res["RiskCategory"]
        
        # Simple Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            title={'text': f"Predicted Risk: {cat.upper()}"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#ef4444" if cat == "High" else ("#f59e0b" if cat == "Medium" else "#10b981")},
                'steps': [
                    {'range': [0, 35], 'color': "#dcfce7"},
                    {'range': [35, 70], 'color': "#fef3c7"},
                    {'range': [70, 100], 'color': "#fee2e2"}
                ]
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Risk Category Alert
        if cat == "High":
            st.error(f"⚠️ **High Attrition Risk**: Employee has a {prob*100:.1f}% probability of leaving.")
        elif cat == "Medium":
            st.warning(f"⚡ **Medium Attrition Risk**: Employee has a {prob*100:.1f}% probability of leaving.")
        else:
            st.success(f"✅ **Low Attrition Risk**: Employee is stable ({prob*100:.1f}% probability of leaving).")
            
        st.info(f"**Recommended Action:** {res['RecommendedIntervention']}")
        
        st.markdown("#### 🔍 Top Risk Contributing Factors")
        for d in res["TopRiskDrivers"]:
            st.write(f"- **{d['factor']}** ({d['severity']} impact): {d['impact']}")

# -------------------------------------------------------------
# PAGE 3: SKILL GAP & UPSKILLING
# -------------------------------------------------------------
elif menu == "🧠 Skill Gap & Upskilling":
    st.title("🧠 Skill Gap Analysis & Upskilling Recommendation")
    
    st.subheader("1. Organization-Wide Skill Deficits")
    if not df_gaps.empty:
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            st.metric("Total Skill Gaps Identified", f"{df_gaps['GapCount'].sum():,}")
        with col_g2:
            st.metric("Internal Reskill Target", f"{df_gaps['ReskillTarget'].sum():,}", "70% target")
        with col_g3:
            st.metric("External Hire Target", f"{df_gaps['ExternalHireTarget'].sum():,}", "30% target")
            
        top_gaps = df_gaps.groupby('Skill')['GapCount'].sum().reset_index().sort_values('GapCount', ascending=False).head(8)
        fig_gaps = px.bar(top_gaps, x='GapCount', y='Skill', orientation='h', title="Top In-Demand Skills with Gaps")
        fig_gaps.update_layout(yaxis={'autorange': 'reversed'}, height=300)
        st.plotly_chart(fig_gaps, use_container_width=True)
    
    st.markdown("---")
    st.subheader("2. Individual Role Pathway & Course Recommendations")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        roles = sorted(df_intel['JobRole'].unique().tolist()) if not df_intel.empty else ["Developer", "Engineer"]
        curr_role = st.selectbox("Current Role", roles, index=roles.index("Developer") if "Developer" in roles else 0)
        target_role = st.selectbox("Aspirational Target Role", roles, index=roles.index("Engineer") if "Engineer" in roles else 0)
        
        current_skills = st.multiselect(
            "Known Competencies",
            ["Python", "SQL & Database Design", "Git Version Control", "Docker", "REST APIs", "Cloud Infrastructure (AWS/GCP)", "QA Testing"],
            default=["Python", "SQL & Database Design"]
        )
        
    with col_p2:
        gap_res = skill_gap_service.calculate_employee_skill_gap(
            current_role=curr_role,
            target_role=target_role,
            current_skills=current_skills
        )
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Current Role Fit", f"{gap_res['ReadinessScoreToday']}%")
        with m2:
            st.metric("Projected Fit (Post-Training)", f"{gap_res['ProjectedReadinessAfterPlan']}%", f"+{gap_res['ProjectedReadinessAfterPlan'] - gap_res['ReadinessScoreToday']:.1f}%")
            
        st.write(f"**Action Plan:** {gap_res['ActionPlan']}")
        
    st.markdown("#### 📚 Recommended Courses")
    for idx, c in enumerate(gap_res["RecommendedCourses"], 1):
        with st.container():
            st.write(f"**{idx}. {c['course_title']}** — Skill: `{c['skill']}` | Level: `{c['level']}` | Provider: *{c['provider']}*")

# -------------------------------------------------------------
# PAGE 4: EMPLOYEE 360 PROFILE
# -------------------------------------------------------------
elif menu == "👤 Employee 360 Profile":
    st.title("👤 Employee 360 Intelligence Profile")
    
    if not filtered_df.empty:
        emp_names = filtered_df['Name'].tolist()
        chosen_emp = st.selectbox("Select Employee to View Dossier", emp_names)
        
        emp = filtered_df[filtered_df['Name'] == chosen_emp].iloc[0]
        
        col_info, col_risk = st.columns([1, 2])
        with col_info:
            st.subheader(emp['Name'])
            st.write(f"**Employee ID:** #{emp['EmployeeID']}")
            st.write(f"**Department:** {emp['Department']}")
            st.write(f"**Job Role:** {emp['JobRole']}")
            st.write(f"**Tenure:** {emp['YearsAtCompany']} years")
            st.write(f"**Salary:** ${emp['MonthlySalary']:,.0f}/mo")
            st.write(f"**Performance:** {'⭐' * int(emp['PerformanceRating'])}")
            
        with col_risk:
            st.subheader("Retention & Skill Evaluation")
            k1, k2, k3 = st.columns(3)
            with k1:
                st.metric("Attrition Risk", emp['AttritionRiskCategory'])
            with k2:
                st.metric("Probability", f"{emp['AttritionProbability']*100:.1f}%")
            with k3:
                st.metric("Readiness Score", f"{emp['ReadinessScoreToday']}%")
                
            st.write(f"**Missing Skills:** `{emp['MissingSkills']}`")
            st.write(f"**Upskilling Recommendation:** **{emp['PrimaryRecommendation']}**")
            st.write(f"**Projected Readiness After Training:** `{emp['ProjectedReadinessAfterTraining']}%`")
            
        st.markdown("---")
        st.subheader("Department Employee Directory")
        st.dataframe(
            filtered_df[['EmployeeID', 'Name', 'Department', 'JobRole', 'AttritionRiskCategory', 'EngagementScore', 'WorkLifeBalanceScore', 'PrimaryRecommendation']],
            use_container_width=True,
            height=300
        )

# -------------------------------------------------------------
# PAGE 5: HR POLICY ASSISTANT (RAG)
# -------------------------------------------------------------
elif menu == "🤖 HR Policy Assistant (RAG)":
    st.title("🤖 HR Policy Q&A Assistant (RAG)")
    st.write("Ask natural language questions about company policies, leave entitlements, benefits, or employee handbooks.")
    
    sample_queries = [
        "What is our parental leave and maternity policy?",
        "How many PTO days can be rolled over to the next year?",
        "What is the annual professional development stipend?",
        "What is the company remote work and hybrid policy?",
        "How do promotion and compensation review cycles work?"
    ]
    
    selected_sample = st.selectbox("Choose a sample question (or type below)", ["-- Type my own --"] + sample_queries)
    
    default_text = "" if selected_sample == "-- Type my own --" else selected_sample
    user_query = st.text_input("Enter your policy question", value=default_text)
    
    if st.button("Submit Question"):
        if user_query.strip():
            with st.spinner("Searching policy knowledge base..."):
                res = agent_service.query_policy_rag(user_query)
                
                if res.get("found"):
                    st.success(f"**Topic:** {res['topic']}")
                    st.info(f"**Answer:** {res['answer']}")
                    st.caption(f"Source: {res['source']}")
                else:
                    st.warning(res['answer'])
        else:
            st.error("Please enter a question.")

# -------------------------------------------------------------
# PAGE 6: ABOUT PROJECT
# -------------------------------------------------------------
elif menu == "ℹ️ About Project":
    st.title("ℹ️ About Enterprise HR AI Platform")
    st.markdown("""
    ### 🎯 Project Overview
    This project is an **Enterprise HR Analytics & Machine Learning Platform** built to assist Human Resource departments in:
    1. **Predicting Employee Attrition:** Identifying flight risks early using ML classification models.
    2. **Explainable AI (XAI):** Highlighting primary risk factors (overtime, low work-life balance, promotion stagnation).
    3. **Skill Gap Analysis:** Analyzing organization-wide skill shortages and suggesting personalized learning pathways.
    4. **HR Policy Retrieval (RAG):** Providing grounded answers to company policy questions.

    ### 🛠️ Technology Stack
    - **Language:** Python 3.12
    - **Frontend:** Streamlit, Plotly Express
    - **Backend:** FastAPI, Pydantic
    - **Machine Learning:** Scikit-Learn (Logistic Regression, Random Forest Ensemble, SMOTE)
    - **Testing:** Pytest (11 unit & integration tests)

    ### 📂 Machine Learning Models
    - **Model v1:** Baseline Logistic Regression (Interpretable linear model)
    - **Model v2:** Tuned Random Forest Classifier with SMOTE balancing (~87% ROC-AUC)
    """)
