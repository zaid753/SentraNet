import React, { createContext, useContext, useState, useEffect } from 'react';

type AuthState = 'loading' | 'authenticated' | 'unauthenticated';

interface AuthContextType {
  status: AuthState;
  user: any | null;
  workspaceName: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string, workspace: string) => Promise<void>;
  logout: () => void;
  setOnboarded: () => void;
  isOnboarded: boolean;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [status, setStatus] = useState<AuthState>('loading');
  const [user, setUser] = useState<any | null>(null);
  const [workspaceName, setWorkspaceName] = useState<string | null>(null);
  const [isOnboarded, setIsOnboarded] = useState<boolean>(false);

  const getToken = () => localStorage.getItem('sentranet_token');

  const fetchUser = async (token: string) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) throw new Error('Session expired');
      const data = await response.json();
      setUser({ name: data.name, email: data.email, id: data.id });
      setWorkspaceName(data.workspace_name);
      setIsOnboarded(data.onboarded);
      setStatus('authenticated');
    } catch (err) {
      console.warn("Auth check failed:", err);
      logout();
    }
  };

  useEffect(() => {
    const token = getToken();
    if (token) {
      fetchUser(token);
    } else {
      setStatus('unauthenticated');
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || data.detail || 'Login failed');
    
    localStorage.setItem('sentranet_token', data.access_token);
    await fetchUser(data.access_token);
  };

  const signup = async (name: string, email: string, password: string, workspace: string) => {
    const response = await fetch('http://127.0.0.1:8000/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, workspace_name: workspace })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || data.detail || 'Signup failed');
    
    localStorage.setItem('sentranet_token', data.access_token);
    await fetchUser(data.access_token);
  };

  const logout = () => {
    setStatus('unauthenticated');
    setUser(null);
    setWorkspaceName(null);
    setIsOnboarded(false);
    localStorage.removeItem('sentranet_token');
  };

  const setOnboarded = () => {
    setIsOnboarded(true);
    // In a full implementation, we might update the backend user record here.
    // For Phase 6, we treat signup as onboarded, but keep local API consistent.
  };

  if (status === 'loading') {
    return <div className="h-screen w-screen flex items-center justify-center bg-slate-950 text-cyan-400 font-mono text-sm">LOADING IDENTITY...</div>;
  }

  return (
    <AuthContext.Provider value={{ status, user, workspaceName, login, signup, logout, setOnboarded, isOnboarded, getToken }}>
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
