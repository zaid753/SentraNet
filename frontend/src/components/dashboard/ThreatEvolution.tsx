import React from 'react';
import type { AnalyzeResponse } from '../../types';

import { Shield, Target, AlertTriangle, Skull } from 'lucide-react';

interface ThreatEvolutionProps {
  risk: AnalyzeResponse | null;
}

export const ThreatEvolution: React.FC<ThreatEvolutionProps> = ({ risk }) => {
  if (!risk) {
    return (
      <div className="soc-panel rounded-lg p-4 h-full border border-[var(--color-border)] flex flex-col justify-center items-center text-center">
        <span className="text-[10px] text-slate-500 font-mono mb-2">THREAT EVOLUTION UNKNOWN</span>
        <span className="text-xs text-slate-400">Awaiting sufficient telemetry to map threat trajectory.</span>
      </div>
    );
  }

  const stages = [
    { class: 'BENIGN', label: 'Benign', icon: Shield, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
    { class: 'SCANNING', label: 'Scanning', icon: Target, color: 'text-blue-400', bg: 'bg-blue-400/10' },
    { class: 'DDOS', label: 'DDoS', icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-400/10' },
    { class: 'BOTNET', label: 'Botnet', icon: Skull, color: 'text-red-400', bg: 'bg-red-400/10' }
  ];

  const currentClass = risk.attack_class;
  const currentStageIndex = stages.findIndex(s => s.class === currentClass);

  return (
    <div className="soc-panel rounded-lg p-4 h-full border border-[var(--color-border)] flex flex-col">
      <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center justify-between">
        <span>Threat Evolution</span>
        {currentStageIndex > 0 && <span className="text-amber-400 animate-pulse text-[8px] border border-amber-400/30 px-1 rounded">EVOLVING</span>}
      </h3>
      
      <div className="flex-1 flex flex-col justify-center">
        {currentClass === 'BENIGN' ? (
          <div className="flex flex-col items-center text-center">
            <Shield className="w-8 h-8 text-emerald-400 mb-2 opacity-50" />
            <span className="text-[10px] text-emerald-400/70 font-mono mb-1">STABLE ENVIRONMENT</span>
            <span className="text-xs text-slate-400">No active threat progression detected.</span>
          </div>
        ) : (
          <div className="relative flex flex-col gap-4">
            {/* Connecting Line */}
            <div className="absolute left-4 top-4 bottom-4 w-px bg-slate-800" />
            
            {stages.map((stage, index) => {
              const isCurrent = stage.class === currentClass;
              const isPast = index < currentStageIndex;
              const isFuture = index > currentStageIndex;
              
              const Icon = stage.icon;
              
              return (
                <div key={stage.class} className={`relative flex items-center gap-4 ${isFuture ? 'opacity-30' : 'opacity-100'}`}>
                  <div className={`w-8 h-8 rounded bg-[var(--color-elevated)] border flex items-center justify-center z-10 
                    ${isCurrent ? `border-${stage.color.split('-')[1]}-500 shadow-[0_0_10px_currentColor] ${stage.color}` : isPast ? 'border-slate-600 text-slate-400' : 'border-[var(--color-border)] text-slate-600'}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex flex-col">
                    <span className={`text-xs font-bold font-mono tracking-wide ${isCurrent ? stage.color : isPast ? 'text-slate-300' : 'text-slate-500'}`}>
                      {stage.label.toUpperCase()}
                    </span>
                    {isCurrent && (
                      <span className="text-[9px] text-slate-400 font-mono mt-0.5">CURRENT STAGE</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
