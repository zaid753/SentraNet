import type {
  HealthResponse,
  SystemStatus,
  AnalyzeResponse,
  CurrentAlertResponse,
  AlertItemResponse,
  IncidentItemResponse,
  IncidentDetailResponse,
  TimelineResponse,
  ReplayStartRequest,
  ReplayStatusResponse,
  ReplayActionResponse,
  TelemetryStatusResponse,
  SyntheticStartRequest,
  SyntheticStatusResponse,
  TelemetryActionResponse,
  EvaluationSummary,
  EvaluationDatasetResult,
} from '../types';
import type { ExplanationResponse, IncidentExplanation } from '../types/explainability';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

export class ApiError extends Error {
  code: string;
  statusCode: number;
  details?: unknown;

  constructor(message: string, statusCode: number, code: string = 'API_ERROR', details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
  }
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  private async fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    let response: Response;

    try {
      response = await fetch(url, {
        ...options,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          ...(options?.headers || {}),
        },
      });
    } catch (netErr: unknown) {
      const msg = netErr instanceof Error ? netErr.message : 'Network error';
      throw new ApiError(
        `Unable to connect to SENTRANET API at ${this.baseUrl}. (${msg})`,
        0,
        'NETWORK_ERROR'
      );
    }

    if (!response.ok) {
      let errorBody: { error?: { code?: string; message?: string; details?: unknown } } | null = null;
      try {
        errorBody = await response.json();
      } catch {
        // Not a JSON response
      }

      const code = errorBody?.error?.code || `HTTP_${response.status}`;
      const message = errorBody?.error?.message || `HTTP ${response.status}: ${response.statusText}`;
      const details = errorBody?.error?.details;

      throw new ApiError(message, response.status, code, details);
    }

    return response.json() as Promise<T>;
  }

  // Health & System
  async getHealth(): Promise<HealthResponse> {
    return this.fetchJson<HealthResponse>('/api/health');
  }

  async getSystemStatus(): Promise<SystemStatus> {
    return this.fetchJson<SystemStatus>('/api/system/status');
  }

  // Risk & Telemetry
  async getCurrentRisk(): Promise<AnalyzeResponse | null> {
    try {
      return await this.fetchJson<AnalyzeResponse>('/api/risk/current');
    } catch (err: unknown) {
      if (err instanceof ApiError && (err.statusCode === 404 || err.code === 'NO_CURRENT_STATE')) {
        // Clean empty state before any telemetry or replay has run
        return null;
      }
      throw err;
    }
  }

  // Timeline
  async getTimeline(limit: number = 50): Promise<TimelineResponse> {
    return this.fetchJson<TimelineResponse>(`/api/timeline?limit=${limit}`);
  }

  // Alerts
  async getCurrentAlert(): Promise<CurrentAlertResponse> {
    return this.fetchJson<CurrentAlertResponse>('/api/alerts/current');
  }

  async getAlerts(
    limit: number = 20,
    severity?: string,
    attackClass?: string
  ): Promise<AlertItemResponse[]> {
    const params = new URLSearchParams();
    params.set('limit', limit.toString());
    if (severity) params.set('severity', severity);
    if (attackClass) params.set('attack_class', attackClass);
    return this.fetchJson<AlertItemResponse[]>(`/api/alerts?${params.toString()}`);
  }

  // Incidents
  async getIncidents(): Promise<IncidentItemResponse[]> {
    return this.fetchJson<IncidentItemResponse[]>('/api/incidents');
  }

  async getIncident(incidentId: string): Promise<IncidentDetailResponse> {
    return this.fetchJson<IncidentDetailResponse>(`/api/incidents/${encodeURIComponent(incidentId)}`);
  }

  async resolveIncident(incidentId: string): Promise<IncidentDetailResponse> {
    return this.fetchJson<IncidentDetailResponse>(`/api/incidents/${encodeURIComponent(incidentId)}/resolve`, {
      method: 'POST',
    });
  }

  // Replay Lifecycle
  async startReplay(request: ReplayStartRequest): Promise<ReplayActionResponse> {
    return this.fetchJson<ReplayActionResponse>('/api/replay/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async stopReplay(): Promise<ReplayActionResponse> {
    return this.fetchJson<ReplayActionResponse>('/api/replay/stop', {
      method: 'POST',
    });
  }

  async pauseReplay(): Promise<ReplayActionResponse> {
    return this.fetchJson<ReplayActionResponse>('/api/replay/pause', {
      method: 'POST',
    });
  }

  async resumeReplay(): Promise<ReplayActionResponse> {
    return this.fetchJson<ReplayActionResponse>('/api/replay/resume', {
      method: 'POST',
    });
  }

  async stepReplay(): Promise<ReplayActionResponse> {
    return this.fetchJson<ReplayActionResponse>('/api/replay/step', {
      method: 'POST',
    });
  }

  async getReplayStatus(): Promise<ReplayStatusResponse> {
    return this.fetchJson<ReplayStatusResponse>('/api/replay/status');
  }

  async getReplayEvents(
    limit: number = 50,
    eventType?: string
  ): Promise<Record<string, unknown>[]> {
    const params = new URLSearchParams();
    params.set('limit', limit.toString());
    if (eventType) params.set('event_type', eventType);
    return this.fetchJson<Record<string, unknown>[]>(`/api/replay/events?${params.toString()}`);
  }

  // Stream Reset
  async resetStream(): Promise<{ status: string; message: string }> {
    return this.fetchJson<{ status: string; message: string }>('/api/stream/reset', {
      method: 'POST',
    });
  }

  // Phase 9: Telemetry & Synthetic Stream Endpoints
  async getTelemetryStatus(): Promise<TelemetryStatusResponse> {
    return this.fetchJson<TelemetryStatusResponse>('/api/telemetry/status');
  }

  async flushTelemetry(): Promise<Record<string, unknown>> {
    return this.fetchJson<Record<string, unknown>>('/api/telemetry/flush', {
      method: 'POST',
    });
  }

  async resetTelemetry(): Promise<TelemetryActionResponse> {
    return this.fetchJson<TelemetryActionResponse>('/api/telemetry/reset', {
      method: 'POST',
    });
  }

  async startSyntheticStream(req: SyntheticStartRequest): Promise<SyntheticStatusResponse> {
    return this.fetchJson<SyntheticStatusResponse>('/api/telemetry/synthetic/start', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async stopSyntheticStream(): Promise<SyntheticStatusResponse> {
    return this.fetchJson<SyntheticStatusResponse>('/api/telemetry/synthetic/stop', {
      method: 'POST',
    });
  }

  async pauseSyntheticStream(): Promise<SyntheticStatusResponse> {
    return this.fetchJson<SyntheticStatusResponse>('/api/telemetry/synthetic/pause', {
      method: 'POST',
    });
  }

  async resumeSyntheticStream(): Promise<SyntheticStatusResponse> {
    return this.fetchJson<SyntheticStatusResponse>('/api/telemetry/synthetic/resume', {
      method: 'POST',
    });
  }

  async getSyntheticStatus(): Promise<SyntheticStatusResponse> {
    return this.fetchJson<SyntheticStatusResponse>('/api/telemetry/synthetic/status');
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }

  // Phase 10: Benchmark Evaluation
  async getEvaluationSummary(): Promise<EvaluationSummary> {
    return this.fetchJson<EvaluationSummary>('/api/evaluation/summary');
  }

  async getDatasetEvaluation(dataset: string): Promise<EvaluationDatasetResult> {
    return this.fetchJson<EvaluationDatasetResult>(`/api/evaluation/${dataset}`);
  }

  // Phase 11: Explainability
  async getCurrentExplanation(): Promise<ExplanationResponse> {
    return this.fetchJson<ExplanationResponse>('/api/explanations/current');
  }

  async getIncidentExplanation(incidentId: string): Promise<IncidentExplanation> {
    return this.fetchJson<IncidentExplanation>(`/api/incidents/${incidentId}/explanation`);
  }

  // Phase 7: Analytics
  async getAnalyticsOverview(timeRange: string = 'all'): Promise<any> {
    return this.fetchJson<any>(`/api/analytics/overview?time_range=${timeRange}`);
  }

  async getAnalyticsSystemHealth(): Promise<any> {
    return this.fetchJson<any>('/api/system/health');
  }


}

export const api = new ApiService(API_BASE_URL);

export const getHealth = () => api.getHealth();
export const getSystemStatus = () => api.getSystemStatus();
export const getCurrentRisk = () => api.getCurrentRisk();
export const getTimeline = (limit?: number) => api.getTimeline(limit);
export const getCurrentAlert = () => api.getCurrentAlert();
export const getAlerts = (limit?: number, severity?: string, attackClass?: string) =>
  api.getAlerts(limit, severity, attackClass);
export const getIncidents = () => api.getIncidents();
export const getIncident = (id: string) => api.getIncident(id);
export const startReplay = (req: ReplayStartRequest) => api.startReplay(req);
export const stopReplay = () => api.stopReplay();
export const pauseReplay = () => api.pauseReplay();
export const resumeReplay = () => api.resumeReplay();
export const stepReplay = () => api.stepReplay();
export const getReplayStatus = () => api.getReplayStatus();
export const getReplayEvents = (limit?: number, eventType?: string) =>
  api.getReplayEvents(limit, eventType);
export const resetStream = () => api.resetStream();

// Telemetry Exports
export const getTelemetryStatus = () => api.getTelemetryStatus();
export const flushTelemetry = () => api.flushTelemetry();
export const resetTelemetry = () => api.resetTelemetry();
export const startSyntheticStream = (req: SyntheticStartRequest) => api.startSyntheticStream(req);
export const stopSyntheticStream = () => api.stopSyntheticStream();
export const pauseSyntheticStream = () => api.pauseSyntheticStream();
export const resumeSyntheticStream = () => api.resumeSyntheticStream();
export const getSyntheticStatus = () => api.getSyntheticStatus();

// Phase 10: Evaluation Exports
export const getEvaluationSummary = () => api.getEvaluationSummary();
export const getDatasetEvaluation = (dataset: string) => api.getDatasetEvaluation(dataset);

// Phase 11: Explainability Exports
export const getCurrentExplanation = () => api.getCurrentExplanation();
export const getIncidentExplanation = (id: string) => api.getIncidentExplanation(id);

// Phase 7: Analytics Exports
export const getAnalyticsOverview = (timeRange?: string) => api.getAnalyticsOverview(timeRange);
export const getAnalyticsSystemHealth = () => api.getAnalyticsSystemHealth();
export const resolveIncident = (id: string) => api.resolveIncident(id);

