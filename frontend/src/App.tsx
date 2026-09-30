import { useState } from 'react';
import { Header } from './components/layout/Header';
import { DashboardPage } from './pages/DashboardPage';
import { FoundationPage } from './pages/FoundationPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { useSystemStatus } from './hooks/useSystemStatus';
import { useReplay } from './hooks/useReplay';

function App() {
  const [activeView, setActiveView] = useState<'dashboard' | 'foundation' | 'evaluation'>('dashboard');
  const { connectionState, isRefreshing, refresh } = useSystemStatus(10000);
  const replay = useReplay();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans soc-grid-bg selection:bg-cyan-500/30 selection:text-cyan-200">
      <Header
        connectionState={connectionState}
        replayStatus={replay.status}
        activeView={activeView}
        onViewChange={setActiveView}
        onRefresh={refresh}
        isRefreshing={isRefreshing}
      />

      <main className="flex-1 flex flex-col">
        {activeView === 'dashboard' ? (
          <DashboardPage />
        ) : activeView === 'evaluation' ? (
          <EvaluationPage />
        ) : (
          <FoundationPage showHeader={false} />
        )}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950/95 py-4 px-6 text-center text-xs font-mono text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl w-full mx-auto">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
          <span>SENTRANET SOC • SIH 2026 Problem SIH26153</span>
        </div>
        <div className="text-slate-400">
          From detecting attacks to forecasting them.
        </div>
        <div>
          Historical Replay Simulation Mode // Zero Falsified Metrics
        </div>
      </footer>
    </div>
  );
}

export default App;
