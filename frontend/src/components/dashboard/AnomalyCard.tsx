import React from 'react';
import type { AnalyzeResponse } from '../../types';
import { formatRiskScore } from '../../utils/formatters';
import { Radio, AlertOctagon, CheckCircle2 } from 'lucide-react';

interface AnomalyCardProps {
  risk: AnalyzeResponse | null;
}

export const AnomalyCard: React.FC<AnomalyCardProps> = ({ risk }) => {
  const isAnomalous = Boolean(risk?.is_anomalous);
  const anomalyScore = risk?.anomaly_score;

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between min-h-[220px]">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Anomaly Detection
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
          Isolation Forest
        </span>
      </div>

      <div className="my-4">
        <div className="text-[10px] font-mono uppercase text-slate-500 tracking-wider">
          Unsupervised Divergence
        </div>
        <div className="flex items-baseline justify-between mt-1">
          <span
            className={`text-2xl font-bold font-mono tracking-tight ${
              isAnomalous ? 'text-amber-400' : 'text-emerald-400'
            }`}
          >
            {formatRiskScore(anomalyScore)}
          </span>
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded font-mono text-xs font-bold border ${
              isAnomalous
                ? 'bg-amber-950/60 border-amber-700/60 text-amber-300'
                : 'bg-emerald-950/60 border-emerald-700/60 text-emerald-300'
            }`}
          >
            {isAnomalous ? (
              <>
                <AlertOctagon className="w-3.5 h-3.5 text-amber-400" />
                <span>ANOMALOUS</span>
              </>
            ) : (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>NORMAL</span>
              </>
            )}
          </span>
        </div>

        <div className="mt-3 p-2.5 rounded bg-slate-900/60 border border-slate-800 text-xs font-mono text-slate-400">
          <span className="text-slate-500 text-[10px] block">Model Signal</span>
          <span className="text-slate-300">
            Isolation Forest unsupervised deviation signal across 17 canonical features.
          </span>
        </div>
      </div>

      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <span>Anomaly threshold: 0.50</span>
        <span>Zero Synthetic Logic</span>
      </div>
    </div>
  );
};
