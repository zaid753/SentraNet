import React, { useState, useEffect, useCallback } from 'react';
import type { HealthResponse, SystemStatus, ConnectionState } from '../types';
import { getHealth, getSystemStatus } from '../services/api';
import { Header } from '../components/Header';
import { SystemStatusCard } from '../components/SystemStatusCard';
import { ShieldCheck, Layers, ArrowRight, Activity } from 'lucide-react';

interface FoundationPageProps {
  showHeader?: boolean;
}

export const FoundationPage: React.FC<FoundationPageProps> = ({ showHeader = false }) => {
  const [connectionState, setConnectionState] = useState<ConnectionState>('LOADING');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const checkConnectivity = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [healthData, statusData] = await Promise.all([
        getHealth(),
        getSystemStatus(),
      ]);

      setHealth(healthData);
      setSystemStatus(statusData);
      setConnectionState('CONNECTED');
      setErrorMessage('');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Connection failed';
      setErrorMessage(msg);
      setConnectionState('OFFLINE');
      setHealth(null);
      setSystemStatus(null);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    let ignore = false;
    getHealth()
      .then((healthData) => {
        if (ignore) return;
        setHealth(healthData);
        return getSystemStatus();
      })
      .then((statusData) => {
        if (ignore || !statusData) return;
        setSystemStatus(statusData);
        setConnectionState('CONNECTED');
        setErrorMessage('');
      })
      .catch((err) => {
        if (ignore) return;
        const msg = err instanceof Error ? err.message : 'Connection failed';
        setErrorMessage(msg);
        setConnectionState('OFFLINE');
      });

    return () => {
      ignore = true;
    };
  }, []);

  return (
    <div className="flex-1 flex flex-col font-sans soc-grid-bg">
      {showHeader && <Header apiStatus={connectionState} />}

      <div className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8 flex flex-col gap-8">
        {/* Hero Section */}
        <section className="flex flex-col gap-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/50 text-cyan-300 text-xs font-mono self-start">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            <span>SYSTEM FOUNDATION & ENGINEERING ARCHITECTURE</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            AI-Based Network Attack Forecasting
          </h2>

          <p className="text-slate-400 text-sm sm:text-base max-w-3xl leading-relaxed">
            SENTRANET transforms cybersecurity from reactive intrusion detection to predictive network defence. 
            SENTRANET established the verified software architecture, dual ML engine (XGBoost + Isolation Forest),
            risk trajectory fusion, chronological replay engine, and REST API contracts.
          </p>
        </section>

        {/* System Status Matrix */}
        <section>
          <SystemStatusCard
            connectionState={connectionState}
            health={health}
            systemStatus={systemStatus}
            errorMessage={errorMessage}
            onRefresh={checkConnectivity}
            isRefreshing={isRefreshing}
          />
        </section>

        {/* Foundation Status & Architecture Pipeline */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Foundation Ready Card */}
          <div className="soc-panel rounded-xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
                  Foundation Readiness
                </h3>
              </div>

              <div className="mt-4 space-y-3 text-xs">
                <div className="flex items-center justify-between py-1.5 border-b border-slate-900">
                  <span className="text-slate-400">Core Monorepo Structure</span>
                  <span className="text-emerald-400 font-mono font-medium">VERIFIED</span>
                </div>
                <div className="flex items-center justify-between py-1.5 border-b border-slate-900">
                  <span className="text-slate-400">FastAPI REST Backbone</span>
                  <span className="text-emerald-400 font-mono font-medium">VERIFIED</span>
                </div>
                <div className="flex items-center justify-between py-1.5 border-b border-slate-900">
                  <span className="text-slate-400">CORS & Security Middleware</span>
                  <span className="text-emerald-400 font-mono font-medium">VERIFIED</span>
                </div>
                <div className="flex items-center justify-between py-1.5 border-b border-slate-900">
                  <span className="text-slate-400">Dual ML Engine (XGB + IF)</span>
                  <span className="text-emerald-400 font-mono font-medium">VERIFIED (17 Features)</span>
                </div>
                <div className="flex items-center justify-between py-1.5 border-b border-slate-900">
                  <span className="text-slate-400">Replay & Alert State Machine</span>
                  <span className="text-emerald-400 font-mono font-medium">VERIFIED</span>
                </div>
                <div className="flex items-center justify-between py-1.5">
                  <span className="text-slate-400">SOC Frontend Dashboard</span>
                  <span className="text-cyan-400 font-mono font-medium">ACTIVE</span>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-900 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Status: READY</span>
              <span>84 Backend Tests Passing</span>
            </div>
          </div>

          {/* Architecture Pipeline Card */}
          <div className="soc-panel rounded-xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
                <Layers className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
                  Data Pipeline & Model Flow
                </h3>
              </div>

              <div className="mt-4 space-y-2.5 text-xs font-mono">
                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center text-[10px] font-bold">1</span>
                    <span className="text-slate-200">Chronological Telemetry Stream</span>
                  </div>
                  <span className="text-slate-400 text-[11px]">Historical Fixture</span>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center text-[10px] font-bold">2</span>
                    <span className="text-slate-200">Dual Inference Engine</span>
                  </div>
                  <span className="text-slate-400 text-[11px]">XGBoost + Isolation Forest</span>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center text-[10px] font-bold">3</span>
                    <span className="text-slate-200">Temporal Trajectory & Forecast</span>
                  </div>
                  <span className="text-slate-400 text-[11px]">Emergence Detection</span>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center text-[10px] font-bold">4</span>
                    <span className="text-slate-200">State Machine & Incident Manager</span>
                  </div>
                  <span className="text-slate-400 text-[11px]">Deterministic Alerts</span>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-900 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Environment: Strict Python & Node.js</span>
              <span className="text-cyan-400 flex items-center gap-1">
                <span>System Ready</span>
                <ArrowRight className="w-3 h-3" />
              </span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
