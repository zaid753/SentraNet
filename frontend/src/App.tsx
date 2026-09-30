import { useState } from 'react';
import { SOCLayout } from './components/layout/SOCLayout';
import { DashboardPage } from './pages/DashboardPage';
import { FoundationPage } from './pages/FoundationPage';
import { EvaluationPage } from './pages/EvaluationPage';

function App() {
  const [activeView, setActiveView] = useState<'dashboard' | 'foundation' | 'evaluation'>('dashboard');

  return (
    <SOCLayout activeView={activeView} onViewChange={(v) => setActiveView(v as any)}>
      {activeView === 'dashboard' ? (
        <DashboardPage />
      ) : activeView === 'evaluation' ? (
        <EvaluationPage />
      ) : (
        <FoundationPage showHeader={false} />
      )}
    </SOCLayout>
  );
}

export default App;
