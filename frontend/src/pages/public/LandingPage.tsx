import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Target, ArrowRight, Activity, Server } from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* SECTION 1 - HERO */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/10 to-[#070B14] z-0" />
        <div className="container mx-auto px-4 relative z-10 text-center max-w-4xl">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 font-mono text-xs mb-8">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            SYNTHETIC STREAM // SIMULATION
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6">
            From detecting attacks to <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">forecasting them.</span>
          </h1>
          <p className="text-lg md:text-xl text-[var(--color-text-secondary)] mb-10 max-w-2xl mx-auto leading-relaxed">
            SENTRANET is an AI-driven network security intelligence platform designed to detect anomalous traffic behavior, understand emerging threats, and forecast attack progression.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup" className="w-full sm:w-auto px-8 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold transition-colors flex items-center justify-center gap-2">
              Open SOC <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/how-it-works" className="w-full sm:w-auto px-8 py-3 rounded-lg bg-[var(--color-elevated)] hover:bg-slate-800 text-white font-bold border border-[var(--color-border)] transition-colors text-center">
              Explore how it works
            </Link>
          </div>
        </div>
      </section>

      {/* SECTION 2 - PRODUCT VALUE */}
      <section className="py-24 bg-[#0A0F1C] border-y border-[var(--color-border)]">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="flex flex-col">
              <div className="w-12 h-12 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-6">
                <Target className="w-6 h-6 text-emerald-400" />
              </div>
              <h3 className="text-lg font-bold text-white mb-3">DETECT</h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                Identify suspicious network behavior using isolation forest anomaly detection and XGBoost classification on flow-level metadata.
              </p>
            </div>
            <div className="flex flex-col">
              <div className="w-12 h-12 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-6">
                <SearchIcon className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-lg font-bold text-white mb-3">UNDERSTAND</h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                Surface the signals contributing to risk. Model-native explainability highlights which canonical features drive inferences.
              </p>
            </div>
            <div className="flex flex-col">
              <div className="w-12 h-12 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-6">
                <Activity className="w-6 h-6 text-violet-400" />
              </div>
              <h3 className="text-lg font-bold text-white mb-3">FORECAST</h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                Track temporal changes and emerging attack states across rolling 60-second windows to predict trajectory.
              </p>
            </div>
            <div className="flex flex-col">
              <div className="w-12 h-12 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-6">
                <Shield className="w-6 h-6 text-rose-400" />
              </div>
              <h3 className="text-lg font-bold text-white mb-3">RESPOND</h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                Organize alerts and incidents for investigation. The active incident manager deduplicates noise for rapid response.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 3 - HOW SENTRANET WORKS */}
      <section className="py-24">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <h2 className="text-3xl font-bold text-white mb-16">The Intelligence Pipeline</h2>
          
          <div className="flex flex-col items-center max-w-xl mx-auto font-mono text-sm">
            <div className="w-full bg-[var(--color-elevated)] border border-[var(--color-border)] py-4 rounded-lg text-slate-300">Network Flow Metadata</div>
            <ArrowDown />
            <div className="w-full bg-[var(--color-elevated)] border border-[var(--color-border)] py-4 rounded-lg text-slate-300">60s Feature Windows</div>
            <ArrowDown />
            <div className="w-full flex gap-4">
              <div className="flex-1 bg-blue-900/20 border border-blue-500/30 py-4 rounded-lg text-blue-300">XGBoost Classification</div>
              <div className="flex-1 bg-emerald-900/20 border border-emerald-500/30 py-4 rounded-lg text-emerald-300">Isolation Forest Anomaly</div>
            </div>
            <ArrowDown />
            <div className="w-full bg-violet-900/20 border border-violet-500/30 py-4 rounded-lg text-violet-300">Risk Fusion</div>
            <ArrowDown />
            <div className="w-full bg-[var(--color-elevated)] border border-[var(--color-border)] py-4 rounded-lg text-slate-300">Temporal Forecasting</div>
            <ArrowDown />
            <div className="w-full bg-rose-900/20 border border-rose-500/30 py-4 rounded-lg text-rose-300">Alerts / Incidents</div>
            <ArrowDown />
            <div className="w-full bg-slate-800 border border-slate-700 py-4 rounded-lg text-white font-bold tracking-widest">SOC INVESTIGATION</div>
          </div>
        </div>
      </section>

      {/* SECTION 4 - THREAT INTELLIGENCE */}
      <section className="py-24 bg-[#0A0F1C] border-y border-[var(--color-border)]">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl font-bold text-white mb-6">Unified Threat Intelligence</h2>
              <p className="text-[var(--color-text-secondary)] mb-6 leading-relaxed">
                SENTRANET combines heuristic forecasting with deep machine learning. By fusing an XGBoost multi-class classifier with an Isolation Forest anomaly detector, the engine generates a highly robust composite risk score.
              </p>
              <ul className="space-y-4">
                {[
                  'Classification of DDoS, Port Scanning, and Botnets',
                  'Unsupervised anomaly detection for zero-day behaviors',
                  'Temporal behavior tracking across time windows',
                  'Model-native explainability via feature gain',
                  'State-machine driven incident management'
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <div className="mt-1 w-4 h-4 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                    </div>
                    <span className="text-slate-300">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 shadow-2xl relative">
               <div className="absolute top-0 right-0 p-4 opacity-50">
                 <Shield className="w-32 h-32 text-[var(--color-border)]" />
               </div>
               <div className="relative z-10 space-y-6 font-mono text-sm">
                 <div className="border-b border-[var(--color-border)] pb-2 flex justify-between">
                   <span className="text-slate-500">ENGINE STATE</span>
                   <span className="text-emerald-400">OPERATIONAL</span>
                 </div>
                 <div className="border-b border-[var(--color-border)] pb-2 flex justify-between">
                   <span className="text-slate-500">RISK FUSION</span>
                   <span className="text-blue-400">ENABLED</span>
                 </div>
                 <div className="border-b border-[var(--color-border)] pb-2 flex justify-between">
                   <span className="text-slate-500">CANONICAL FEATURES</span>
                   <span className="text-slate-300">17</span>
                 </div>
                 <div className="border-b border-[var(--color-border)] pb-2 flex justify-between">
                   <span className="text-slate-500">WINDOW SIZE</span>
                   <span className="text-slate-300">60 SECONDS</span>
                 </div>
               </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 6 - SCIENTIFIC HONESTY */}
      <section className="py-24 border-b border-[var(--color-border)]">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-800 border border-slate-700 mb-6">
            <Server className="w-5 h-5 text-slate-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-6">Scientific Transparency</h2>
          <p className="text-[var(--color-text-secondary)] leading-relaxed max-w-2xl mx-auto mb-8">
            SENTRANET is built for demonstration and evaluation of the SIH26153 problem statement. The current system operates exclusively on flow-level network metadata via a synthetic stream simulation engine. Heuristic forecasting and model-native explainability are utilized without fabricating performance metrics. Real benchmark datasets are currently simulated.
          </p>
        </div>
      </section>

      {/* SECTION 7 - FINAL CTA */}
      <section className="py-32 relative overflow-hidden text-center">
        <div className="absolute inset-0 bg-gradient-to-t from-blue-900/10 to-transparent z-0" />
        <div className="container mx-auto px-4 relative z-10">
          <h2 className="text-4xl font-bold text-white mb-8">Ready to analyze network behavior?</h2>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup" className="px-8 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold transition-colors">
              Launch SENTRANET
            </Link>
            <Link to="/docs" className="px-8 py-3 rounded-lg bg-transparent hover:bg-slate-800 text-white font-bold border border-[var(--color-border)] transition-colors">
              Explore the architecture
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

const ArrowDown = () => (
  <div className="py-2 text-slate-600">
    ↓
  </div>
);

// Fallback search icon
const SearchIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
);
