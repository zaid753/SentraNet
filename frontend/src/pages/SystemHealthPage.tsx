import { useState, useEffect } from 'react';
import { getAnalyticsSystemHealth } from '../services/api';

export function SystemHealthPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchHealth() {
      try {
        const resp = await getAnalyticsSystemHealth();
        setData(resp);
      } catch (e: any) {
        setError(e.message || "Failed to load system health");
      } finally {
        setLoading(false);
      }
    }
    
    fetchHealth();
    // Refresh every 30s
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'operational':
      case 'available':
      case 'connected':
        return 'text-primary bg-primary/10 border-primary/20';
      case 'degraded':
      case 'reconnecting':
        return 'text-warning bg-warning/10 border-warning/20';
      case 'unavailable':
      case 'disconnected':
        return 'text-destructive bg-destructive/10 border-destructive/20';
      default:
        return 'text-muted-foreground bg-secondary border-border';
    }
  };

  const getStatusDot = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'operational':
      case 'available':
      case 'connected':
        return 'bg-primary shadow-[0_0_8px_rgba(var(--primary),0.6)]';
      case 'degraded':
      case 'reconnecting':
        return 'bg-warning shadow-[0_0_8px_rgba(var(--warning),0.6)]';
      case 'unavailable':
      case 'disconnected':
        return 'bg-destructive shadow-[0_0_8px_rgba(var(--destructive),0.6)]';
      default:
        return 'bg-muted-foreground';
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 lg:p-8 animate-in fade-in duration-500 bg-background text-foreground">
      <div className="max-w-5xl mx-auto space-y-8">
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/50 pb-6">
          <div>
            <h1 className="text-3xl font-light tracking-tight">System & Model Health</h1>
            <p className="text-muted-foreground mt-2 text-sm max-w-2xl">
              Real-time operational status of backend services, detection models, and inference engines. 
              Reported evaluation metrics are based on synthetic baseline datasets.
            </p>
          </div>
          {data && (
            <div className={`flex items-center gap-3 px-4 py-2 rounded-full border ${getStatusColor(data.status)}`}>
              <div className={`w-2 h-2 rounded-full ${getStatusDot(data.status)}`} />
              <span className="text-sm font-medium tracking-wide uppercase">{data.status}</span>
            </div>
          )}
        </header>

        {loading && !data ? (
          <div className="flex items-center justify-center h-64 border border-border/50 rounded-lg bg-card/20 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-4">
              <div className="w-8 h-8 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
              <span className="text-sm text-muted-foreground uppercase tracking-widest font-mono">Running Diagnostics</span>
            </div>
          </div>
        ) : error && !data ? (
          <div className="p-6 border border-destructive/50 rounded-lg bg-destructive/10 text-destructive text-sm flex items-center gap-3">
            <svg className="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="font-medium">Diagnostic Error</p>
              <p className="text-destructive/80 mt-1">{error}</p>
            </div>
          </div>
        ) : data && (
          <div className="space-y-10">
            
            {/* Core Infrastructure */}
            <section className="space-y-4">
              <h2 className="text-xs font-semibold tracking-widest uppercase text-muted-foreground">Core Infrastructure</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                {/* API */}
                <div className="p-5 border border-border rounded-lg bg-card/40 flex flex-col justify-between">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-foreground">API Services</h3>
                      <p className="text-xs text-muted-foreground mt-1">REST Endpoints</p>
                    </div>
                    <div className={`w-2.5 h-2.5 rounded-full ${getStatusDot(data.api)}`} />
                  </div>
                  <div className="mt-6">
                    <span className={`text-xs font-medium px-2 py-1 rounded border ${getStatusColor(data.api)}`}>
                      {data.api}
                    </span>
                  </div>
                </div>

                {/* Database */}
                <div className="p-5 border border-border rounded-lg bg-card/40 flex flex-col justify-between">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-foreground">Database</h3>
                      <p className="text-xs text-muted-foreground mt-1">SQLite Persistence</p>
                    </div>
                    <div className={`w-2.5 h-2.5 rounded-full ${getStatusDot(data.database)}`} />
                  </div>
                  <div className="mt-6">
                    <span className={`text-xs font-medium px-2 py-1 rounded border ${getStatusColor(data.database)}`}>
                      {data.database}
                    </span>
                  </div>
                </div>

                {/* Realtime */}
                <div className="p-5 border border-border rounded-lg bg-card/40 flex flex-col justify-between">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-foreground">Realtime Transport</h3>
                      <p className="text-xs text-muted-foreground mt-1">WebSocket & EventBus</p>
                    </div>
                    <div className={`w-2.5 h-2.5 rounded-full ${getStatusDot(data.realtime)}`} />
                  </div>
                  <div className="mt-6">
                    <span className={`text-xs font-medium px-2 py-1 rounded border ${getStatusColor(data.realtime)}`}>
                      {data.realtime}
                    </span>
                  </div>
                </div>

              </div>
            </section>

            {/* Machine Learning Models */}
            <section className="space-y-4">
              <h2 className="text-xs font-semibold tracking-widest uppercase text-muted-foreground">Machine Learning Inference</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                
                {/* XGBoost */}
                <div className="p-6 border border-border rounded-lg bg-card/40">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h3 className="font-medium text-foreground text-lg">XGBoost Classifier</h3>
                      <p className="text-xs text-muted-foreground mt-1">Multi-class Threat Detection</p>
                    </div>
                    <span className={`text-xs font-medium px-2 py-1 rounded border ${getStatusColor(data.xgboost?.status)}`}>
                      {data.xgboost?.status}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-y-4 gap-x-6 text-sm">
                    <div>
                      <span className="text-muted-foreground text-xs block mb-1">Model Version</span>
                      <span className="font-mono text-foreground/80">{data.xgboost?.version}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground text-xs block mb-1">Feature Schema</span>
                      <span className="font-mono text-foreground/80">{data.xgboost?.feature_count || '--'} Features</span>
                    </div>
                    <div className="col-span-2">
                      <span className="text-muted-foreground text-xs block mb-2">Detection Classes</span>
                      <div className="flex flex-wrap gap-2">
                        {data.xgboost?.classes?.map((c: string) => (
                          <span key={c} className="text-[10px] bg-secondary text-secondary-foreground px-2 py-1 rounded font-mono">
                            {c}
                          </span>
                        )) || <span className="text-muted-foreground text-xs">Unavailable</span>}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Isolation Forest */}
                <div className="p-6 border border-border rounded-lg bg-card/40">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h3 className="font-medium text-foreground text-lg">Isolation Forest</h3>
                      <p className="text-xs text-muted-foreground mt-1">Unsupervised Anomaly Detection</p>
                    </div>
                    <span className={`text-xs font-medium px-2 py-1 rounded border ${getStatusColor(data.isolation_forest?.status)}`}>
                      {data.isolation_forest?.status}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-y-4 gap-x-6 text-sm">
                    <div>
                      <span className="text-muted-foreground text-xs block mb-1">Model Version</span>
                      <span className="font-mono text-foreground/80">{data.isolation_forest?.version}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground text-xs block mb-1">Feature Schema</span>
                      <span className="font-mono text-foreground/80">{data.isolation_forest?.feature_count || '--'} Features</span>
                    </div>
                    <div className="col-span-2">
                      <span className="text-muted-foreground text-xs block mb-2">Evaluation Note</span>
                      <p className="text-xs text-muted-foreground/80 leading-relaxed border-l-2 border-primary/40 pl-3">
                        Reported evaluation is based on synthetic data. Real benchmark datasets (CICIDS2017, UNSW-NB15) are currently unavailable in this environment.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Forecast Engine */}
                <div className="p-6 border border-border rounded-lg bg-card/40 lg:col-span-2">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-medium text-foreground text-lg">Temporal Forecast Engine</h3>
                      <p className="text-xs text-muted-foreground mt-1">Heuristic Risk Trajectory Analysis</p>
                    </div>
                    <span className={`text-xs font-medium px-2 py-1 rounded border ${getStatusColor(data.forecast_engine?.status)}`}>
                      {data.forecast_engine?.status}
                    </span>
                  </div>
                  <div className="mt-4 p-4 rounded-md bg-secondary/30 text-sm text-muted-foreground border border-border/50">
                    <strong>Heuristic Warning:</strong> Forecast precursor lead-time validation is limited by abrupt synthetic transitions. Forecasts are heuristic estimations based on cascading anomaly scores and do not represent calibrated probability.
                  </div>
                </div>

              </div>
            </section>
            
          </div>
        )}
      </div>
    </div>
  );
}
