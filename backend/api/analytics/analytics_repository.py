import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List, Optional
from backend.api.models import Incident, Alert

class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self, workspace_id: str, start_time: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        incidents_query = self.db.query(Incident).filter(Incident.workspace_id == workspace_id)
        alerts_query = self.db.query(Alert).filter(Alert.workspace_id == workspace_id)

        if start_time:
            incidents_query = incidents_query.filter(Incident.created_at >= start_time)
            alerts_query = alerts_query.filter(Alert.created_at >= start_time)

        all_incidents = incidents_query.all()
        all_alerts = alerts_query.all()

        total_incidents = len(all_incidents)
        active_incidents = sum(1 for i in all_incidents if i.status != "RESOLVED")
        resolved_incidents = total_incidents - active_incidents
        total_alerts = len(all_alerts)
        
        peak_risk = max([i.peak_risk_score for i in all_incidents] + [0.0])

        resolution_times = [
            (i.resolved_at - i.created_at).total_seconds()
            for i in all_incidents if i.status == "RESOLVED" and i.resolved_at
        ]
        avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else None

        threat_dist = {}
        for i in all_incidents:
            tc = i.attack_class or "UNKNOWN"
            threat_dist[tc] = threat_dist.get(tc, 0) + 1

        # Calculate basic trends (daily buckets if data spans multiple days, or hourly)
        # For simplicity in Phase 7, we will just return points for each incident/alert
        # Grouping by hour is a good middle ground
        incident_trend_dict = {}
        risk_trend_dict = {}
        
        for i in all_incidents:
            hr = i.created_at.strftime("%Y-%m-%dT%H:00:00Z")
            incident_trend_dict[hr] = incident_trend_dict.get(hr, 0) + 1
            if hr not in risk_trend_dict or i.peak_risk_score > risk_trend_dict[hr]:
                risk_trend_dict[hr] = i.peak_risk_score

        alert_trend_dict = {}
        for a in all_alerts:
            hr = a.created_at.strftime("%Y-%m-%dT%H:00:00Z")
            alert_trend_dict[hr] = alert_trend_dict.get(hr, 0) + 1

        def format_trend(d):
            return [{"timestamp": k, "value": v} for k, v in sorted(d.items())]

        return {
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "resolved_incidents": resolved_incidents,
            "total_alerts": total_alerts,
            "peak_risk": peak_risk,
            "average_resolution_seconds": avg_resolution,
            "threat_distribution": threat_dist,
            "incident_trend": format_trend(incident_trend_dict),
            "alert_trend": format_trend(alert_trend_dict),
            "risk_trend": format_trend(risk_trend_dict)
        }
