from typing import Dict, Any, List
from pydantic import BaseModel
import os

class ModelRegistryEntry(BaseModel):
    model_id: str
    model_name: str
    dataset: str
    training_type: str
    feature_contract_version: str
    scaler_path: str
    xgboost_artifact: str
    isolation_forest_artifact: str
    status: str
    evaluation_report: str

class ModelRegistry:
    """Simple deterministc registry for SENTRANET model tracking."""
    
    _registry = {
        "sentranet_synthetic_v1": ModelRegistryEntry(
            model_id="sentranet_synthetic_v1",
            model_name="Baseline Synthetic Model",
            dataset="Synthetic Internal",
            training_type="SYNTHETIC",
            feature_contract_version="v1.0",
            scaler_path="models/scaler/sentranet_scaler.joblib",
            xgboost_artifact="models/xgboost/sentranet_xgboost.json",
            isolation_forest_artifact="models/isolation_forest/sentranet_isolation_forest.joblib",
            status="PRODUCTION",
            evaluation_report="reports/PHASE10_EVALUATION_REPORT.md"
        ),
        "sentranet_cicids2017_v1": ModelRegistryEntry(
            model_id="sentranet_cicids2017_v1",
            model_name="CIC-IDS2017 Experimental Model",
            dataset="CIC-IDS2017",
            training_type="REAL DATASET",
            feature_contract_version="v1.0",
            scaler_path="models/experiments/cicids2017/scaler.joblib",
            xgboost_artifact="models/experiments/cicids2017/xgboost.joblib",
            isolation_forest_artifact="models/experiments/cicids2017/isolation_forest.joblib",
            status="EXPERIMENTAL",
            evaluation_report="reports/cicids2017_step7_evaluation.md"
        )
    }

    @classmethod
    def get_model(cls, model_id: str) -> ModelRegistryEntry:
        if model_id not in cls._registry:
            raise ValueError(f"Model ID '{model_id}' not found in registry.")
        
        entry = cls._registry[model_id]
        if not os.path.exists(entry.xgboost_artifact):
            raise FileNotFoundError(f"Missing XGBoost artifact for {model_id} at {entry.xgboost_artifact}")
        if not os.path.exists(entry.isolation_forest_artifact):
            raise FileNotFoundError(f"Missing IF artifact for {model_id} at {entry.isolation_forest_artifact}")
            
        return entry

    @classmethod
    def list_models(cls) -> List[ModelRegistryEntry]:
        return list(cls._registry.values())
