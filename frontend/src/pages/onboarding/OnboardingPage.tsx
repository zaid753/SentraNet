import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Shield, Database, Activity, CheckCircle2, ArrowRight } from 'lucide-react';

export const OnboardingPage: React.FC = () => {
  const [step, setStep] = useState(1);
  const [mode, setMode] = useState<'synthetic' | 'live' | null>(null);
  const { user, workspaceName, setOnboarded } = useAuth();
  const navigate = useNavigate();

  const handleComplete = () => {
    setOnboarded();
    navigate('/app');
  };

  return (
    <div className="min-h-screen bg-[#070B14] flex flex-col items-center py-20 px-4">
      <div className="w-full max-w-3xl">
        <div className="flex items-center gap-3 mb-12">
          <Shield className="w-8 h-8 text-blue-500" />
          <span className="font-bold tracking-widest text-xl text-white">SENTRANET</span>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-8 md:p-12 shadow-2xl">
          {step === 1 && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h1 className="text-3xl font-bold text-white mb-4">Welcome to {workspaceName}</h1>
              <p className="text-slate-400 text-lg mb-8">
                Hello, {user?.name}. Your workspace has been provisioned. SENTRANET is ready to analyze network traffic and forecast emerging threats.
              </p>
              <button 
                onClick={() => setStep(2)}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold transition-colors"
              >
                Configure Telemetry Source <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h2 className="text-2xl font-bold text-white mb-2">Select Telemetry Mode</h2>
              <p className="text-slate-400 mb-8">Choose how you want to ingest network flow data into the pipeline.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div 
                  onClick={() => setMode('synthetic')}
                  className={`p-6 rounded-xl border-2 cursor-pointer transition-all ${
                    mode === 'synthetic' 
                      ? 'border-blue-500 bg-blue-500/10' 
                      : 'border-slate-800 bg-slate-900 hover:border-slate-600'
                  }`}
                >
                  <div className="w-12 h-12 rounded-full bg-blue-900/30 flex items-center justify-center mb-4 text-blue-400">
                    <Database className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                    Synthetic Stream
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-500/20 text-blue-400">AVAILABLE</span>
                  </h3>
                  <p className="text-sm text-slate-400">
                    Run the evaluation pipeline using pre-computed historical datasets (e.g., CIC-IDS). Ideal for testing detection efficacy and explainability.
                  </p>
                </div>

                <div 
                  className="p-6 rounded-xl border-2 border-slate-800/50 bg-slate-900/50 opacity-60 cursor-not-allowed"
                >
                  <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-4 text-slate-500">
                    <Activity className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                    Live Telemetry
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-400">PHASE 4</span>
                  </h3>
                  <p className="text-sm text-slate-500">
                    Connect real-time network sensors via WebSockets or Kafka streams. This capability is planned for a future platform update.
                  </p>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <button 
                  onClick={() => setStep(1)}
                  className="px-6 py-3 text-slate-400 hover:text-white font-medium transition-colors"
                >
                  Back
                </button>
                <button 
                  onClick={() => setStep(3)}
                  disabled={!mode}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continue <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 text-center py-8">
              <div className="w-20 h-20 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto mb-6">
                <CheckCircle2 className="w-10 h-10" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Setup Complete</h2>
              <p className="text-slate-400 mb-8 max-w-md mx-auto">
                Your workspace is ready. You will now be redirected to the Security Operations Center.
              </p>
              <button 
                onClick={handleComplete}
                className="flex items-center gap-2 px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold transition-colors mx-auto"
              >
                Enter SOC <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
