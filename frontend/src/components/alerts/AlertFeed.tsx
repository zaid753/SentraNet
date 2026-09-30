import React, { useState } from 'react';
import type { AlertItemResponse } from '../../types';
import {
  formatTimestamp,
  formatRiskScore,
  formatAttackClass,
  formatSeverity,
  getSeverityConfig,
} from '../../utils/formatters';
import { Bell, Filter, Zap, CheckCircle2 } from 'lucide-react';

interface AlertFeedProps {
  alerts: AlertItemResponse[];
  isLoading?: boolean;
  onSelectIncident?: (incidentId: string) => void;
}

export const AlertFeed: React.FC<AlertFeedProps> = ({
  alerts,
  isLoading = false,
  onSelectIncident,
}) => {
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const filteredAlerts = alerts.filter((a) => {
    if (severityFilter === 'ALL') return true;
    return a.severity.toUpperCase() === severityFilter;
  });

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between min-h-[360px]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-2">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Chronological Alert Feed
          </h3>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
            {alerts.length}
          </span>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <Filter className="w-3 h-3 text-slate-500" />
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-slate-300 text-xs focus:outline-none"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium / Watch</option>
            <option value="LOW">Low / Info</option>
          </select>
        </div>
      </div>

      {/* Feed list */}
      <div className="my-3 space-y-2 max-h-[300px] overflow-y-auto pr-1">
        {filteredAlerts.length === 0 ? (
          <div className="py-12 text-center text-xs font-mono text-slate-500">
            {isLoading ? 'Loading alerts...' : 'No alerts recorded in the current replay stream.'}
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const sevConfig = getSeverityConfig(alert.severity);
            const isResolved = alert.event_type.toUpperCase().includes('RESOLVED');
            const isForecast = alert.forecast_active;

            return (
              <div
                key={alert.alert_event_id}
                className="p-3 rounded-lg bg-slate-900/50 hover:bg-slate-900/80 border border-slate-800/80 transition-all font-mono text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2"
              >
                <div className="flex items-center gap-2.5">
                  <span className="text-[11px] text-slate-500 min-w-[65px]">
                    {formatTimestamp(alert.timestamp)}
                  </span>

                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${sevConfig.badgeBg} ${sevConfig.badgeBorder} ${sevConfig.text}`}
                  >
                    {formatSeverity(alert.severity)}
                  </span>

                  <div className="flex flex-col">
                    <span className="text-white font-semibold">
                      {formatAttackClass(alert.attack_class)}
                    </span>
                    <span className="text-[10px] text-slate-400">
                      {alert.event_type}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-auto text-[11px]">
                  {alert.incident_id && (
                    <button
                      onClick={() => onSelectIncident && onSelectIncident(alert.incident_id!)}
                      className="text-cyan-400 hover:underline cursor-pointer"
                    >
                      {alert.incident_id}
                    </button>
                  )}

                  <span className="text-rose-400 font-bold">
                    {formatRiskScore(alert.risk_score)}
                  </span>

                  {isForecast && (
                    <span className="p-1 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 text-[10px]" title="Forecast Active">
                      <Zap className="w-3 h-3" />
                    </span>
                  )}

                  {isResolved && (
                    <span className="p-1 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px]" title="Resolved">
                      <CheckCircle2 className="w-3 h-3" />
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <span>Order: Latest First</span>
        <span>Alert Engine: Deterministic State Machine</span>
      </div>
    </div>
  );
};
