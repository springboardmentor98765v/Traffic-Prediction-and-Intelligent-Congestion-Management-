# TrafficVision AI — Exploratory Data Analysis (EDA) Notes
**Prepared by:** Saksham Pandey (AI/ML & Intelligent Routing — Intern 1)  
**Team Lead:** Anmol Sharma (Data Engineering — Intern 2)  
**Dataset:** `traffic_dataset_1000_combined.xlsx`

---

### What We Looked At
I analyzed the simulated traffic dataset provided by Anmol containing 1,000 readings across our 4 road junctions. The data is clean with zero missing values across all 22 columns.

For Milestone 1 heuristic rules and future ML feature engineering, I focused on the primary signals: `road_id`, `density`, `vehicle_count`, `vehicle_capacity`, and `timestamp`.

---

### Key Observations & Traffic Patterns

1. **Clear Peak-Hour Surges:**
   - Morning rush hour runs from **07:00 AM to 10:00 AM**.
   - Evening rush hour runs from **05:00 PM to 08:00 PM**.
   - Almost all severe and high congestion instances happen during these two daily windows (33 out of 35 severe records occurred here).

2. **Night / Off-Peak Lulls:**
   - Between **12:00 AM and 05:00 AM**, traffic is minimal.
   - Average density drops down to ~0.23, and congestion stays strictly in the LOW to MEDIUM range with zero high/severe spikes.

3. **Junction Bottlenecks:**
   - **Junction 4** is the most congested bottleneck with an average density of 0.54, easily hitting 100% capacity due to its smaller limit (20 vehicles).
   - **Junction 2** is also fairly busy with a 0.47 average density.
   - **Junction 1** handles high volume well due to its 100-vehicle capacity.
   - **Junction 3** has the smoothest flow, averaging around 0.36 density.

---

### Density Rules Established for Milestone 1 Heuristics

Looking at the dataset labels, here are the exact density thresholds we can rely on for our rule-based predictor:
- **LOW Congestion:** Density < 0.30 (Typical average: ~0.18)
- **MEDIUM Congestion:** Density between 0.30 and 0.60 (Typical average: ~0.45)
- **HIGH Congestion:** Density between 0.61 and 0.80 (Typical average: ~0.70)
- **SEVERE Congestion:** Density ≥ 0.81 (Typical average: ~0.88)

---

### Next Steps (Day 3)
- Scaffold our AI Engine service using FastAPI.
- Set up the initial placeholder endpoint (`GET /api/v1/predict/congestion?road_id={id}`) returning `generated_by: "heuristic-v0"` so backend and frontend teammates can hook into it.