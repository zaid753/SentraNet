/**
 * SENTRANET — TypeScript Definitions (Phase 8 SOC Dashboard)
 * Maps strictly to Phase 7 FastAPI Schemas.
 */

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  simulation: boolean;
}

export interface ComponentStatus {
  status: string;
}

export interface SystemStatus {
  service: string;
  status: string;
  simulation: boolean;
  models: Record<string, string>;
  pipeline: Record<string, string>;
  feature_count: number;
  backend?: ComponentStatus;
  ml_models?: ComponentStatus;
  replay_engine?: ComponentStatus;
  database?: ComponentStatus;
  websocket?: ComponentStatus;
}

export interface NetworkFeatures {
  flow_count: number;
  total_packets: number;
  total_bytes: number;
  avg_packet_rate: number;
  avg_byte_rate: number;
  unique_sources: number;
  unique_destinations: number;
  avg_packet_size: number;
  avg_flow_duration: number;
  syn_flag_count: number;
  ack_flag_count: number;
  privileged_port_ratio: number;
  rolling_5_flow_count: number;
  rolling_5_total_packets: number;
  rolling_5_total_bytes: number;
  rolling_5_avg_byte_rate: number;
  rolling_5_unique_sources: number;
}

export interface AlertEventSummary {
  event_type: string;
  incident_id?: string | null;
  severity: string;
}

export interface AnalyzeResponse {
  timestamp: string;
  attack_class: string;
  class_probability: number;
  attack_likelihood: number;
  anomaly_score: number;
  is_anomalous: boolean;
  risk_score: number;
  risk_state: string;
  risk_velocity?: number | null;
  risk_acceleration?: number | null;
  risk_trend: string;
  emergence_detected: boolean;
  forecast_active: boolean;
  forecast_class?: string | null;
  estimated_eta_seconds?: number | null;
  forecast_confidence?: number | null;
  alert_state: string;
  incident_id?: string | null;
  reasons: string[];
  alert_event?: AlertEventSummary | null;
  simulation: boolean;
}

export interface CurrentAlertResponse {
  active: boolean;
  incident?: Record<string, unknown> | null;
  alert_state: string;
  severity: string;
  attack_class?: string | null;
  risk_score?: number | null;
  anomaly_score?: number | null;
  forecast_active: boolean;
  estimated_eta_seconds?: number | null;
  forecast_confidence?: number | null;
  reasons: string[];
}

export interface AlertItemResponse {
  alert_event_id: string;
  incident_id?: string | null;
  event_type: string;
  timestamp: string;
  attack_class: string;
  severity: string;
  risk_score: number;
  anomaly_score: number;
  reasons: string[];
  forecast_active: boolean;
  estimated_eta_seconds?: number | null;
  forecast_confidence?: number | null;
}

export interface IncidentItemResponse {
  incident_id: string;
  status: string;
  attack_class: string;
  severity: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
  peak_risk: number;
  max_anomaly: number;
  forecast_triggered: boolean;
  event_count: number;
}

export interface IncidentDetailResponse {
  incident_id: string;
  status: string;
  attack_class: string;
  severity: string;
  created_at: string;
  updated_at: string;
  resolution_timestamp?: string | null;
  first_risk_score: number;
  current_risk_score: number;
  peak_risk_score: number;
  max_anomaly_score: number;
  forecast_triggered: boolean;
  estimated_eta_seconds?: number | null;
  confidence: number;
  event_count: number;
  timestamps: string[];
}

export interface TimelinePointResponse {
  timestamp: string;
  risk_score: number;
  risk_state: string;
  anomaly_score: number;
  attack_class: string;
  forecast_active: boolean;
  eta_seconds?: number | null;
}

export interface TimelineResponse {
  total_points: number;
  points: TimelinePointResponse[];
}

export interface ReplayStartRequest {
  mode: 'batch' | 'realtime' | 'step';
  speed: number;
  dataset: string;
}

export interface ReplayStatusResponse {
  running: boolean;
  paused: boolean;
  mode: string;
  speed: number;
  dataset?: string | null;
  current_timestamp?: string | null;
  windows_processed: number;
  total_windows: number;
  progress: number;
}

export interface ReplayActionResponse {
  status: string;
  message: string;
  timestamp: string;
  details?: Record<string, unknown> | null;
}

export interface NotificationToast {
  id: string;
  type: 'ALERT' | 'FORECAST' | 'INFO';
  title: string;
  message: string;
  timestamp: string;
  severity?: string;
  incidentId?: string;
}

export type ConnectionState = 'LOADING' | 'CONNECTED' | 'DEGRADED' | 'OFFLINE' | 'ERROR';

// Phase 9: Telemetry & Synthetic Stream Types
export type TelemetrySource = 'historical' | 'synthetic' | 'live';

export interface TelemetryStatusResponse {
  active: boolean;
  source_type: string;
  current_window_start?: string | null;
  current_window_end?: string | null;
  flows_in_window: number;
  windows_processed: number;
  flows_processed: number;
  latest_timestamp?: string | null;
  latest_risk?: number | null;
  latest_decision?: Record<string, unknown> | null;
}

export interface SyntheticStartRequest {
  speed: number;
  seed: number;
  profile: string;
  duration_seconds?: number | null;
}

export interface SyntheticStatusResponse {
  running: boolean;
  status: 'idle' | 'running' | 'paused' | 'stopped';
  speed: number;
  seed: number;
  profile: string;
  flows_generated: number;
  windows_generated: number;
  duration_seconds?: number | null;
}

export interface TelemetryActionResponse {
  status: string;
  message: string;
  timestamp: string;
  details?: Record<string, unknown> | null;
}

// ============================================================
// Phase 10: Benchmark Evaluation Types
// ============================================================

export interface EvaluationClassification {
  accuracy: number | null;
  macro_f1: number | null;
  weighted_f1: number | null;
  macro_pr_auc: number | null;
  log_loss: number | null;
}

export interface EvaluationAnomalyDetection {
  attack_detection_rate?: number | null;
  detection_rate?: number | null;
  benign_anomaly_fpr?: number | null;
  [key: string]: unknown;
}

export interface EvaluationRiskFusion {
  risk_state_counts?: Record<string, number>;
  state_breakdown?: Record<string, number>;
  attack_high_rate?: number | null;
  [key: string]: unknown;
}

export interface EvaluationForecasting {
  attack_onsets_count: number;
  forecasted_onsets_count: number;
  mean_lead_time_seconds: number | null;
  median_lead_time_seconds: number | null;
  horizon_1m_f1: number | null;
  horizon_5m_f1: number | null;
}

export interface EvaluationPerformance {
  latency_ms_mean?: number | null;
  latency_ms_p95?: number | null;
  throughput_windows_per_second?: number | null;
  [key: string]: unknown;
}

export interface EvaluationDatasetResult {
  dataset_id: string;
  name: string;
  category: string;
  status: 'COMPLETED' | 'NOT_AVAILABLE' | 'NOT_EVALUATED';
  evaluation_mode?: string;
  windows_evaluated?: number;
  classification?: EvaluationClassification;
  anomaly_detection?: EvaluationAnomalyDetection;
  risk_fusion?: EvaluationRiskFusion;
  forecasting?: EvaluationForecasting;
  performance?: EvaluationPerformance;
  macro_f1?: number | null;
  message?: string;
  display_label?: string;
  [key: string]: unknown;
}

export interface EvaluationSummary {
  status?: string;
  evaluation_type?: string;
  display_label: string;
  caution?: string;
  datasets: Record<string, EvaluationDatasetResult>;
  evaluated_at?: string;
  message?: string;
}
