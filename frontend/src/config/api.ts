// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_PREFIX = process.env.REACT_APP_API_PREFIX || '/api/v1';

export const API_ENDPOINTS = {
  ANALYZE: `${API_BASE_URL}${API_PREFIX}/analyze`,
  GENERATE_TEMPLATE: `${API_BASE_URL}${API_PREFIX}/generate-template`,
  GENERATE_PREVIEW: `${API_BASE_URL}${API_PREFIX}/generate-preview`,
  EXPORT: `${API_BASE_URL}${API_PREFIX}/export`,
  UPLOADS: `${API_BASE_URL}/uploads`,
  TEMPLATES: `${API_BASE_URL}/templates`,
  PREVIEWS: `${API_BASE_URL}/previews`,
  FONTS: `${API_BASE_URL}/fonts`
};

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  PREFIX: API_PREFIX,
  TIMEOUT: 30000, // 30 seconds
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
};

export default API_ENDPOINTS;