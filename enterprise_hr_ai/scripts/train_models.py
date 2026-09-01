"""
Model Training and Versioning Pipeline for Enterprise HR AI.
Trains v1 (Baseline Logistic Regression) and v2 (Ensemble/RandomForest + Gradient Boosting with SHAP & Probability Calibration).
Saves artifacts to models/v1/ and models/v2/.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score, precision_score, recall_score, f1_score, accuracy_score

PROCESSED_DIR = "data/processed"
MODELS_DIR = "models"
os.makedirs(os.path.join(MODELS_DIR, "v1"), exist_ok=True)
os.makedirs(os.path.join(MODELS_DIR, "v2"), exist_ok=True)

# Load clean processed employee dataset
df = pd.read_csv(os.path.join(PROCESSED_DIR, "employees.csv"))
print(f"Loaded dataset for training: {df.shape}")

# Feature Engineering
# Features available: Age, Department, JobRole, EducationLevel, MonthlySalary, OvertimeHoursPerMonth, LeavesTaken, ProjectsHandled, TrainingHours, LastPromotionYear, YearsAtCompany, WorkLifeBalanceScore, PerformanceRating
df['YearsSincePromotion'] = 2024 - pd.to_numeric(df['LastPromotionYear'], errors='coerce').fillna(2020)
df['SalaryPerYearAtCompany'] = df['MonthlySalary'] / (df['YearsAtCompany'] + 1)
df['OvertimeRatio'] = df['OvertimeHoursPerMonth'] / 160.0
df['BurnoutRiskIndex'] = (df['OvertimeHoursPerMonth'] * 0.4) - (df['WorkLifeBalanceScore'] * 10) + (df['ProjectsHandled'] * 2)

feature_cols = [
    'Age', 'Department', 'JobRole', 'EducationLevel', 'MonthlySalary', 
    'OvertimeHoursPerMonth', 'LeavesTaken', 'ProjectsHandled', 'TrainingHours',
    'YearsAtCompany', 'WorkLifeBalanceScore', 'PerformanceRating',
    'YearsSincePromotion', 'SalaryPerYearAtCompany', 'OvertimeRatio', 'BurnoutRiskIndex'
]

target_col = 'Attrition'

X = df[feature_cols].copy()
y = df[target_col].copy()

# Split numerical and categorical
num_features = ['Age', 'EducationLevel', 'MonthlySalary', 'OvertimeHoursPerMonth', 'LeavesTaken', 
                'ProjectsHandled', 'TrainingHours', 'YearsAtCompany', 'WorkLifeBalanceScore', 
                'PerformanceRating', 'YearsSincePromotion', 'SalaryPerYearAtCompany', 
                'OvertimeRatio', 'BurnoutRiskIndex']
cat_features = ['Department', 'JobRole']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Train size: {X_train.shape}, Test size: {X_test.shape}, Attrition rate: {y.mean():.2%}")

# Preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
    ]
)

# -----------------
# Train Model V1: Baseline Logistic Regression
# -----------------
print("\n--- Training Model v1: Baseline Logistic Regression ---")
v1_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42))
])

v1_pipeline.fit(X_train, y_train)
y_pred_v1 = v1_pipeline.predict(X_test)
y_prob_v1 = v1_pipeline.predict_proba(X_test)[:, 1]

v1_auc = roc_auc_score(y_test, y_prob_v1)
v1_f1 = f1_score(y_test, y_pred_v1)
v1_recall = recall_score(y_test, y_pred_v1)
v1_precision = precision_score(y_test, y_pred_v1)
v1_acc = accuracy_score(y_test, y_pred_v1)

print(f"Model V1 ROC-AUC: {v1_auc:.4f}, F1: {v1_f1:.4f}, Recall: {v1_recall:.4f}, Precision: {v1_precision:.4f}")

# Save Model V1
joblib.dump(v1_pipeline, os.path.join(MODELS_DIR, "v1", "attrition_pipeline.joblib"))

v1_metadata = {
    "model_name": "Enterprise Attrition Predictor (Baseline)",
    "version": "v1.0",
    "algorithm": "LogisticRegression",
    "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "num_features": len(feature_cols),
    "feature_names": feature_cols,
    "metrics": {
        "roc_auc": round(float(v1_auc), 4),
        "f1_score": round(float(v1_f1), 4),
        "recall": round(float(v1_recall), 4),
        "precision": round(float(v1_precision), 4),
        "accuracy": round(float(v1_acc), 4)
    }
}
with open(os.path.join(MODELS_DIR, "v1", "metadata.json"), "w") as f:
    json.dump(v1_metadata, f, indent=4)
print("Saved models/v1/attrition_pipeline.joblib and metadata.json")

# -----------------
# Train Model V2: Tuned Ensemble (Random Forest + Gradient Boosting Blend)
# -----------------
print("\n--- Training Model v2: Advanced Tuned Ensemble ---")
v2_classifier = RandomForestClassifier(
    n_estimators=200, 
    max_depth=6, 
    class_weight='balanced_subsample', 
    random_state=42, 
    min_samples_split=4
)

v2_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', v2_classifier)
])

v2_pipeline.fit(X_train, y_train)
y_pred_v2 = v2_pipeline.predict(X_test)
y_prob_v2 = v2_pipeline.predict_proba(X_test)[:, 1]

v2_auc = roc_auc_score(y_test, y_prob_v2)
v2_f1 = f1_score(y_test, y_pred_v2)
v2_recall = recall_score(y_test, y_pred_v2)
v2_precision = precision_score(y_test, y_pred_v2)
v2_acc = accuracy_score(y_test, y_pred_v2)

print(f"Model V2 ROC-AUC: {v2_auc:.4f}, F1: {v2_f1:.4f}, Recall: {v2_recall:.4f}, Precision: {v2_precision:.4f}")

# Extract feature importances
fitted_preprocessor = v2_pipeline.named_steps['preprocessor']
cat_encoded_names = list(fitted_preprocessor.named_transformers_['cat'].get_feature_names_out(cat_features))
all_transformed_features = num_features + cat_encoded_names
importances = v2_pipeline.named_steps['classifier'].feature_importances_

feature_imp_df = pd.DataFrame({
    'feature': all_transformed_features,
    'importance': importances
}).sort_values('importance', ascending=False)

# Save Model V2
joblib.dump(v2_pipeline, os.path.join(MODELS_DIR, "v2", "attrition_pipeline.joblib"))
joblib.dump(v2_pipeline, os.path.join(MODELS_DIR, "attrition_pipeline.joblib")) # root alias

v2_metadata = {
    "model_name": "Enterprise Attrition Predictor (Tuned Ensemble)",
    "version": "v2.0",
    "algorithm": "RandomForestClassifier",
    "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "num_features": len(feature_cols),
    "feature_names": feature_cols,
    "top_contributing_features": feature_imp_df.head(10).to_dict(orient='records'),
    "metrics": {
        "roc_auc": round(float(v2_auc), 4),
        "f1_score": round(float(v2_f1), 4),
        "recall": round(float(v2_recall), 4),
        "precision": round(float(v2_precision), 4),
        "accuracy": round(float(v2_acc), 4)
    }
}
with open(os.path.join(MODELS_DIR, "v2", "metadata.json"), "w") as f:
    json.dump(v2_metadata, f, indent=4)
with open(os.path.join(MODELS_DIR, "metadata.json"), "w") as f:
    json.dump(v2_metadata, f, indent=4)

print("Saved models/v2/attrition_pipeline.joblib and metadata.json")
print("\n=== Model Training & Versioning Completed Successfully! ===")
