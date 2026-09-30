import { api } from './api';
import type { ExplanationResponse, IncidentExplanation } from '../types/explainability';

export const explainabilityApi = {
  /**
   * Fetches the explanation for the most recently processed stream window.
   */
  getCurrentExplanation: async (): Promise<ExplanationResponse> => {
    return api.getCurrentExplanation();
  },

  /**
   * Fetches the explanation for a specific incident.
   */
  getIncidentExplanation: async (incidentId: string): Promise<IncidentExplanation> => {
    return api.getIncidentExplanation(incidentId);
  }
};
