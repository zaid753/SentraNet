import type { SystemStatus, HealthResponse, ConnectionState } from '../types';
import { StatusIndicator } from './StatusIndicator';
import { Server, Database, BrainCircuit, PlaySquare, Radio, RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface SystemStatusCardProps {
  connectionState: ConnectionState;
  health: HealthResponse | null;
  systemStatus: SystemStatus | null;
  errorMessage?: string;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const SystemStatusCard: React.FC<SystemStatusCardProps> = ({
  connectionState,
  health,
  systemStatus,
  errorMessage,
  onRefresh,
  isRefreshing,
}) => {
  const isConnected = connectionState === 'CONNECTED';
  const isOffline = connectionState === 'OFFLINE' || connectionState === 'ERROR';

  return (
    <div className="soc-panel rounded-xl p-6 sm:p-7 relative overflow-hidden">
      {/* Top bar of status panel */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
            <h2 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
              System Infrastructure Matrix
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time backend service telemetry & component status
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700/80 hover:border-slate-600 text-xs font-mono text-slate-300 hover:text-white transition-all disabled:opacity-50 self-start sm:self-auto cursor-pointer"
          title="Query backend health endpoints"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-cyan-400' : 'text-slate-400'}`} />
          <span>{isRefreshing ? 'Syncing...' : 'Poll Status'}</span>
        </button>
      </div>

      {/* When offline / error */}
      {isOffline && (
        <div className="mt-5 p-4 rounded-lg bg-rose-950/30 border border-rose-800/50 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-rose-200">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-sm">Backend unavailable</div>
              <p className="text-xs text-rose-300/80 mt-0.5">
                {errorMessage || 'Unable to establish connection to SENTRANET FastAPI service.'}
              </p>
              <div className="text-[11px] font-mono mt-2 text-rose-300 bg-rose-950/60 px-2.5 py-1 rounded inline-block border border-rose-900/60">
                Start FastAPI backend to connect: <span className="text-rose-100 font-bold">uvicorn app.main:app --reload</span>
              </div>
            </div>
          </div>
          <button
            onClick={onRefresh}
            className="px-3 py-1.5 rounded bg-rose-900/60 hover:bg-rose-900 border border-rose-700 text-xs font-mono text-white transition-colors cursor-pointer shrink-0"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Grid of status indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
        {/* Frontend status */}
        <div className="soc-panel-subtle rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <div className="text-xs text-slate-400 font-medium">Frontend Client</div>
              <div className="text-sm font-semibold text-slate-100 font-mono">React / Vite</div>
            </div>
          </div>
          <StatusIndicator status="online" label="ONLINE" />
        </div>

        {/* Backend status */}
        <div className="soc-panel-subtle rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300">
              <Server className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <div className="text-xs text-slate-400 font-medium">Backend API</div>
              <div className="text-sm font-semibold text-slate-100 font-mono">
                {health?.service || 'FastAPI Service'}
              </div>
            </div>
          </div>
          <StatusIndicator
            status={isConnected ? (systemStatus?.backend?.status || 'online') : 'offline'}
          />
        </div>

        {/* ML Engine status */}
        <div className="soc-panel-subtle rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400">
              <BrainCircuit className="w-4 h-4 text-purple-400" />
            </div>
            <div>
              <div className="text-xs text-slate-400 font-medium">ML Platform</div>
              <div className="text-sm font-semibold text-slate-300 font-mono">Attack Forecaster</div>
            </div>
          </div>
          <StatusIndicator
            status={isConnected ? (systemStatus?.ml_models?.status || 'not_loaded') : 'not_initialized'}
          />
        </div>

        {/* Replay Engine status */}
        <div className="soc-panel-subtle rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400">
              <PlaySquare className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <div className="text-xs text-slate-400 font-medium">Replay Engine</div>
              <div className="text-sm font-semibold text-slate-300 font-mono">Traffic Streamer</div>
            </div>
          </div>
          <StatusIndicator
            status={isConnected ? (systemStatus?.replay_engine?.status || 'not_initialized') : 'not_initialized'}
          />
        </div>

        {/* Database status */}
        <div className="soc-panel-subtle rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400">
              <Database className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <div className="text-xs text-slate-400 font-medium">Persistence Layer</div>
              <div className="text-sm font-semibold text-slate-300 font-mono">Database</div>
            </div>
          </div>
          <StatusIndicator
            status={isConnected ? (systemStatus?.database?.status || 'not_configured') : 'not_configured'}
          />
        </div>

        {/* WebSocket Stream status */}
        <div className="soc-panel-subtle rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400">
              <Radio className="w-4 h-4 text-teal-400" />
            </div>
            <div>
              <div className="text-xs text-slate-400 font-medium">Telemetry Stream</div>
              <div className="text-sm font-semibold text-slate-300 font-mono">WebSocket</div>
            </div>
          </div>
          <StatusIndicator
            status={isConnected ? (systemStatus?.websocket?.status || 'not_initialized') : 'not_initialized'}
          />
        </div>
      </div>

      {/* Meta detail row */}
      {isConnected && health && (
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-400 gap-2">
          <div className="flex items-center gap-2">
            <span className="text-slate-500">Service:</span>
            <span className="text-slate-300 font-semibold">{health.service}</span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-500">Version:</span>
            <span className="text-cyan-400">{health.version}</span>
          </div>
          <div className="text-emerald-400 font-semibold">
            Health Check: 200 OK
          </div>
        </div>
      )}
    </div>
  );
};
