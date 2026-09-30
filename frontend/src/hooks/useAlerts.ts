import { useState, useEffect, useCallback, useRef } from 'react';
import type { AlertItemResponse, CurrentAlertResponse } from '../types';
import { getAlerts, getCurrentAlert } from '../services/api';

export function useAlerts(isReplayActive: boolean, limit: number = 20) {
  const [alerts, setAlerts] = useState<AlertItemResponse[]>([]);
  const [currentAlert, setCurrentAlert] = useState<CurrentAlertResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchAlerts = useCallback(async () => {
    try {
      const [alertsData, currentData] = await Promise.all([
        getAlerts(limit),
        getCurrentAlert(),
      ]);
      setAlerts(alertsData);
      setCurrentAlert(currentData);
      setError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error fetching alerts';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchAlerts();

    const intervalMs = isReplayActive ? 2500 : 6000;

    const setupTimer = () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      if (!document.hidden) {
        timerRef.current = window.setInterval(fetchAlerts, intervalMs);
      }
    };

    setupTimer();

    const handleVisibilityChange = () => {
      if (document.hidden) {
        if (timerRef.current) {
          window.clearInterval(timerRef.current);
          timerRef.current = null;
        }
      } else {
        fetchAlerts();
        setupTimer();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [fetchAlerts, isReplayActive]);

  return {
    alerts,
    currentAlert,
    isLoading,
    error,
    refresh: fetchAlerts,
  };
}
