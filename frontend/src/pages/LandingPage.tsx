import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Zap, Network, Lock, Cpu, Activity, AlertTriangle } from 'lucide-react';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 flex flex-col font-sans relative overflow-hidden selection:bg-cyan-500/30 selection:text-cyan-200">
      
      {/* Dynamic Animated Background Mesh */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-blue-900/20 blur-[150px] mix-blend-screen animate-pulse" style={{ animationDuration: '8s' }} />
        <div className="absolute bottom-[-20%] right-[-10%] w-[60vw] h-[60vw] rounded-full bg-cyan-900/20 blur-[150px] mix-blend-screen animate-pulse" style={{ animationDuration: '12s' }} />
        <div className="absolute top-[20%] right-[10%] w-[40vw] h-[40vw] rounded-full bg-indigo-900/10 blur-[120px] mix-blend-screen animate-pulse" style={{ animationDuration: '10s' }} />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAzNHYtNGgtMnY0aC00djJoNHY0aDJ2LTRoNHYtMmgtNHptMC0zMFYwaC0ydjRoLTR2Mmg0djRoMnYtNGg0VjRoLTR6bS0yMCAwdjRoMnYtNGg0VjJoLTRWMGgtMnYyaC00djJoNHptMCAzMHYtNGgydjRoNHYyaC00djRoLTJ2LTRoLTR2LTJoNHoiIGZpbGw9IiM5NDBhYTIiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPjwvZz48L3N2Zz4=')] opacity-50" />
      </div>

      {/* Navigation / Header */}
      <nav className="w-full relative z-20 flex items-center justify-between px-8 py-6 border-b border-white/5 bg-white/[0.02] backdrop-blur-md">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="SentraNet" className="w-8 h-8 object-contain drop-shadow-[0_0_10px_rgba(6,182,212,0.5)]" />
          <span className="font-bold text-xl tracking-wider text-white">SENTRANET</span>
        </div>
        <div className="hidden md:flex items-center gap-6">
          <a href="https://github.com/zaid753/SentraNet" target="_blank" rel="noreferrer" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Documentation</a>
          <a href="#" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Architecture</a>
          <button 
            onClick={() => navigate('/soc')}
            className="px-5 py-2 rounded-full bg-white/5 border border-white/10 text-white text-sm font-medium hover:bg-white/10 transition-all hover:scale-105 active:scale-95"
          >
            Launch Platform
          </button>
        </div>
      </nav>
      
      <div className="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 relative z-10 w-full max-w-7xl mx-auto pt-12 pb-24">
        
        {/* Main Hero */}
        <div className="text-center max-w-4xl flex flex-col items-center">
          <div className="group inline-flex items-center gap-3 px-4 py-2 rounded-full bg-cyan-950/30 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-10 backdrop-blur-md hover:bg-cyan-900/40 transition-all cursor-default shadow-[0_0_20px_rgba(6,182,212,0.15)]">
            <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)] animate-pulse" />
            <span className="tracking-wider">SIH26153 — BLOCKCHAIN & CYBERSECURITY</span>
          </div>

          <h1 className="text-6xl sm:text-7xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-200 to-slate-500 mb-6 drop-shadow-sm">
            SENTRANET
          </h1>
          
          <h2 className="text-xl sm:text-3xl md:text-4xl font-semibold mb-6 tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400">
            AI-Assisted Network Attack Forecasting
          </h2>

          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-12 font-light leading-relaxed">
            Move beyond reactive security. SentraNet analyzes live telemetry streams, predicts malicious intent before execution, and provides automated, deterministic early warnings.
          </p>

          <div className="flex flex-col sm:flex-row items-center gap-6">
            <button 
              onClick={() => navigate('/soc')}
              className="group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl font-semibold text-base tracking-wide transition-all overflow-hidden border border-cyan-400/50 shadow-[0_0_40px_rgba(8,145,178,0.3)] hover:shadow-[0_0_60px_rgba(8,145,178,0.5)] hover:-translate-y-1"
            >
              <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
              <span className="relative z-10 flex items-center gap-2">
                ENTER SOC DASHBOARD
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1.5 transition-transform" />
              </span>
            </button>
            <button className="px-8 py-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 text-white font-medium transition-all hover:-translate-y-1">
              Read Documentation
            </button>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-32 relative">
          <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-transparent blur-3xl -z-10" />
          
          <div className="group bg-slate-900/40 border border-white/10 hover:border-cyan-500/50 rounded-2xl p-8 backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_10px_40px_-10px_rgba(6,182,212,0.2)]">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-cyan-500/30 flex items-center justify-center mb-6 text-cyan-400 group-hover:scale-110 transition-transform">
              <Network className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Live Telemetry</h3>
            <p className="text-slate-400 leading-relaxed text-sm">
              Continuous ingestion of PCAP flows, computing the canonical 17-feature vector in real-time with ultra-low latency.
            </p>
          </div>

          <div className="group bg-slate-900/40 border border-white/10 hover:border-indigo-500/50 rounded-2xl p-8 backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_10px_40px_-10px_rgba(99,102,241,0.2)]">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center mb-6 text-indigo-400 group-hover:scale-110 transition-transform">
              <Zap className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Predictive Fusion</h3>
            <p className="text-slate-400 leading-relaxed text-sm">
              Mathematical risk fusion engines evaluate sequence-based anomalies, turning retrospective threats into proactive alerts.
            </p>
          </div>

          <div className="group bg-slate-900/40 border border-white/10 hover:border-emerald-500/50 rounded-2xl p-8 backdrop-blur-xl transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_10px_40px_-10px_rgba(16,185,129,0.2)]">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 flex items-center justify-center mb-6 text-emerald-400 group-hover:scale-110 transition-transform">
              <Lock className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Deterministic Defense</h3>
            <p className="text-slate-400 leading-relaxed text-sm">
              Zero black-box logic. Full explainability using SHAP metadata to provide SOC analysts with exact threat attribution.
            </p>
          </div>
        </div>

        {/* How It Works Pipeline */}
        <div className="w-full mt-32 mb-16">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-white mb-4">The Forecasting Pipeline</h3>
            <p className="text-slate-400 max-w-2xl mx-auto">A deterministic approach to threat modeling, transforming raw packets into actionable intelligence.</p>
          </div>
          
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 md:gap-8 max-w-5xl mx-auto relative">
            {/* Connecting Line (Desktop) */}
            <div className="hidden md:block absolute top-1/2 left-[10%] right-[10%] h-[2px] bg-gradient-to-r from-blue-500/20 via-cyan-500/20 to-indigo-500/20 -translate-y-1/2 z-0" />
            
            {[
              { icon: Activity, title: "1. Capture", desc: "Line-rate PCAP ingestion" },
              { icon: Cpu, title: "2. Extract", desc: "17 Canonical Features" },
              { icon: Zap, title: "3. Predict", desc: "Risk fusion matrices" },
              { icon: AlertTriangle, title: "4. Alert", desc: "Zero-day early warnings" }
            ].map((step, i) => (
              <div key={i} className="flex flex-col items-center text-center relative z-10 w-48 group">
                <div className="w-16 h-16 rounded-full bg-slate-900 border-2 border-slate-700 group-hover:border-cyan-500 flex items-center justify-center mb-4 transition-all duration-300 shadow-[0_0_15px_rgba(0,0,0,0.5)] group-hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] group-hover:-translate-y-1">
                  <step.icon className="w-7 h-7 text-slate-400 group-hover:text-cyan-400 transition-colors" />
                </div>
                <h4 className="text-lg font-bold text-white mb-1 group-hover:text-cyan-300 transition-colors">{step.title}</h4>
                <p className="text-xs text-slate-500 font-mono">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 w-full mt-24">
          {[
            { value: "17", label: "Canonical Features" },
            { value: "2.4K+", label: "CIC-IDS2017 Windows" },
            { value: "3.1M", label: "Historical Flows" },
            { value: "<50ms", label: "Inference Latency" }
          ].map((stat, i) => (
            <div key={i} className="flex flex-col items-center justify-center text-center p-6 border-t border-white/5 hover:border-cyan-500/30 transition-colors">
              <span className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-b from-white to-slate-500 mb-2">
                {stat.value}
              </span>
              <span className="text-xs font-mono text-slate-400 uppercase tracking-widest">{stat.label}</span>
            </div>
          ))}
        </div>
        
      </div>
      
      {/* Footer */}
      <div className="py-8 text-center text-xs font-mono text-slate-500 border-t border-white/5 relative z-10 bg-slate-950/50 backdrop-blur-md">
        <div className="flex items-center justify-center gap-4 mb-2">
          <img src="/logo.png" alt="SentraNet" className="w-4 h-4 opacity-50 grayscale" />
          <span>TEAM OUTLIERS // SIH26153</span>
        </div>
        <p className="opacity-60">© 2026 SENTRANET. All rights reserved.</p>
      </div>

    </div>
  );
};
