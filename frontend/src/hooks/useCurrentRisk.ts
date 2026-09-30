import { useState, useEffect, useCallback, useRef } from 'react';
import type { AnalyzeResponse } from '../types';
import { getCurrentRisk } from '../services/api';
import { useRealtime } from '../context/RealtimeContext';

export function useCurrentRisk(isReplayActive: boolean) {
  const [risk, setRisk] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchRisk = useCallback(async () => {
    try {
      const data = await getCurrentRisk();
      setRisk(data);
      setError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error fetching telemetry';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRisk();

    // Still keep a slow fallback poll for safety (e.g. 30s)
    const intervalMs = 30000;

    const setupTimer = () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      if (!document.hidden) {
        timerRef.current = window.setInterval(fetchRisk, intervalMs);
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
        fetchRisk();
        setupTimer();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [fetchRisk, isReplayActive]);

  const { subscribe } = useRealtime();

  useEffect(() => {
    const unsubscribe = subscribe('risk.updated', (payload: any) => {
      setRisk((prev) => {
        // If there's an existing risk, keep its fields but override with the event payload
        if (prev) {
            return {
                ...prev,
                ...payload
            };
        }
        return payload;
      });
      setIsLoading(false);
    });
    return () => {
        unsubscribe();
    };
  }, [subscribe]);

  return {
    risk,
    isLoading,
    error,
    refresh: fetchRisk,
  };
}
