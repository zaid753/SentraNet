import React from 'react';
import type { AnalyzeResponse } from '../../types';
import {
  formatRiskScore,
  formatAttackClass,
  formatRiskState,
  getRiskStateConfig,
  getTrendIcon,
} from '../../utils/formatters';
import { RiskGauge } from '../common/RiskGauge';
import { Shield, Activity } from 'lucide-react';

interface RiskHeroCardProps {
  risk: AnalyzeResponse | null;
  isLoading?: boolean;
}

export const RiskHeroCard: React.FC<RiskHeroCardProps> = ({ risk, isLoading = false }) => {
  // If no risk or empty state
  if (!risk) {
    return (
      <div className="soc-panel rounded-xl p-6 sm:p-7 relative overflow-hidden flex flex-col justify-between min-h-[280px]">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
              Network Threat Risk
            </h2>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
            Awaiting Stream
          </span>
        </div>

        <div className="my-8 text-center flex flex-col items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mb-3">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <h3 className="text-base font-bold font-mono text-slate-300">
            {isLoading ? 'Connecting Telemetry Stream...' : 'NO ACTIVE TELEMETRY'}
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mt-1 font-sans">
            Start a historical replay simulation to feed chronological network flow telemetry into the XGBoost & Isolation Forest engines.
          </p>
        </div>

        <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono text-slate-500">
          <span>Signal: DUAL ML ENGINE</span>
          <span>Zero Fabricated Data</span>
        </div>
      </div>
    );
  }

  const config = getRiskStateConfig(risk.risk_score);
  const trend = getTrendIcon(risk.risk_trend);

  return (
    <div
      className={`soc-panel rounded-xl p-6 sm:p-7 relative overflow-hidden flex flex-col justify-between min-h-[280px] transition-all duration-300 ${config.glow}`}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Shield className={`w-5 h-5 ${config.text}`} />
          <h2 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
            Network Threat Risk
          </h2>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded border font-mono text-xs font-bold uppercase tracking-wider ${config.badgeBg} ${config.badgeBorder} ${config.text}`}
          >
            <span className={`w-2 h-2 rounded-full ${config.dotBg}`} />
            <span>{formatRiskState(risk.risk_state)}</span>
          </span>
        </div>
      </div>

      {/* Main Score & Classification Grid */}
      <div className="my-6 grid grid-cols-1 sm:grid-cols-2 gap-6 items-center">
        <div>
          <div className="text-xs font-mono uppercase text-slate-400 tracking-wider mb-1">
            Fused Composite Risk
          </div>
          <div className="flex items-baseline gap-3">
            <span className={`text-5xl sm:text-6xl font-bold font-mono tracking-tight ${config.text}`}>
              {formatRiskScore(risk.risk_score)}
            </span>
          </div>

          <div className="mt-3 flex items-center gap-2 font-mono text-xs text-slate-400">
            <span>Trend:</span>
            <span className={`font-semibold flex items-center gap-1 ${trend.color}`}>
              <span>{trend.symbol}</span>
              <span>{trend.text}</span>
            </span>
            {risk.risk_velocity !== null && risk.risk_velocity !== undefined && (
              <span className="text-[11px] text-slate-500">
                (v: {risk.risk_velocity > 0 ? '+' : ''}{risk.risk_velocity.toFixed(3)})
              </span>
            )}
          </div>
        </div>

        {/* Classification & Sub-signals */}
        <div className="flex flex-col gap-3 font-mono text-xs bg-slate-900/60 p-4 rounded-lg border border-slate-800/80">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="text-slate-400">Classified Threat:</span>
            <span className="text-white font-bold tracking-wide">
              {formatAttackClass(risk.attack_class)}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400">Attack Likelihood:</span>
            <span className="text-cyan-400 font-semibold">
              {formatRiskScore(risk.attack_likelihood)}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400">Anomaly Signal:</span>
            <span
              className={`font-semibold ${
                risk.is_anomalous ? 'text-amber-400' : 'text-emerald-400'
              }`}
            >
              {formatRiskScore(risk.anomaly_score)}
            </span>
          </div>

          <div className="flex items-center justify-between text-[11px]">
            <span className="text-slate-500">Confidence:</span>
            <span className="text-slate-300">
              {formatRiskScore(risk.class_probability)}
            </span>
          </div>
        </div>
      </div>

      {/* Visual Risk Gauge */}
      <div className="pt-2">
        <RiskGauge score={risk.risk_score} />
      </div>

      {/* Footer Timestamp */}
      <div className="pt-4 mt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-500 gap-2">
        <span>Window TS: {risk.timestamp}</span>
        {risk.incident_id && (
          <span className="text-cyan-400">Active Incident: {risk.incident_id}</span>
        )}
      </div>
    </div>
  );
};
