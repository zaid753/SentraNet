import React, { useState } from 'react';
import type { TelemetryStatusResponse, SyntheticStatusResponse, SyntheticStartRequest } from '../../types';
import { Play, Pause, Square, RotateCcw, Activity, ArrowDownToLine, Sparkles } from 'lucide-react';

interface SyntheticStreamControlsProps {
  telemetryStatus: TelemetryStatusResponse | null;
  syntheticStatus: SyntheticStatusResponse | null;
  isRunning: boolean;
  isPaused: boolean;
  isLoading: boolean;
  actionError: string | null;
  onStart: (req: SyntheticStartRequest) => Promise<void>;
  onStop: () => Promise<void>;
  onPause: () => Promise<void>;
  onResume: () => Promise<void>;
  onFlush: () => Promise<void>;
  onReset: () => Promise<void>;
}

export const SyntheticStreamControls: React.FC<SyntheticStreamControlsProps> = ({
  telemetryStatus,
  syntheticStatus,
  isRunning,
  isPaused,
  isLoading,
  actionError,
  onStart,
  onStop,
  onPause,
  onResume,
  onFlush,
  onReset,
}) => {
  const [profile, setProfile] = useState<string>('scenario_1');
  const [speed, setSpeed] = useState<number>(10.0);
  const [seed, setSeed] = useState<number>(42);

  const handleStartClick = () => {
    onStart({
      speed,
      seed,
      profile,
    });
  };

  const handleQuickForward = () => {
    setProfile('scenario_1');
    setSpeed(10.0);
    setSeed(42);
    onStart({
      speed: 10.0,
      seed: 42,
      profile: 'scenario_1',
    });
  };

  const canStart = !isRunning && !isPaused;
  const canPause = isRunning && !isPaused;
  const canResume = isPaused;
  const canStop = isRunning || isPaused;

  const currentWindowDisplay = telemetryStatus?.current_window_start
    ? new Date(telemetryStatus.current_window_start).toLocaleTimeString()
    : 'None';

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Network Telemetry Ingestion
          </h3>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 font-semibold">
            SYNTHETIC STREAM — SIMULATION
          </span>
        </div>
      </div>

      {actionError && (
        <div className="my-2 p-2.5 rounded bg-rose-950/50 border border-rose-800/60 text-rose-300 text-xs font-mono">
          {actionError}
        </div>
      )}

      {/* Selectors */}
      <div className="my-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
        {/* Profile */}
        <div>
          <label className="text-slate-400 text-[10px] uppercase block mb-1">
            Traffic Profile / Scenario
          </label>
          <select
            value={profile}
            disabled={isRunning || isPaused || isLoading}
            onChange={(e) => setProfile(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-emerald-600 focus:outline-none disabled:opacity-50"
          >
            <option value="scenario_1">Scenario 1 (Baseline &rarr; Scan &rarr; DDoS)</option>
            <option value="BASELINE">Baseline Enterprise Traffic</option>
            <option value="SCANNING">Recon / Port Scanning</option>
            <option value="DDOS">Volumetric DDoS Flood</option>
            <option value="BOTNET">Botnet C2 Beaconing</option>
          </select>
        </div>

        {/* Speed */}
        <div>
          <label className="text-slate-400 text-[10px] uppercase block mb-1">
            Simulation Speed
          </label>
          <select
            value={speed}
            disabled={isRunning || isPaused || isLoading}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-emerald-600 focus:outline-none disabled:opacity-50"
          >
            <option value={1.0}>1x (Realtime Telemetry)</option>
            <option value={5.0}>5x Accelerated</option>
            <option value={10.0}>10x Accelerated (Default)</option>
            <option value={25.0}>25x Fast Forward</option>
            <option value={50.0}>50x High-Throughput</option>
          </select>
        </div>

        {/* Seed */}
        <div>
          <label className="text-slate-400 text-[10px] uppercase block mb-1">
            Deterministic Random Seed
          </label>
          <input
            type="number"
            value={seed}
            disabled={isRunning || isPaused || isLoading}
            onChange={(e) => setSeed(parseInt(e.target.value, 10) || 42)}
            className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-emerald-600 focus:outline-none disabled:opacity-50"
          />
        </div>
      </div>

      {/* Control Buttons */}
      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80">
        {/* Quick Forward 10x */}
        {canStart && (
          <button
            onClick={handleQuickForward}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs font-mono transition-colors shadow-sm disabled:opacity-50 cursor-pointer"
            title="Start Scenario 1 at 10x with seed 42"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Scenario 1 (10x)</span>
          </button>
        )}

        {/* Start Button */}
        <button
          onClick={handleStartClick}
          disabled={!canStart || isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 font-mono text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
        >
          <Play className="w-3.5 h-3.5" />
          <span>Start Stream</span>
        </button>

        {/* Pause Button */}
        <button
          onClick={onPause}
          disabled={!canPause || isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 font-mono text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
        >
          <Pause className="w-3.5 h-3.5" />
          <span>Pause</span>
        </button>

        {/* Resume Button */}
        <button
          onClick={onResume}
          disabled={!canResume || isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 font-mono text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
        >
          <Play className="w-3.5 h-3.5" />
          <span>Resume</span>
        </button>

        {/* Stop Button */}
        <button
          onClick={onStop}
          disabled={!canStop || isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 font-mono text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
        >
          <Square className="w-3.5 h-3.5" />
          <span>Stop</span>
        </button>

        {/* Flush Window Button */}
        <button
          onClick={onFlush}
          disabled={isLoading || (!isRunning && (telemetryStatus?.flows_in_window || 0) === 0)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-mono text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer ml-auto"
          title="Force current accumulation window to complete and trigger AI inference"
        >
          <ArrowDownToLine className="w-3.5 h-3.5 text-cyan-400" />
          <span>Flush Window</span>
        </button>

        {/* Reset Stream */}
        <button
          onClick={onReset}
          disabled={isRunning || isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700/80 text-slate-400 hover:text-slate-200 font-mono text-xs transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          title="Reset telemetry counters and window buffers"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
      </div>

      {/* Live Ingestion Metrics Status Bar */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
        <div>
          <span className="text-slate-400 text-[10px] block">Stream Status</span>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span
              className={`w-2 h-2 rounded-full ${
                isRunning
                  ? 'bg-emerald-400 animate-pulse'
                  : isPaused
                  ? 'bg-amber-400'
                  : 'bg-slate-500'
              }`}
            />
            <span className="font-semibold text-slate-200 uppercase">
              {syntheticStatus?.status || (isRunning ? 'STREAMING' : 'IDLE')}
            </span>
          </div>
        </div>

        <div>
          <span className="text-slate-400 text-[10px] block">Total Flows</span>
          <span className="text-slate-200 font-semibold mt-0.5 block">
            {(syntheticStatus?.flows_generated ?? telemetryStatus?.flows_processed ?? 0).toLocaleString()}
          </span>
        </div>

        <div>
          <span className="text-slate-400 text-[10px] block">Active Window Flows</span>
          <span className="text-cyan-300 font-semibold mt-0.5 block">
            {(telemetryStatus?.flows_in_window ?? 0).toLocaleString()}
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
