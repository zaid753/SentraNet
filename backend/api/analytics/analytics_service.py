from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional
import datetime
from backend.api.analytics.analytics_repository import AnalyticsRepository
from backend.api.services.sentranet_service import SentranetService
from backend.api.services.replay_service import ReplayService
from backend.api.realtime.websocket_manager import ws_manager

class AnalyticsService:
    def __init__(self, db: Session):
        self.repo = AnalyticsRepository(db)
        self.db = db

    def get_overview(self, range_filter: str = "all") -> Dict[str, Any]:
        start_time = None
        now = datetime.datetime.now(datetime.timezone.utc)
        if range_filter == "24h":
            start_time = now - datetime.timedelta(hours=24)
        elif range_filter == "7d":
            start_time = now - datetime.timedelta(days=7)
        elif range_filter == "30d":
            start_time = now - datetime.timedelta(days=30)
            
        return self.repo.get_overview(start_time)

    def get_system_health(self) -> Dict[str, Any]:
        # 1. DB Health
        db_status = "Operational"
        try:
            self.db.execute(text("SELECT 1"))
        except Exception:
            db_status = "Unavailable"

        # 2. Sentranet Service Health (ML components)
        try:
            service = SentranetService.get_instance()
            
            # XGBoost
            xgboost_status = "Available" if service.risk_engine and service.risk_engine.clf else "Unavailable"
            xgboost_detail = {
                "status": xgboost_status,
                "version": "Not tracked",
                "feature_count": len(service.risk_engine.feature_names) if service.risk_engine else 0,
                "classes": service.risk_engine.classes if service.risk_engine else []
            }
            
            # Isolation Forest
            if_status = "Available" if service.anomaly_detector and service.anomaly_detector.clf else "Unavailable"
            if_detail = {
                "status": if_status,
                "version": "Not tracked",
                "feature_count": len(service.anomaly_detector.feature_names) if service.anomaly_detector else 0,
                "classes": ["ANOMALY"]
            }

            # Forecast Engine
            forecast_status = "Available" if service.forecast_engine else "Unavailable"
            forecast_detail = {
                "status": forecast_status,
                "version": "Not tracked",
                "feature_count": 0,
                "classes": []
            }
            
        except Exception:
            xgboost_detail = {"status": "Unknown"}
            if_detail = {"status": "Unknown"}
            forecast_detail = {"status": "Unknown"}

        # 3. Realtime Health
        try:
            active_conns = len(ws_manager.active_connections)
            realtime_status = "Connected" if active_conns > 0 else "Idle"
        except Exception:
            realtime_status = "Unknown"

        # 4. Replay Health
        try:
            replay = ReplayService.get_instance()
            replay_status = "Operational" if replay.is_active() else "Idle"
        except Exception:
            replay_status = "Unknown"

        api_status = "Operational"
        if db_status == "Unavailable":
            api_status = "Degraded"

        overall_status = "Operational" if api_status == "Operational" else "Degraded"

        return {
            "status": overall_status,
            "api": api_status,
            "database": db_status,
            "realtime": realtime_status,
            "xgboost": xgboost_detail,
            "isolation_forest": if_detail,
            "forecast_engine": forecast_detail,
            "replay": replay_status
        }
