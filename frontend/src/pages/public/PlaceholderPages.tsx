import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, ArrowLeft, ShieldAlert } from 'lucide-react';

const PageTemplate: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="container mx-auto px-4 py-16 max-w-4xl min-h-[60vh]">
    <Link to="/" className="inline-flex items-center gap-2 text-sm text-[var(--color-text-secondary)] hover:text-white transition-colors mb-8">
      <ArrowLeft className="w-4 h-4" /> Back to Home
    </Link>
    <h1 className="text-4xl font-bold text-white mb-8">{title}</h1>
    <div className="prose prose-invert prose-blue max-w-none text-slate-300">
      {children}
    </div>
  </div>
);

export const FeaturesPage: React.FC = () => (
  <PageTemplate title="Product Features">
    <div className="space-y-8">
      <div className="bg-[var(--color-surface)] p-6 rounded-xl border border-[var(--color-border)]">
        <h3 className="text-xl font-bold text-white mb-2">Detection & Anomaly Detection</h3>
        <p>SENTRANET utilizes an XGBoost multi-class classifier paired with an Isolation Forest unsupervised anomaly detector to identify both known attack vectors and zero-day anomalous behaviors.</p>
      </div>
      <div className="bg-[var(--color-surface)] p-6 rounded-xl border border-[var(--color-border)]">
        <h3 className="text-xl font-bold text-white mb-2">Risk Fusion & Forecasting</h3>
        <p>By fusing detection probabilities across a 60-second temporal window, SENTRANET computes a composite risk score and heuristically forecasts impending state transitions (e.g., BENIGN → SCANNING → DDOS).</p>
      </div>
      <div className="bg-[var(--color-surface)] p-6 rounded-xl border border-[var(--color-border)]">
        <h3 className="text-xl font-bold text-white mb-2">Model Explainability</h3>
        <p>Security operators receive model-native explanations highlighting exactly which flow-level features (e.g., packet rate, byte counts) contributed to the current risk classification.</p>
      </div>
    </div>
  </PageTemplate>
);

export const HowItWorksPage: React.FC = () => (
  <PageTemplate title="How It Works">
    <p className="mb-6 leading-relaxed">
      SENTRANET processes network flow metadata through a multi-stage machine learning pipeline to provide actionable security intelligence.
    </p>
    <div className="p-6 bg-slate-900 rounded-xl border border-slate-800 font-mono text-sm space-y-4">
      <div className="flex gap-4 items-center">
        <span className="w-8 h-8 rounded bg-blue-900/50 flex items-center justify-center text-blue-400">01</span>
        <div><strong>Telemetry:</strong> Ingestion of raw network flow metadata.</div>
      </div>
      <div className="flex gap-4 items-center">
        <span className="w-8 h-8 rounded bg-blue-900/50 flex items-center justify-center text-blue-400">02</span>
        <div><strong>Windows:</strong> Aggregation into 60-second temporal windows.</div>
      </div>
      <div className="flex gap-4 items-center">
        <span className="w-8 h-8 rounded bg-emerald-900/50 flex items-center justify-center text-emerald-400">03</span>
        <div><strong>Classification:</strong> XGBoost evaluates the window against known signatures.</div>
      </div>
      <div className="flex gap-4 items-center">
        <span className="w-8 h-8 rounded bg-emerald-900/50 flex items-center justify-center text-emerald-400">04</span>
        <div><strong>Anomaly Detection:</strong> Isolation Forest checks for structural deviations.</div>
      </div>
      <div className="flex gap-4 items-center">
        <span className="w-8 h-8 rounded bg-violet-900/50 flex items-center justify-center text-violet-400">05</span>
        <div><strong>Risk Fusion:</strong> A unified risk score is calculated from the models.</div>
      </div>
      <div className="flex gap-4 items-center">
        <span className="w-8 h-8 rounded bg-rose-900/50 flex items-center justify-center text-rose-400">06</span>
        <div><strong>Incidents:</strong> State machines track sustained threats and generate alerts.</div>
      </div>
    </div>
  </PageTemplate>
);

export const TechnologyPage: React.FC = () => (
  <PageTemplate title="Technology Stack">
    <p className="mb-6">SENTRANET leverages modern, proven technologies optimized for machine learning inference and high-performance UI.</p>
    <ul className="space-y-4 list-disc pl-6">
      <li><strong>Frontend:</strong> React 19, TypeScript, Vite, Tailwind CSS v4</li>
      <li><strong>Backend:</strong> FastAPI (Python 3)</li>
      <li><strong>Machine Learning:</strong> XGBoost, Scikit-learn (Isolation Forest), Pandas, NumPy</li>
      <li><strong>Telemetry:</strong> Simulated PCAP / CSV Network Flow data ingestion</li>
    </ul>
  </PageTemplate>
);

export const SecurityPage: React.FC = () => (
  <PageTemplate title="Security Posture">
    <div className="p-4 bg-amber-900/20 border border-amber-500/30 rounded-lg flex items-start gap-3 mb-8">
      <ShieldAlert className="w-5 h-5 text-amber-400 mt-0.5" />
      <div>
        <h4 className="font-bold text-amber-400">Development Scope</h4>
        <p className="text-sm text-amber-200 mt-1">
          This system is currently in a demonstration/evaluation state for SIH26153. It does not possess production-grade authentication, SOC 2 compliance, or ISO certifications.
        </p>
      </div>
    </div>
    <p>
      Currently, authentication is handled via a conceptual demonstration layer designed to establish architecture for future OIDC/SAML integration.
    </p>
  </PageTemplate>
);

export const DocsPage: React.FC = () => (
  <PageTemplate title="Documentation">
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
      {[
        { title: 'Architecture', desc: 'System design and component boundaries.' },
        { title: 'Detection', desc: 'XGBoost and Isolation Forest mechanics.' },
        { title: 'Forecasting', desc: 'Heuristic temporal state predictions.' },
        { title: 'Explainability', desc: 'Understanding feature gain and risk attribution.' },
        { title: 'Replay API', desc: 'HTTP contracts for the synthetic replay engine.' }
      ].map((item) => (
        <div key={item.title} className="p-5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg hover:border-blue-500/50 cursor-pointer transition-colors flex items-start gap-4">
          <FileText className="w-6 h-6 text-blue-400 mt-1" />
          <div>
            <h4 className="font-bold text-white">{item.title}</h4>
            <p className="text-sm text-slate-400 mt-1">{item.desc}</p>
          </div>
        </div>
      ))}
    </div>
  </PageTemplate>
);

export const DemoPage: React.FC = () => (
  <PageTemplate title="Simulation Demo">
    <p className="mb-4 text-lg">
      The SENTRANET platform operates using a <strong className="text-blue-400">Synthetic Stream // Simulation</strong>.
    </p>
    <p className="mb-8">
      This allows evaluators to observe the machine learning pipeline, risk fusion mechanics, and SOC interface behavior using pre-computed network flow datasets injected as pseudo-live telemetry.
    </p>
    <Link to="/signup" className="px-8 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold transition-colors inline-block">
      Launch Simulation
    </Link>
  </PageTemplate>
);
