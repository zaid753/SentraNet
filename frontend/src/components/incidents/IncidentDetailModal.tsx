import React, { useState, useEffect } from 'react';
import type { IncidentDetailResponse } from '../../types';
import type { IncidentExplanation } from '../../types/explainability';
import { getIncident } from '../../services/api';
import { explainabilityApi } from '../../services/explainabilityApi';
import {
  formatRiskScore,
  formatAttackClass,
  formatSeverity,
  getSeverityConfig,
  formatDateTime,
} from '../../utils/formatters';
import { X, ShieldAlert, Zap, Clock, Activity, AlertTriangle, List, Info, ChevronRight } from 'lucide-react';
import { LoadingSkeleton } from '../common/LoadingSkeleton';

interface IncidentDetailModalProps {
  incidentId: string | null;
  onClose: () => void;
}

type TabKey = 'OVERVIEW' | 'EVIDENCE' | 'RISK' | 'FORECAST' | 'TIMELINE';

export const IncidentDetailModal: React.FC<IncidentDetailModalProps> = ({
  incidentId,
  onClose,
}) => {
  const [incident, setIncident] = useState<IncidentDetailResponse | null>(null);
  const [explanation, setExplanation] = useState<IncidentExplanation | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('OVERVIEW');

  useEffect(() => {
    if (!incidentId) return;

    let mounted = true;
    setIsLoading(true);
    setError(null);
    setActiveTab('OVERVIEW'); // reset

    Promise.all([
      getIncident(incidentId),
      explainabilityApi.getIncidentExplanation(incidentId).catch(err => {
        console.warn('Failed to load explanation for incident:', err);
        return null;
      })
    ])
      .then(([incData, explData]) => {
        if (mounted) {
          setIncident(incData);
          setExplanation(explData);
        }
      })
      .catch((err) => {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to load incident details');
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [incidentId]);

  if (!incidentId) return null;

  const sevConfig = getSeverityConfig(incident?.severity);

  const tabs: { key: TabKey; label: string; icon: React.ReactNode }[] = [
    { key: 'OVERVIEW', label: 'Overview', icon: <Info className="w-3.5 h-3.5" /> },
    { key: 'EVIDENCE', label: 'Evidence', icon: <ShieldAlert className="w-3.5 h-3.5" /> },
    { key: 'RISK', label: 'Risk', icon: <Activity className="w-3.5 h-3.5" /> },
    { key: 'FORECAST', label: 'Forecast', icon: <Zap className="w-3.5 h-3.5" /> },
    { key: 'TIMELINE', label: 'Timeline', icon: <List className="w-3.5 h-3.5" /> },
  ];

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="incident-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm"
    >
      <div className="bg-slate-950 border border-slate-700 rounded-xl max-w-3xl w-full flex flex-col shadow-2xl relative h-[85vh] font-mono text-xs overflow-hidden">
        {/* Modal Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors z-10"
          aria-label="Close incident details"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 p-6 pb-4 border-b border-slate-800 shrink-0">
          <div className="p-2 rounded-lg bg-rose-950/80 border border-rose-800/80 text-rose-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 id="incident-modal-title" className="text-lg font-bold text-white tracking-wide">
                {incidentId}
              </h2>
              {incident && (
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${sevConfig.badgeBg} ${sevConfig.badgeBorder} ${sevConfig.text}`}
                >
                  {formatSeverity(incident.severity)}
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Correlated Security Incident Dossier & Explainability
            </p>
          </div>
        </div>

        {/* Modal Body */}
        {isLoading ? (
          <div className="p-8">
            <LoadingSkeleton lines={6} />
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-400">
            <p>{error}</p>
          </div>
        ) : incident ? (
          <div className="flex flex-col flex-1 overflow-hidden">
            {/* Tabs Navigation */}
            <div className="flex px-6 border-b border-slate-800 shrink-0 overflow-x-auto">
              {tabs.map((t) => (
                <button
                  key={t.key}
                  onClick={() => setActiveTab(t.key)}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 font-bold transition-colors ${
                    activeTab === t.key
                      ? 'border-cyan-400 text-cyan-400'
                      : 'border-transparent text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {t.icon}
                  {t.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              
              {activeTab === 'OVERVIEW' && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  {explanation && (
                    <div className="p-4 rounded-lg bg-blue-950/20 border border-blue-900/40 text-blue-200">
                      <h3 className="font-bold text-blue-400 flex items-center gap-2 mb-2">
                        <Info className="w-4 h-4" /> AI Summary
                      </h3>
                      <p className="leading-relaxed">{explanation.explanation_summary}</p>
                    </div>
                  )}

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">Status</span>
                      <span className="text-white font-bold uppercase">{incident.status}</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">Attack Vector</span>
                      <span className="text-white font-bold">{formatAttackClass(incident.attack_class)}</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">Peak Threat Risk</span>
                      <span className="text-rose-400 font-bold">{formatRiskScore(incident.peak_risk_score)}</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">Max Anomaly</span>
                      <span className="text-amber-400 font-bold">{formatRiskScore(incident.max_anomaly_score)}</span>
                    </div>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                    <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5 pb-1 border-b border-slate-800">
                      <Clock className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Incident Lifecycle</span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 text-[11px]">
                      <div>
                        <span className="text-slate-500 block">Created</span>
                        <span className="text-slate-200">{formatDateTime(incident.created_at)}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">Duration</span>
                        <span className="text-slate-200">{explanation?.duration || 'Unknown'}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">Resolved</span>
                        <span className="text-slate-200">
                          {incident.resolution_timestamp ? formatDateTime(incident.resolution_timestamp) : '— (Active)'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'EVIDENCE' && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <h3 className="text-sm font-bold text-slate-300 border-b border-slate-800 pb-2">Telemetry Evidence</h3>
                  <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800">
                    <div className="flex justify-between pb-2 mb-2 border-b border-slate-800">
                      <span className="text-slate-400">Total Analyzed Windows</span>
                      <span className="text-cyan-400 font-bold">{incident.event_count}</span>
                    </div>
                    <div className="flex justify-between pb-2 mb-2 border-b border-slate-800">
                      <span className="text-slate-400">Alerts Emitted</span>
                      <span className="text-amber-400 font-bold">{explanation?.alert_count || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Attack Classes Detected</span>
                      <span className="text-rose-400 font-bold">
                        {explanation?.attack_classes_observed?.join(', ') || formatAttackClass(incident.attack_class)}
                      </span>
                    </div>
                  </div>
                  {/* Detailed evidence could be added here in the future from full explanation data */}
                  <div className="text-slate-500 p-4 text-center border border-dashed border-slate-800 rounded-lg">
                    Full feature extraction evidence is available in the real-time panel during active windows.
                  </div>
                </div>
              )}

              {activeTab === 'RISK' && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <h3 className="text-sm font-bold text-slate-300 border-b border-slate-800 pb-2">Risk Trajectory</h3>
                  
                  {explanation && (
                    <div className="p-4 rounded-lg bg-amber-950/20 border border-amber-900/40 text-amber-200 mb-4">
                      <p>{explanation.risk_trajectory_summary}</p>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-lg bg-slate-900 border border-slate-800 text-center">
                      <span className="text-slate-500 text-[10px] uppercase block mb-1">First Detected Risk</span>
                      <span className="text-white font-bold text-lg">{formatRiskScore(incident.first_risk_score)}</span>
                    </div>
                    <div className="p-4 rounded-lg bg-slate-900 border border-slate-800 text-center">
                      <span className="text-slate-500 text-[10px] uppercase block mb-1">Peak Trajectory Risk</span>
                      <span className="text-rose-400 font-bold text-lg">{formatRiskScore(incident.peak_risk_score)}</span>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'FORECAST' && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <h3 className="text-sm font-bold text-slate-300 border-b border-slate-800 pb-2">Emergence Forecast</h3>
                  
                  {incident.forecast_triggered ? (
                    <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
                      <div className="flex items-center gap-3 mb-4 text-amber-500">
                        <AlertTriangle className="w-5 h-5" />
                        <span className="font-bold">Emergence Engine Triggered</span>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-slate-500 text-[10px] block">Estimated Time to Impact</span>
                          <span className="text-white font-bold">
                            {incident.estimated_eta_seconds !== null 
                              ? `${incident.estimated_eta_seconds} seconds` 
                              : 'Unknown'}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 text-[10px] block">Model Confidence</span>
                          <span className="text-cyan-400 font-bold">{formatRiskScore(incident.confidence)}</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-6 text-center rounded-lg border border-slate-800 text-slate-500">
                      No forecast triggered during this incident. Risk velocity remained below emergence thresholds.
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'TIMELINE' && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <h3 className="text-sm font-bold text-slate-300 border-b border-slate-800 pb-2">Event Timeline</h3>
                  
                  {explanation?.timeline && explanation.timeline.length > 0 ? (
                    <div className="relative border-l border-slate-700 ml-3 space-y-6">
                      {explanation.timeline.map((event, idx) => (
                        <div key={idx} className="relative pl-6">
                          <div className="absolute -left-1.5 top-1 w-3 h-3 rounded-full bg-slate-800 border-2 border-cyan-500"></div>
                          <div className="flex flex-col gap-1">
                            <div className="text-cyan-400 font-bold">{formatDateTime(event.timestamp)}</div>
                            <div className="bg-slate-900 border border-slate-800 rounded p-3 text-slate-300">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-bold text-white text-[10px] uppercase bg-slate-800 px-1.5 py-0.5 rounded">
                                  {event.event_type}
                                </span>
                                <span className="text-rose-400">Risk: {event.risk.toFixed(2)}</span>
                                <span className="text-amber-400">Anomaly: {event.anomaly.toFixed(2)}</span>
                              </div>
                              <p className="text-slate-400 mt-2 flex items-start gap-2">
                                <ChevronRight className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                                {event.explanation}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-slate-500 p-4 text-center border border-slate-800 rounded-lg">
                      No detailed alert timeline available for this incident.
                    </div>
                  )}
                </div>
              )}

            </div>
          </div>
        ) : null}

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 flex justify-end shrink-0 bg-slate-950">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors cursor-pointer"
          >
            Close Dossier
          </button>
        </div>
      </div>
    </div>
  );
};
