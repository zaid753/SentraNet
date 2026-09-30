import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

// Public pages
import { PublicLayout } from './components/public/PublicLayout';
import { LandingPage } from './pages/public/LandingPage';
import {
  FeaturesPage,
  HowItWorksPage,
  TechnologyPage,
  SecurityPage,
  DocsPage,
  DemoPage
} from './pages/public/PlaceholderPages';

// Auth & Onboarding
import { LoginPage } from './pages/auth/LoginPage';
import { SignupPage } from './pages/auth/SignupPage';
import { OnboardingPage } from './pages/onboarding/OnboardingPage';

// SOC App
import { SOCApp } from './SOCApp';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* PUBLIC ROUTES */}
          <Route element={<PublicLayout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/features" element={<FeaturesPage />} />
            <Route path="/how-it-works" element={<HowItWorksPage />} />
            <Route path="/technology" element={<TechnologyPage />} />
            <Route path="/security" element={<SecurityPage />} />
            <Route path="/docs" element={<DocsPage />} />
            <Route path="/demo" element={<DemoPage />} />
          </Route>

          {/* AUTH ROUTES */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          {/* PROTECTED ROUTES */}
          <Route element={<ProtectedRoute />}>
            <Route path="/onboarding" element={<OnboardingPage />} />
            {/* The SOCApp uses its own activeView state for Phase 2 compatibility.
                We mount it at /app and match any subroutes to it. */}
            <Route path="/app/*" element={<SOCApp />} />
          </Route>

          {/* FALLBACK */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
