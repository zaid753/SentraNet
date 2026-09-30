import { useState, useEffect, useCallback, useRef } from 'react';
import type { AnalyzeResponse } from '../types';
import { getCurrentRisk } from '../services/api';

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

    const intervalMs = isReplayActive ? 1500 : 5000;

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

  return {
    risk,
    isLoading,
    error,
    refresh: fetchRisk,
  };
}
