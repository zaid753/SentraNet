import React from 'react';
import { Database, Activity } from 'lucide-react';
import type { TelemetrySource } from '../../types';

interface SimulationBannerProps {
  isRunning?: boolean;
  datasetName?: string | null;
  sourceType?: TelemetrySource;
  className?: string;
}

export const SimulationBanner: React.FC<SimulationBannerProps> = ({
  isRunning = false,
  datasetName = 'validation',
  sourceType = 'historical',
  className = '',
}) => {
  const isSynthetic = sourceType === 'synthetic';

  return (
    <div
      role="region"
      aria-label="Simulation Environment Disclosure"
      className={`rounded-lg px-4 py-2.5 ${
        isSynthetic
          ? 'bg-emerald-950/30 border border-emerald-800/40 text-emerald-200'
          : 'bg-amber-950/30 border border-amber-800/40 text-amber-200'
      } flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs font-mono ${className}`}
    >
      <div className="flex items-center gap-2.5">
        <div
          className={`p-1 rounded border shrink-0 ${
            isSynthetic
              ? 'bg-emerald-900/50 border-emerald-700/50 text-emerald-400'
              : 'bg-amber-900/50 border-amber-700/50 text-amber-400'
          }`}
        >
          {isSynthetic ? (
            <Activity className="w-3.5 h-3.5" />
          ) : (
            <Database className="w-3.5 h-3.5" />
          )}
        </div>
        <div>
          <span
            className={`font-semibold tracking-wider mr-2 ${
              isSynthetic ? 'text-emerald-300' : 'text-amber-300'
            }`}
          >
            {isSynthetic
              ? 'SYNTHETIC STREAM // SIMULATION'
              : 'REAL DATASET REPLAY'}
          </span>
          <span className={isSynthetic ? 'text-emerald-200/80' : 'text-amber-200/80'}>
            {isSynthetic
              ? 'Network telemetry is dynamically generated metadata feeding 60s feature aggregation. No packet payloads are captured.'
              : `Network telemetry is being chronologically replayed from a verified real-world historical dataset (Dataset: ${
                  datasetName || 'CIC-IDS2017'
                }).`}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto">
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-[11px] ${
            isSynthetic
              ? 'bg-emerald-900/40 border-emerald-700/40 text-emerald-300'
              : 'bg-amber-900/40 border-amber-700/40 text-amber-300'
          }`}
        >
          {isRunning ? (
            <>
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  isSynthetic ? 'bg-emerald-400' : 'bg-amber-400'
                } animate-pulse`}
              />
              {isSynthetic ? 'STREAM ACTIVE' : 'CLOCK ACTIVE'}
            </>
          ) : (
            <>
              <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
              {isSynthetic ? 'STREAM IDLE' : 'CLOCK IDLE'}
            </>
          )}
        </span>
        <span
          className="text-slate-400 hidden lg:inline"
          title="Synthetic simulation boundary notice"
        >
          [Scientific Honesty]
        </span>
      </div>
    </div>
  );
};
