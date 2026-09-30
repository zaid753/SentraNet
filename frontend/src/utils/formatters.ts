/**
 * SENTRANET — Semantic Formatters & Color Tokens (Phase 8 SOC Dashboard)
 * Centralizes all data presentation logic without fabricating or rounding falsified values.
 */

export function formatRiskScore(score: number | null | undefined): string {
  if (score === null || score === undefined || isNaN(score)) return '—';
  return `${(score * 100).toFixed(1)}%`;
}

export function formatProbability(prob: number | null | undefined): string {
  if (prob === null || prob === undefined || isNaN(prob)) return '—';
  return `${(prob * 100).toFixed(0)}%`;
}

export function formatEta(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined || isNaN(seconds)) return '—';
  if (seconds === 0) return '0s (Immediate)';
  if (seconds < 60) return `${seconds}s`;
  const mins = Math.floor(seconds / 60);
  const remSec = seconds % 60;
  return `${mins}m ${remSec}s`;
}

export function formatTimestamp(ts: string | null | undefined): string {
  if (!ts) return '—';
  try {
    const d = new Date(ts);
    if (isNaN(d.getTime())) {
      // Fallback for time string e.g. 08:42:00
      return ts.includes('T') ? ts.split('T')[1].slice(0, 8) : ts;
    }
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
  } catch {
    return ts;
  }
}

export function formatDateTime(ts: string | null | undefined): string {
  if (!ts) return '—';
  try {
    const d = new Date(ts);
    if (isNaN(d.getTime())) return ts;
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}`;
  } catch {
    return ts;
  }
}

export function formatAttackClass(cls: string | null | undefined): string {
  if (!cls) return '—';
  const upper = cls.toUpperCase();
  switch (upper) {
    case 'BENIGN':
      return 'Benign';
    case 'SCANNING':
      return 'Port Scanning';
    case 'DDOS':
      return 'DDoS Flooding';
    case 'BOTNET':
      return 'Botnet Command';
    case 'OTHER_ATTACK':
      return 'Other Attack';
    default:
      return cls.charAt(0).toUpperCase() + cls.slice(1).toLowerCase();
  }
}

export function formatSeverity(sev: string | null | undefined): string {
  if (!sev) return '—';
  return sev.toUpperCase();
}

export function formatRiskState(state: string | null | undefined): string {
  if (!state) return '—';
  return state.toUpperCase();
}

/**
 * Returns color classes and semantic meaning for Risk States (Phase 5 thresholds).
 * LOW: 0.00–0.24
 * GUARDED: 0.25–0.49
 * ELEVATED: 0.50–0.74
 * HIGH: 0.75–1.00
 */
export interface SemanticColorConfig {
  badgeBg: string;
  badgeBorder: string;
  text: string;
  dotBg: string;
  glow: string;
  barColor: string;
}

export function getRiskStateConfig(stateOrScore: string | number | null | undefined): SemanticColorConfig {
  let state = 'LOW';

  if (typeof stateOrScore === 'number') {
    if (stateOrScore >= 0.75) state = 'HIGH';
    else if (stateOrScore >= 0.50) state = 'ELEVATED';
    else if (stateOrScore >= 0.25) state = 'GUARDED';
    else state = 'LOW';
  } else if (typeof stateOrScore === 'string') {
    state = stateOrScore.toUpperCase();
  }

  switch (state) {
    case 'HIGH':
    case 'CRITICAL':
      return {
        badgeBg: 'bg-rose-950/60',
        badgeBorder: 'border-rose-700/60',
        text: 'text-rose-400',
        dotBg: 'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.7)]',
        glow: 'shadow-[0_0_20px_-3px_rgba(244,63,94,0.3)]',
        barColor: '#f43f5e',
      };
    case 'ELEVATED':
    case 'ALERT':
      return {
        badgeBg: 'bg-orange-950/60',
        badgeBorder: 'border-orange-700/60',
        text: 'text-orange-400',
        dotBg: 'bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.7)]',
        glow: 'shadow-[0_0_20px_-3px_rgba(249,115,22,0.25)]',
        barColor: '#f97316',
      };
    case 'GUARDED':
    case 'WATCH':
    case 'MEDIUM':
      return {
        badgeBg: 'bg-amber-950/60',
        badgeBorder: 'border-amber-700/60',
        text: 'text-amber-400',
        dotBg: 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.7)]',
        glow: 'shadow-[0_0_20px_-3px_rgba(245,158,11,0.2)]',
        barColor: '#f59e0b',
      };
    case 'LOW':
    case 'NORMAL':
    case 'INFO':
    default:
      return {
        badgeBg: 'bg-emerald-950/60',
        badgeBorder: 'border-emerald-700/60',
        text: 'text-emerald-400',
        dotBg: 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.7)]',
        glow: 'shadow-[0_0_20px_-3px_rgba(16,185,129,0.2)]',
        barColor: '#10b981',
      };
  }
}

export function getSeverityConfig(severity: string | null | undefined): SemanticColorConfig {
  const sev = (severity || '').toUpperCase();
  switch (sev) {
    case 'CRITICAL':
    case 'HIGH':
      return getRiskStateConfig('HIGH');
    case 'MEDIUM':
    case 'WATCH':
      return getRiskStateConfig('GUARDED');
    case 'LOW':
      return getRiskStateConfig('LOW');
    default:
      return {
        badgeBg: 'bg-slate-900',
        badgeBorder: 'border-slate-700',
        text: 'text-slate-400',
        dotBg: 'bg-slate-500',
        glow: '',
        barColor: '#94a3b8',
      };
  }
}

export function getTrendIcon(trend: string | null | undefined): { symbol: string; text: string; color: string } {
  const t = (trend || '').toUpperCase();
  if (t === 'RISING') {
    return { symbol: '↑', text: 'RISING', color: 'text-rose-400' };
  }
  if (t === 'FALLING') {
    return { symbol: '↓', text: 'FALLING', color: 'text-emerald-400' };
  }
  return { symbol: '→', text: 'STABLE', color: 'text-slate-400' };
}
