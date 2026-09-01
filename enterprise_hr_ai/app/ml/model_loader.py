import os
import joblib
import json
from app.utils.config import settings
from app.utils.logger import logger

class ModelLoader:
    _instance = None
    _models = {}
    _metadata = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.load_all_models()
        return cls._instance

    def load_all_models(self):
        for version in ["v1", "v2"]:
            model_path = os.path.join(settings.MODELS_DIR, version, "attrition_pipeline.joblib")
            meta_path = os.path.join(settings.MODELS_DIR, version, "metadata.json")
            
            if os.path.exists(model_path):
                try:
                    self._models[version] = joblib.load(model_path)
                    logger.info(f"Successfully loaded Model {version} from {model_path}")
                except Exception as e:
                    logger.error(f"Error loading model {version}: {e}")
                    
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        self._metadata[version] = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading metadata for {version}: {e}")

    def get_model(self, version: str = None):
        ver = version or settings.ACTIVE_MODEL_VERSION
        return self._models.get(ver) or self._models.get("v2") or self._models.get("v1")

    def get_metadata(self, version: str = None):
        ver = version or settings.ACTIVE_MODEL_VERSION
        return self._metadata.get(ver, {})

model_loader = ModelLoader.get_instance()
