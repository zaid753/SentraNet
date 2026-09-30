import { ShieldAlert, RefreshCw, LayoutDashboard, Layers, FlaskConical } from 'lucide-react';
import type { ConnectionState, ReplayStatusResponse } from '../../types';

interface HeaderProps {
  connectionState: ConnectionState;
  replayStatus: ReplayStatusResponse | null;
  activeView: 'dashboard' | 'foundation' | 'evaluation';
  onViewChange: (view: 'dashboard' | 'foundation' | 'evaluation') => void;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  connectionState,
  replayStatus,
  activeView,
  onViewChange,
  onRefresh,
  isRefreshing = false,
}) => {
  const isOnline = connectionState === 'CONNECTED';
  const isReplayRunning = Boolean(replayStatus?.running);

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left: Brand & Tagline */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/60 border border-cyan-800/60 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.25)] shrink-0">
            <ShieldAlert className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-bold tracking-wider font-mono text-white flex items-center gap-2">
                SENTRANET
              </h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-700/50 text-cyan-300 font-semibold tracking-wide">
                SIH26153
              </span>
              <span className="hidden sm:inline-block text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-700/60 text-slate-400">
                Phase 10
              </span>
            </div>
            <p className="text-xs text-slate-400 tracking-wide mt-0.5 font-sans">
              From detecting attacks to forecasting them.
            </p>
          </div>
        </div>

        {/* Center: View Switcher */}
        <div className="flex items-center bg-slate-900/90 border border-slate-800 rounded-lg p-1 self-start md:self-auto font-mono text-xs">
          <button
            onClick={() => onViewChange('dashboard')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all cursor-pointer ${
              activeView === 'dashboard'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/60 shadow-sm font-semibold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>SOC Dashboard</span>
          </button>
          <button
            onClick={() => onViewChange('foundation')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all cursor-pointer ${
              activeView === 'foundation'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/60 shadow-sm font-semibold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Architecture & Health</span>
          </button>
          <button
            onClick={() => onViewChange('evaluation')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all cursor-pointer ${
              activeView === 'evaluation'
                ? 'bg-amber-950/70 text-amber-300 border border-amber-700/50 shadow-sm font-semibold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <FlaskConical className="w-3.5 h-3.5" />
            <span>Benchmark Eval</span>
          </button>
        </div>

        {/* Right: Telemetry Badges */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs font-mono">
          {/* Replay indicator */}
          <div className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                isReplayRunning
                  ? 'bg-amber-400 animate-pulse shadow-[0_0_8px_rgba(251,191,36,0.6)]'
                  : 'bg-slate-500'
              }`}
            />
            <span className="text-slate-400">REPLAY:</span>
            <span className={`font-semibold ${isReplayRunning ? 'text-amber-400' : 'text-slate-400'}`}>
              {replayStatus?.mode ? replayStatus.mode.toUpperCase() : 'IDLE'}
            </span>
          </div>

          {/* API Health indicator */}
          <div className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                isOnline
                  ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]'
                  : 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]'
              }`}
            />
            <span className="text-slate-400">API:</span>
            <span className={`font-semibold ${isOnline ? 'text-emerald-400' : 'text-rose-400'}`}>
              {connectionState}
            </span>
          </div>

          {/* Refresh button */}
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="p-1.5 rounded-md bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition-all cursor-pointer disabled:opacity-50"
              title="Refresh all metrics"
              aria-label="Refresh telemetry"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
