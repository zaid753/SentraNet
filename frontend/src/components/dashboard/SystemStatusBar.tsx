import React from 'react';
import type { SystemStatus } from '../../types';

interface SystemStatusBarProps {
  status: SystemStatus | null;
  isLoading?: boolean;
}

export const SystemStatusBar: React.FC<SystemStatusBarProps> = ({ status, isLoading = false }) => {
  const isReady = status?.status === 'ready' || status?.status === 'ok';
  const xgboostStatus = status?.models?.xgboost || (status?.ml_models?.status === 'loaded' ? 'READY' : 'OFFLINE');
  const anomalyStatus = status?.models?.isolation_forest || (status?.ml_models?.status === 'loaded' ? 'READY' : 'OFFLINE');
  const forecastStatus = status?.models?.forecast_engine || (status?.ml_models?.status === 'loaded' ? 'READY' : 'OFFLINE');
  const featureCount = status?.feature_count || 17;

  return (
    <div className="soc-panel rounded-xl px-4 py-3 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
      {/* System Status State */}
      <div className="flex items-center gap-2.5">
        <span
          className={`w-2 h-2 rounded-full ${
            isReady
              ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]'
              : 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)]'
          }`}
        />
        <span className="text-slate-400 uppercase">SYSTEM STATUS:</span>
        <span className={`font-semibold uppercase tracking-wider ${isReady ? 'text-emerald-400' : 'text-rose-400'}`}>
          {isLoading && !status ? 'LOADING...' : (status?.status?.toUpperCase() || 'OFFLINE')}
        </span>
      </div>

      {/* Model Readiness from API */}
      <div className="flex flex-wrap items-center gap-3 sm:gap-5 text-slate-300">
        <div className="flex items-center gap-1.5">
          <span className="text-slate-500">XGBoost:</span>
          <span
            className={`font-semibold uppercase ${
              xgboostStatus.toUpperCase() === 'READY' || xgboostStatus.toUpperCase() === 'LOADED'
                ? 'text-cyan-400'
                : 'text-amber-400'
            }`}
          >
            {xgboostStatus.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-slate-500">Anomaly:</span>
          <span
            className={`font-semibold uppercase ${
              anomalyStatus.toUpperCase() === 'READY' || anomalyStatus.toUpperCase() === 'LOADED'
                ? 'text-cyan-400'
                : 'text-amber-400'
            }`}
          >
            {anomalyStatus.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-slate-500">Forecast:</span>
          <span
            className={`font-semibold uppercase ${
              forecastStatus.toUpperCase() === 'READY' || forecastStatus.toUpperCase() === 'LOADED'
                ? 'text-cyan-400'
                : 'text-amber-400'
            }`}
          >
            {forecastStatus.toUpperCase()}
          </span>
        </div>

        <div className="hidden md:flex items-center gap-1.5 pl-3 border-l border-slate-800 text-slate-400">
          <span className="text-slate-500">Schema:</span>
          <span className="text-slate-200 font-bold">{featureCount} FEATURES</span>
        </div>

        <div className="hidden lg:flex items-center gap-1.5 pl-3 border-l border-slate-800 text-slate-400">
          <span className="text-slate-500">Env:</span>
          <span className="text-amber-400 font-semibold">HISTORICAL REPLAY</span>
        </div>
      </div>
    </div>
  );
};
