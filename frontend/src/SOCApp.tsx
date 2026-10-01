import React from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { SOCLayout } from './components/layout/SOCLayout';
import { DashboardPage } from './pages/DashboardPage';
import { FoundationPage } from './pages/FoundationPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { RealtimeProvider } from './context/RealtimeContext';
import { InvestigationPage } from './pages/InvestigationPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SystemHealthPage } from './pages/SystemHealthPage';

export const SOCApp: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  let activeView = 'dashboard';
  if (location.pathname.includes('/evaluation')) activeView = 'evaluation';
  if (location.pathname.includes('/foundation')) activeView = 'foundation';
  if (location.pathname.includes('/incidents')) activeView = 'incidents';
  if (location.pathname.includes('/analytics')) activeView = 'analytics';
  if (location.pathname.includes('/system')) activeView = 'health';

  return (
    <RealtimeProvider>
      <SOCLayout 
        activeView={activeView} 
        onViewChange={(v) => {
          if (v === 'evaluation') navigate('/app/evaluation');
          else if (v === 'architecture' || v === 'foundation') navigate('/app/foundation');
          else if (v === 'incidents') navigate('/app'); // We don't have a standalone incidents list yet, use dashboard
          else if (v === 'analytics') navigate('/app/analytics');
          else if (v === 'health') navigate('/app/system');
          else navigate('/app');
        }}
      >
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/evaluation" element={<EvaluationPage />} />
          <Route path="/foundation" element={<FoundationPage showHeader={false} />} />
          <Route path="/incidents/:incidentId" element={<InvestigationPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/system" element={<SystemHealthPage />} />
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
      </SOCLayout>
    </RealtimeProvider>
  );
};
