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
import { SystemStatusBar } from '../components/dashboard/SystemStatusBar';
import { RiskHeroCard } from '../components/dashboard/RiskHeroCard';
import { ForecastCard } from '../components/dashboard/ForecastCard';
import { RiskTimelineChart } from '../components/charts/RiskTimelineChart';
import { AttackClassificationCard } from '../components/dashboard/AttackClassificationCard';
import { AnomalyCard } from '../components/dashboard/AnomalyCard';
import { ActiveIncidentCard } from '../components/dashboard/ActiveIncidentCard';
import { AttackTimeline } from '../components/dashboard/AttackTimeline';
import { ReplayControls } from '../components/replay/ReplayControls';
import { ReplayStatusCard } from '../components/replay/ReplayStatusCard';
import { AlertFeed } from '../components/alerts/AlertFeed';
import { IncidentTable } from '../components/incidents/IncidentTable';
import { IncidentDetailModal } from '../components/incidents/IncidentDetailModal';
import { ExplanationPanel } from '../components/explainability/ExplanationPanel';
import { DataSourceSelector } from '../components/telemetry/DataSourceSelector';
import { SyntheticStreamControls } from '../components/telemetry/SyntheticStreamControls';
import { useSyntheticStream } from '../hooks/useSyntheticStream';
import type { TelemetrySource } from '../types';

import { AlertTriangle, RefreshCw } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  // Data source mode
  const [activeDataSource, setActiveDataSource] = useState<TelemetrySource>('historical');

  // Global hooks
  const { systemStatus, connectionState, refresh: refreshSystem } = useSystemStatus(10000);
  const replay = useReplay();
  const synthetic = useSyntheticStream();

  // Active stream state (either historical replay or synthetic stream)
  const isStreamActive = activeDataSource === 'synthetic' ? synthetic.isRunning : replay.isRunning;
  const { risk, isLoading: isRiskLoading, refresh: refreshRisk } = useCurrentRisk(isStreamActive);
  const { points: timelinePoints, isLoading: isTimelineLoading, refresh: refreshTimeline } = useTimeline(isStreamActive, 50);
  const { alerts, currentAlert, isLoading: isAlertsLoading, refresh: refreshAlerts } = useAlerts(isStreamActive, 20);
  const { incidents, activeIncident, isLoading: isIncidentsLoading, refresh: refreshIncidents } = useIncidents(isStreamActive);

  // Notification toasts
  const { toasts, dismissToast } = useNotifications(alerts, risk);

  // Modal state
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);

  const handleRefreshAll = () => {
    refreshSystem();
    replay.refresh();
    synthetic.refresh();
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
        datasetName={activeDataSource === 'historical' ? replay.status?.dataset : synthetic.syntheticStatus?.profile}
      />

      {/* Telemetry Data Source Selector (Phase 9) */}
      <DataSourceSelector
        currentSource={activeDataSource}
        onSelectSource={(src) => setActiveDataSource(src)}
        isHistoricalRunning={replay.isRunning}
        isSyntheticRunning={synthetic.isRunning}
      />

      {/* 1. Top Status Bar */}
      <SystemStatusBar
        status={systemStatus}
        isLoading={connectionState === 'LOADING'}
      />

      {/* 2 & 5. Hero Risk Card & AI Forecast Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7">
          <RiskHeroCard risk={risk} isLoading={isRiskLoading} />
        </div>
        <div className="lg:col-span-5">
          <ForecastCard risk={risk} />
        </div>
      </div>

      {/* 4. Risk Timeline Time-series Chart */}
      <div>
        <RiskTimelineChart
          points={timelinePoints}
          isLoading={isTimelineLoading}
        />
      </div>

      {/* Phase 11: AI Decision Explainability */}
      <div>
        <ExplanationPanel />
      </div>

      {/* 6, 7, 8. Classification, Anomaly Detection, Active Incident */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <AttackClassificationCard risk={risk} />
        <AnomalyCard risk={risk} />
        <ActiveIncidentCard
          activeIncident={activeIncident}
          currentAlert={currentAlert}
          onViewDetails={(id) => setSelectedIncidentId(id)}
        />
      </div>

      {/* 11. Threat Evolution & Attack Vector Transitions */}
      <div>
        <AttackTimeline alerts={alerts} />
      </div>

      {/* 12 & 13. Telemetry Stream Controls (Historical Replay or Synthetic Stream) */}
      {activeDataSource === 'historical' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-8">
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
            />
          </div>
          <div className="lg:col-span-4">
            <ReplayStatusCard status={replay.status} />
          </div>
        </div>
      ) : (
        <div className="w-full">
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
        </div>
      )}

      {/* 9 & 10. Alert Feed & Incident Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5">
          <AlertFeed
            alerts={alerts}
            isLoading={isAlertsLoading}
            onSelectIncident={(id) => setSelectedIncidentId(id)}
          />
        </div>
        <div className="lg:col-span-7">
          <IncidentTable
            incidents={incidents}
            isLoading={isIncidentsLoading}
            onSelectIncident={(id) => setSelectedIncidentId(id)}
          />
        </div>
      </div>

      {/* Incident Detail Modal */}
      <IncidentDetailModal
        incidentId={selectedIncidentId}
        onClose={() => setSelectedIncidentId(null)}
      />

      {/* Real-time Notification Toasts */}
      <NotificationToastContainer
        toasts={toasts}
        onDismiss={dismissToast}
      />
    </div>
  );
};
