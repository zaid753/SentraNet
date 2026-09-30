import { useState, useEffect, useCallback, useRef } from 'react';
import type { IncidentItemResponse } from '../types';
import { getIncidents } from '../services/api';
import { useRealtime } from '../context/RealtimeContext';

export function useIncidents(isReplayActive: boolean) {
  const [incidents, setIncidents] = useState<IncidentItemResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchIncidents = useCallback(async () => {
    try {
      const data = await getIncidents();
      setIncidents(data);
      setError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error fetching incidents';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncidents();

    // Slower fallback interval (e.g. 30s)
    const intervalMs = 30000;

    const setupTimer = () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      if (!document.hidden) {
        timerRef.current = window.setInterval(fetchIncidents, intervalMs);
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
        fetchIncidents();
        setupTimer();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [fetchIncidents, isReplayActive]);

  const { subscribe } = useRealtime();

  useEffect(() => {
    const handleEvent = (_payload: any) => {
        fetchIncidents();
    };

    const unsubCreated = subscribe('alert.created', handleEvent);
    const unsubUpdated = subscribe('alert.updated', handleEvent);
    const unsubResolved = subscribe('incident.resolved', handleEvent);

    return () => {
        unsubCreated();
        unsubUpdated();
        unsubResolved();
    };
  }, [subscribe, fetchIncidents]);

  const activeIncident = incidents.find(
    (inc) => inc.status.toUpperCase() === 'ACTIVE'
  ) || null;

  return {
    incidents,
    activeIncident,
    isLoading,
    error,
    refresh: fetchIncidents,
  };
}
