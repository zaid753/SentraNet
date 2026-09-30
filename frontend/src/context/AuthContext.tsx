import React, { createContext, useContext, useState, useEffect } from 'react';

type AuthState = 'loading' | 'authenticated' | 'unauthenticated' | 'demo';

interface AuthContextType {
  status: AuthState;
  user: any | null;
  workspaceName: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string, workspace: string) => Promise<void>;
  logout: () => void;
  setDemoMode: () => void;
  setOnboarded: () => void;
  isOnboarded: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [status, setStatus] = useState<AuthState>('unauthenticated');
  const [user, setUser] = useState<any | null>(null);
  const [workspaceName, setWorkspaceName] = useState<string | null>(null);
  const [isOnboarded, setIsOnboarded] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const isDemo = localStorage.getItem('sentranet_demo_auth');
    const onboarded = localStorage.getItem('sentranet_onboarded');
    
    if (isDemo === 'true') {
      setStatus('demo');
      setUser({ name: 'Demo User', email: 'demo@example.com' });
      setWorkspaceName(localStorage.getItem('sentranet_workspace') || 'Demo Workspace');
    }
    
    if (onboarded === 'true') {
      setIsOnboarded(true);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, _password: string) => {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        setStatus('demo');
        setUser({ name: 'Demo User', email });
        setWorkspaceName(localStorage.getItem('sentranet_workspace') || 'Demo Workspace');
        localStorage.setItem('sentranet_demo_auth', 'true');
        resolve();
      }, 800);
    });
  };

  const signup = async (name: string, email: string, _password: string, workspace: string) => {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        setStatus('demo');
        setUser({ name, email });
        setWorkspaceName(workspace);
        localStorage.setItem('sentranet_demo_auth', 'true');
        localStorage.setItem('sentranet_workspace', workspace);
        resolve();
      }, 800);
    });
  };

  const logout = () => {
    setStatus('unauthenticated');
    setUser(null);
    setWorkspaceName(null);
    setIsOnboarded(false);
    localStorage.removeItem('sentranet_demo_auth');
    localStorage.removeItem('sentranet_workspace');
    localStorage.removeItem('sentranet_onboarded');
  };

  const setDemoMode = () => {
    setStatus('demo');
    setUser({ name: 'Demo User', email: 'demo@example.com' });
    setWorkspaceName('Demo Workspace');
    localStorage.setItem('sentranet_demo_auth', 'true');
  };

  const setOnboarded = () => {
    setIsOnboarded(true);
    localStorage.setItem('sentranet_onboarded', 'true');
  };

  if (isLoading) {
    return null; // Or a loading spinner
  }

  return (
    <AuthContext.Provider value={{ status, user, workspaceName, login, signup, logout, setDemoMode, setOnboarded, isOnboarded }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
