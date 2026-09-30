import React from 'react';
import type { ForecastExplanation } from '../../types/explainability';
import { Clock, AlertTriangle, ShieldCheck } from 'lucide-react';

interface ForecastEvidenceCardProps {
  forecast: ForecastExplanation;
}

export const ForecastEvidenceCard: React.FC<ForecastEvidenceCardProps> = ({ forecast }) => {
  if (!forecast.forecast_available) {
    return (
      <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between h-full">
        <div className="pb-3 border-b border-slate-800 mb-4">
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-emerald-400 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" />
            Forecast Status
          </h3>
          <p className="text-[10px] text-slate-500">Predictive emergence engine</p>
        </div>
        <div className="flex flex-col items-center justify-center py-4 text-center h-full">
          <p className="text-sm text-slate-400">{forecast.narrative}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between h-full border border-amber-500/30 bg-amber-500/5">
      <div className="pb-3 border-b border-amber-500/20 mb-4">
        <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-amber-500 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          Forecast Triggered
        </h3>
        <p className="text-[10px] text-amber-500/60">Predictive emergence engine</p>
      </div>
      <div className="space-y-4">
        <div className="flex justify-between items-center bg-slate-900/80 p-3 rounded-lg border border-amber-500/20">
          <div>
            <p className="text-sm font-medium text-slate-300">Predicted Class</p>
            <p className="text-xs text-slate-500">High confidence trajectory</p>
          </div>
          <div className="text-lg font-bold font-mono text-amber-400">
            {forecast.forecast_class}
          </div>
        </div>
        
        <div className="flex justify-between items-center bg-slate-900/80 p-3 rounded-lg border border-amber-500/20">
          <div>
            <p className="text-sm font-medium text-slate-300">Estimated Time to Impact</p>
            <p className="text-xs text-slate-500">Based on risk velocity</p>
          </div>
          <div className="flex items-center gap-2 text-lg font-bold font-mono text-rose-400">
            <Clock className="w-4 h-4" />
            {forecast.eta_narrative}
          </div>
        </div>
        
        <div className="text-sm p-3 bg-amber-950/40 text-amber-200 rounded-lg border border-amber-900/60 italic">
          "{forecast.narrative}"
        </div>
      </div>
    </div>
  );
};
