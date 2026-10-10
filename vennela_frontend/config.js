/**
 * TrafficVision AI - Production Runtime Configuration
 * Milestone 4 Deployment Configuration
 * 
 * In production cloud environments, set GATEWAY_URL to the public API Gateway
 * domain or cloud IP provided by Intern 1 on Day 3.
 */

window.__TRAFFICVISION_CONFIG__ = {
    // Leave null or set to custom live gateway URL (e.g. "https://api.trafficvision.ai")
    // If null, api.js automatically defaults to origin or local development fallbacks.
    GATEWAY_URL: null,

    // Optional discrete service overrides (leave null to use unified Gateway)
    BASE_URL: null,         // e.g. "https://api.trafficvision.ai/api/v1"
    ANALYTICS_BASE: null,   // e.g. "https://api.trafficvision.ai/analytics"
    AI_ENGINE_BASE: null,   // e.g. "https://api.trafficvision.ai/ai-engine"

    // Request timeout in milliseconds
    TIMEOUT: 10000,

    // Environment descriptor
    ENVIRONMENT: "production",
    VERSION: "1.0.0-m4"
};
