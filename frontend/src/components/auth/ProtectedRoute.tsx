import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const ProtectedRoute: React.FC = () => {
  const { status, isOnboarded } = useAuth();
  const location = useLocation();

  if (status === 'unauthenticated') {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Enforce onboarding unless the user is explicitly on the onboarding route
  if (!isOnboarded && !location.pathname.startsWith('/onboarding')) {
    return <Navigate to="/onboarding" replace />;
  }

  // Prevent users from accessing onboarding after they are already onboarded
  if (isOnboarded && location.pathname.startsWith('/onboarding')) {
    return <Navigate to="/app" replace />;
  }

  return <Outlet />;
};
