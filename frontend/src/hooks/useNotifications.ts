import { useState, useEffect, useRef, useCallback } from 'react';
import type { AlertItemResponse, AnalyzeResponse, NotificationToast } from '../types';
import { formatRiskScore, formatAttackClass } from '../utils/formatters';

export function useNotifications(
  alerts: AlertItemResponse[],
  currentRisk: AnalyzeResponse | null
) {
  const [toasts, setToasts] = useState<NotificationToast[]>([]);
  const processedEventIdsRef = useRef<Set<string>>(new Set());
  const lastForecastTsRef = useRef<string | null>(null);

  const addToast = useCallback((toast: Omit<NotificationToast, 'id'>) => {
    const id = `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const newToast: NotificationToast = { ...toast, id };
    setToasts((prev) => [newToast, ...prev.slice(0, 4)]); // Keep max 5

    // Auto dismiss after 6 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 6000);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // Monitor alert events for meaningful transitions
  useEffect(() => {
    if (!alerts || alerts.length === 0) return;

    for (const alert of alerts) {
      if (processedEventIdsRef.current.has(alert.alert_event_id)) continue;
      processedEventIdsRef.current.add(alert.alert_event_id);

      const type = alert.event_type.toUpperCase();
      if (type === 'ALERT_CREATED') {
        addToast({
          type: 'ALERT',
          title: 'NEW SECURITY ALERT',
          message: `${formatAttackClass(alert.attack_class)} detected. Risk: ${formatRiskScore(alert.risk_score)}.`,
          timestamp: alert.timestamp,
          severity: alert.severity,
          incidentId: alert.incident_id || undefined,
        });
      } else if (type === 'ALERT_ESCALATED') {
        addToast({
          type: 'ALERT',
          title: 'ALERT ESCALATED',
          message: `Escalated to ${alert.severity}. Peak risk: ${formatRiskScore(alert.risk_score)}.`,
          timestamp: alert.timestamp,
          severity: alert.severity,
          incidentId: alert.incident_id || undefined,
        });
      } else if (type === 'ALERT_RESOLVED') {
        addToast({
          type: 'INFO',
          title: 'ALERT RESOLVED',
          message: `Incident ${alert.incident_id || 'Alert'} has stabilized and resolved.`,
          timestamp: alert.timestamp,
          severity: 'INFO',
          incidentId: alert.incident_id || undefined,
        });
      }
    }
  }, [alerts, addToast]);

  // Monitor forecast triggers
  useEffect(() => {
    if (!currentRisk) return;
    if (
      currentRisk.forecast_active &&
      currentRisk.timestamp &&
      currentRisk.timestamp !== lastForecastTsRef.current
    ) {
      lastForecastTsRef.current = currentRisk.timestamp;
      addToast({
        type: 'FORECAST',
        title: 'AI FORECAST SIGNAL',
        message: `Predictive emergence signal: ${formatAttackClass(currentRisk.forecast_class || currentRisk.attack_class)}. Forecast confidence: ${formatRiskScore(currentRisk.forecast_confidence)}.`,
        timestamp: currentRisk.timestamp,
        severity: 'ALERT',
      });
    }
  }, [currentRisk, addToast]);

  return {
    toasts,
    dismissToast,
  };
}
