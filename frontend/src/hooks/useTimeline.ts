import { useState, useEffect, useCallback, useRef } from 'react';
import type { TimelineResponse, TimelinePointResponse } from '../types';
import { getTimeline } from '../services/api';
import { useRealtime } from '../context/RealtimeContext';

export function useTimeline(isReplayActive: boolean, limit: number = 50) {
  const [timeline, setTimeline] = useState<TimelineResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchTimeline = useCallback(async () => {
    try {
      const data = await getTimeline(limit);
      setTimeline(data);
      setError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error fetching timeline';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchTimeline();

    // Slower fallback interval (e.g. 30s)
    const intervalMs = 30000;

    const setupTimer = () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      if (!document.hidden) {
        timerRef.current = window.setInterval(fetchTimeline, intervalMs);
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
        fetchTimeline();
        setupTimer();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [fetchTimeline, isReplayActive]);

  const { subscribe } = useRealtime();

  useEffect(() => {
    const unsub = subscribe('risk.updated', () => {
        // Timeline updates whenever there's a new window/risk state
        fetchTimeline();
    });

    return () => {
        unsub();
    };
  }, [subscribe, fetchTimeline]);

  const points: TimelinePointResponse[] = timeline?.points || [];

  return {
    timeline,
    points,
    isLoading,
    error,
    refresh: fetchTimeline,
  };
}
