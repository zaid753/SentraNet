import React from 'react';
import type { AlertItemResponse } from '../../types';
import {
  formatTimestamp,
  formatAttackClass,
  getSeverityConfig,
} from '../../utils/formatters';
import { GitCommit, ArrowRight, ShieldCheck, ShieldAlert } from 'lucide-react';

interface AttackTimelineProps {
  alerts: AlertItemResponse[];
}

export const AttackTimeline: React.FC<AttackTimelineProps> = ({ alerts }) => {
  // Extract state/attack transition sequence chronologically
  // Distinct consecutive attack/state changes
  const chronologicalAlerts = [...alerts].reverse();
  const transitions: AlertItemResponse[] = [];
  let lastVector = '';
  let lastEvent = '';

  for (const item of chronologicalAlerts) {
    if (item.attack_class !== lastVector || item.event_type !== lastEvent) {
      transitions.push(item);
      lastVector = item.attack_class;
      lastEvent = item.event_type;
    }
  }

  // Display recent transitions (up to 8)
  const displayTransitions = transitions.slice(-8);

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <GitCommit className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Threat Evolution & Attack Vector Transitions
          </h3>
        </div>
        <span className="text-[10px] font-mono text-slate-500">
          State Transitions
        </span>
      </div>

      {/* Transition chain */}
      <div className="my-3 overflow-x-auto py-2">
        {displayTransitions.length === 0 ? (
          <div className="py-6 text-center text-xs font-mono text-slate-500">
            No attack vector transitions recorded yet. Awaiting replay telemetry.
          </div>
        ) : (
          <div className="flex items-center gap-3 min-w-max px-2">
            {displayTransitions.map((item, idx) => {
              const sevConfig = getSeverityConfig(item.severity);
              const isBenign = item.attack_class.toUpperCase() === 'BENIGN';

              return (
                <React.Fragment key={item.alert_event_id || idx}>
                  <div className="flex flex-col items-center bg-slate-900/80 border border-slate-800 rounded-lg p-3 min-w-[130px] font-mono text-xs">
                    <span className="text-[10px] text-slate-500 mb-1">
                      {formatTimestamp(item.timestamp)}
                    </span>

                    <span className="font-bold text-white mb-1 flex items-center gap-1">
                      {isBenign ? (
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                      )}
                      <span>{formatAttackClass(item.attack_class)}</span>
                    </span>

                    <span
                      className={`px-1.5 py-0.5 rounded text-[9px] font-bold border uppercase ${sevConfig.badgeBg} ${sevConfig.badgeBorder} ${sevConfig.text}`}
                    >
                      {item.event_type.replace('ALERT_', '')}
                    </span>
                  </div>

                  {idx < displayTransitions.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-slate-600 shrink-0" />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <span>Dynamic Vector Pipeline</span>
        <span>BENIGN → SCANNING → DDOS → BOTNET</span>
      </div>
    </div>
  );
};
