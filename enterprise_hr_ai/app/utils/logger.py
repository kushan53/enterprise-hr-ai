import logging
import os
import json
from datetime import datetime
from app.utils.config import settings

# Setup standard application logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EnterpriseHRAI")

def log_prediction(employee_id: str or int, model_version: str, probability: float, risk_category: str, features: dict):
    """
    Persists prediction logs to data/predictions/ for drift monitoring and audit compliance.
    """
    record = {
        "timestamp": datetime.now().isoformat(),
        "employee_id": str(employee_id),
        "model_version": model_version,
        "attrition_probability": probability,
        "risk_category": risk_category,
        "input_features": features
    }
    
    log_file = os.path.join(settings.PREDICTIONS_DIR, f"predictions_{datetime.now().strftime('%Y%m%d')}.jsonl")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        logger.info(f"Prediction logged for Employee {employee_id} [Risk: {risk_category}, Prob: {probability}]")
    except Exception as e:
        logger.error(f"Failed to log prediction record: {e}")
