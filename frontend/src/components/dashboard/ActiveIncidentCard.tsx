import React from 'react';
import type { IncidentItemResponse, CurrentAlertResponse } from '../../types';
import {
  formatAttackClass,
  formatRiskScore,
  formatTimestamp,
  formatSeverity,
  getSeverityConfig,
} from '../../utils/formatters';
import { Flame, ShieldCheck, Zap } from 'lucide-react';

interface ActiveIncidentCardProps {
  activeIncident: IncidentItemResponse | null;
  currentAlert?: CurrentAlertResponse | null;
  onViewDetails?: (incidentId: string) => void;
}

export const ActiveIncidentCard: React.FC<ActiveIncidentCardProps> = ({
  activeIncident,
  currentAlert: _currentAlert,
  onViewDetails,
}) => {
  // If no active incident
  if (!activeIncident) {
    return (
      <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between min-h-[220px]">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
              Active Security Incident
            </h3>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/60 text-emerald-400">
            NOMINAL
          </span>
        </div>

        <div className="my-6 text-center flex flex-col items-center justify-center">
          <div className="w-9 h-9 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-2">
            <ShieldCheck className="w-5 h-5 text-emerald-500/70" />
          </div>
          <div className="font-mono text-sm text-slate-300 font-semibold">
            NO ACTIVE INCIDENTS
          </div>
          <p className="text-xs text-slate-500 max-w-xs mt-1 font-sans">
            Start a historical replay to stream network flows and trigger automated incident correlation.
          </p>
        </div>

        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span>Incident Manager: State Machine</span>
          <span>Zero Fabricated Alerts</span>
        </div>
      </div>
    );
  }

  const sevConfig = getSeverityConfig(activeIncident.severity);

  return (
    <div
      className={`soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between min-h-[220px] border-l-4 border-l-rose-500 ${sevConfig.glow}`}
    >
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Flame className="w-4 h-4 text-rose-500 animate-pulse" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Active Security Incident
          </h3>
        </div>

        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded font-mono text-xs font-bold uppercase border ${sevConfig.badgeBg} ${sevConfig.badgeBorder} ${sevConfig.text}`}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${sevConfig.dotBg}`} />
          <span>{formatSeverity(activeIncident.severity)}</span>
        </span>
      </div>

      <div className="my-3 space-y-2.5 font-mono text-xs">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Incident ID:</span>
          <button
            onClick={() => onViewDetails && onViewDetails(activeIncident.incident_id)}
            className="text-cyan-400 font-bold hover:underline cursor-pointer"
          >
            {activeIncident.incident_id}
          </button>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-400">Attack Class:</span>
          <span className="text-white font-bold">
            {formatAttackClass(activeIncident.attack_class)}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-2 pt-1">
          <div className="p-2 rounded bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 text-[10px] block">Peak Risk</span>
            <span className="text-rose-400 font-bold">
              {formatRiskScore(activeIncident.peak_risk)}
            </span>
          </div>

          <div className="p-2 rounded bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 text-[10px] block">Max Anomaly</span>
            <span className="text-amber-400 font-bold">
              {formatRiskScore(activeIncident.max_anomaly)}
            </span>
          </div>

          <div className="p-2 rounded bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 text-[10px] block">Forecast</span>
            <span
              className={`font-bold flex items-center gap-1 ${
                activeIncident.forecast_triggered ? 'text-cyan-400' : 'text-slate-400'
              }`}
            >
              {activeIncident.forecast_triggered ? (
                <>
                  <Zap className="w-3 h-3 text-cyan-400" />
                  <span>TRIGGERED</span>
                </>
              ) : (
                'NONE'
              )}
            </span>
          </div>
        </div>
      </div>

      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <span>Created: {formatTimestamp(activeIncident.created_at)}</span>
        <span>Events: {activeIncident.event_count}</span>
      </div>
    </div>
  );
};
