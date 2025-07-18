// filepath: c:\Users\20399\Desktop\VPN\frontend\src\config\api.js
// ===================================================================
// API Configuration File - Environment-specific API endpoint configuration
// Supports different configurations for development and production environments
// ===================================================================

// Get current environment
const isDevelopment = import.meta.env.MODE === 'development'
const isProduction = import.meta.env.MODE === 'production'

// API base configuration
export const API_CONFIG = {
  // Base URL configuration
  BASE_URL: isDevelopment 
    ? 'http://localhost:5000'  // Development: direct backend connection
    : '/api',                  // Production: via Nginx proxy

  // WebSocket configuration
  WEBSOCKET_URL: isDevelopment
    ? 'http://localhost:5000'  // Development: direct WebSocket connection
    : window.location.origin,  // Production: use current domain
  // Request timeout configuration
  TIMEOUT: 10000, // 10 seconds

  // Retry configuration
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second

  // API endpoint definitions
  ENDPOINTS: {
    // Proxy management
    PROXY_STATUS: '/api/proxy/status',
    PROXY_START: '/api/proxy/start',
    PROXY_STOP: '/api/proxy/stop',
    PROXY_TEST: '/api/proxy/test',
    
    // IP detection
    IP_CHECK: '/api/ip/check',
    IP_DETAILS: '/api/ip/details',
      // Connection monitoring
    CONNECTIONS: '/api/connections',
    
    // Health check
    HEALTH: '/health',
    READY: '/ready'
  }
}

// Environment information
export const ENV_INFO = {
  NODE_ENV: import.meta.env.MODE,
  DEV: isDevelopment,
  PROD: isProduction,
  BASE_URL: window.location.origin,
  BUILD_TIME: new Date().toISOString()
}

// HTTP status code definitions
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503
}

// Common HTTP request configuration
export const REQUEST_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: API_CONFIG.TIMEOUT
}

// API response status definitions
export const API_STATUS = {
  SUCCESS: 'success',
  ERROR: 'error',
  LOADING: 'loading',
  IDLE: 'idle'
}

// Log levels
export const LOG_LEVELS = {
  ERROR: 'error',
  WARN: 'warn',
  INFO: 'info',
  DEBUG: 'debug'
}

// Export default configuration
export default API_CONFIG
