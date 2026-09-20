# Milestone 3 - Analytics Service Plan

## Day 1: Data Analysis

### Dataset
Historical traffic dataset contains 2688 records
covering 4 roads.

### Fields
- road_id
- timestamp
- vehicle_count
- density
- congestion_level

### Data Quality
No missing values were found.

### Congestion Distribution
- Low: 750 records (27.90%)
- Medium: 1055 records (39.25%)
- High: 883 records (32.85%)

### Density Analysis
Observed density ranges:

- Low: 0.15 - 0.39
- Medium: 0.40 - 0.69
- High: 0.70 - 1.48

### Road Coverage
Each of the four roads contains 672 records.

### Road-level Analysis
The dataset supports road-wise traffic analysis using
road_id, density, timestamp and congestion_level.

### Milestone 3 Preparation
The density and congestion_level fields can be used
as inputs for congestion-threshold monitoring and
traffic analytics.

## Planned Analytics
1. Traffic trend analysis
2. Congestion heatmap aggregation
3. Historical traffic reports
4. Congestion threshold monitoring