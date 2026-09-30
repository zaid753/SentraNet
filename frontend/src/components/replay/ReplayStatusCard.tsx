import React from 'react';
import type { ReplayStatusResponse } from '../../types';
import { formatTimestamp } from '../../utils/formatters';
import { Activity, Clock, Gauge } from 'lucide-react';

interface ReplayStatusCardProps {
  status: ReplayStatusResponse | null;
}

export const ReplayStatusCard: React.FC<ReplayStatusCardProps> = ({ status }) => {
  const isRunning = Boolean(status?.running);
  const isPaused = Boolean(status?.paused);
  const progressPercent = status ? Math.min(Math.max(status.progress * 100, 0), 100) : 0;

  const getStatusBadge = () => {
    if (isRunning) {
      return {
        label: 'RUNNING',
        bg: 'bg-emerald-950/60 border-emerald-700/60 text-emerald-400',
        dot: 'bg-emerald-400 animate-pulse',
      };
    }
    if (isPaused) {
      return {
        label: 'PAUSED',
        bg: 'bg-amber-950/60 border-amber-700/60 text-amber-400',
        dot: 'bg-amber-400',
      };
    }
    if (status && status.windows_processed > 0 && status.windows_processed >= status.total_windows) {
      return {
        label: 'COMPLETED',
        bg: 'bg-cyan-950/60 border-cyan-700/60 text-cyan-400',
        dot: 'bg-cyan-400',
      };
    }
    return {
      label: 'IDLE',
      bg: 'bg-slate-900 border-slate-800 text-slate-400',
      dot: 'bg-slate-500',
    };
  };

  const badge = getStatusBadge();

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Simulation Status
          </h3>
        </div>

        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded font-mono text-xs font-bold border ${badge.bg}`}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
          <span>{badge.label}</span>
        </span>
      </div>

      {/* Progress & Simulated Clock */}
      <div className="my-4 space-y-3 font-mono text-xs">
        <div>
          <div className="flex justify-between items-center text-slate-400 mb-1.5">
            <span>Replay Progress</span>
            <span className="font-bold text-white">
              {status ? `${status.windows_processed} / ${status.total_windows}` : '0 / 0'}{' '}
              <span className="text-cyan-400 font-normal">
                ({progressPercent.toFixed(1)}%)
              </span>
            </span>
          </div>

          {/* Real progress bar */}
          <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className="h-full bg-cyan-500 rounded-full transition-all duration-300 shadow-[0_0_10px_rgba(6,182,212,0.6)]"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-1">
          <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 text-[10px] block">Simulated Timestamp</span>
            <span className="text-white font-bold flex items-center gap-1.5 mt-0.5">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>{formatTimestamp(status?.current_timestamp)}</span>
            </span>
          </div>

          <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 text-[10px] block">Speed Multiplier</span>
            <span className="text-cyan-400 font-bold flex items-center gap-1.5 mt-0.5">
              <Gauge className="w-3.5 h-3.5 text-cyan-400" />
              <span>{status?.speed ? `${status.speed}x` : '—'}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <span>Dataset: {status?.dataset || 'validation'}</span>
        <span>Mode: {status?.mode?.toUpperCase() || 'REALTIME'}</span>
      </div>
    </div>
  );
};
