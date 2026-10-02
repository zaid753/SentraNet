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
  currentAttackClass?: string | null;
}

export const ReplayControls: React.FC<ReplayControlsProps> = ({
  status,
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
  currentAttackClass,
}) => {
  const [mode, setMode] = useState<'realtime' | 'step' | 'batch'>('realtime');
  const [speed, setSpeed] = useState<number>(10.0);
  const [dataset, setDataset] = useState<string>('validation');

  const handleStartClick = () => {
    onStart({ mode, speed, dataset });
  };

  const handleDemoReplay = () => {
    setMode('realtime');
    setSpeed(10.0);
    setDataset('validation');
    onStart({ mode: 'realtime', speed: 10.0, dataset: 'validation' });
  };

  const canStart = !isRunning && !isPaused;
  const canPause = isRunning && !isPaused;
  const canResume = isPaused;
  const canStep = isPaused || (!isRunning && mode === 'step');
  const canStop = isRunning || isPaused;

  const stages = ['BENIGN', 'SCANNING', 'DDOS', 'BOTNET'];
  let currentStageIndex = 0;
  if (currentAttackClass) {
    const cls = currentAttackClass.toUpperCase();
    if (cls.includes('BOTNET')) currentStageIndex = 3;
    else if (cls.includes('DDOS') || cls.includes('DOS')) currentStageIndex = 2;
    else if (cls.includes('SCAN') || cls.includes('PORT')) currentStageIndex = 1;
    else currentStageIndex = 0;
  }

  return (
    <div className="soc-panel rounded-xl p-4 sm:p-5 flex flex-col gap-4 border border-[var(--color-border)] shadow-md">
      {/* Top Header / Mode Selectors */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <PlayCircle className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold tracking-widest font-mono uppercase text-slate-200">
            Replay Simulator
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/60 text-amber-300 font-bold ml-2">
            {isRunning ? 'RUNNING' : isPaused ? 'PAUSED' : 'IDLE'}
          </span>
        </div>
        
        <div className="flex flex-wrap items-center gap-4 text-[10px] font-mono font-bold text-slate-400">
          <div className="flex items-center gap-2">
            <span>MODE:</span>
            <select value={mode} disabled={isRunning || isPaused || isLoading} onChange={(e) => setMode(e.target.value as any)} className="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-white focus:outline-none focus:border-cyan-500">
              <option value="realtime">LIVE</option>
              <option value="batch">BATCH</option>
              <option value="step">STEP</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span>DATASET:</span>
            <select value={dataset} disabled={isRunning || isPaused || isLoading} onChange={(e) => setDataset(e.target.value)} className="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-white focus:outline-none focus:border-cyan-500">
              <option value="validation">validation</option>
              <option value="test">test.parquet</option>
              <option value="train">train.parquet</option>
              <option value="cicids2017_friday_morning">CIC-IDS2017 (Fri Morning)</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span>SPEED:</span>
            <select value={speed} disabled={isRunning || isPaused || isLoading} onChange={(e) => setSpeed(Number(e.target.value))} className="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-white focus:outline-none focus:border-cyan-500">
              <option value={1.0}>1x</option>
              <option value={5.0}>5x</option>
              <option value={10.0}>10x</option>
              <option value={60.0}>60x</option>
            </select>
          </div>
        </div>
      </div>

      {actionError && (
        <div className="p-2 rounded bg-rose-950/50 border border-rose-800/60 text-rose-300 text-xs font-mono">
          {actionError}
        </div>
      )}

      {/* Progress & Stage Indicator */}
      <div className="flex flex-col gap-3 font-mono">
        <div className="flex justify-between items-center text-xs">
          <div className="flex items-center gap-4">
            <span className="text-slate-500 font-bold">TS: <span className="text-white">{status?.current_timestamp || '--:--:--'}</span></span>
            <span className="text-slate-500 font-bold">PROG: <span className="text-cyan-400">{status ? `${status.windows_processed}/${status.total_windows}` : '0/0'}</span></span>
          </div>
        </div>

        <div className="flex items-center text-[10px] font-bold text-slate-500 w-full overflow-hidden">
          {stages.map((stage, idx) => (
            <React.Fragment key={stage}>
              <span className={`px-2 py-1 rounded transition-colors ${idx === currentStageIndex ? 'bg-cyan-950 text-cyan-400 border border-cyan-800' : 'text-slate-600'}`}>
                {stage}
              </span>
              {idx < stages.length - 1 && (
                <span className={`flex-1 flex px-1 transition-colors ${idx < currentStageIndex ? 'text-cyan-800' : 'text-slate-800'}`}>
                  ━━━━━━━━━━━━━━━━
                </span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800/80 mt-1">
        <div className="flex flex-wrap items-center gap-2">
          {canStart && (
            <button onClick={handleStartClick} disabled={isLoading} className="flex items-center gap-1.5 px-4 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-[10px] font-bold transition-all cursor-pointer">
              <Play className="w-3.5 h-3.5" /> START
            </button>
          )}
          {canPause && (
            <button onClick={onPause} disabled={isLoading} className="flex items-center gap-1.5 px-4 py-1.5 rounded bg-amber-600 hover:bg-amber-500 text-white font-mono text-[10px] font-bold transition-all cursor-pointer">
              <Pause className="w-3.5 h-3.5" /> PAUSE
            </button>
          )}
          {canResume && (
            <button onClick={onResume} disabled={isLoading} className="flex items-center gap-1.5 px-4 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-[10px] font-bold transition-all cursor-pointer">
              <Play className="w-3.5 h-3.5" /> RESUME
            </button>
          )}
          <button onClick={onStep} disabled={!canStep || isLoading} className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-white font-mono text-[10px] font-bold transition-all disabled:opacity-40 cursor-pointer">
            <SkipForward className="w-3.5 h-3.5" /> STEP
          </button>
          <button onClick={onStop} disabled={!canStop || isLoading} className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-rose-900 hover:bg-rose-950 text-rose-400 font-mono text-[10px] font-bold transition-all disabled:opacity-40 cursor-pointer">
            <Square className="w-3.5 h-3.5" /> STOP
          </button>
        </div>
        
        <div className="flex items-center gap-2">
          {!isRunning && !isPaused && (
            <button onClick={handleDemoReplay} disabled={isLoading} className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-cyan-800 text-cyan-400 hover:bg-cyan-950 font-mono text-[10px] font-bold cursor-pointer transition-all">
              <FastForward className="w-3.5 h-3.5" /> DEMO (10x)
            </button>
          )}
          <button onClick={onReset} disabled={isRunning || isLoading} className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-900 border border-slate-700 hover:bg-slate-800 text-slate-300 font-mono text-[10px] font-bold transition-all disabled:opacity-40 cursor-pointer">
            <RotateCcw className="w-3 h-3" /> RESET
          </button>
        </div>
      </div>
    </div>
  );
};
