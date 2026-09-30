import { useState, useEffect, useCallback, useRef } from 'react';
import type { AlertItemResponse, CurrentAlertResponse } from '../types';
import { getAlerts, getCurrentAlert } from '../services/api';
import { useRealtime } from '../context/RealtimeContext';

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

    // Slower fallback interval (e.g. 30s)
    const intervalMs = 30000;

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

  const { subscribe } = useRealtime();

  useEffect(() => {
    const handleAlertEvent = (_payload: any) => {
        // Just trigger a refetch of the alerts API to keep things simple for now
        // since alerts state merges can be complex.
        fetchAlerts();
    };

    const unsubCreated = subscribe('alert.created', handleAlertEvent);
    const unsubUpdated = subscribe('alert.updated', handleAlertEvent);
    const unsubResolved = subscribe('incident.resolved', handleAlertEvent);

    return () => {
        unsubCreated();
        unsubUpdated();
        unsubResolved();
    };
  }, [subscribe, fetchAlerts]);

  return {
    alerts,
    currentAlert,
    isLoading,
    error,
    refresh: fetchAlerts,
  };
}
