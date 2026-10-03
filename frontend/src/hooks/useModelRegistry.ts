import { useState, useEffect } from 'react';

export interface ModelRegistryEntry {
  model_id: string;
  model_name: string;
  dataset: string;
  training_type: string;
  feature_contract_version: string;
  scaler_path: string;
  xgboost_artifact: string;
  isolation_forest_artifact: string;
  status: string;
  evaluation_report: string;
}

export function useModelRegistry() {
  const [models, setModels] = useState<ModelRegistryEntry[]>([]);
  const [activeModel, setActiveModel] = useState<ModelRegistryEntry | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchModels = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/models/');
      if (!response.ok) throw new Error('Failed to fetch models');
      const data = await response.json();
      setModels(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchActiveModel = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/models/active');
      if (!response.ok) throw new Error('Failed to fetch active model');
      const data = await response.json();
      setActiveModel(data);
    } catch (err) {
      console.error(err);
    }
  };

  const setModel = async (modelId: string) => {
    try {
      setError(null);
      const response = await fetch('http://127.0.0.1:8000/api/models/active', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ model_id: modelId })
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to set model');
      }
      await fetchActiveModel();
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      await Promise.all([fetchModels(), fetchActiveModel()]);
      setIsLoading(false);
    };
    init();
  }, []);

  return { models, activeModel, setModel, isLoading, error };
}
