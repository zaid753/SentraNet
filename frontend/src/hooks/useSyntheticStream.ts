import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  TelemetryStatusResponse,
  SyntheticStatusResponse,
  SyntheticStartRequest,
} from '../types';
import {
  getTelemetryStatus,
  getSyntheticStatus,
  startSyntheticStream,
  stopSyntheticStream,
  pauseSyntheticStream,
  resumeSyntheticStream,
  flushTelemetry,
  resetTelemetry,
} from '../services/api';
import { useRealtime } from '../context/RealtimeContext';

export function useSyntheticStream() {
  const [telemetryStatus, setTelemetryStatus] = useState<TelemetryStatusResponse | null>(null);
  const [syntheticStatus, setSyntheticStatus] = useState<SyntheticStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const [tStatus, sStatus] = await Promise.all([
        getTelemetryStatus().catch(() => null),
        getSyntheticStatus().catch(() => null),
      ]);
      if (tStatus) setTelemetryStatus(tStatus);
      if (sStatus) setSyntheticStatus(sStatus);
      setActionError(null);
      return { tStatus, sStatus };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch telemetry status';
      setActionError(msg);
      return null;
    }
  }, []);

  const handleStart = async (request: SyntheticStartRequest) => {
    setIsLoading(true);
    setActionError(null);
    try {
      await startSyntheticStream(request);
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to start synthetic stream';
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
      await stopSyntheticStream();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to stop synthetic stream';
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
      await pauseSyntheticStream();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to pause synthetic stream';
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
      await resumeSyntheticStream();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to resume synthetic stream';
      setActionError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handleFlush = async () => {
    setIsLoading(true);
    setActionError(null);
    try {
      await flushTelemetry();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to flush telemetry window';
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
      await resetTelemetry();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to reset telemetry';
      setActionError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();

    // Slower fallback polling
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
    // If the window updates, the telemetry state updates
    const unsub = subscribe('telemetry.window.created', () => {
        fetchStatus();
    });

    return () => {
        unsub();
    };
  }, [subscribe, fetchStatus]);

  return {
    telemetryStatus,
    syntheticStatus,
    isRunning: Boolean(syntheticStatus?.running),
    isPaused: syntheticStatus?.status === 'paused',
    isLoading,
    actionError,
    start: handleStart,
    stop: handleStop,
    pause: handlePause,
    resume: handleResume,
    flush: handleFlush,
    reset: handleReset,
    refresh: fetchStatus,
  };
}
