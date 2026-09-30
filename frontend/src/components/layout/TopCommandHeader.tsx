import React, { useEffect, useState } from 'react';
import { Search, Server, Activity, Clock, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import type { SystemStatus } from '../../types';
import { useRealtime } from '../../context/RealtimeContext';

interface TopCommandHeaderProps {
  status: SystemStatus | null;
  isLoading?: boolean;
}

export const TopCommandHeader: React.FC<TopCommandHeaderProps> = ({ status, isLoading = false }) => {
  const isReady = status?.status === 'ready' || status?.status === 'ok';
  
  const [currentTime, setCurrentTime] = useState(new Date());
  const { status: wsStatus } = useRealtime();

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

      {/* Center: Global Search / Command (Visual placeholder as requested) */}
      <div className="hidden lg:flex max-w-md w-full mx-8">
        <div className="relative w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-[var(--color-text-secondary)]" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-1.5 bg-[var(--color-elevated)] border border-[var(--color-border)] rounded-md text-sm placeholder-[var(--color-text-secondary)] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            placeholder="Search incidents, IPs, or run commands (Ctrl+K)"
            disabled
          />
        </div>
      </div>

      {/* Right: Telemetry & Time */}
      <div className="flex items-center gap-6">
        <div className="hidden md:flex flex-col items-end">
          <div className="flex items-center gap-1.5 text-xs text-[var(--color-text-secondary)]">
            <Server className="w-3.5 h-3.5" />
            <span className="font-mono text-blue-400 mr-2">{status?.simulation ? 'SYNTHETIC STREAM // SIMULATION' : 'LIVE NETWORK'}</span>
            
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
            <span className="font-mono">17 FEATURES ACTIVE</span>
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
