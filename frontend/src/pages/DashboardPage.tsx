import React, { useState } from 'react';
import { useSystemStatus } from '../hooks/useSystemStatus';
import { useReplay } from '../hooks/useReplay';
import { useCurrentRisk } from '../hooks/useCurrentRisk';
import { useTimeline } from '../hooks/useTimeline';
import { useAlerts } from '../hooks/useAlerts';
import { useIncidents } from '../hooks/useIncidents';
import { useNotifications } from '../hooks/useNotifications';

import { SimulationBanner } from '../components/common/SimulationBanner';
import { NotificationToastContainer } from '../components/common/NotificationToast';
import { IntelligenceRow } from '../components/dashboard/IntelligenceRow';
import { RiskHeroCard } from '../components/dashboard/RiskHeroCard';
import { RiskTimelineChart } from '../components/charts/RiskTimelineChart';
import { ActiveIncidentCard } from '../components/dashboard/ActiveIncidentCard';
import { ThreatEvolution } from '../components/dashboard/ThreatEvolution';
import { ReplayControls } from '../components/replay/ReplayControls';
import { AlertFeed } from '../components/alerts/AlertFeed';
import { IncidentTable } from '../components/incidents/IncidentTable';
import { ExplanationPanel } from '../components/explainability/ExplanationPanel';
import { DataSourceSelector } from '../components/telemetry/DataSourceSelector';
import { SyntheticStreamControls } from '../components/telemetry/SyntheticStreamControls';
import { LiveStreamControls } from '../components/telemetry/LiveStreamControls';
import { useSyntheticStream } from '../hooks/useSyntheticStream';
import { useLiveStream } from '../hooks/useLiveStream';
import type { TelemetrySource } from '../types';

import { AlertTriangle, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC<{ section?: string }> = ({ section }) => {
  const navigate = useNavigate();
  // Data source mode
  const [activeDataSource, setActiveDataSource] = useState<TelemetrySource>('historical');

  // Global hooks
  const { connectionState, refresh: refreshSystem } = useSystemStatus();
  const replay = useReplay();
  const synthetic = useSyntheticStream();
  const live = useLiveStream();

  // Active stream state (either historical replay or synthetic stream or live)
  const isStreamActive = activeDataSource === 'synthetic' 
    ? synthetic.isRunning 
    : activeDataSource === 'live'
    ? live.isRunning
    : replay.isRunning;
  const { risk, isLoading: isRiskLoading, refresh: refreshRisk } = useCurrentRisk(isStreamActive);
  const { points: timelinePoints, isLoading: isTimelineLoading, refresh: refreshTimeline } = useTimeline(isStreamActive, 50);
  const { alerts, currentAlert, isLoading: isAlertsLoading, refresh: refreshAlerts } = useAlerts(isStreamActive, 20);
  const { incidents, activeIncident, isLoading: isIncidentsLoading, refresh: refreshIncidents } = useIncidents(isStreamActive);

  // Notification toasts
  const { toasts, dismissToast } = useNotifications(alerts, risk);

  const handleRefreshAll = () => {
    refreshSystem();
    replay.refresh();
    synthetic.refresh();
    live.refresh();
    refreshRisk();
    refreshTimeline();
    refreshAlerts();
    refreshIncidents();
  };

  const isOffline = connectionState === 'OFFLINE' || connectionState === 'ERROR';

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 flex flex-col gap-6 font-sans">
      {/* Backend Offline Banner */}
      {isOffline && (
        <div
          role="alert"
          className="p-4 rounded-xl bg-rose-950/80 border border-rose-700/80 text-rose-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg font-mono text-xs"
        >
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
            <div>
              <span className="font-bold text-rose-300 mr-2">BACKEND OFFLINE //</span>
              <span>Unable to establish HTTP connection to SENTRANET API at http://127.0.0.1:8000.</span>
              <p className="text-[11px] text-rose-300/70 mt-0.5 font-sans">
                Please verify that the FastAPI backend server is running (`uvicorn backend.api.app:app --port 8000`).
              </p>
            </div>
          </div>

          <button
            onClick={handleRefreshAll}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-900/80 hover:bg-rose-800 text-white font-semibold self-start sm:self-auto cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry Connection</span>
          </button>
        </div>
      )}

      {/* Mandatory Simulation Disclosure Banner (Scientific Honesty) */}
      <SimulationBanner
        isRunning={isStreamActive}
        sourceType={activeDataSource}
      />

      {/* Telemetry Data Source Selector (Phase 9) */}
      <DataSourceSelector
        currentSource={activeDataSource}
        onSelectSource={(src) => setActiveDataSource(src)}
        isHistoricalRunning={replay.isRunning}
        isSyntheticRunning={synthetic.isRunning}
        isLiveRunning={live.isRunning}
      />

      {/* Section Conditional Rendering */}
      {(!section || section === 'dashboard') && (
        <>
          <RiskHeroCard risk={risk} isLoading={isRiskLoading} />
          <IntelligenceRow risk={risk} />
          <RiskTimelineChart points={timelinePoints} isLoading={isTimelineLoading} />
          <ThreatEvolution risk={risk} />
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4">
              <ActiveIncidentCard
                activeIncident={activeIncident}
                currentAlert={currentAlert}
                onViewDetails={(id) => navigate(`/soc/incidents/${id}`)}
              />
            </div>
            <div className="lg:col-span-8">
              <AlertFeed
                alerts={alerts}
                isLoading={isAlertsLoading}
                onSelectIncident={(id) => navigate(`/soc/incidents/${id}`)}
              />
            </div>
          </div>
          <ExplanationPanel />
        </>
      )}

      {section === 'telemetry' && (
        <div className="space-y-6">
          <div className="text-sm font-mono text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">Live Telemetry & Ingestion</div>
          {activeDataSource === 'historical' ? (
            <ReplayControls
              status={replay.status}
              isRunning={replay.isRunning}
              isPaused={replay.isPaused}
              isLoading={replay.isLoading}
              actionError={replay.actionError}
              onStart={replay.start}
              onStop={replay.stop}
              onPause={replay.pause}
              onResume={replay.resume}
              onStep={replay.step}
              onReset={replay.reset}
              currentAttackClass={risk?.attack_class}
            />
          ) : activeDataSource === 'synthetic' ? (
            <SyntheticStreamControls
              telemetryStatus={synthetic.telemetryStatus}
              syntheticStatus={synthetic.syntheticStatus}
              isRunning={synthetic.isRunning}
              isPaused={synthetic.isPaused}
              isLoading={synthetic.isLoading}
              actionError={synthetic.actionError}
              onStart={synthetic.start}
              onStop={synthetic.stop}
              onPause={synthetic.pause}
              onResume={synthetic.resume}
              onFlush={synthetic.flush}
              onReset={synthetic.reset}
            />
          ) : (
            <LiveStreamControls
              telemetryStatus={live.telemetryStatus}
              liveStatus={live.liveStatus}
              interfaces={live.interfaces}
              isRunning={live.isRunning}
              isLoading={live.isLoading}
              actionError={live.actionError}
              onStart={live.start}
              onStop={live.stop}
            />
          )}
        </div>
      )}

      {section === 'traffic' && (
        <div className="space-y-6">
          <div className="text-sm font-mono text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">Traffic Analysis</div>
          <RiskTimelineChart points={timelinePoints} isLoading={isTimelineLoading} />
          <IntelligenceRow risk={risk} />
        </div>
      )}

      {section === 'threats' && (
        <div className="space-y-6">
          <div className="text-sm font-mono text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">Threat Intelligence</div>
          <RiskHeroCard risk={risk} isLoading={isRiskLoading} />
          <ThreatEvolution risk={risk} />
        </div>
      )}

      {section === 'incidents' && (
        <div className="space-y-6">
          <div className="text-sm font-mono text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">Incident Management</div>
          <ActiveIncidentCard
            activeIncident={activeIncident}
            currentAlert={currentAlert}
            onViewDetails={(id) => navigate(`/soc/incidents/${id}`)}
          />
          <IncidentTable
            incidents={incidents}
            isLoading={isIncidentsLoading}
            onSelectIncident={(id) => navigate(`/soc/incidents/${id}`)}
          />
        </div>
      )}

      {section === 'alerts' && (
        <div className="space-y-6">
          <div className="text-sm font-mono text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">Alert Activity</div>
          <AlertFeed
            alerts={alerts}
            isLoading={isAlertsLoading}
            onSelectIncident={(id) => navigate(`/soc/incidents/${id}`)}
          />
        </div>
      )}

      {/* Functional Modules for Settings, Integrations, API */}
      {section === 'api' && (
        <div className="space-y-6 max-w-4xl">
          <div className="text-sm font-mono text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">API Documentation & Keys</div>
          
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/50">
            <h3 className="text-lg font-bold text-slate-200 mb-2">REST API Endpoints</h3>
            <p className="text-slate-400 text-sm mb-6">SENTRANET exposes a fully documented OpenAPI schema for programmatic access to telemetry and predictions.</p>
            
            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-center gap-4 p-3 rounded bg-slate-950 border border-slate-800">
                <span className="text-emerald-400 font-bold w-12">GET</span>
                <span className="text-slate-300 flex-1">/api/health</span>
                <span className="text-slate-500 hidden sm:block">System Status Check</span>
              </div>
              <div className="flex items-center gap-4 p-3 rounded bg-slate-950 border border-slate-800">
                <span className="text-emerald-400 font-bold w-12">GET</span>
                <span className="text-slate-300 flex-1">/api/risk/current</span>
                <span className="text-slate-500 hidden sm:block">Current Security Posture</span>
              </div>
              <div className="flex items-center gap-4 p-3 rounded bg-slate-950 border border-slate-800">
                <span className="text-emerald-400 font-bold w-12">GET</span>
                <span className="text-slate-300 flex-1">/api/alerts</span>
                <span className="text-slate-500 hidden sm:block">Retrieve active alerts</span>
              </div>
              <div className="flex items-center gap-4 p-3 rounded bg-slate-950 border border-slate-800">
                <span className="text-blue-400 font-bold w-12">POST</span>
                <span className="text-slate-300 flex-1">/api/telemetry/synthetic/start</span>
                <span className="text-slate-500 hidden sm:block">Trigger synthetic stream</span>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <a href="/docs" target="_blank" rel="noreferrer" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer">
                Open Swagger UI
              </a>
            </div>
          </div>
        </div>
      )}

      {section === 'integrations' && (
        <div className="space-y-6 max-w-4xl">
          <div className="text-sm font-mono text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">Third-Party Integrations</div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 flex flex-col">
              <div className="flex justify-between items-start mb-4">
                <div className="w-10 h-10 rounded bg-slate-800 flex items-center justify-center">
                  <div className="w-5 h-5 rounded bg-blue-500" />
                </div>
                <span className="px-2 py-1 rounded text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">CONNECTED</span>
              </div>
              <h3 className="text-base font-bold text-slate-200">Webhook Forwarder</h3>
              <p className="text-sm text-slate-400 mt-1 flex-1">Forward high-severity incidents to external HTTP endpoints.</p>
              <button className="mt-4 px-3 py-1.5 text-sm font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded transition-colors self-start cursor-pointer">Configure</button>
            </div>

            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 flex flex-col opacity-60">
              <div className="flex justify-between items-start mb-4">
                <div className="w-10 h-10 rounded bg-slate-800 flex items-center justify-center">
                  <div className="w-5 h-5 rounded bg-rose-500" />
                </div>
                <span className="px-2 py-1 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">DISCONNECTED</span>
              </div>
              <h3 className="text-base font-bold text-slate-200">Slack Notifications</h3>
              <p className="text-sm text-slate-400 mt-1 flex-1">Send alerts and daily summaries directly to a Slack channel.</p>
              <button className="mt-4 px-3 py-1.5 text-sm font-medium text-blue-400 border border-blue-900 hover:bg-blue-950/30 rounded transition-colors self-start cursor-pointer">Connect</button>
            </div>
            
            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 flex flex-col opacity-60">
              <div className="flex justify-between items-start mb-4">
                <div className="w-10 h-10 rounded bg-slate-800 flex items-center justify-center">
                  <div className="w-5 h-5 rounded bg-emerald-500" />
                </div>
                <span className="px-2 py-1 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">DISCONNECTED</span>
              </div>
              <h3 className="text-base font-bold text-slate-200">PagerDuty</h3>
              <p className="text-sm text-slate-400 mt-1 flex-1">Trigger incident response workflows automatically.</p>
              <button className="mt-4 px-3 py-1.5 text-sm font-medium text-blue-400 border border-blue-900 hover:bg-blue-950/30 rounded transition-colors self-start cursor-pointer">Connect</button>
            </div>
          </div>
        </div>
      )}

      {section === 'settings' && (
        <div className="space-y-6 max-w-3xl">
          <div className="text-sm font-mono text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">Platform Settings</div>
          
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/50 space-y-6">
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-slate-200 font-medium">Data Retention Policy</h4>
                <p className="text-sm text-slate-400">How long to store incident logs and telemetry evidence.</p>
              </div>
              <select className="bg-slate-950 border border-slate-700 text-slate-300 rounded px-3 py-1.5 text-sm outline-none focus:border-blue-500 cursor-pointer">
                <option>7 Days</option>
                <option>30 Days</option>
                <option>90 Days</option>
                <option>Forever</option>
              </select>
            </div>

            <div className="h-px bg-slate-800 w-full" />

            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-slate-200 font-medium">Strict Anomaly Threshold</h4>
                <p className="text-sm text-slate-400">Require multiple high-risk signals before emitting alerts.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="h-px bg-slate-800 w-full" />

            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-slate-200 font-medium">Automatic Model Updates</h4>
                <p className="text-sm text-slate-400">Download the latest validated Sentinel models periodically.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

          </div>
        </div>
      )}

      {/* Dashboard only elements at bottom */}
      {(!section || section === 'dashboard') && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-6">
          <div className="lg:col-span-6">
            {activeDataSource === 'historical' ? (
              <ReplayControls
                status={replay.status}
                isRunning={replay.isRunning}
                isPaused={replay.isPaused}
                isLoading={replay.isLoading}
                actionError={replay.actionError}
                onStart={replay.start}
                onStop={replay.stop}
                onPause={replay.pause}
                onResume={replay.resume}
                onStep={replay.step}
                onReset={replay.reset}
                currentAttackClass={risk?.attack_class}
              />
            ) : activeDataSource === 'synthetic' ? (
              <SyntheticStreamControls
                telemetryStatus={synthetic.telemetryStatus}
                syntheticStatus={synthetic.syntheticStatus}
                isRunning={synthetic.isRunning}
                isPaused={synthetic.isPaused}
                isLoading={synthetic.isLoading}
                actionError={synthetic.actionError}
                onStart={synthetic.start}
                onStop={synthetic.stop}
                onPause={synthetic.pause}
                onResume={synthetic.resume}
                onFlush={synthetic.flush}
                onReset={synthetic.reset}
              />
            ) : (
              <LiveStreamControls
                telemetryStatus={live.telemetryStatus}
                liveStatus={live.liveStatus}
                interfaces={live.interfaces}
                isRunning={live.isRunning}
                isLoading={live.isLoading}
                actionError={live.actionError}
                onStart={live.start}
                onStop={live.stop}
              />
            )}
          </div>
          <div className="lg:col-span-6">
            <IncidentTable
              incidents={incidents}
              isLoading={isIncidentsLoading}
              onSelectIncident={(id) => navigate(`/soc/incidents/${id}`)}
            />
          </div>
        </div>
      )}

      {/* Real-time Notification Toasts */}
      <NotificationToastContainer
        toasts={toasts}
        onDismiss={dismissToast}
      />
    </div>
  );
};
