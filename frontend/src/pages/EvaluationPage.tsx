import { useState, useEffect, useCallback } from 'react';
import { FlaskConical, CheckCircle2, XCircle, AlertTriangle, RefreshCw, Clock, Cpu, Target, TrendingUp, ShieldCheck, BarChart3, Database } from 'lucide-react';
import type { EvaluationSummary, EvaluationDatasetResult } from '../types';
import { getEvaluationSummary, getDatasetEvaluation } from '../services/api';

const DATASET_KEYS = ['forecast_scenario', 'sample', 'cicids2017', 'unsw_nb15', 'cic_ddos2019'] as const;
type DatasetKey = typeof DATASET_KEYS[number];

const DATASET_META: Record<DatasetKey, { label: string; shortLabel: string; category: string; color: string }> = {
  forecast_scenario: {
    label: 'Forecastable Synthetic Escalation',
    shortLabel: 'FORECAST-VAL',
    category: 'Category B',
    color: 'emerald',
  },
  sample: {
    label: 'Synthetic Development Fixture',
    shortLabel: 'SAMPLE',
    category: 'Category B',
    color: 'amber',
  },
  cicids2017: {
    label: 'CICIDS2017',
    shortLabel: 'CICIDS17',
    category: 'Category A',
    color: 'cyan',
  },
  unsw_nb15: {
    label: 'UNSW-NB15',
    shortLabel: 'UNSW-NB15',
    category: 'Category A',
    color: 'cyan',
  },
  cic_ddos2019: {
    label: 'CIC-DDoS2019',
    shortLabel: 'DDoS2019',
    category: 'Category A',
    color: 'cyan',
  },
};


function fmt(v: number | null | undefined, decimals = 4): string {
  if (v == null) return 'N/A';
  return v.toFixed(decimals);
}

// ──────────────────────────────────────────────
// Metric card
// ──────────────────────────────────────────────
function MetricCard({
  label,
  value,
  sub,
  highlight = false,
}: {
  label: string;
  value: string;
  sub?: string;
  highlight?: boolean;
}) {
  return (
    <div className={`rounded-lg border p-3 ${highlight ? 'border-cyan-700/60 bg-cyan-950/30' : 'border-slate-800 bg-slate-900/60'}`}>
      <div className="text-[10px] font-mono uppercase tracking-widest text-slate-500 mb-1">{label}</div>
      <div className={`text-lg font-mono font-bold ${highlight ? 'text-cyan-300' : 'text-slate-100'}`}>{value}</div>
      {sub && <div className="text-[10px] text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

// ──────────────────────────────────────────────
// Dataset evaluation panel
// ──────────────────────────────────────────────
function DatasetPanel({ result }: { result: EvaluationDatasetResult }) {
  const isComplete = result.status === 'COMPLETED';
  const isNA = result.status === 'NOT_AVAILABLE';
  const isNotEvaluated = result.status === 'NOT_EVALUATED';

  const clf = result.classification;
  const perf = result.performance;
  const anomaly = result.anomaly_detection;
  const risk = result.risk_fusion;
  const forecast = result.forecasting;

  const stateBreakdown =
    (risk?.risk_state_counts as Record<string, number> | undefined) ||
    (risk?.state_breakdown as Record<string, number> | undefined) ||
    {};

  const detectionRate =
    anomaly?.attack_detection_rate ?? anomaly?.detection_rate;

  const latency =
    (perf?.latency_ms_mean as number | null | undefined) ??
    (perf?.mean_latency_ms as number | null | undefined);

  const throughput = perf?.throughput_windows_per_second as number | null | undefined;

  return (
    <div className="space-y-4">
      {/* Status banner */}
      {isNA && (
        <div className="flex items-start gap-3 p-4 rounded-lg border border-slate-700/50 bg-slate-900/40">
          <XCircle className="w-5 h-5 text-rose-400 mt-0.5 shrink-0" />
          <div>
            <div className="font-mono font-semibold text-rose-300 text-sm">NOT AVAILABLE — Raw Benchmark Files Missing</div>
            <div className="text-xs text-slate-400 mt-1">
              {result.message || `Dataset '${result.dataset_id}' raw files are not locally available.`}
            </div>
            {Boolean(result.download_instructions) && (
              <div className="text-xs text-slate-500 mt-2 font-mono border-t border-slate-800 pt-2">
                {String(result.download_instructions ?? '')}
              </div>
            )}
          </div>
        </div>
      )}
      {result.dataset_id === 'forecast_scenario' && isComplete && (
        <div className="flex items-start gap-3 p-4 rounded-lg border border-purple-700/40 bg-purple-950/20 mb-4">
          <AlertTriangle className="w-5 h-5 text-purple-400 mt-0.5 shrink-0" />
          <div>
            <div className="font-mono font-bold text-purple-300 text-sm tracking-wider">
              SYNTHETIC VALIDATION // NOT REAL NETWORK TRAFFIC
            </div>
            <div className="text-xs text-purple-400/80 mt-1">
              This scenario is explicitly designed to evaluate the multi-horizon temporal forecasting pipeline under controlled, deterministic conditions. It contains artificial, gradual precursors to validate the AI engine's lead-time calculation and no-future-leakage guarantees.
            </div>
          </div>
        </div>
      )}
      {isNotEvaluated && (
        <div className="flex items-start gap-3 p-4 rounded-lg border border-amber-700/30 bg-amber-950/20">
          <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5 shrink-0" />
          <div>
            <div className="font-mono font-semibold text-amber-300 text-sm">NOT EVALUATED</div>
            <div className="text-xs text-slate-400 mt-1">{result.message}</div>
          </div>
        </div>
      )}

      {isComplete && (
        <>
          {/* Mode badge */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-700/40 text-emerald-300 uppercase tracking-wider">
              {result.evaluation_mode?.includes('QUICK') ? '⚡ Quick Mode' : '✓ Full Evaluation'}
            </span>
            <span className="text-[10px] font-mono text-slate-500">
              {result.windows_evaluated} windows evaluated
            </span>
          </div>

          {/* Classification */}
          {clf && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-3.5 h-3.5 text-cyan-400" />
                <span className="text-xs font-mono uppercase tracking-widest text-slate-400">XGBoost Classifier (Frozen)</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <MetricCard label="Accuracy" value={fmt(clf.accuracy)} highlight />
                <MetricCard label="Macro F1" value={fmt(clf.macro_f1)} highlight />
                <MetricCard label="Weighted F1" value={fmt(clf.weighted_f1)} />
                <MetricCard label="Macro PR-AUC" value={fmt(clf.macro_pr_auc)} />
              </div>
            </div>
          )}

          {/* Anomaly Detection */}
          {anomaly && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <ShieldCheck className="w-3.5 h-3.5 text-violet-400" />
                <span className="text-xs font-mono uppercase tracking-widest text-slate-400">Isolation Forest (Frozen)</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <MetricCard label="Detection Rate" value={fmt(detectionRate)} />
                <MetricCard label="Benign FPR" value={fmt(anomaly.benign_anomaly_fpr)} />
              </div>
            </div>
          )}

          {/* Risk Fusion */}
          {risk && Object.keys(stateBreakdown).length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-3.5 h-3.5 text-orange-400" />
                <span className="text-xs font-mono uppercase tracking-widest text-slate-400">Dual-Engine Risk Fusion</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(stateBreakdown).map(([state, count]) => (
                  <div key={state} className="flex items-center gap-1.5 text-xs font-mono px-2.5 py-1.5 rounded border border-slate-800 bg-slate-900/60">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      state === 'HIGH' ? 'bg-rose-400' :
                      state === 'ELEVATED' ? 'bg-amber-400' :
                      state === 'MODERATE' ? 'bg-yellow-400' :
                      'bg-emerald-400'
                    }`} />
                    <span className="text-slate-400">{state}:</span>
                    <span className="text-slate-200 font-bold">{count}</span>
                  </div>
                ))}
                {risk.attack_high_rate != null && (
                  <MetricCard label="Attack→HIGH Rate" value={fmt(risk.attack_high_rate as number)} />
                )}
              </div>
            </div>
          )}

          {/* Forecasting */}
          {forecast && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-xs font-mono uppercase tracking-widest text-slate-400">Temporal Forecasting</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <MetricCard label="Attack Onsets" value={String(forecast.attack_onsets_count)} />
                <MetricCard label="Early Forecasts" value={String(forecast.early_forecast_count ?? 0)} highlight />
                <MetricCard label="Onset Forecasts" value={String(forecast.onset_forecast_count ?? 0)} />
                <MetricCard label="Post-Onset" value={String(forecast.post_onset_forecast_count ?? 0)} />
                <MetricCard label="False Forecasts" value={String(forecast.false_forecast_count ?? 0)} />
                <MetricCard label="Mean Lead Time" value={forecast.mean_lead_time_seconds != null ? `${forecast.mean_lead_time_seconds.toFixed(1)}s` : 'N/A'} highlight />
                <MetricCard label="1m Horizon F1" value={fmt(forecast.horizon_1m_f1)} />
                <MetricCard label="5m Horizon F1" value={fmt(forecast.horizon_5m_f1)} />
              </div>
            </div>
          )}

          {/* Performance */}
          {perf && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Cpu className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-xs font-mono uppercase tracking-widest text-slate-400">Inference Latency</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <MetricCard label="Mean Latency" value={latency != null ? `${latency.toFixed(2)} ms` : 'N/A'} />
                <MetricCard label="P95 Latency" value={(perf?.latency_ms_p95 as number | null) != null ? `${(perf?.latency_ms_p95 as number).toFixed(2)} ms` : 'N/A'} />
                <MetricCard label="Throughput" value={throughput != null ? `${throughput.toFixed(1)} win/s` : 'N/A'} />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────
// Main EvaluationPage
// ──────────────────────────────────────────────
export function EvaluationPage() {
  const [summary, setSummary] = useState<EvaluationSummary | null>(null);
  const [selected, setSelected] = useState<DatasetKey>('sample');
  const [datasetResult, setDatasetResult] = useState<EvaluationDatasetResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [dsLoading, setDsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getEvaluationSummary();
      setSummary(data);
    } catch (e) {
      setError('Unable to reach evaluation API. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDataset = useCallback(async (key: DatasetKey) => {
    setDsLoading(true);
    try {
      const data = await getDatasetEvaluation(key);
      setDatasetResult(data);
    } catch {
      setDatasetResult(null);
    } finally {
      setDsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  useEffect(() => {
    fetchDataset(selected);
  }, [selected, fetchDataset]);

  const datasets = summary?.datasets ?? {};

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      {/* ── Header banner */}
      <div className="rounded-xl border border-amber-700/40 bg-amber-950/20 p-4 flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-amber-950/60 border border-amber-700/50 flex items-center justify-center shrink-0">
          <FlaskConical className="w-5 h-5 text-amber-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-base font-mono font-bold text-amber-200 tracking-wide">
              BENCHMARK EVALUATION — Frozen Models
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/80 border border-amber-700/40 text-amber-400 uppercase">
              Phase 10
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-700/40 text-slate-400 uppercase">
              Zero Retraining
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed max-w-3xl">
            Out-of-sample evaluation of the frozen SENTRANET AI Core (XGBoost + Isolation Forest + Risk Fusion) against benchmark datasets.
            <strong className="text-amber-300 ml-1">Category A real benchmarks require external download.</strong>
            {' '}Category B Synthetic Fixture (sample) reflects development-environment performance only.
          </p>
        </div>
        <button
          onClick={fetchSummary}
          disabled={loading}
          className="shrink-0 flex items-center gap-1.5 text-xs font-mono px-3 py-1.5 rounded border border-slate-700 bg-slate-900 text-slate-400 hover:text-white hover:border-slate-600 transition-all cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          Refresh
        </button>
      </div>

      {/* ── Error */}
      {error && (
        <div className="flex items-center gap-3 p-4 rounded-lg border border-rose-700/40 bg-rose-950/20 text-sm text-rose-300 font-mono">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* ── Cross-dataset summary row */}
      {summary && (
        <div>
          <div className="text-[10px] font-mono uppercase tracking-widest text-slate-500 mb-2">
            Dataset Availability Overview
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {DATASET_KEYS.map((key) => {
              const meta = DATASET_META[key];
              const ds = datasets[key];
              const status = ds?.status ?? 'NOT_EVALUATED';
              const isAvail = status === 'COMPLETED';
              const isNA = status === 'NOT_AVAILABLE';

              return (
                <button
                  key={key}
                  id={`eval-dataset-${key}`}
                  onClick={() => setSelected(key)}
                  className={`text-left rounded-xl border p-3 transition-all cursor-pointer group ${
                    selected === key
                      ? 'border-cyan-700/70 bg-cyan-950/30 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
                      : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-1 mb-2">
                    <div className="flex items-center gap-1.5">
                      {isAvail ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      ) : isNA ? (
                        <XCircle className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                      ) : (
                        <Clock className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                      )}
                      <span className="text-[10px] font-mono text-slate-500">{meta.category}</span>
                    </div>
                    <Database className={`w-3 h-3 shrink-0 ${selected === key ? 'text-cyan-400' : 'text-slate-700 group-hover:text-slate-500'}`} />
                  </div>
                  <div className={`text-sm font-mono font-bold ${selected === key ? 'text-cyan-200' : 'text-slate-300'}`}>
                    {meta.shortLabel}
                  </div>
                  <div className={`text-[10px] font-mono mt-1 ${
                    isAvail ? 'text-emerald-400' :
                    isNA ? 'text-slate-600' :
                    'text-slate-500'
                  }`}>
                    {isAvail ? (
                      `F1: ${ds?.macro_f1 != null ? (ds.macro_f1 as number).toFixed(4) : (ds?.classification?.macro_f1 != null ? (ds.classification.macro_f1 as number).toFixed(4) : '—')}`
                    ) : isNA ? 'NOT AVAILABLE' : 'NOT EVALUATED'}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Per-dataset detail */}
      <div className="rounded-xl border border-slate-800 bg-slate-950/60 divide-y divide-slate-800/60">
        {/* Header row */}
        <div className="flex items-center justify-between px-5 py-3">
          <div className="flex items-center gap-3">
            <span className="text-sm font-mono font-bold text-slate-200">
              {DATASET_META[selected].label}
            </span>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase tracking-wider ${
              selected === 'sample'
                ? 'bg-amber-950/60 border border-amber-700/40 text-amber-400'
                : 'bg-cyan-950/40 border border-cyan-800/40 text-cyan-400'
            }`}>
              {DATASET_META[selected].category}
            </span>
          </div>
          {dsLoading && (
            <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
          )}
        </div>

        {/* Content */}
        <div className="px-5 py-4">
          {!datasetResult && !dsLoading && (
            <div className="text-sm text-slate-500 font-mono text-center py-8">
              No evaluation data available for this dataset.
            </div>
          )}
          {dsLoading && (
            <div className="text-sm text-slate-500 font-mono text-center py-8 flex items-center justify-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin" />
              Loading evaluation results…
            </div>
          )}
          {datasetResult && !dsLoading && (
            <DatasetPanel result={datasetResult} />
          )}
        </div>
      </div>

      {/* ── Scientific integrity footer */}
      {summary?.caution && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-[10px] font-mono text-slate-500 leading-relaxed">
          <span className="text-slate-400 font-semibold">⚠ Scientific Note: </span>
          {summary.caution}
        </div>
      )}
    </div>
  );
}
