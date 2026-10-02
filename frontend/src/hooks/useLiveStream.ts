import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  TelemetryStatusResponse,
  LiveStatusResponse,
  LiveStartRequest,
  InterfaceResponse
} from '../types';
import {
  getTelemetryStatus,
  getLiveStatus,
  startLiveCapture,
  stopLiveCapture,
  getInterfaces
} from '../services/api';
import { useRealtime } from '../context/RealtimeContext';

export function useLiveStream() {
  const [telemetryStatus, setTelemetryStatus] = useState<TelemetryStatusResponse | null>(null);
  const [liveStatus, setLiveStatus] = useState<LiveStatusResponse | null>(null);
  const [interfaces, setInterfaces] = useState<InterfaceResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchInterfaces = useCallback(async () => {
    try {
      const ifaces = await getInterfaces();
      setInterfaces(ifaces);
    } catch (err: unknown) {
      console.error("Failed to fetch interfaces", err);
    }
  }, []);

  const fetchStatus = useCallback(async () => {
    try {
      const [tStatus, lStatus] = await Promise.all([
        getTelemetryStatus().catch(() => null),
        getLiveStatus().catch(() => null),
      ]);
      if (tStatus) setTelemetryStatus(tStatus);
      if (lStatus) setLiveStatus(lStatus);
      
      // if (lStatus?.error_message) {
      //   setActionError(lStatus.error_message);
      // } else {
      //   setActionError(null);
      // }
      
      return { tStatus, lStatus };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch telemetry status';
      setActionError(msg);
      return null;
    }
  }, []);

  const handleStart = async (request: LiveStartRequest) => {
    setIsLoading(true);
    setActionError(null);
    try {
      await startLiveCapture(request);
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to start live stream';
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
      await stopLiveCapture();
      await fetchStatus();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to stop live stream';
      setActionError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInterfaces();
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
  }, [fetchStatus, fetchInterfaces]);

  const { subscribe } = useRealtime();

  useEffect(() => {
    // If the window updates or status changes
    const unsubWin = subscribe('telemetry.window.created', () => {
        fetchStatus();
    });
    const unsubStat = subscribe('system.status.changed', () => {
        fetchStatus();
    });

    return () => {
        unsubWin();
        unsubStat();
    };
  }, [subscribe, fetchStatus]);

  return {
    telemetryStatus,
    liveStatus,
    interfaces,
    isRunning: liveStatus?.state === 'RUNNING' || liveStatus?.state === 'STARTING',
    isLoading,
    actionError,
    start: handleStart,
    stop: handleStop,
    refresh: fetchStatus,
  };
}
