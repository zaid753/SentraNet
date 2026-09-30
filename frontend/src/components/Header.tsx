import React from 'react';
import { Header as LayoutHeader } from './layout/Header';
import type { ConnectionState, ReplayStatusResponse } from '../types';

interface HeaderProps {
  apiStatus?: string;
  connectionState?: ConnectionState;
  replayStatus?: ReplayStatusResponse | null;
  activeView?: 'dashboard' | 'foundation' | 'evaluation';
  onViewChange?: (view: 'dashboard' | 'foundation' | 'evaluation') => void;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  apiStatus,
  connectionState,
  replayStatus = null,
  activeView = 'dashboard',
  onViewChange = () => {},
  onRefresh,
  isRefreshing = false,
}) => {
  const normalizedState: ConnectionState =
    connectionState || (apiStatus === 'CONNECTED' ? 'CONNECTED' : apiStatus === 'LOADING' ? 'LOADING' : 'OFFLINE');

  return (
    <LayoutHeader
      connectionState={normalizedState}
      replayStatus={replayStatus}
      activeView={activeView}
      onViewChange={onViewChange}
      onRefresh={onRefresh}
      isRefreshing={isRefreshing}
    />
  );
};
