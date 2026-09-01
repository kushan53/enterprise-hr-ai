# ⚡ Enterprise HR AI — Workforce Intelligence & Upskilling Platform

An enterprise-grade, agentic HR platform combining **predictive machine learning**, **skills intelligence**, **automated upskilling recommendations**, and **policy RAG workflows**.

---

## 🏛️ System Architecture

```
enterprise_hr_ai/
│
├── data/
│   ├── raw/                  <-- 5+ raw CSV datasets (attrition, engagement, performance, skills)
│   ├── processed/            <-- Clean relational data (employees, skills, courses, intelligence)
│   └── predictions/          <-- Real-time prediction audit logs (drift monitoring)
│
├── notebooks/                <-- Complete 16-Step Modular ML & Analytics Pipelines
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_validation.ipynb
│   ├── 03_data_cleaning.ipynb
│   ├── 04_data_relationships.ipynb
│   ├── 05_feature_engineering.ipynb
│   ├── 06_baseline_model.ipynb
│   ├── 07_model_comparison.ipynb
│   ├── 08_model_explainability.ipynb
│   ├── 09_model_versioning.ipynb
│   ├── 10_engagement_intelligence.ipynb
│   ├── 11_role_intelligence.ipynb
│   ├── 12_employee_skills.ipynb
│   ├── 13_skill_gap_engine.ipynb
│   ├── 14_organization_skill_gap.ipynb
│   ├── 15_recommendation_engine.ipynb
│   └── 16_employee_intelligence.ipynb
│
├── models/                   <-- Versioned ML models & metadata
│   ├── v1/                   <-- Baseline Logistic Regression pipeline
│   └── v2/                   <-- Tuned Ensemble Random Forest & SHAP weights
│
├── app/                      <-- Production FastAPI Backend
│   ├── main.py               <-- FastAPI Application & Middleware
│   ├── api/                  <-- REST Endpoints (attrition, dashboard, skills, agent)
│   ├── services/             <-- Business Logic (attrition, engagement, skill gap, recommend, RAG)
│   ├── ml/                   <-- Singleton ModelLoader & AttritionPredictor
│   ├── validation/           <-- Pydantic V2 Schemas
│   └── utils/                <-- Config & Structured Logger
│
├── frontend/
│   └── streamlit_app.py      <-- Executive Command Center Dashboard
│
├── tests/                    <-- Pytest unit & integration test suite
├── docs/                     <-- Architecture, data relations & build notes
├── Dockerfile & docker-compose.yml
└── requirements.txt
```

---

## 🚀 Quickstart & How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Data Processing & Model Training
```bash
python scripts/process_data.py
python scripts/train_models.py
```

### 3. Start the FastAPI Backend
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive API Documentation (Swagger): `http://localhost:8000/docs`
* Health Check: `http://localhost:8000/health`

### 4. Launch the Streamlit Dashboard
```bash
streamlit run frontend/streamlit_app.py
```
* Access Dashboard at `http://localhost:8501`

### 5. Run Automated Test Suite
```bash
pytest tests/ -v
```

---

## 🔑 Core Features & Modules

1. **Predictive Attrition & SHAP Explainability**:
   - Predicts flight risk probability (0.0 to 1.0) and assigns risk tiers (*Low*, *Medium*, *High*).
   - Identifies local top-3 risk drivers per employee (e.g. overtime burnout, promotion stagnation, compensation mismatch).
2. **Interactive What-If Simulator**:
   - HR leaders can simulate compensation raises, workload reductions, or promotion cycles to test retention outcomes before making policy changes.
3. **Organization-Wide Skill Gap & Hire-vs-Reskill Decision Engine**:
   - Calculates talent shortfalls across departments.
   - Recommends 70/30 internal reskilling vs. external hiring targets.
4. **Personalized Upskilling & Career Readiness**:
   - Computes role readiness today and projected readiness post-learning plan.
   - Maps missing competencies directly to course curriculum.
5. **Agentic HR Orchestrator & Policy RAG**:
   - Grounded Q&A over company benefits, PTO rollover, parental leave, and learning stipends.
