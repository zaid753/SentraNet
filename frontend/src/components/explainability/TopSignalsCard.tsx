import React from 'react';
import type { FeatureExplanation } from '../../types/explainability';

interface TopSignalsCardProps {
  features: FeatureExplanation[];
}

export const TopSignalsCard: React.FC<TopSignalsCardProps> = ({ features }) => {
  const renderBlocks = (importance: number) => {
    const totalBlocks = 20;
    const activeBlocks = Math.max(1, Math.round(importance * totalBlocks));
    return '█'.repeat(activeBlocks) + '▒'.repeat(totalBlocks - activeBlocks);
  };

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between h-full">
      <div className="pb-3 border-b border-slate-800 mb-4">
        <h3 className="text-xs font-bold tracking-wider font-mono uppercase text-slate-200">Why Is Risk Elevated?</h3>
        <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mt-1">Top Attributing Signals</p>
      </div>
      <div className="space-y-5 overflow-y-auto custom-scrollbar pr-2">
        {features.map((feat, idx) => (
          <div key={feat.feature} className="flex flex-col gap-1.5 font-mono">
            <div className="flex justify-between items-start">
              <div className="flex gap-3">
                <span className="text-[10px] text-cyan-500 font-bold mt-0.5">
                  {(idx + 1).toString().padStart(2, '0')}
                </span>
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-slate-200">{feat.display_name}</span>
                  <p className="text-[10px] text-slate-500 font-sans mt-0.5 max-w-[200px]">
                    {feat.description}
                  </p>
                </div>
              </div>
              <span className="bg-slate-900 px-2 py-0.5 rounded text-xs text-white border border-slate-800 font-bold whitespace-nowrap">
                {feat.current_value !== null ? feat.current_value.toFixed(2) : 'N/A'} <span className="text-slate-500 text-[10px]">{feat.unit}</span>
              </span>
            </div>
            
            <div className="flex items-center gap-2 mt-1">
              <span className="text-[10px] text-cyan-400 tracking-tighter">
                {renderBlocks(feat.global_importance || 0)}
              </span>
              <span className="text-[9px] text-slate-600">
                {((feat.global_importance || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
        {features.length === 0 && (
          <div className="text-[10px] text-slate-500 font-mono text-center py-4">
            Awaiting active features...
          </div>
        )}
      </div>
    </div>
  );
};
