import os

class Settings:
    PROJECT_NAME: str = "Enterprise HR AI Platform"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_RAW_DIR: str = os.path.join(BASE_DIR, "data", "raw")
    DATA_PROCESSED_DIR: str = os.path.join(BASE_DIR, "data", "processed")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    PREDICTIONS_DIR: str = os.path.join(BASE_DIR, "data", "predictions")
    
    # Active Model
    ACTIVE_MODEL_VERSION: str = os.getenv("ACTIVE_MODEL_VERSION", "v2")

settings = Settings()
os.makedirs(settings.PREDICTIONS_DIR, exist_ok=True)
