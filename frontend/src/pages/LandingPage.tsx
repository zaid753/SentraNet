import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, Activity, Database, Server, ArrowRight } from 'lucide-react';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#050B14] text-slate-200 flex flex-col font-sans relative overflow-hidden">
      {/* Background ambient light */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none" />
      
      <div className="flex-1 flex flex-col items-center justify-center p-6 relative z-10">
        
        {/* Main Hero */}
        <div className="text-center max-w-4xl flex flex-col items-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-950/40 border border-blue-800/60 text-blue-300 text-xs font-mono mb-8">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
            SIH26153 - BLOCKCHAIN & CYBERSECURITY
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6">
            SENTRANET
          </h1>
          
          <h2 className="text-xl md:text-3xl text-cyan-400 font-medium mb-4 tracking-wide uppercase">
            AI-Assisted Network Attack<br/>Forecasting & Early Warning
          </h2>

          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-12 font-light">
            "From detecting attacks to forecasting them."
          </p>

          <button 
            onClick={() => navigate('/soc')}
            className="group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg font-mono text-sm tracking-widest uppercase transition-all overflow-hidden border border-cyan-400/50 shadow-[0_0_20px_rgba(8,145,178,0.4)]"
          >
            <span className="relative z-10 flex items-center gap-2">
              OPEN SOC
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </span>
          </button>
        </div>

        {/* Pipeline Steps */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8 mt-24 mb-16 w-full max-w-4xl text-center">
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-slate-400">
              <Activity className="w-5 h-5" />
            </div>
            <span className="font-mono text-sm tracking-widest text-slate-300 uppercase">Detect</span>
          </div>
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-slate-400">
              <Database className="w-5 h-5" />
            </div>
            <span className="font-mono text-sm tracking-widest text-slate-300 uppercase">Understand</span>
          </div>
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-blue-900/50 border border-blue-700 flex items-center justify-center text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.2)]">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <span className="font-mono text-sm tracking-widest text-blue-300 uppercase">Forecast</span>
          </div>
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-slate-400">
              <Server className="w-5 h-5" />
            </div>
            <span className="font-mono text-sm tracking-widest text-slate-300 uppercase">Respond</span>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-5xl">
          <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 flex flex-col items-center justify-center text-center backdrop-blur-sm">
            <span className="text-3xl font-bold text-white mb-2">17</span>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Canonical Features</span>
          </div>
          <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 flex flex-col items-center justify-center text-center backdrop-blur-sm">
            <span className="text-3xl font-bold text-white mb-2">2,454</span>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">CIC-IDS2017 Windows</span>
          </div>
          <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 flex flex-col items-center justify-center text-center backdrop-blur-sm">
            <span className="text-3xl font-bold text-white mb-2">~3.1M</span>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Historical Flows</span>
          </div>
          <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 flex flex-col items-center justify-center text-center backdrop-blur-sm">
            <span className="text-3xl font-bold text-white mb-2">236</span>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Backend Tests</span>
          </div>
        </div>
      </div>
      
      <div className="py-6 text-center text-xs font-mono text-slate-600 border-t border-slate-900/50 relative z-10">
        TEAM OUTLIERS // SIH26153
      </div>
    </div>
  );
};
