import React from 'react';
import { getRiskStateConfig, getSeverityConfig } from '../../utils/formatters';

interface MetricBadgeProps {
  label: string;
  type?: 'risk' | 'severity' | 'neutral';
  value?: string | number | null;
  size?: 'sm' | 'md';
  className?: string;
}

export const MetricBadge: React.FC<MetricBadgeProps> = ({
  label,
  type = 'neutral',
  value,
  size = 'md',
  className = '',
}) => {
  let config = {
    badgeBg: 'bg-slate-900',
    badgeBorder: 'border-slate-800',
    text: 'text-slate-300',
    dotBg: 'bg-slate-500',
    glow: '',
    barColor: '#64748b',
  };

  if (type === 'risk') {
    config = getRiskStateConfig(value ?? label);
  } else if (type === 'severity') {
    config = getSeverityConfig(String(value ?? label));
  }

  const padding = size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono uppercase font-semibold tracking-wider rounded border ${config.badgeBg} ${config.badgeBorder} ${config.text} ${config.glow} ${padding} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dotBg}`} />
      <span>{label}</span>
    </span>
  );
};
