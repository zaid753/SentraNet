export interface FeatureExplanation {
  feature: string;
  display_name: string;
  category: string;
  current_value: number | null;
  unit: string;
  global_importance: number | null;
  importance_rank: number | null;
  description: string;
}

export interface RiskComponents {
  attack_likelihood: number;
  attack_likelihood_contribution: number;
  anomaly_score: number;
  anomaly_contribution: number;
  combined_risk: number;
}

export interface RiskExplanation {
  risk_score: number;
  risk_state: string;
  components: RiskComponents;
  narrative: string;
}

export interface ClassificationExplanation {
  predicted_class: string;
  attack_likelihood: number;
  class_probabilities: Record<string, number>;
  top_contributing_features: string[];
}

export interface AnomalyExplanation {
  is_anomalous: boolean;
  anomaly_score: number;
  threshold: number;
  status: string;
}

export interface ForecastExplanation {
  forecast_available: boolean;
  forecast_class: string | null;
  time_to_impact_seconds: number | null;
  eta_narrative: string | null;
  narrative: string;
}

export interface ExplanationResponse {
  window_id: string;
  generated_at: string;
  data_source: string;
  risk: RiskExplanation;
  classification: ClassificationExplanation;
  anomaly: AnomalyExplanation;
  forecast: ForecastExplanation;
  top_features: FeatureExplanation[];
  features: FeatureExplanation[];
}

export interface IncidentTimelineEvent {
  timestamp: string;
  event_type: string;
  risk: number;
  anomaly: number;
  attack_class: string;
  explanation: string;
}

export interface IncidentExplanation {
  incident_id: string;
  start_time: string;
  end_time: string;
  duration: string;
  highest_risk: number;
  highest_anomaly: number;
  attack_classes_observed: string[];
  alert_count: number;
  forecast_signals: number;
  risk_trajectory_summary: string;
  explanation_summary: string;
  timeline: IncidentTimelineEvent[];
}
