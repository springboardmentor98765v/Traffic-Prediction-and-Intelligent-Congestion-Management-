# TrafficVision AI - API Contracts (Milestone 1)

## 1. Authentication Service
* POST /api/v1/auth/register 
  - Input: { name, email, password, role } 
  - Output: 201 { user_id }
* POST /api/v1/auth/login 
  - Input: { email, password } 
  - Output: 200 { access_token, refresh_token, role }
* POST /api/v1/auth/refresh 
  - Input: { refresh_token } 
  - Output: 200 { access_token }
* GET /api/v1/auth/me 
  - Header: Bearer token 
  - Output: 200 { user_id, name, role }

## 2. Traffic Monitoring Service
* GET /api/v1/traffic/live 
  - Output: 200 [ { road_id, vehicle_count, density, congestion_level, updated_at } ]
* GET /api/v1/traffic/road/{road_id} 
  - Output: 200 { road_id, name, congestion_level, history[] }
* GET /api/v1/traffic/density 
  - Output: 200 aggregated density metrics for dashboard KPIs

## 3. AI Engine Service (ML Inference)
* POST /api/v1/predict/congestion 
  - Input: { vehicle_count, density, avg_speed_kmph, road_capacity, road_length_km }
  - Output: 200 { predicted_level, confidence, generated_by }