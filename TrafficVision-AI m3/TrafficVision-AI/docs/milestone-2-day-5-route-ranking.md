# Milestone 2 — Day 5 Route Ranking

## 1. Objective

Implement a smart route-ranking service that evaluates candidate routes
using traffic congestion, prediction confidence, estimated delay, and
route distance.

The ranking service is designed to select the most suitable route by
assigning a lower score to better routes.

---

## 2. Route Ranking Service

The route-ranking logic is implemented in:

`traffic-monitoring/src/route_ranking.py`

The service accepts candidate routes containing:

- `route_id`
- `distance_km`
- `congestion_level`
- `confidence`
- `delay_minutes`

---

## 3. Congestion Scoring

Congestion levels are converted into numerical scores:

| Congestion Level | Score |
| ---------------- | ----: |
| Low              |     0 |
| Medium           |     1 |
| High             |     2 |
| Severe           |     3 |

Higher congestion results in a higher route penalty.

---

## 4. Route Scoring Formula

The current route score is:

```text
route_score =
    congestion × 60
    + delay_minutes × 8
    + distance_km × 2
    + (1 - confidence) × 10
```
