import React from 'react';
import type { AnalyzeResponse } from '../../types';
import {
  formatAttackClass,
  formatRiskScore,
} from '../../utils/formatters';
import { Crosshair, ShieldAlert } from 'lucide-react';

interface AttackClassificationCardProps {
  risk: AnalyzeResponse | null;
}

export const AttackClassificationCard: React.FC<AttackClassificationCardProps> = ({ risk }) => {
  const attackClass = risk?.attack_class || '—';
  const confidence = risk?.class_probability;
  const likelihood = risk?.attack_likelihood;
  const isAttack = attackClass.toUpperCase() !== 'BENIGN' && attackClass !== '—';

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between min-h-[220px]">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Crosshair className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Attack Classification
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
          XGBoost
        </span>
      </div>

      <div className="my-4">
        <div className="text-[10px] font-mono uppercase text-slate-500 tracking-wider">
          Dominant Vector
        </div>
        <div
          className={`text-2xl font-bold font-mono tracking-tight mt-1 flex items-center gap-2 ${
            isAttack ? 'text-rose-400' : 'text-emerald-400'
          }`}
        >
          {isAttack && <ShieldAlert className="w-5 h-5 shrink-0" />}
          <span>{formatAttackClass(attackClass)}</span>
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 text-[10px] block">Confidence</span>
            <span className="text-white font-bold">{formatRiskScore(confidence)}</span>
          </div>
          <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 text-[10px] block">Attack Likelihood</span>
            <span className="text-cyan-400 font-bold">{formatRiskScore(likelihood)}</span>
          </div>
        </div>
      </div>

      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <span>Classifier: Multi-Class 17-Dim</span>
        <span>Raw API Telemetry</span>
      </div>
    </div>
  );
};
