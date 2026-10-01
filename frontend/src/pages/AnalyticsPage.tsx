import { useState, useEffect } from 'react';
import { getAnalyticsOverview } from '../services/api';

export function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | 'all'>('all');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAnalytics() {
      setLoading(true);
      setError(null);
      try {
        const resp = await getAnalyticsOverview(timeRange);
        setData(resp);
      } catch (e: any) {
        setError(e.message || "Failed to load analytics");
      } finally {
        setLoading(false);
      }
    }
    fetchAnalytics();
  }, [timeRange]);

  return (
    <div className="flex-1 overflow-y-auto p-6 lg:p-8 animate-in fade-in duration-500 bg-background text-foreground">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-light tracking-tight">Operational Analytics</h1>
            <p className="text-muted-foreground mt-1 text-sm">Workspace detection and risk telemetry over time.</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Period:</span>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="bg-card text-foreground text-sm rounded-md border border-border px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary/50"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="all">All Available</option>
            </select>
          </div>
        </header>

        {loading ? (
          <div className="flex items-center justify-center h-64 border border-border/50 rounded-lg bg-card/20 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-4">
              <div className="w-8 h-8 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
              <span className="text-sm text-muted-foreground uppercase tracking-widest font-mono">Aggregating telemetry</span>
            </div>
          </div>
        ) : error ? (
          <div className="p-6 border border-destructive/50 rounded-lg bg-destructive/10 text-destructive text-sm flex items-center gap-3">
            <svg className="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="font-medium">Analytics Unavailable</p>
              <p className="text-destructive/80 mt-1">{error}</p>
            </div>
          </div>
        ) : !data || (data.total_incidents === 0 && data.total_alerts === 0) ? (
          <div className="flex flex-col items-center justify-center h-64 border border-border/50 rounded-lg bg-card/20 backdrop-blur-sm text-center px-4">
            <svg className="w-10 h-10 text-muted-foreground/50 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p className="text-foreground font-medium">No recorded telemetry</p>
            <p className="text-sm text-muted-foreground mt-1 max-w-sm">No incidents or alerts were recorded in the selected time period. Start a replay simulation to generate synthetic events.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-lg border border-border bg-card/40 backdrop-blur-sm flex flex-col justify-between hover:bg-card/60 transition-colors">
                <span className="text-xs uppercase tracking-wider text-muted-foreground font-medium">Total Incidents</span>
                <div className="mt-4 flex items-end justify-between">
                  <span className="text-3xl font-light tabular-nums">{data.total_incidents}</span>
                  <span className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded-full">{data.active_incidents} Active</span>
                </div>
              </div>
              <div className="p-5 rounded-lg border border-border bg-card/40 backdrop-blur-sm flex flex-col justify-between hover:bg-card/60 transition-colors">
                <span className="text-xs uppercase tracking-wider text-muted-foreground font-medium">Total Alerts</span>
                <div className="mt-4 flex items-end justify-between">
                  <span className="text-3xl font-light tabular-nums">{data.total_alerts}</span>
                </div>
              </div>
              <div className="p-5 rounded-lg border border-border bg-card/40 backdrop-blur-sm flex flex-col justify-between hover:bg-card/60 transition-colors">
                <span className="text-xs uppercase tracking-wider text-muted-foreground font-medium">Peak Risk</span>
                <div className="mt-4 flex items-end justify-between">
                  <span className={`text-3xl font-light tabular-nums ${data.peak_risk > 0.8 ? 'text-destructive' : data.peak_risk > 0.4 ? 'text-warning' : 'text-primary'}`}>
                    {(data.peak_risk * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="p-5 rounded-lg border border-border bg-card/40 backdrop-blur-sm flex flex-col justify-between hover:bg-card/60 transition-colors">
                <span className="text-xs uppercase tracking-wider text-muted-foreground font-medium">Avg Resolution Time</span>
                <div className="mt-4 flex items-end justify-between">
                  <span className="text-3xl font-light tabular-nums">
                    {data.average_resolution_seconds !== null 
                      ? `${(data.average_resolution_seconds).toFixed(1)}s` 
                      : '--'}
                  </span>
                </div>
              </div>
            </div>

            {/* Charts Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Threat Distribution */}
              <div className="lg:col-span-1 border border-border rounded-lg bg-card/20 p-5 flex flex-col">
                <h3 className="text-sm font-medium tracking-wide uppercase text-muted-foreground mb-6">Threat Distribution</h3>
                <div className="flex-1 flex flex-col justify-center space-y-4">
                  {Object.entries(data.threat_distribution).length > 0 ? (
                    Object.entries(data.threat_distribution).map(([threat, count]: any) => (
                      <div key={threat} className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="font-mono text-foreground/80">{threat}</span>
                          <span className="tabular-nums text-muted-foreground">{count}</span>
                        </div>
                        <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary rounded-full"
                            style={{ width: `${(count / data.total_incidents) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-sm text-muted-foreground">No threat classification data</div>
                  )}
                </div>
              </div>

              {/* Synthetic disclaimer */}
              <div className="lg:col-span-2 border border-border rounded-lg bg-card/20 p-5 flex flex-col items-center justify-center text-center space-y-4">
                 <svg className="w-8 h-8 text-primary/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
                <div className="space-y-1">
                  <h3 className="font-medium text-foreground">Trend Visualization Note</h3>
                  <p className="text-sm text-muted-foreground max-w-md">Detailed timeseries rendering relies on continuous synthetic replay data. Advanced charting modules are initializing based on workspace events.</p>
                </div>
              </div>

            </div>

          </div>
        )}
      </div>
    </div>
  );
}
