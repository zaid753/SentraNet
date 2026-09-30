import React from 'react';

export type StatusType = 
  | 'online' 
  | 'offline' 
  | 'not_initialized' 
  | 'not_configured' 
  | 'not_loaded' 
  | 'loading' 
  | 'degraded' 
  | 'error';

interface StatusIndicatorProps {
  status: StatusType | string;
  label?: string;
  className?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, label, className = '' }) => {
  const normalized = status.toLowerCase();

  const getStatusConfig = () => {
    switch (normalized) {
      case 'online':
      case 'healthy':
        return {
          dotClass: 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]',
          textClass: 'text-emerald-400 font-medium',
          displayLabel: label || 'ONLINE',
          isFilled: true,
        };
      case 'loading':
        return {
          dotClass: 'bg-cyan-400 animate-ping shadow-[0_0_8px_rgba(6,182,212,0.6)]',
          textClass: 'text-cyan-400 font-medium',
          displayLabel: label || 'LOADING',
          isFilled: true,
        };
      case 'offline':
      case 'error':
        return {
          dotClass: 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]',
          textClass: 'text-rose-400 font-medium',
          displayLabel: label || 'OFFLINE',
          isFilled: true,
        };
      case 'degraded':
        return {
          dotClass: 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]',
          textClass: 'text-amber-400 font-medium',
          displayLabel: label || 'DEGRADED',
          isFilled: true,
        };
      case 'not_initialized':
        return {
          dotClass: 'border-2 border-slate-500 bg-transparent',
          textClass: 'text-slate-400',
          displayLabel: label || 'NOT INITIALIZED',
          isFilled: false,
        };
      case 'not_configured':
        return {
          dotClass: 'border-2 border-slate-500 bg-transparent',
          textClass: 'text-slate-400',
          displayLabel: label || 'NOT CONFIGURED',
          isFilled: false,
        };
      case 'not_loaded':
        return {
          dotClass: 'border-2 border-slate-500 bg-transparent',
          textClass: 'text-slate-400',
          displayLabel: label || 'NOT LOADED',
          isFilled: false,
        };
      default:
        return {
          dotClass: 'border-2 border-slate-600 bg-transparent',
          textClass: 'text-slate-400',
          displayLabel: label || normalized.toUpperCase(),
          isFilled: false,
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`inline-flex items-center gap-2 font-mono text-xs tracking-wider ${className}`}>
      <span className={`inline-block w-2.5 h-2.5 rounded-full ${config.dotClass}`} />
      <span className={config.textClass}>{config.displayLabel}</span>
    </div>
  );
};
