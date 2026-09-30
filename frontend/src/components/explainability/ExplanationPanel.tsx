import React, { useState, useEffect } from 'react';
import type { ExplanationResponse } from '../../types/explainability';
import { explainabilityApi } from '../../services/explainabilityApi';
import { RiskBreakdownCard } from './RiskBreakdownCard';
import { TopSignalsCard } from './TopSignalsCard';
import { ForecastEvidenceCard } from './ForecastEvidenceCard';
import { Loader2, RefreshCw, Info } from 'lucide-react';
import { useRealtime } from '../../context/RealtimeContext';

export const ExplanationPanel: React.FC = () => {
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchExplanation = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await explainabilityApi.getCurrentExplanation();
      setExplanation(data);
    } catch (err: any) {
      if (err.statusCode === 404 || err.message?.includes('404')) {
        setError('No telemetry data available for explanation.');
      } else {
        setError(err.message || 'Failed to fetch explanation.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExplanation();
    const interval = setInterval(fetchExplanation, 60000); // Slower fallback interval (1m)
    return () => clearInterval(interval);
  }, []);

  const { subscribe } = useRealtime();

  useEffect(() => {
    // Whenever risk updates, explanations also update
    const unsub = subscribe('risk.updated', () => {
        fetchExplanation();
    });
    return () => unsub();
  }, [subscribe]);

  if (loading && !explanation) {
    return (
      <div className="soc-panel rounded-xl p-8 flex items-center justify-center h-64 border border-dashed border-slate-700">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
      </div>
    );
  }

  if (error && !explanation) {
    return (
      <div className="soc-panel rounded-xl p-8 flex flex-col items-center justify-center gap-4 h-64 border border-dashed border-slate-700 text-slate-500">
        <Info className="w-8 h-8 opacity-50" />
        <p className="text-sm font-mono">{error}</p>
        <button 
          onClick={fetchExplanation}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-mono text-xs transition-colors"
        >
          <RefreshCw className="w-3 h-3" /> Retry
        </button>
      </div>
    );
  }

  if (!explanation) return null;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-end border-b border-slate-800 pb-2">
        <div>
          <h2 className="text-sm font-bold tracking-widest text-slate-300 font-mono uppercase">AI Decision Explainability</h2>
          <p className="text-[10px] text-slate-500 font-mono mt-1">Live breakdown of model inference and predictive emergence</p>
        </div>
        <div className="text-[10px] text-slate-500 font-mono bg-slate-900 px-2 py-1 rounded border border-slate-800">
          <span className="text-cyan-500 font-bold mr-1">WINDOW:</span>
          {explanation.window_id} ({explanation.data_source})
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
        <RiskBreakdownCard risk={explanation.risk} />
        <ForecastEvidenceCard forecast={explanation.forecast} />
        <TopSignalsCard features={explanation.top_features} />
      </div>
    </div>
  );
};
