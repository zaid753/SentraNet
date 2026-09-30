import React from 'react';
import type { AnalyzeResponse } from '../../types';
import {
  formatRiskScore,
  formatAttackClass,
  formatRiskState,
  getRiskStateConfig,
  getTrendIcon,
} from '../../utils/formatters';
import { Shield, Activity } from 'lucide-react';

interface RiskHeroCardProps {
  risk: AnalyzeResponse | null;
  isLoading?: boolean;
}

export const RiskHeroCard: React.FC<RiskHeroCardProps> = ({ risk, isLoading = false }) => {
  if (!risk) {
    return (
      <div className="soc-panel rounded-xl p-6 sm:p-7 relative overflow-hidden flex flex-col justify-center min-h-[200px] border border-[var(--color-border)] shadow-md">
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
              Security Posture
            </h2>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
            Awaiting Stream
          </span>
        </div>
        <div className="text-center flex flex-col items-center justify-center py-4">
          <Activity className="w-6 h-6 text-slate-500 animate-pulse mb-3" />
          <h3 className="text-sm font-bold font-mono text-slate-300">
            {isLoading ? 'Connecting Telemetry Stream...' : 'NO ACTIVE TELEMETRY'}
          </h3>
        </div>
      </div>
    );
  }

  const config = getRiskStateConfig(risk.risk_score);
  const trend = getTrendIcon(risk.risk_trend);

  return (
    <div className={`soc-panel rounded-xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[200px] transition-all duration-300 border border-[var(--color-border)] shadow-md ${config.glow}`}>
      {/* Top Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <Shield className={`w-5 h-5 ${config.text}`} />
          <h2 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
            Security Posture
          </h2>
        </div>
        <div className="flex items-center gap-3 text-[10px] font-mono">
          <span className="text-slate-400">{risk.timestamp}</span>
          {risk.incident_id && (
            <span className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-400">
              {risk.incident_id}
            </span>
          )}
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between gap-6 w-full">
        <div className="flex flex-col flex-1">
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest mb-1">Current Threat Level</span>
          <div className="flex items-baseline gap-4">
            <span className={`text-6xl font-bold font-mono tracking-tighter ${config.text}`}>
              {formatRiskScore(risk.risk_score)}
            </span>
            <div className="flex flex-col">
              <span className={`text-xl font-bold uppercase tracking-wider ${config.text}`}>
                {formatRiskState(risk.risk_state)}
              </span>
              <span className="flex items-center gap-1.5 text-xs font-mono text-slate-400 mt-1">
                <span className={trend.color}>{trend.symbol}</span>
                {risk.risk_velocity !== null && risk.risk_velocity !== undefined && (
                  <span>
                    Delta: {risk.risk_velocity > 0 ? '+' : ''}{risk.risk_velocity.toFixed(3)}
                  </span>
                )}
              </span>
            </div>
          </div>
        </div>

        <div className="flex-1 w-full max-w-sm">
          <div className="grid grid-cols-2 gap-x-6 gap-y-3 font-mono text-xs">
            <div className="flex flex-col">
              <span className="text-slate-500 text-[10px] uppercase">Threat Class</span>
              <span className="text-slate-200 font-bold uppercase tracking-wide">{formatAttackClass(risk.attack_class)}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-slate-500 text-[10px] uppercase">Forecast State</span>
              <span className={risk.forecast_active ? 'text-[var(--color-status-forecast)] font-bold' : 'text-slate-400'}>
                {risk.forecast_active ? 'ACTIVE SIGNAL' : 'QUIET'}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-slate-500 text-[10px] uppercase">Anomaly Score</span>
              <span className={`font-bold ${risk.is_anomalous ? 'text-amber-400' : 'text-emerald-400'}`}>
                {formatRiskScore(risk.anomaly_score)}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-slate-500 text-[10px] uppercase">Network Status</span>
              <span className="text-slate-200">{risk.is_anomalous || risk.risk_score > 50 ? 'INVESTIGATE' : 'NOMINAL'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
