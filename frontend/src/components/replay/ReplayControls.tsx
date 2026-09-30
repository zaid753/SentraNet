import React, { useState } from 'react';
import type { ReplayStatusResponse, ReplayStartRequest } from '../../types';
import { Play, Pause, Square, SkipForward, RotateCcw, FastForward, PlayCircle } from 'lucide-react';

interface ReplayControlsProps {
  status: ReplayStatusResponse | null;
  isRunning: boolean;
  isPaused: boolean;
  isLoading: boolean;
  actionError: string | null;
  onStart: (req: ReplayStartRequest) => Promise<void>;
  onStop: () => Promise<void>;
  onPause: () => Promise<void>;
  onResume: () => Promise<void>;
  onStep: () => Promise<void>;
  onReset: () => Promise<void>;
}

export const ReplayControls: React.FC<ReplayControlsProps> = ({
  status: _status,
  isRunning,
  isPaused,
  isLoading,
  actionError,
  onStart,
  onStop,
  onPause,
  onResume,
  onStep,
  onReset,
}) => {
  const [mode, setMode] = useState<'realtime' | 'step' | 'batch'>('realtime');
  const [speed, setSpeed] = useState<number>(10.0);
  const [dataset, setDataset] = useState<string>('validation');

  const handleStartClick = () => {
    onStart({
      mode,
      speed,
      dataset,
    });
  };

  const handleDemoReplay = () => {
    setMode('realtime');
    setSpeed(10.0);
    setDataset('validation');
    onStart({
      mode: 'realtime',
      speed: 10.0,
      dataset: 'validation',
    });
  };

  // State-based button availability rules
  const canStart = !isRunning && !isPaused;
  const canPause = isRunning && !isPaused;
  const canResume = isPaused;
  const canStep = isPaused || (!isRunning && mode === 'step');
  const canStop = isRunning || isPaused;

  return (
    <div className="soc-panel rounded-xl p-5 relative overflow-hidden flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <PlayCircle className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200">
            Historical Replay Controls
          </h3>
        </div>

        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/60 text-amber-300 font-semibold">
          SIMULATION
        </span>
      </div>

      {actionError && (
        <div className="my-2 p-2.5 rounded bg-rose-950/50 border border-rose-800/60 text-rose-300 text-xs font-mono">
          {actionError}
        </div>
      )}

      {/* Selectors */}
      <div className="my-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
        {/* Mode */}
        <div>
          <label className="text-slate-400 text-[10px] uppercase block mb-1">
            Replay Mode
          </label>
          <select
            value={mode}
            disabled={isRunning || isPaused || isLoading}
            onChange={(e) => setMode(e.target.value as 'realtime' | 'step' | 'batch')}
            className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-cyan-600 focus:outline-none disabled:opacity-50"
          >
            <option value="realtime">Realtime Clock</option>
            <option value="step">Step-by-Step</option>
            <option value="batch">Fast Batch</option>
          </select>
        </div>

        {/* Speed */}
        <div>
          <label className="text-slate-400 text-[10px] uppercase block mb-1">
            Playback Speed
          </label>
          <select
            value={speed}
            disabled={isRunning || isPaused || isLoading}
            onChange={(e) => setSpeed(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-cyan-600 focus:outline-none disabled:opacity-50"
          >
            <option value={1.0}>1x Normal</option>
            <option value={5.0}>5x Accelerated</option>
            <option value={10.0}>10x Recommended</option>
            <option value={20.0}>20x Fast</option>
            <option value={60.0}>60x Turbo</option>
          </select>
        </div>

        {/* Dataset */}
        <div>
          <label className="text-slate-400 text-[10px] uppercase block mb-1">
            Dataset Fixture
          </label>
          <select
            value={dataset}
            disabled={isRunning || isPaused || isLoading}
            onChange={(e) => setDataset(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-cyan-600 focus:outline-none disabled:opacity-50"
          >
            <option value="validation">validation (Attack scenarios)</option>
            <option value="test">test.parquet</option>
            <option value="train">train.parquet</option>
            <option value="full">full_synthetic_fixture</option>
          </select>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="flex flex-wrap items-center gap-2 pt-2">
        {/* Start button */}
        {canStart ? (
          <button
            onClick={handleStartClick}
            disabled={isLoading}
            className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-semibold shadow-md transition-all disabled:opacity-50 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Start Replay</span>
          </button>
        ) : null}

        {/* Pause button */}
        {canPause && (
          <button
            onClick={onPause}
            disabled={isLoading}
            className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-mono text-xs font-semibold shadow-md transition-all disabled:opacity-50 cursor-pointer"
          >
            <Pause className="w-3.5 h-3.5 fill-current" />
            <span>Pause</span>
          </button>
        )}

        {/* Resume button */}
        {canResume && (
          <button
            onClick={onResume}
            disabled={isLoading}
            className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-semibold shadow-md transition-all disabled:opacity-50 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Resume</span>
          </button>
        )}

        {/* Step button */}
        <button
          onClick={onStep}
          disabled={!canStep || isLoading}
          className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-600 text-slate-300 font-mono text-xs transition-all disabled:opacity-40 cursor-pointer"
          title="Step forward one window"
        >
          <SkipForward className="w-3.5 h-3.5" />
          <span>Step Window</span>
        </button>

        {/* Stop button */}
        <button
          onClick={onStop}
          disabled={!canStop || isLoading}
          className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-slate-900 border border-rose-900/60 hover:bg-rose-950/40 text-rose-300 font-mono text-xs transition-all disabled:opacity-40 cursor-pointer"
          title="Stop playback"
        >
          <Square className="w-3.5 h-3.5 fill-current" />
          <span>Stop</span>
        </button>

        {/* Reset Stream button */}
        <button
          onClick={onReset}
          disabled={isRunning || isLoading}
          className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white font-mono text-xs transition-all disabled:opacity-40 cursor-pointer"
          title="Reset in-memory temporal trajectory and alerts"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Stream</span>
        </button>

        {/* Quick Demo Replay shortcut */}
        {!isRunning && !isPaused && (
          <button
            onClick={handleDemoReplay}
            disabled={isLoading}
            className="ml-auto hidden xl:flex items-center gap-1.5 px-3 py-2 rounded-lg bg-cyan-950/80 border border-cyan-800/80 text-cyan-300 hover:bg-cyan-900/90 font-mono text-xs font-medium cursor-pointer"
          >
            <FastForward className="w-3.5 h-3.5" />
            <span>Start Demo Replay (10x)</span>
          </button>
        )}
      </div>

      <div className="pt-3 mt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
        <span>Dataset safety: Predefined identifiers only</span>
        <span>Replay Thread: In-Memory FIFO</span>
      </div>
    </div>
  );
};
