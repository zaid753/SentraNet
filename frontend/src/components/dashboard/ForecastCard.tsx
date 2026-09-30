import React from 'react';
import type { AnalyzeResponse } from '../../types';
import {
  formatRiskScore,
  formatAttackClass,
  formatEta,
  getTrendIcon,
} from '../../utils/formatters';
import { Zap, Clock, Compass } from 'lucide-react';

interface ForecastCardProps {
  risk: AnalyzeResponse | null;
}

export const ForecastCard: React.FC<ForecastCardProps> = ({ risk }) => {
  const isForecastActive = Boolean(risk?.forecast_active);
  const trend = getTrendIcon(risk?.risk_trend);

  return (
    <div className="soc-panel rounded-xl p-6 sm:p-7 relative overflow-hidden flex flex-col justify-between min-h-[280px]">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-cyan-950/80 border border-cyan-800/60 text-cyan-400">
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
              AI Forecast Signal
            </h2>
          </div>
        </div>

        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded font-mono text-xs font-semibold tracking-wider border ${
            isForecastActive
              ? 'bg-cyan-950/80 border-cyan-700/80 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.3)] animate-pulse'
              : 'bg-slate-900 border-slate-800 text-slate-400'
          }`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isForecastActive ? 'bg-cyan-400' : 'bg-slate-500'
            }`}
          />
          <span>{isForecastActive ? 'FORECAST ACTIVE' : 'INACTIVE'}</span>
        </span>
      </div>

      {/* Main Content */}
      {isForecastActive && risk ? (
        <div className="my-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2">
            <div>
              <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500">
                Emerging Threat Vector
              </div>
              <div className="text-xl sm:text-2xl font-bold font-mono text-cyan-300 mt-0.5">
                {formatAttackClass(risk.forecast_class || risk.attack_class)}
              </div>
            </div>

            <div className="sm:text-right">
              <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500">
                Estimated Time to Impact (ETA)
              </div>
              <div className="text-lg font-bold font-mono text-white flex items-center gap-1 sm:justify-end mt-0.5">
                <Clock className="w-4 h-4 text-cyan-400" />
                <span>{formatEta(risk.estimated_eta_seconds)}</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 text-xs font-mono">
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="text-slate-500 text-[10px]">Confidence Signal</div>
              <div className="text-cyan-400 font-bold text-sm mt-1">
                {formatRiskScore(risk.forecast_confidence || risk.class_probability)}
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="text-slate-500 text-[10px]">Risk Trajectory</div>
              <div className={`font-bold text-sm mt-1 flex items-center gap-1 ${trend.color}`}>
                <span>{trend.symbol}</span>
                <span>{trend.text}</span>
              </div>
            </div>
          </div>

          {risk.reasons && risk.reasons.length > 0 && (
            <div className="p-3 rounded-lg bg-cyan-950/30 border border-cyan-800/40 text-xs font-mono text-cyan-200/90">
              <div className="text-[10px] uppercase text-cyan-400 font-semibold mb-1">
                Trigger Basis:
              </div>
              <div className="space-y-0.5">
                {risk.reasons.map((r, i) => (
                  <div key={i} className="leading-snug">• {r}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="my-8 text-center flex flex-col items-center justify-center">
          <div className="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-2">
            <Compass className="w-5 h-5" />
          </div>
          <div className="font-mono text-sm text-slate-400 font-medium">
            No active forecast signal
          </div>
          <p className="text-xs text-slate-500 max-w-xs mt-1 font-sans">
            Forecasting engine evaluates temporal acceleration and emerging anomalies before attack thresholds breach.
          </p>
        </div>
      )}

      {/* Footer */}
      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <span>Emergence: {risk?.emergence_detected ? 'DETECTED' : 'QUIET'}</span>
        <span>Predictive Model Signal</span>
      </div>
    </div>
  );
};
