MY PROJECT NOTES

Enterprise HR AI — Workforce Intelligence & Upskilling Platform

A day-by-day build log for an agentic HR system that predicts attrition, tracks engagement, finds skill gaps, and recommends what people should learn next.

Why I'm writing this down

I'm building this project in pieces over a few days, and I know from experience that if I don't write down the plan, I'll forget why I made a decision two days later. So this document is basically my own working notebook — the goal, the reasoning, and the exact steps, in the order I'm actually going to do them.

The short version of what I'm building: an HR system that looks at employee data and tells the company three things — who is at risk of quitting, where the skill gaps are across the organisation, and what each employee should learn next to close those gaps. Underneath, it's a mix of a proper ML model (for attrition), some honest data-engineering work (for skills and engagement), and a small web app on top so someone can actually look at the results without opening a notebook.

Note to self: Don't skip straight to the ML model. Everything downstream depends on understanding the data first — I learned this the hard way on other projects. Data → cleaning → relationships → features → model, in that order.

What I'm working with

Five raw CSV files, sitting in data/raw/:

employee_attrition.csv — one row per employee, used to predict who might leave

hr_performance_engagement.csv — performance and engagement scores

occupation_data.csv — a master list of roles/occupations

essential_skills.csv — which skills each role needs

software_skills.csv — which tools/software each role needs

The folder structure I'm using

enterprise_hr_ai/

├── data/

│   ├── raw/              <- the 5 CSVs go here, untouched

│   ├── processed/        <- cleaned versions I generate

│   └── external/

├── notebooks/            <- one notebook per step, numbered in order

├── models/                <- saved model files (.joblib) + metadata

├── app/                   <- FastAPI backend, once I get there

├── frontend/              <- Streamlit dashboard

├── tests/

└── requirements.txt

The order I'm doing this in

I split the whole thing into four working days, plus an optional 'harden it' phase once the core app actually works. I'm not touching Docker, MLflow, or monitoring until the basic pipeline runs end to end — no point productionising something that isn't finished.

Day 1 — Data foundation (understand, validate, clean, connect the datasets)

Day 2 — Machine learning (features, baseline model, model comparison, explainability, versioning)

Day 3 — Workforce intelligence (engagement, roles, skills, skill gaps, recommendations)

Day 4 — Application (turn the notebooks into a real API + dashboard)

Later — enterprise hardening (Docker, drift monitoring, retraining rules, docs, deployment)

Day 1 — Data Foundation

Today is only about understanding the data. No modelling. If I rush this, I'll end up joining tables on the wrong key or feeding leaky columns into the model later — so slow down.

1. Data Understanding — notebooks/01_data_understanding.ipynb

First step, before anything else: load every file and just look at it. For each of the five datasets I want to know the shape, the columns, the data types, how much is missing, and whether there's an obvious ID column I can join on.

Setup

import pandas as pd

import numpy as np

import os

import matplotlib.pyplot as plt

 

pd.set_option("display.max_columns", None)

DATA_PATH = "../data/raw"

 

print(os.listdir(DATA_PATH))

# should print all 5 filenames — if it doesn't, my paths are wrong

For each dataset, I run the same checklist

df = pd.read_csv(f"{DATA_PATH}/employee_attrition.csv")

print(df.shape)

df.head()

df.info()

df.isnull().sum().sort_values(ascending=False).head(20)

df.duplicated().sum()

 

# for the attrition file specifically, check the target balance

df['Attrition'].value_counts(normalize=True) * 100

I'll do the same five checks for the other four files too — hr_performance_engagement.csv, occupation_data.csv, essential_skills.csv, software_skills.csv. Along the way I'm hunting for any column with 'id' in the name, since that's my best guess at a join key between tables:

[c for c in df.columns if 'id' in c.lower()]

Note to self: Don't merge anything yet, even if two files look like they share an ID. Confirm the IDs actually refer to the same employees before joining — a matching column name isn't proof of a matching key.

What each dataset is actually for

employee_attrition.csv → feeds the attrition ML model directly

hr_performance_engagement.csv → engagement analytics, no ML needed at first

occupation_data.csv → becomes my 'role master' reference table

essential_skills.csv + software_skills.csv → combine into one required-skills table per role

End of the day, write down for each dataset: row/column count, the likely primary key, how much is missing, what it's for, and what it can join to. That's the report I carry into tomorrow.

2. Data Validation — notebooks/02_data_validation.ipynb

This step earns its place because HR data changes over time, and one day someone will hand me a CSV with an EngagementScore of 250 out of 100. If I don't check for that, a bad row quietly turns into a bad prediction. So before cleaning, I define what 'valid' actually means for this data.

Schema check — do the expected columns (EmployeeID, Age, Department, JobRole, ...) actually exist?

Type check — Age is an integer, MonthlyIncome is numeric, Department is text

Range check — Age between 18–100, Engagement Score 0–100, Attrition probability 0–1

Uniqueness — EmployeeID should never repeat

Category check — Attrition should only ever be Yes/No

For the MVP I'll just write this as plain pandas checks. Once it works, I can swap in a proper library like Pandera so the rules live in one place instead of scattered across notebooks.

assert df['Age'].between(18, 100).all(), "Age out of range"

assert df['EmployeeID'].is_unique, "Duplicate EmployeeID found"

assert set(df['Attrition'].unique()) <= {'Yes', 'No'}, "Unexpected Attrition value"

Longer term this logic moves into app/validation/employee_schema.py, but for now it's fine sitting in the notebook.

3. Data Cleaning — notebooks/03_data_cleaning.ipynb

Now that I know what's wrong with the data, I actually fix it: missing values, duplicates, wrong types, inconsistent categories, outliers, and messy skill-name spelling ('AWS' vs 'Amazon Web Services' vs 'AWS Cloud' all meaning the same thing).

Output of today is a clean copy of every file, saved separately from the raw data so I never overwrite the originals:

data/processed/

├── employee_attrition_processed.csv

├── engagement_processed.csv

├── occupation_master.csv

├── essential_skills_processed.csv

└── software_skills_processed.csv

4. Data Relationships — notebooks/04_data_relationships.ipynb

Last piece of Day 1: actually decide how these five tables connect. I'm writing this down properly in docs/data_relationships.md — for every pair of tables, the join key, the relationship type (one-to-one, one-to-many), and why.

EMPLOYEE

   |

   +-- Employee ID --- Engagement Data

   |

   +-- Job Role ------ Occupation Data

                            |

                            +-- Essential Skills

                            +-- Software Skills

Example row for that markdown table: employee_attrition joins to hr_performance_engagement on EmployeeID, one-to-one, because it's the same employee's performance record.

Day 2 — Machine Learning

Data's clean and I understand how it connects, so now the actual attrition model. I'm being deliberate about not jumping straight to XGBoost — build a boring baseline first so I have something to compare against.

5. Feature Engineering — notebooks/05_feature_engineering.ipynb

Turning raw columns into model-ready features: handle missing values, encode categoricals, scale where it matters, and remove anything that would leak the answer (like a column that's basically a proxy for 'already left').

Starting columns I care about: OverTime, JobSatisfaction, MonthlyIncome, YearsAtCompany, WorkLifeBalance

Engineered ideas: income per year at the company, gap since last promotion, an overall satisfaction score, experience ratio

Note to self: Every engineered feature needs an actual reason — statistical or business — not just 'it seemed interesting'. Otherwise I'm just adding noise.

6. Baseline Model — notebooks/06_baseline_model.ipynb

Logistic Regression, on purpose. It's fast, explainable, and gives me a real probability instead of just a label — which matters here because I want to bucket people into risk levels later, not just yes/no.

from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split

from sklearn.metrics import classification_report, roc_auc_score

 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

 

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

 

probs = model.predict_proba(X_test)[:, 1]

print(roc_auc_score(y_test, probs))

I'm judging this on precision, recall, F1, and ROC-AUC — not accuracy. Attrition is imbalanced (way more people stay than leave), so accuracy alone would just reward the model for predicting 'stays' every time.

7. Model Comparison — notebooks/07_model_comparison.ipynb

Now the same train/test split, same preprocessing pipeline, but three models: Logistic Regression, Random Forest, XGBoost.

Logistic Regression — the explainable baseline

Random Forest — picks up non-linear relationships the linear model can't

XGBoost — usually strongest on tabular data like this

I build one comparison table (Precision / Recall / F1 / ROC-AUC per model) and pick a winner based on the actual cost of mistakes, not just the top number. For attrition specifically, missing a genuinely high-risk employee is expensive — so I'd rather lean toward recall than chase a slightly higher accuracy.

Whichever model wins gets saved:

models/attrition_pipeline.joblib

8. Model Explainability (SHAP) — notebooks/08_model_explainability.ipynb

A prediction like 'Employee 101 — 82% attrition risk' is useless to an actual HR person unless I can answer 'why'. SHAP gives me two levels of explanation:

Global — what generally drives attrition across the whole company (e.g. overtime, low job satisfaction, poor work-life balance, ranked by importance)

Local — why this specific employee is flagged (their personal top 3 contributing factors)

import shap

explainer = shap.TreeExplainer(model)

shap_values = explainer.shap_values(X_test)

shap.summary_plot(shap_values, X_test)   # global view

shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])  # one employee

9. Model Versioning + MLflow — notebooks/09_model_versioning.ipynb

Simple versioning first, before reaching for a whole platform. Every time I train a new model, it gets its own folder with metadata attached, so I can always trace a prediction back to exactly which model made it.

models/

├── v1/

│   ├── attrition_pipeline.joblib

│   └── metadata.json

└── v2/

    ├── attrition_pipeline.joblib

    └── metadata.json

{

  "model_name": "Attrition Prediction Model",

  "version": "v1.0",

  "algorithm": "XGBoost",

  "training_date": "2026-08-27",

  "roc_auc": 0.89,

  "f1_score": 0.78

}

Once that habit is in place, MLflow is the natural next step — it tracks every training run's parameters, metrics, and artifacts automatically instead of me hand-writing JSON files. I'll add it once manual versioning feels like it's holding me back, not before.

Day 3 — Workforce Intelligence

This is the part of the project I actually care most about — the skill-gap and upskilling logic. None of it needs a fancy model to start; it's mostly honest data work with set comparisons and business rules. I can always add a smarter recommendation model later.

10. Engagement Analytics — notebooks/09_engagement_intelligence.ipynb

No ML here yet — just aggregation. Average engagement score, engagement broken down by department, and a list of the lowest-engagement employees so HR can look at them directly.

performance_df.groupby('Department')['EngagementScore'].mean().sort_values()

If later there's a meaningful target to predict, I can revisit this with regression or even a KMeans-based employee segmentation. Not needed for the MVP.

11. Role Intelligence — notebooks/10_role_intelligence.ipynb

occupation_data.csv becomes my 'role master' table — no ML, it's reference data. Every role gets a clean ID and name, so I can later say 'ML Engineer requires Python, MLOps, Docker, AWS' without ambiguity about which role I mean.

12. Employee Skills Table — notebooks/11_employee_skills.ipynb

Here's the catch I need to check for honestly: my current five datasets might not actually contain what skills each employee currently has. Without that, a real skill-gap calculation is impossible — I'd just be comparing role requirements to nothing.

If employee skill data already exists somewhere → use it directly

If it doesn't → build a controlled table for the MVP so the rest of the pipeline has something real to work with

employee_id,current_skill

101,Python

101,SQL

101,AWS

102,Python

102,Docker

13. Skill Gap Engine — notebooks/12_skill_gap_engine.ipynb

The core logic is just set subtraction — required skills minus what the employee already has.

required = {'Python', 'SQL', 'MLOps', 'Docker', 'AWS'}   # ML Engineer

has = {'Python', 'SQL', 'AWS'}                            # Employee 101

gap = required - has

print(gap)   # {'MLOps', 'Docker'}

That's it — Python set operations plus pandas plus a skill-importance weighting, no model required for this part.

14. Organization-Wide Skill Gap — notebooks/13_organization_skill_gap.ipynb

Same logic, rolled up across every employee, so I can see which skills are missing organisation-wide, not just per person.

MLOps           120 employees missing

Cloud            98 employees missing

Generative AI    75 employees missing

Then a simple severity rule: 100+ missing → HIGH, 50+ → MEDIUM, else LOW. That feeds the 'critical organisation skill gaps' chart on the dashboard.

15. Upskilling Recommendation Engine — notebooks/14_recommendation_engine.ipynb

Version 1 is deliberately dumb — plain if/else rules mapping a missing skill to a training recommendation:

if "MLOps" in missing_skills:

    recommend("Learn MLOps")

Version 2, once the basics work, upgrades this with semantic matching. A sentence-transformer model turns both the missing skill and each course description into vectors, then I compare them with cosine similarity — so 'MLOps' can match a course literally called 'Deploying and Monitoring Machine Learning Systems' even though the words don't overlap at all.

16. Employee Intelligence Table — notebooks/15_employee_intelligence.ipynb

Everything from the last two days lands here — one row per employee that pulls together attrition risk, engagement, role, skill gaps, and the recommendation. This table is the actual business output of the whole project; the dashboard is basically just a view onto it.

Employee_ID | Dept | Attrition_Prob | Risk | Engagement | Role         | Skill_Gap | Recommendation

101         | IT   | 0.81           | HIGH | 62         | Data Analyst | MLOps,Docker | Learn MLOps

Day 4 — Application

Time to get this out of notebooks and into something that actually runs as a service. Notebooks are great for exploring, terrible for anything anyone else needs to rely on.

17. Refactor Into Modules

Move the logic I've been writing in cells into real Python modules, organised by responsibility rather than by notebook:

app/

├── main.py

├── api/

│   ├── attrition.py

│   ├── dashboard.py

│   └── skills.py

├── services/

│   ├── attrition_service.py

│   ├── engagement_service.py

│   ├── skill_gap_service.py

│   └── recommendation_service.py

├── validation/

│   ├── employee_schema.py

│   └── engagement_schema.py

├── ml/

│   ├── model_loader.py

│   └── predictor.py

└── utils/

    ├── config.py

    └── logger.py

18. FastAPI Backend

Building this with FastAPI. The endpoints I actually need:

POST /predict/attrition — run the model on a single employee

GET /dashboard/summary — total employees, high-risk count, average engagement

GET /dashboard/attrition-by-department — chart data

GET /dashboard/skill-gaps — the organisation-wide gap table

GET /dashboard/recommendations — per-employee recommendations

GET /employees/{employee_id} — full intelligence record for one person

@app.get("/dashboard/summary")

def dashboard_summary():

    return {

        "total_employees": 2500,

        "high_risk_employees": 124,

        "average_engagement": 72

    }

19. API Input Validation

Every request gets checked with a Pydantic model before it touches any business logic or the ML model — bad data gets a 400 response and never reaches the model, instead of quietly producing a garbage prediction.

20. Logging

Plain Python logging module for the app lifecycle: startup, dataset loaded, prediction requested, model version used, prediction completed, errors.

2026-08-27 10:30:15 | INFO | Prediction request received

2026-08-27 10:30:16 | INFO | Model v1.0 loaded

2026-08-27 10:30:17 | INFO | Prediction completed

21. Prediction Logging

Separately from application logs, I keep a record of every prediction — timestamp, employee ID, model version, probability, risk level — under data/predictions/. This is what lets me later check the prediction distribution for anything unexpected, which is an early warning sign of model drift.

22. Unit Testing

pytest, covering the pieces most likely to break silently:

Missing required column is caught

Invalid engagement score is rejected

Attrition prediction returns a real probability

Risk level is assigned correctly from that probability

Skill gap calculation matches expected output

API returns the expected status codes

23. Streamlit Dashboard

Streamlit because it's the fastest way to turn Python + FastAPI results into something visual, without writing a separate frontend framework. Layout I'm aiming for:

AI WORKFORCE INTELLIGENCE PLATFORM

------------------------------------------------------

| Employees: 2,500 | High Risk: 124 | Avg Engage: 72% |

------------------------------------------------------

          Attrition Risk by Department  [chart]

------------------------------------------------------

  Critical Organisation Skill Gaps

  MLOps          HIGH

  Cloud          HIGH

  Generative AI  MEDIUM

------------------------------------------------------

  AI Upskilling Recommendations

  Employee 101 -> Learn MLOps

  Employee 102 -> Learn AWS

------------------------------------------------------

KPI cards at the top

Department filter

Risk distribution chart

Skill gap chart

Recommendation table

Drill-down into a single employee's details

Later — Enterprise Hardening

Everything below is worth doing, but only once Days 1–4 actually work end to end. There's no point wrapping something in Docker or hooking up drift monitoring if the underlying pipeline still has bugs.

24. Docker

A Dockerfile, docker-compose.yml, and .dockerignore, splitting the backend (FastAPI) and frontend (Streamlit) into separate containers. Mainly so the whole thing can run on someone else's machine without a two-hour setup conversation.

25. Data Drift Monitoring

Compare the distribution of production data against what the model was trained on — e.g. if the average employee age in training was 35 but production data is averaging 47, that's worth investigating. Start with plain pandas + basic statistical comparison; move to a proper tool like Evidently AI once the basic version proves useful.

Watch: age, monthly income, years at company, job satisfaction, overtime, prediction probability

26. Model Performance Monitoring

Once real attrition outcomes come in (i.e. we find out who actually left), compare them against what the model predicted, and recompute precision/recall/F1/ROC-AUC on live data. If performance has genuinely dropped, that's the trigger to retrain — not a fixed calendar date.

27. Retraining Strategy

Writing down the actual rule in advance so it's not a judgement call under pressure later:

IF drift > threshold

OR F1 drops below threshold

OR 6 months of new data collected

THEN retrain the model

Full lifecycle: new data → validation → training → evaluation → MLflow tracking → approval → deploy new version.

28. Documentation

README needs: problem statement, architecture diagram, dataset description, setup instructions, how to run it, the ML models used, evaluation metrics, the API list, dashboard screenshots, Docker instructions, monitoring strategy, and a future-improvements section.

29. Deployment

Final shape of the whole thing:

                        USER

                         |

                Streamlit UI (frontend)

                         |

                FastAPI Backend

                         |

     +-------------------+-------------------+

ML Prediction      Skill Engine         Analytics

     +-------------------+-------------------+

              Employee Intelligence

                         |

              Logging + Monitoring

                         |

                  Model Registry

Master Checklist

Everything from above, in the exact order I'm actually going to do it.

Day 1 — Data

☐ 01 Data Understanding

☐ 02 Data Validation

☐ 03 Data Cleaning

☐ 04 Data Relationships

Day 2 — Machine Learning

☐ 05 Feature Engineering

☐ 06 Baseline Model

☐ 07 Model Comparison

☐ 08 SHAP Explainability

☐ 09 Model Versioning + MLflow

Day 3 — Workforce Intelligence

☐ 10 Engagement Intelligence

☐ 11 Role Intelligence

☐ 12 Employee Skills

☐ 13 Skill Gap Engine

☐ 14 Organization Skill Gap

☐ 15 Recommendation Engine

☐ 16 Employee Intelligence Layer

Day 4 — Application

☐ 17 Refactor Notebook Code Into Modules

☐ 18 FastAPI Backend

☐ 19 API Input Validation

☐ 20 Logging

☐ 21 Prediction Logging

☐ 22 Unit Testing

☐ 23 Streamlit Dashboard

Later — Enterprise Hardening

☐ 24 Docker

☐ 25 Data Drift Monitoring

☐ 26 Model Performance Monitoring

☐ 27 Retraining Strategy

☐ 28 Documentation

☐ 29 Deployment

Rule I'm holding myself to: don't jump ahead to SHAP, MLflow, Docker, or deployment before the four Day-1 steps are actually finished. A shaky data foundation makes every later step slower, not faster.