import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Shield, Lock, Mail, ArrowRight, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await login(email, password);
    setLoading(false);
    navigate('/app');
  };

  return (
    <div className="min-h-screen bg-[#070B14] flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans">
      <div className="sm:mx-auto sm:w-full sm:max-w-md flex flex-col items-center">
        <Link to="/" className="flex items-center gap-3 mb-8">
          <Shield className="w-8 h-8 text-blue-500" />
          <span className="font-bold tracking-widest text-xl text-white">SENTRANET</span>
        </Link>
        <h2 className="text-center text-2xl font-bold tracking-tight text-white">
          Sign in to your SOC
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-[var(--color-surface)] py-8 px-4 shadow-2xl sm:rounded-xl sm:px-10 border border-[var(--color-border)]">
          <div className="mb-6 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
            <p className="text-sm text-blue-200">
              <strong>Demo Mode Active:</strong> Authentication backend not configured. Any credentials will grant access to the simulation.
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium text-slate-300">Email address</label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-slate-700 rounded-md leading-5 bg-slate-900 text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors"
                  placeholder="operator@sentranet.local"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300">Password</label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-slate-700 rounded-md leading-5 bg-slate-900 text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="text-sm">
                <a href="#" className="font-medium text-blue-400 hover:text-blue-300">
                  Forgot password?
                </a>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-bold text-white bg-blue-600 hover:bg-blue-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Authenticating...' : 'Sign In'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-700" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-[var(--color-surface)] text-slate-500">
                  New to SentraNet?
                </span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                to="/signup"
                className="w-full flex justify-center items-center gap-2 py-2.5 px-4 border border-slate-700 rounded-md shadow-sm text-sm font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 transition-colors"
              >
                Create workspace <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
