import React, { useEffect, useState } from 'react';
import { Server, Activity, Clock, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import type { SystemStatus } from '../../types';
import { useRealtime } from '../../context/RealtimeContext';
import { useModelRegistry } from '../../hooks/useModelRegistry';

interface TopCommandHeaderProps {
  status: SystemStatus | null;
  isLoading?: boolean;
}

export const TopCommandHeader: React.FC<TopCommandHeaderProps> = ({ status, isLoading = false }) => {
  const isReady = status?.status === 'ready' || status?.status === 'ok';
  
  const [currentTime, setCurrentTime] = useState(new Date());
  const { status: wsStatus } = useRealtime();
  const registry = useModelRegistry();

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-16 shrink-0 bg-[var(--color-surface)] border-b border-[var(--color-border)] flex items-center justify-between px-6">
      
      {/* Left: Branding & Status */}
      <div className="flex items-center gap-6">
        <div className="flex flex-col">
          <h1 className="text-lg font-bold tracking-tight text-white leading-none">SENTRANET</h1>
          <span className="text-[10px] uppercase tracking-wider text-[var(--color-text-secondary)] mt-0.5">
            Security Intelligence Platform
          </span>
        </div>
        
        <div className="hidden sm:flex items-center gap-2 pl-6 border-l border-[var(--color-border)]">
          <div className={`w-2 h-2 rounded-full ${isReady ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'}`} />
          <span className="text-xs font-mono font-medium text-[var(--color-text-secondary)]">
            {isLoading && !status ? 'CONNECTING...' : isReady ? 'SYSTEM OPERATIONAL' : 'SYSTEM DEGRADED'}
          </span>
        </div>
      </div>

      {/* Center: Model Selector & Warning */}
      <div className="hidden lg:flex flex-1 items-center justify-center mx-8">
        {registry.activeModel && (
          <div className="flex flex-col items-center justify-center">
            <div className="flex items-center gap-3">
              <span className="text-xs text-[var(--color-text-secondary)] font-mono">MODEL:</span>
              <select 
                className="bg-[var(--color-elevated)] border border-[var(--color-border)] rounded text-sm text-[var(--color-text-primary)] px-2 py-1 outline-none font-medium focus:border-blue-500"
                value={registry.activeModel.model_id}
                onChange={(e) => registry.setModel(e.target.value)}
                disabled={registry.isLoading}
              >
                {registry.models.map(m => (
                  <option key={m.model_id} value={m.model_id}>
                    {m.model_name}
                  </option>
                ))}
              </select>
              <div className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider ${registry.activeModel.status === 'EXPERIMENTAL' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}`}>
                {registry.activeModel.status}
              </div>
            </div>
            {registry.activeModel.status === 'EXPERIMENTAL' && (
              <div className="text-[10px] text-amber-400 font-mono mt-1 font-bold animate-pulse">
                REAL DATASET EXPERIMENT - NOT LIVE NETWORK TRAFFIC
              </div>
            )}
            {registry.error && (
              <div className="text-[10px] text-red-400 font-mono mt-1">
                ERROR: {registry.error}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right: Telemetry & Time */}
      <div className="flex items-center gap-6">
        <div className="hidden md:flex flex-col items-end">
          <div className="flex items-center gap-1.5 text-xs text-[var(--color-text-secondary)]">
            <Server className="w-3.5 h-3.5" />
            <span className="font-mono text-blue-400 mr-2">
              {registry.activeModel ? `DATA: ${registry.activeModel.dataset}` : 'LOADING...'}
            </span>
            
            {wsStatus === 'connected' && (
               <div className="flex items-center gap-1 text-emerald-400">
                  <Wifi className="w-3.5 h-3.5" />
                  <span className="font-mono">CONNECTED</span>
               </div>
            )}
            {(wsStatus === 'connecting' || wsStatus === 'reconnecting') && (
               <div className="flex items-center gap-1 text-amber-400">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span className="font-mono">{wsStatus.toUpperCase()}</span>
               </div>
            )}
            {wsStatus === 'disconnected' && (
               <div className="flex items-center gap-1 text-red-400">
                  <WifiOff className="w-3.5 h-3.5" />
                  <span className="font-mono">DISCONNECTED</span>
               </div>
            )}
            {wsStatus === 'error' && (
               <div className="flex items-center gap-1 text-red-500">
                  <WifiOff className="w-3.5 h-3.5" />
                  <span className="font-mono">WS ERROR</span>
               </div>
            )}
          </div>
          <div className="flex items-center gap-1.5 text-xs text-[var(--color-text-secondary)] mt-0.5">
            <Activity className="w-3.5 h-3.5" />
            <span className="font-mono">{registry.activeModel ? `${registry.activeModel.feature_contract_version} FEATURES` : 'FEATURES ACTIVE'}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2 text-[var(--color-text-primary)] bg-[var(--color-elevated)] px-3 py-1.5 rounded-md border border-[var(--color-border)]">
          <Clock className="w-4 h-4 text-blue-400" />
          <span className="font-mono text-sm tracking-wide">
            {currentTime.toLocaleTimeString('en-US', { hour12: false, timeZoneName: 'short' })}
          </span>
        </div>
      </div>
      
    </header>
  );
};
