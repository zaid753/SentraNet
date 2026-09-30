import React from 'react';
import type { FeatureExplanation } from '../../types/explainability';

interface TopSignalsCardProps {
  features: FeatureExplanation[];
}

export const TopSignalsCard: React.FC<TopSignalsCardProps> = ({ features }) => {
  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between h-full">
      <div className="pb-3 border-b border-slate-800 mb-4">
        <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-400">Top Attributing Signals</h3>
        <p className="text-[10px] text-slate-500">Network features driving the current model decision</p>
      </div>
      <div className="space-y-4">
        {features.map((feat, idx) => (
          <div key={feat.feature} className="flex flex-col gap-1">
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium flex items-center gap-2 text-slate-300">
                <span className="bg-cyan-500/20 text-cyan-400 w-5 h-5 flex items-center justify-center rounded-full text-[10px] font-bold">
                  {idx + 1}
                </span>
                {feat.display_name}
              </span>
              <span className="font-mono bg-slate-900 px-2 py-0.5 rounded text-xs text-slate-300 border border-slate-800">
                {feat.current_value !== null ? feat.current_value.toFixed(2) : 'N/A'} <span className="text-slate-500">{feat.unit}</span>
              </span>
            </div>
            
            <div className="w-full bg-slate-800 rounded-full h-1 mt-1">
              <div 
                className="bg-cyan-500 h-1 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.6)]" 
                style={{ width: `${(feat.global_importance || 0) * 100}%` }}
              ></div>
            </div>
            
            <p className="text-[10px] text-slate-500">
              {feat.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
