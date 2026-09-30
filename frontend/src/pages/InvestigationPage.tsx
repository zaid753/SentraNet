import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { IncidentDetailResponse } from '../types';
import type { IncidentExplanation } from '../types/explainability';
import { getIncident } from '../services/api';
import { explainabilityApi } from '../services/explainabilityApi';
import {
  formatRiskScore,
  formatAttackClass,
  formatSeverity,
  getSeverityConfig,
  formatDateTime,
} from '../utils/formatters';
import { 
  ShieldAlert, 
  Zap, 
  Clock, 
  Activity, 
  List, 
  Info, 
  ChevronRight, 
  ArrowLeft,
  AlertTriangle
} from 'lucide-react';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { useRealtime } from '../context/RealtimeContext';

export const InvestigationPage: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>();
  const navigate = useNavigate();
  
  const [incident, setIncident] = useState<IncidentDetailResponse | null>(null);
  const [explanation, setExplanation] = useState<IncidentExplanation | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { subscribe } = useRealtime();

  const fetchIncidentDetails = async () => {
    if (!incidentId) return;
    try {
      const [incData, explData] = await Promise.all([
        getIncident(incidentId),
        explainabilityApi.getIncidentExplanation(incidentId).catch(err => {
          console.warn('Failed to load explanation for incident:', err);
          return null;
        })
      ]);
      setIncident(incData);
      setExplanation(explData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load incident details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidentDetails();
  }, [incidentId]);

  // Realtime updates for this incident
  useEffect(() => {
    const handleUpdate = (payload: any) => {
      // Refresh incident if a related event occurred
      if (!payload.alert || !payload.alert.incident_id || payload.alert.incident_id === incidentId) {
          fetchIncidentDetails();
      }
    };

    const unsubAlertCreated = subscribe('alert.created', handleUpdate);
    const unsubAlertUpdated = subscribe('alert.updated', handleUpdate);
    const unsubIncidentResolved = subscribe('incident.resolved', handleUpdate);
    const unsubRiskUpdated = subscribe('risk.updated', handleUpdate);
    const unsubForecastUpdated = subscribe('forecast.updated', handleUpdate);
    const unsubIncidentUpdated = subscribe('incident.updated', handleUpdate);

    return () => {
      unsubAlertCreated();
      unsubAlertUpdated();
      unsubIncidentResolved();
      unsubRiskUpdated();
      unsubForecastUpdated();
      unsubIncidentUpdated();
    };
  }, [incidentId, subscribe]);

  if (isLoading) {
    return (
      <div className="flex-1 p-6">
        <LoadingSkeleton lines={10} />
      </div>
    );
  }

  if (error || !incident) {
    return (
      <div className="flex-1 p-6 flex flex-col items-center justify-center text-rose-400">
        <AlertTriangle className="w-12 h-12 mb-4" />
        <h2 className="text-xl font-bold mb-2">Investigation Unavailable</h2>
        <p className="text-sm font-mono">{error || 'Incident not found'}</p>
        <button 
          onClick={() => navigate('/app')}
          className="mt-6 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-white text-sm font-bold flex items-center gap-2 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Dashboard
        </button>
      </div>
    );
  }

  const sevConfig = getSeverityConfig(incident.severity);

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 flex flex-col gap-6 font-sans">
      
      {/* Investigation Navigation */}
      <div className="flex items-center gap-4 text-sm font-mono text-slate-400">
        <button 
          onClick={() => navigate('/app')}
          className="hover:text-white transition-colors flex items-center gap-1 cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" /> SOC Dashboard
        </button>
        <span className="text-slate-600">/</span>
        <span className="text-slate-200 font-bold">Investigation: {incident.incident_id}</span>
      </div>

      {/* Top Command Area */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 p-6 rounded-xl bg-slate-900 border border-slate-800 relative overflow-hidden shadow-lg">
        <div className={`absolute top-0 left-0 w-1 h-full ${sevConfig.badgeBg.replace('/60', '')}`} />
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-white tracking-wide">{incident.incident_id}</h1>
            <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold border uppercase ${sevConfig.badgeBg} ${sevConfig.badgeBorder} ${sevConfig.text}`}>
              {formatSeverity(incident.severity)}
            </span>
            <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase border ${incident.status === 'RESOLVED' ? 'bg-emerald-950/50 border-emerald-800/50 text-emerald-400' : 'bg-rose-950/50 border-rose-800/50 text-rose-400'}`}>
              {incident.status}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5 text-cyan-400" /> Opened: {formatDateTime(incident.created_at)}</span>
            <span className="flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5 text-rose-400" /> Class: {formatAttackClass(incident.attack_class)}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            disabled
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-400 text-sm font-bold cursor-not-allowed opacity-70"
            title="Resolution via API not currently supported"
          >
            Resolve Incident
          </button>
        </div>
      </div>

      {/* Investigation Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Context & Evidence */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          
          {/* Incident Summary */}
          <div className="soc-panel rounded-xl p-5 border border-slate-800 shadow-md">
             <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200 mb-4 flex items-center gap-2">
                <Info className="w-4 h-4 text-cyan-400" /> AI Investigation Summary
             </h3>
             {explanation ? (
               <p className="text-sm leading-relaxed text-slate-300 font-sans">{explanation.explanation_summary}</p>
             ) : (
               <p className="text-sm text-slate-500 italic">No AI explanation available for this incident.</p>
             )}
          </div>

          {/* Risk Timeline & Evidence */}
          <div className="soc-panel rounded-xl p-5 border border-slate-800 shadow-md">
            <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200 mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4 text-rose-400" /> Risk Evolution & Timeline
            </h3>
            
            <div className="grid grid-cols-3 gap-3 mb-6">
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 text-[10px] block font-mono uppercase tracking-wider">Current Risk</span>
                <span className="text-white font-bold font-mono text-lg">{formatRiskScore(incident.current_risk_score)}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 text-[10px] block font-mono uppercase tracking-wider">Peak Risk</span>
                <span className="text-rose-400 font-bold font-mono text-lg">{formatRiskScore(incident.peak_risk_score)}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 text-[10px] block font-mono uppercase tracking-wider">Max Anomaly</span>
                <span className="text-amber-400 font-bold font-mono text-lg">{formatRiskScore(incident.max_anomaly_score)}</span>
              </div>
            </div>

            {explanation?.timeline && explanation.timeline.length > 0 ? (
              <div className="relative border-l border-slate-700 ml-3 space-y-6">
                {explanation.timeline.map((event, idx) => (
                  <div key={idx} className="relative pl-6 group">
                    <div className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-slate-900 border-2 border-cyan-500 transition-transform group-hover:scale-125"></div>
                    <div className="flex flex-col gap-1.5">
                      <div className="text-cyan-400 font-bold text-xs font-mono">{formatDateTime(event.timestamp)}</div>
                      <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4 text-slate-300 shadow-inner">
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
                          <span className="font-bold text-white text-[10px] uppercase font-mono bg-slate-800 px-2 py-0.5 rounded">
                            {event.event_type}
                          </span>
                          <span className="text-rose-400 text-xs font-mono">Risk: {event.risk.toFixed(2)}</span>
                          <span className="text-amber-400 text-xs font-mono">Anomaly: {event.anomaly.toFixed(2)}</span>
                        </div>
                        <p className="text-sm text-slate-400 font-sans flex items-start gap-2 leading-relaxed">
                          <ChevronRight className="w-4 h-4 shrink-0 mt-0.5 text-slate-500" />
                          {event.explanation}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-slate-500 text-sm p-6 text-center border border-dashed border-slate-800 rounded-lg">
                Historical timeline depth is limited by the current in-memory runtime state.
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Forecast & Threat Evolution */}
        <div className="flex flex-col gap-6">
          
          {/* Forecast Context */}
          <div className="soc-panel rounded-xl p-5 border border-slate-800 shadow-md">
            <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200 mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" /> Forecast Context
            </h3>
            
            {incident.forecast_triggered ? (
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30">
                  <div className="flex items-center gap-2 mb-2 text-amber-500">
                    <AlertTriangle className="w-4 h-4" />
                    <span className="font-bold text-sm">Emergence Forecast Triggered</span>
                  </div>
                  <p className="text-xs text-amber-200/70 leading-relaxed font-sans">
                    SENTRANET detected heuristic emergence patterns indicating a potential impending attack state.
                  </p>
                </div>
                
                <div className="grid grid-cols-1 gap-3">
                  <div className="flex justify-between items-center p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono">
                    <span className="text-slate-500 text-xs">Estimated ETA</span>
                    <span className="text-white font-bold text-sm">
                      {incident.estimated_eta_seconds !== null ? `${incident.estimated_eta_seconds}s` : 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono">
                    <span className="text-slate-500 text-xs">Model Confidence</span>
                    <span className="text-cyan-400 font-bold text-sm">{formatRiskScore(incident.confidence)}</span>
                  </div>
                </div>
                <div className="text-[10px] text-slate-500 font-mono text-center pt-2">
                  * ETA and confidence are heuristic estimates.
                </div>
              </div>
            ) : (
              <div className="p-6 text-center rounded-lg border border-slate-800 text-slate-500 text-sm">
                No forecast triggered. Risk velocity remained below emergence thresholds.
              </div>
            )}
          </div>

          {/* Model Signals / Evidence */}
          <div className="soc-panel rounded-xl p-5 border border-slate-800 shadow-md">
            <h3 className="text-xs font-semibold tracking-wider font-mono uppercase text-slate-200 mb-4 flex items-center gap-2">
              <List className="w-4 h-4 text-purple-400" /> Model Signals
            </h3>
            
            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between items-center pb-2 border-b border-slate-800">
                <span className="text-slate-400">Analyzed Windows</span>
                <span className="text-white font-bold">{incident.event_count}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-slate-800">
                <span className="text-slate-400">Attack Classes</span>
                <span className="text-rose-400 font-bold text-right ml-4">
                  {explanation?.attack_classes_observed?.join(', ') || formatAttackClass(incident.attack_class)}
                </span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-slate-800">
                <span className="text-slate-400">Total Alerts</span>
                <span className="text-amber-400 font-bold">{explanation?.alert_count ?? '—'}</span>
              </div>
              
              {explanation?.risk_trajectory_summary && (
                <div className="pt-2 text-slate-400 leading-relaxed font-sans text-xs">
                  {explanation.risk_trajectory_summary}
                </div>
              )}
            </div>
            
            <div className="mt-4 p-3 bg-slate-900/50 rounded border border-slate-800 text-[10px] text-slate-500 font-mono italic leading-relaxed">
              Note: Feature importance indicates model contribution, not causal attribution. SHAP explanations are not currently implemented.
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
