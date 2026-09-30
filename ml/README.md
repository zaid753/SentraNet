# SENTRANET ML Platform

This directory contains the machine learning pipelines for predictive network security analysis.

- `preprocessing/`: Feature extraction, temporal sequence windowing, scaling, and categorical encoding.
- `training/`: Training scripts and hyperparameter tuning for classifiers, anomaly detectors, and sequence forecasters.
- `evaluation/`: Model evaluation, confusion matrices, ROC/PR curves, lead-time benchmarking, and calibration checks.
- `inference/`: Low-latency runtime inference engine serving attack probabilities and risk scores to the FastAPI backend.
- `models/`: Trained model binaries and serialized pipelines (e.g. .pt, .onnx, .joblib).

*Note: Phase 1 establishes the directory structure only. Model training and forecasting implementation begin in Phases 3 and 4.*
