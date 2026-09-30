import { useState, useEffect, useCallback, useRef } from 'react';
import type { ReplayStatusResponse, ReplayStartRequest } from '../types';
import {
  getReplayStatus,
  startReplay,
  stopReplay,
  pauseReplay,
  resumeReplay,
  stepReplay,
  resetStream,
} from '../services/api';
import { useRealtime } from '../context/RealtimeContext';

export function useReplay() {
  const [status, setStatus] = useState<ReplayStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await getReplayStatus();
      setStatus(data);
      setActionError(null);
      return data;
    } catch (err: unknown) {
      // Backend might be offline
      const msg = err instanceof Error ? err.message : 'Failed to fetch replay status';
      setActionError(msg);
      return null;
    }
  }, []);

  const handleStart = async (request: ReplayStartRequest) => {
    setIsLoading(true);
    setActionError(null);
    try {
      await startReplay(request);
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to start replay';
      setActionError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = async () => {
    setIsLoading(true);
    setActionError(null);
    try {
      await stopReplay();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to stop replay';
      setActionError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handlePause = async () => {
    setIsLoading(true);
    setActionError(null);
    try {
      await pauseReplay();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to pause replay';
      setActionError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handleResume = async () => {
    setIsLoading(true);
    setActionError(null);
    try {
      await resumeReplay();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to resume replay';
      setActionError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handleStep = async () => {
    setIsLoading(true);
    setActionError(null);
    try {
      await stepReplay();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to step replay';
      setActionError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    setIsLoading(true);
    setActionError(null);
    try {
      await resetStream();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to reset stream';
      setActionError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();

    // Slower fallback interval
    const intervalMs = 15000;

    const setupTimer = () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      if (!document.hidden) {
        timerRef.current = window.setInterval(fetchStatus, intervalMs);
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
        fetchStatus();
        setupTimer();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [fetchStatus]);

  const { subscribe } = useRealtime();

  useEffect(() => {
    const unsub = subscribe('replay.status.changed', () => {
        // Fetch full status on status change
        fetchStatus();
    });

    return () => {
        unsub();
    };
  }, [subscribe, fetchStatus]);

  return {
    status,
    isRunning: Boolean(status?.running),
    isPaused: Boolean(status?.paused),
    isLoading,
    actionError,
    start: handleStart,
    stop: handleStop,
    pause: handlePause,
    resume: handleResume,
    step: handleStep,
    reset: handleReset,
    refresh: fetchStatus,
  };
}
