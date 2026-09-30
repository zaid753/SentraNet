import React from 'react';
import { getRiskStateConfig } from '../../utils/formatters';

interface RiskGaugeProps {
  score: number | null | undefined;
  className?: string;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score, className = '' }) => {
  const safeScore = score !== null && score !== undefined && !isNaN(score) ? Math.min(Math.max(score, 0), 1) : 0;
  const config = getRiskStateConfig(score);

  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      {/* Segmented bar */}
      <div className="relative h-2.5 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${safeScore * 100}%`,
            backgroundColor: config.barColor,
            boxShadow: `0 0 12px ${config.barColor}`,
          }}
        />
      </div>

      {/* Threshold Labels */}
      <div className="flex justify-between items-center text-[10px] font-mono tracking-wider text-slate-500">
        <span className={safeScore >= 0.0 && safeScore < 0.25 ? 'text-emerald-400 font-bold' : ''}>
          LOW 0.00
        </span>
        <span className={safeScore >= 0.25 && safeScore < 0.50 ? 'text-amber-400 font-bold' : ''}>
          GUARDED 0.25
        </span>
        <span className={safeScore >= 0.50 && safeScore < 0.75 ? 'text-orange-400 font-bold' : ''}>
          ELEVATED 0.50
        </span>
        <span className={safeScore >= 0.75 ? 'text-rose-400 font-bold' : ''}>
          HIGH 0.75
        </span>
      </div>
    </div>
  );
};
