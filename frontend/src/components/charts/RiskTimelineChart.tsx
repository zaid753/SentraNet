import React from 'react';
import type { TimelinePointResponse } from '../../types';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts';
import {
  formatTimestamp,
  formatRiskScore,
  formatAttackClass,
} from '../../utils/formatters';
import { Activity, Clock } from 'lucide-react';

interface RiskTimelineChartProps {
  points: TimelinePointResponse[];
  isLoading?: boolean;
}

interface TooltipItem {
  rawTimestamp: string;
  displayTime: string;
  riskScore: number;
  anomalyScore: number;
  attackClass: string;
  riskState: string;
  forecastActive: boolean;
  etaSeconds: number | null | undefined;
  index: number;
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: TooltipItem }> }) => {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0].payload;

  return (
    <div className="p-3 bg-slate-950/95 border border-slate-700/90 rounded-lg shadow-xl backdrop-blur-md text-xs font-mono text-slate-200 space-y-1.5 min-w-[200px]">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1 text-slate-400 text-[11px]">
        <span>Time: {data.displayTime}</span>
        <span className="text-slate-500">#{data.index + 1}</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-slate-400">Class:</span>
        <span className="font-bold text-white">{formatAttackClass(data.attackClass)}</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-rose-400">Risk Score:</span>
        <span className="font-bold text-rose-300">{formatRiskScore(data.riskScore)}</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-amber-400">Anomaly:</span>
        <span className="font-bold text-amber-300">{formatRiskScore(data.anomalyScore)}</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-slate-400">State:</span>
        <span className="text-cyan-300 font-semibold">{data.riskState}</span>
      </div>
      {data.forecastActive && (
        <div className="pt-1 mt-1 border-t border-slate-800 text-[10px] text-cyan-400 font-semibold flex items-center justify-between">
          <span>FORECAST ACTIVE</span>
          {data.etaSeconds !== null && data.etaSeconds !== undefined && (
            <span>ETA: {data.etaSeconds}s</span>
          )}
        </div>
      )}
    </div>
  );
};

export const RiskTimelineChart: React.FC<RiskTimelineChartProps> = ({
  points,
  isLoading = false,
}) => {
  // Format points for recharts
  const chartData = points.map((p, index) => ({
    rawTimestamp: p.timestamp,
    displayTime: formatTimestamp(p.timestamp),
    riskScore: Number(p.risk_score.toFixed(3)),
    anomalyScore: Number(p.anomaly_score.toFixed(3)),
    attackClass: p.attack_class,
    riskState: p.risk_state,
    forecastActive: p.forecast_active,
    etaSeconds: p.eta_seconds,
    index,
  }));

  if (chartData.length === 0) {
    return (
      <div className="soc-panel rounded-xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[340px]">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
              Risk & Anomaly Trajectory Timeline
            </h2>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
            Chronological
          </span>
        </div>

        <div className="my-12 text-center flex flex-col items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-3">
            <Clock className="w-6 h-6 animate-pulse" />
          </div>
          <h3 className="text-sm font-bold font-mono text-slate-300">
            {isLoading ? 'Loading telemetry timeline...' : 'No Timeline Data Available'}
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mt-1 font-sans">
            Start historical replay to stream chronological risk scores and isolation forest anomaly metrics across temporal windows.
          </p>
        </div>

        <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span>Dual Model Time-series</span>
          <span>Window size: 50 points</span>
        </div>
      </div>
    );
  }

  return (
    <div className="soc-panel rounded-xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[380px]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-semibold tracking-wider font-mono uppercase text-slate-200">
            Risk & Anomaly Trajectory Timeline
          </h2>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="text-slate-400">
            Points: <strong className="text-white">{chartData.length}</strong>
          </span>
          <span className="text-slate-500">|</span>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-0.5 bg-rose-500 rounded" />
            <span className="text-rose-300">Composite Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-0.5 bg-amber-400 rounded" />
            <span className="text-amber-300">Anomaly Signal</span>
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="w-full h-64 sm:h-72 my-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 12, right: 12, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />

            <XAxis
              dataKey="displayTime"
              stroke="#64748b"
              fontSize={11}
              fontFamily="var(--font-mono)"
              tickLine={false}
            />

            <YAxis
              domain={[0, 1]}
              ticks={[0, 0.25, 0.5, 0.75, 1.0]}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              stroke="#64748b"
              fontSize={11}
              fontFamily="var(--font-mono)"
              tickLine={false}
            />

            {/* Threshold Reference Lines (Phase 5) */}
            <ReferenceLine
              y={0.75}
              stroke="#f43f5e"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: 'HIGH (0.75)',
                position: 'insideTopRight',
                fill: '#f43f5e',
                fontSize: 10,
                fontFamily: 'monospace',
              }}
            />
            <ReferenceLine
              y={0.5}
              stroke="#f97316"
              strokeDasharray="3 3"
              strokeWidth={1}
              label={{
                value: 'ELEVATED (0.50)',
                position: 'insideTopRight',
                fill: '#f97316',
                fontSize: 10,
                fontFamily: 'monospace',
              }}
            />
            <ReferenceLine
              y={0.25}
              stroke="#f59e0b"
              strokeDasharray="2 2"
              strokeWidth={1}
              label={{
                value: 'GUARDED (0.25)',
                position: 'insideTopRight',
                fill: '#f59e0b',
                fontSize: 10,
                fontFamily: 'monospace',
              }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Line
              type="monotone"
              dataKey="riskScore"
              name="Composite Risk"
              stroke="#f43f5e"
              strokeWidth={2.5}
              dot={{ r: 2, fill: '#f43f5e' }}
              activeDot={{ r: 5, fill: '#f43f5e', stroke: '#fff', strokeWidth: 1.5 }}
              isAnimationActive={false}
            />

            <Line
              type="monotone"
              dataKey="anomalyScore"
              name="Anomaly Score"
              stroke="#f59e0b"
              strokeWidth={1.5}
              strokeDasharray="2 2"
              dot={{ r: 1.5, fill: '#f59e0b' }}
              activeDot={{ r: 4, fill: '#f59e0b' }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Footer Info */}
      <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-500 gap-2">
        <span>X-Axis: Chronological Replay Windows</span>
        <span>Y-Axis: Normalized Score (0.00–1.00)</span>
      </div>
    </div>
  );
};
