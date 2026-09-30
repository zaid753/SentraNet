import React, { createContext, useContext } from 'react';
import { useRealtimeEvents, type UseRealtimeEventsReturn } from '../hooks/useRealtimeEvents';

const RealtimeContext = createContext<UseRealtimeEventsReturn | null>(null);

export const RealtimeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Use relative URL that Vite/proxy will route correctly, or an absolute one if in prod
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = import.meta.env.DEV ? `ws://localhost:8000/ws/events` : `${protocol}//${window.location.host}/ws/events`;
  
  const realtime = useRealtimeEvents(wsUrl);

  return (
    <RealtimeContext.Provider value={realtime}>
      {children}
    </RealtimeContext.Provider>
  );
};

export const useRealtime = () => {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider');
  }
  return context;
};
