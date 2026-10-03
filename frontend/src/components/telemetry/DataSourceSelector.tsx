import React from 'react';
import type { TelemetrySource } from '../../types';
import { Database, Activity, Radio } from 'lucide-react';

interface DataSourceSelectorProps {
  currentSource: TelemetrySource;
  onSelectSource: (source: TelemetrySource) => void;
  isHistoricalRunning: boolean;
  isSyntheticRunning: boolean;
  isLiveRunning: boolean;
}

export const DataSourceSelector: React.FC<DataSourceSelectorProps> = ({
  currentSource,
  onSelectSource,
  isHistoricalRunning,
  isSyntheticRunning,
  isLiveRunning,
}) => {
  return (
    <div className="soc-panel rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
      {/* Title */}
      <div className="flex items-center gap-2.5">
        <Database className="w-4 h-4 text-cyan-400 shrink-0" />
        <div>
          <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
            Telemetry Data Source
          </div>
          <div className="text-[11px] text-slate-400 font-sans">
            Select the active network telemetry stream feeding the SENTRANET AI Core
          </div>
        </div>
      </div>

      {/* Source Selection Buttons */}
      <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
        {/* Historical Replay */}
        <button
          onClick={() => onSelectSource('historical')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
            currentSource === 'historical'
              ? 'bg-cyan-500/20 border-cyan-500/60 text-cyan-200 font-bold shadow-sm'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
          }`}
        >
          <Database className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-mono tracking-wider">CIC-IDS2017 REAL DATASET REPLAY</span>
          {isHistoricalRunning && (
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          )}
          <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/40">
            AVAILABLE
          </span>
        </button>

        {/* Synthetic Stream */}
        <button
          onClick={() => onSelectSource('synthetic')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
            currentSource === 'synthetic'
              ? 'bg-emerald-500/20 border-emerald-500/60 text-emerald-200 font-bold shadow-sm'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
          }`}
        >
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-mono tracking-wider">SYNTHETIC SIMULATION</span>
          {isSyntheticRunning && (
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          )}
          <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/40">
            AVAILABLE
          </span>
        </button>

        {/* Live Telemetry */}
        <button
          onClick={() => onSelectSource('live')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
            currentSource === 'live'
              ? 'bg-red-500/20 border-red-500/60 text-red-200 font-bold shadow-sm'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
          }`}
        >
          <Radio className="w-3.5 h-3.5 text-red-400" />
          <span className="font-mono tracking-wider">LIVE NETWORK EXPERIMENTAL</span>
          {isLiveRunning && (
            <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
          )}
          <span className={`text-[9px] px-1.5 py-0.2 rounded border ${
            currentSource === 'live' 
            ? 'bg-red-950/80 text-red-400 border-red-800/40' 
            : 'bg-slate-900 text-slate-500 border-slate-800'
          }`}>
            EXPERIMENTAL
          </span>
        </button>
      </div>
    </div>
  );
};
