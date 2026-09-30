# SENTRANET Data Directory

This directory houses network capture files, aggregated NetFlow data, and feature stores for machine learning training and evaluation.

- `raw/`: Raw packet captures (.pcap), raw NetFlow / IPFIX logs, and unmodified benchmark datasets (e.g. CIC-IDS2017, UNSW-NB15, or CSE-CIC-IDS2018). *Git-ignored.*
- `processed/`: Extracted feature sets, normalized temporal windows, and preprocessed arrays ready for model training. *Git-ignored.*
- `samples/`: Lightweight, sanitized sample flow sequences for local development, integration tests, and replay pipeline validation. *Version-controlled.*

*Note: In Phase 1, data directories exist structurally. Data collection and preprocessing workflows begin in Phase 2.*
