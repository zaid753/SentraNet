import React from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { SOCLayout } from './components/layout/SOCLayout';
import { DashboardPage } from './pages/DashboardPage';
import { FoundationPage } from './pages/FoundationPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { RealtimeProvider } from './context/RealtimeContext';
import { InvestigationPage } from './pages/InvestigationPage';

export const SOCApp: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Extract a fake activeView based on URL for the sidebar highlight
  let activeView = 'dashboard';
  if (location.pathname.includes('/evaluation')) activeView = 'evaluation';
  if (location.pathname.includes('/foundation')) activeView = 'foundation';
  if (location.pathname.includes('/incidents')) activeView = 'incidents';

  return (
    <RealtimeProvider>
      <SOCLayout 
        activeView={activeView} 
        onViewChange={(v) => {
          if (v === 'evaluation') navigate('/app/evaluation');
          else if (v === 'foundation') navigate('/app/foundation');
          else if (v === 'incidents') navigate('/app'); // We don't have a standalone incidents list yet, use dashboard
          else navigate('/app');
        }}
      >
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/evaluation" element={<EvaluationPage />} />
          <Route path="/foundation" element={<FoundationPage showHeader={false} />} />
          <Route path="/incidents/:incidentId" element={<InvestigationPage />} />
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
      </SOCLayout>
    </RealtimeProvider>
  );
};
