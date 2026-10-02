import React, { useState, useEffect } from 'react';
import type { TelemetryStatusResponse, LiveStatusResponse, LiveStartRequest, InterfaceResponse } from '../../types';
import { Play, Square, Radio, AlertTriangle } from 'lucide-react';

interface LiveStreamControlsProps {
  telemetryStatus: TelemetryStatusResponse | null;
  liveStatus: LiveStatusResponse | null;
  interfaces: InterfaceResponse[];
  isRunning: boolean;
  isLoading: boolean;
  actionError: string | null;
  onStart: (req: LiveStartRequest) => Promise<void>;
  onStop: () => Promise<void>;
}

export const LiveStreamControls: React.FC<LiveStreamControlsProps> = ({
  telemetryStatus,
  liveStatus,
  interfaces,
  isRunning,
  isLoading,
  actionError,
  onStart,
  onStop,
}) => {
  const [selectedInterface, setSelectedInterface] = useState<string>('');

  useEffect(() => {
    if (interfaces.length > 0 && !selectedInterface) {
      setSelectedInterface(interfaces[0].name);
    }
  }, [interfaces, selectedInterface]);

  const handleStartClick = () => {
    onStart({
      interface: selectedInterface,
    });
  };

  const canStart = !isRunning;
  const canStop = isRunning;

  const currentWindowDisplay = telemetryStatus?.current_window_start
    ? new Date(telemetryStatus.current_window_start).toLocaleTimeString()
    : 'None';

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-red-400" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Live Network Capture
          </h3>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-950/60 border border-red-800/60 text-red-300 font-semibold">
            EXPERIMENTAL
          </span>
        </div>
      </div>

      {(actionError || (liveStatus?.state === 'PERMISSION_DENIED' || liveStatus?.state === 'ERROR')) && (
        <div className="my-2 p-2.5 rounded bg-rose-950/50 border border-rose-800/60 text-rose-300 text-xs font-mono flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{actionError || liveStatus?.error_message || 'Capture error occurred'}</span>
        </div>
      )}

      {/* Selectors */}
      <div className="my-4 grid grid-cols-1 gap-3 text-xs font-mono">
        {/* Interface */}
        <div>
          <label className="text-slate-400 text-[10px] uppercase block mb-1">
            Network Interface
          </label>
          <select
            value={selectedInterface}
            disabled={isRunning || isLoading}
            onChange={(e) => setSelectedInterface(e.target.value)}
            className="w-full max-w-sm bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-red-600 focus:outline-none disabled:opacity-50"
          >
            {interfaces.map((iface) => (
              <option key={iface.name} value={iface.name}>
                {iface.name} - {iface.description}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80">
        {/* Start Button */}
        <button
          onClick={handleStartClick}
          disabled={!canStart || isLoading || !selectedInterface}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 text-red-300 font-mono text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
        >
          <Play className="w-3.5 h-3.5" />
          <span>Start Monitoring</span>
        </button>

        {/* Stop Button */}
        <button
          onClick={onStop}
          disabled={!canStop || isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-mono text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
        >
          <Square className="w-3.5 h-3.5" />
          <span>Stop</span>
        </button>
      </div>

      {/* Live Ingestion Metrics Status Bar */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
        <div>
          <span className="text-slate-400 text-[10px] block">Capture State</span>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span
              className={`w-2 h-2 rounded-full ${
                isRunning
                  ? 'bg-red-400 animate-pulse'
                  : liveStatus?.state === 'ERROR' || liveStatus?.state === 'PERMISSION_DENIED'
                  ? 'bg-rose-600'
                  : 'bg-slate-500'
              }`}
            />
            <span className="font-semibold text-slate-200 uppercase">
              {liveStatus?.state || 'STOPPED'}
            </span>
          </div>
        </div>

        <div>
          <span className="text-slate-400 text-[10px] block">Packets</span>
          <span className="text-slate-200 font-semibold mt-0.5 block">
            {(liveStatus?.packet_count || 0).toLocaleString()}
          </span>
        </div>

        <div>
          <span className="text-slate-400 text-[10px] block">Flows Built</span>
          <span className="text-cyan-300 font-semibold mt-0.5 block">
            {(liveStatus?.flow_count || 0).toLocaleString()}
          </span>
        </div>

        <div>
          <span className="text-slate-400 text-[10px] block">Windows Emitted</span>
          <span className="text-slate-200 font-semibold mt-0.5 block">
            {telemetryStatus?.windows_processed ?? 0}
          </span>
        </div>

        <div>
          <span className="text-slate-400 text-[10px] block">Current Window</span>
          <span className="text-slate-300 font-semibold mt-0.5 block truncate">
            {currentWindowDisplay}
          </span>
        </div>
      </div>
    </div>
  );
};
