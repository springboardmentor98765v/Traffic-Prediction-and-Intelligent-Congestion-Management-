# Milestone 2 — Milestone 3 Handoff Notes

## 1. Overview

This document summarizes the AI/ML and intelligent-routing work completed
during Milestone 2 and identifies the remaining integration dependencies
and recommended improvements for Milestone 3.

---

## 2. Completed Milestone 2 Work

### AI/ML

- Feature engineering completed.
- Congestion classification model trained.
- Chronological train/test validation completed.
- Model evaluation and feature analysis completed.
- MAE/RMSE ordinal analysis completed.
- Trained model saved as `model-v1.joblib`.

### Prediction Service

Implemented and tested:

```text
GET /api/v1/predict/congestion
GET /api/v1/predict/peak-hours
GET /api/v1/predict/delay
```
