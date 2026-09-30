import React from 'react';
import type { IncidentItemResponse } from '../../types';
import {
  formatTimestamp,
  formatRiskScore,
  formatAttackClass,
  formatSeverity,
  getSeverityConfig,
} from '../../utils/formatters';
import { ShieldAlert, Zap, ExternalLink } from 'lucide-react';

interface IncidentTableProps {
  incidents: IncidentItemResponse[];
  isLoading?: boolean;
  onSelectIncident: (id: string) => void;
}

export const IncidentTable: React.FC<IncidentTableProps> = ({
  incidents,
  isLoading = false,
  onSelectIncident,
}) => {
  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Security Incident Register
          </h3>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
            {incidents.length} Records
          </span>
        </div>

        <span className="text-[10px] font-mono text-slate-500">
          Source: GET /api/incidents
        </span>
      </div>

      {/* Table */}
      <div className="my-3 overflow-x-auto">
        <table className="w-full text-left font-mono text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider">
              <th className="py-2.5 px-3">Incident ID</th>
              <th className="py-2.5 px-3">Attack Class</th>
              <th className="py-2.5 px-3">Severity</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3">Created</th>
              <th className="py-2.5 px-3">Updated</th>
              <th className="py-2.5 px-3 text-right">Peak Risk</th>
              <th className="py-2.5 px-3 text-right">Max Anomaly</th>
              <th className="py-2.5 px-3 text-center">Forecast</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {incidents.length === 0 ? (
              <tr>
                <td colSpan={10} className="py-8 text-center text-slate-500">
                  {isLoading ? 'Loading incident records...' : 'No incidents registered. Telemetry stream nominal.'}
                </td>
              </tr>
            ) : (
              incidents.map((inc) => {
                const sevConfig = getSeverityConfig(inc.severity);
                const isActive = inc.status.toUpperCase() === 'ACTIVE';

                return (
                  <tr
                    key={inc.incident_id}
                    className="hover:bg-slate-900/60 transition-colors group cursor-pointer"
                    onClick={() => onSelectIncident(inc.incident_id)}
                  >
                    <td className="py-2.5 px-3 font-bold text-cyan-400 whitespace-nowrap">
                      {inc.incident_id}
                    </td>

                    <td className="py-2.5 px-3 font-semibold text-white whitespace-nowrap">
                      {formatAttackClass(inc.attack_class)}
                    </td>

                    <td className="py-2.5 px-3 whitespace-nowrap">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${sevConfig.badgeBg} ${sevConfig.badgeBorder} ${sevConfig.text}`}
                      >
                        {formatSeverity(inc.severity)}
                      </span>
                    </td>

                    <td className="py-2.5 px-3 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase ${
                          isActive ? 'text-rose-400' : 'text-slate-400'
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            isActive ? 'bg-rose-500 animate-pulse' : 'bg-slate-600'
                          }`}
                        />
                        <span>{inc.status}</span>
                      </span>
                    </td>

                    <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap">
                      {formatTimestamp(inc.created_at)}
                    </td>

                    <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap">
                      {formatTimestamp(inc.updated_at)}
                    </td>

                    <td className="py-2.5 px-3 text-right font-bold text-rose-400 whitespace-nowrap">
                      {formatRiskScore(inc.peak_risk)}
                    </td>

                    <td className="py-2.5 px-3 text-right font-bold text-amber-400 whitespace-nowrap">
                      {formatRiskScore(inc.max_anomaly)}
                    </td>

                    <td className="py-2.5 px-3 text-center whitespace-nowrap">
                      {inc.forecast_triggered ? (
                        <span className="inline-flex items-center gap-1 text-cyan-400 text-[10px] font-bold">
                          <Zap className="w-3 h-3" />
                          <span>YES</span>
                        </span>
                      ) : (
                        <span className="text-slate-500 text-[10px]">NO</span>
                      )}
                    </td>

                    <td className="py-2.5 px-3 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectIncident(inc.incident_id);
                        }}
                        className="p-1 rounded text-slate-400 group-hover:text-cyan-300 hover:bg-slate-800 transition-colors"
                        title="View Incident Dossier"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <span>Click any row to open incident details</span>
        <span>Deterministic IncidentManager lifecycle</span>
      </div>
    </div>
  );
};
