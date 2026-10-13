/**
 * TrafficVision AI - Production Runtime Configuration
 * Milestone 4 Deployment Configuration
 * 
 * In production cloud environments, set GATEWAY_URL to the public API Gateway
 * domain or cloud IP provided by Intern 1 on Day 3.
 */

window.__TRAFFICVISION_CONFIG__ = {
    // Production API Gateway URL (Render deployment)
    GATEWAY_URL: "https://trafficvision-ai-i8e2.onrender.com",

    // Optional discrete service overrides
    BASE_URL: "https://trafficvision-ai-i8e2.onrender.com/api/v1",
    ANALYTICS_BASE: "https://trafficvision-ai-i8e2.onrender.com/analytics",  // mounted by the backend
    AI_ENGINE_BASE: "https://trafficvision-ai-i8e2.onrender.com/ai-engine",  // mounted by the backend

    // Request timeout in milliseconds
    TIMEOUT: 15000,

    // Environment descriptor
    ENVIRONMENT: "production",
    VERSION: "1.0.0-m4"
};
