import React from 'react';
import type { RiskExplanation } from '../../types/explainability';

interface RiskBreakdownCardProps {
  risk: RiskExplanation;
}

export const RiskBreakdownCard: React.FC<RiskBreakdownCardProps> = ({ risk }) => {
  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between h-full">
      <div className="pb-3 border-b border-slate-800 mb-4">
        <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-400">Risk Decomposition</h3>
        <p className="text-[10px] text-slate-500">How the current risk score was calculated</p>
      </div>
      <div className="flex flex-col gap-4">
        <div className="flex justify-between items-center bg-slate-900/50 p-3 rounded-lg border border-slate-800">
          <div>
            <p className="text-sm font-medium text-slate-300">Final Risk Score</p>
            <p className="text-xs text-slate-500">State: <span className="font-semibold text-cyan-400">{risk.risk_state}</span></p>
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {(risk.risk_score * 100).toFixed(1)}%
          </div>
        </div>
        
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1 text-slate-300">
              <span>Threat Classification</span>
              <span className="font-mono">{(risk.components.attack_likelihood * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <div 
                className="bg-rose-500 h-2 rounded-full" 
                style={{ width: `${risk.components.attack_likelihood * 100}%` }}
              ></div>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Contributes {(risk.components.attack_likelihood_contribution * 100).toFixed(1)}% to total risk
            </p>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1 text-slate-300">
              <span>Behavioral Anomaly</span>
              <span className="font-mono">{(risk.components.anomaly_score * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <div 
                className="bg-amber-500 h-2 rounded-full" 
                style={{ width: `${risk.components.anomaly_score * 100}%` }}
              ></div>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Contributes {(risk.components.anomaly_contribution * 100).toFixed(1)}% to total risk
            </p>
          </div>
        </div>
        
        <div className="text-sm p-3 bg-cyan-950/30 text-cyan-200 rounded-lg border border-cyan-900/50 italic">
          "{risk.narrative}"
        </div>
      </div>
    </div>
  );
};
