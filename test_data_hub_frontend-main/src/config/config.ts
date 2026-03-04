// Configuration service for environment variables
export interface AppConfig {
  api: {
    baseUrl: string;
    wsUrl: string;
  };
  app: {
    name: string;
    version: string;
    environment: string;
  };
  features: {
    analytics: boolean;
    debugMode: boolean;
  };
  cors: {
    allowedOrigins: string[];
  };
}

// Load environment variables with fallbacks
const loadConfig = (): AppConfig => {
  // API Configuration
  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
  const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
  
  // App Configuration
  const appName = process.env.REACT_APP_APP_NAME || 'Test Data Environment';
  const appVersion = process.env.REACT_APP_APP_VERSION || '1.0.0';
  const appEnvironment = process.env.REACT_APP_APP_ENVIRONMENT || 'development';
  
  // Feature Flags
  const enableAnalytics = process.env.REACT_APP_ENABLE_ANALYTICS === 'true';
  const enableDebugMode = process.env.REACT_APP_ENABLE_DEBUG_MODE === 'true';
  
  // CORS Configuration
  const allowedOrigins = process.env.REACT_APP_ALLOWED_ORIGINS 
    ? process.env.REACT_APP_ALLOWED_ORIGINS.split(',').map(origin => origin.trim())
    : ['http://localhost:3000'];

  return {
    api: {
      baseUrl: apiBaseUrl,
      wsUrl: wsUrl,
    },
    app: {
      name: appName,
      version: appVersion,
      environment: appEnvironment,
    },
    features: {
      analytics: enableAnalytics,
      debugMode: enableDebugMode,
    },
    cors: {
      allowedOrigins,
    },
  };
};

// Export the configuration
export const config = loadConfig();

// Export individual config sections for convenience
export const { api, app, features, cors } = config;

// Export a function to get the current config (useful for runtime updates)
export const getConfig = (): AppConfig => config;

// Export a function to check if we're in production
export const isProduction = (): boolean => app.environment === 'production';

// Export a function to check if we're in development
export const isDevelopment = (): boolean => app.environment === 'development';

// Export a function to get the API base URL
export const getApiBaseUrl = (): string => api.baseUrl;

// Export a function to get the WebSocket URL
export const getWsUrl = (): string => api.wsUrl;
