import React from 'react';
import type { AnalyzeResponse } from '../../types';
import { formatRiskScore, formatAttackClass, formatRiskState, getRiskStateConfig, getTrendIcon } from '../../utils/formatters';

interface IntelligenceRowProps {
  risk: AnalyzeResponse | null;
}

export const IntelligenceRow: React.FC<IntelligenceRowProps> = ({ risk }) => {
  if (!risk) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="soc-panel rounded-lg p-4 h-24 border border-[var(--color-border)] flex items-center justify-center">
            <span className="text-[10px] text-slate-600 font-mono">AWAITING TELEMETRY</span>
          </div>
        ))}
      </div>
    );
  }

  const riskConfig = getRiskStateConfig(risk.risk_score);
  const trend = getTrendIcon(risk.risk_trend);
  const isForecastActive = risk.forecast_active;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {/* RISK MODULE */}
      <div className="soc-panel rounded-lg p-4 border border-[var(--color-border)] flex flex-col justify-between shadow-sm">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Composite Risk</h3>
        <div className="flex items-end justify-between">
          <div className="flex flex-col">
            <span className={`text-2xl font-bold font-mono leading-none ${riskConfig.text}`}>
              {formatRiskScore(risk.risk_score)}
            </span>
            <span className={`text-[10px] font-bold uppercase mt-1 ${riskConfig.text}`}>
              {formatRiskState(risk.risk_state)}
            </span>
          </div>
          <div className="flex flex-col items-end text-[10px] font-mono text-slate-400">
            <span className="flex items-center gap-1">
              Trend: <span className={trend.color}>{trend.symbol}</span>
            </span>
            {risk.risk_velocity != null && (
              <span>Vel: {risk.risk_velocity > 0 ? '+' : ''}{risk.risk_velocity.toFixed(3)}</span>
            )}
          </div>
        </div>
      </div>

      {/* THREAT MODULE */}
      <div className="soc-panel rounded-lg p-4 border border-[var(--color-border)] flex flex-col justify-between shadow-sm">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Threat Class</h3>
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Current:</span>
            <span className="font-bold text-slate-200 uppercase font-mono tracking-wide">{formatAttackClass(risk.attack_class)}</span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">Likelihood:</span>
            <span className="font-bold text-cyan-400 font-mono">{formatRiskScore(risk.attack_likelihood)}</span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">Confidence:</span>
            <span className="font-bold text-slate-300 font-mono">{formatRiskScore(risk.class_probability)}</span>
          </div>
        </div>
      </div>

      {/* ANOMALY MODULE */}
      <div className="soc-panel rounded-lg p-4 border border-[var(--color-border)] flex flex-col justify-between shadow-sm">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Anomaly (IForest)</h3>
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Score:</span>
            <span className={`font-bold font-mono ${risk.is_anomalous ? 'text-amber-400' : 'text-emerald-400'}`}>
              {formatRiskScore(risk.anomaly_score)}
            </span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">State:</span>
            <span className={`font-bold font-mono uppercase ${risk.is_anomalous ? 'text-amber-400' : 'text-emerald-400'}`}>
              {risk.is_anomalous ? 'ANOMALOUS' : 'NORMAL'}
            </span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">Threshold:</span>
            <span className="font-bold text-slate-400 font-mono">Dynamic</span>
          </div>
        </div>
      </div>

      {/* FORECAST MODULE */}
      <div className="soc-panel rounded-lg p-4 border border-[var(--color-border)] flex flex-col justify-between relative overflow-hidden shadow-sm">
        {isForecastActive && <div className="absolute top-0 left-0 w-full h-0.5 bg-[var(--color-status-forecast)] animate-pulse" />}
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center justify-between">
          <span>Forecast Engine</span>
          {isForecastActive && <span className="text-[var(--color-status-forecast)] text-[8px] font-bold px-1 border border-[var(--color-status-forecast)] rounded">ACTIVE</span>}
        </h3>
        
        {isForecastActive ? (
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400">Candidate:</span>
              <span className="font-bold text-[var(--color-status-forecast)] font-mono">{risk.forecast_class ? formatAttackClass(risk.forecast_class) : 'UNKNOWN'}</span>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">ETA:</span>
              <span className="font-bold text-white font-mono">{risk.estimated_eta_seconds ? `~${risk.estimated_eta_seconds}s` : 'IMMINENT'}</span>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Emergence:</span>
              <span className="font-bold text-slate-300 font-mono">{risk.emergence_detected ? 'DETECTED' : 'MONITORING'}</span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col justify-center h-full">
            <span className="text-[10px] text-slate-400 font-mono text-center">AWAITING TEMPORAL EVIDENCE</span>
            <span className="text-[9px] text-slate-500 font-mono text-center mt-0.5">Quiet</span>
          </div>
        )}
      </div>
    </div>
  );
};
