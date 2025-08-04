import axios, { AxiosProgressEvent } from 'axios';
import {
  AnalysisResult,
  TemplateData,
  FontInfo,
  TemplateUpdate,
  PreviewOptions,
  ApiResponse,
  FontUploadResult
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000',
  timeout: 300000, // 5 minutes for analysis operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    
    // Handle common error cases
    if (error.response?.status === 413) {
      throw new Error('File too large. Please upload a smaller image.');
    }
    
    if (error.response?.status === 422) {
      const detail = error.response.data?.detail;
      if (Array.isArray(detail)) {
        throw new Error(detail.map((d: any) => d.msg).join(', '));
      }
      throw new Error(detail || 'Invalid request data');
    }
    
    if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.');
    }
    
    throw new Error(error.response?.data?.message || error.message || 'An error occurred');
  }
);

// Image Analysis API
export const analyzeImage = async (
  file: File,
  onProgress?: (percentage: number) => void
): Promise<AnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<ApiResponse<AnalysisResult>>('/api/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent: AxiosProgressEvent) => {
      if (progressEvent.total && onProgress) {
        const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentage);
      }
    },
  });

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Analysis failed');
  }

  return response.data.data;
};

// Template Generation API
export const generateTemplate = async (
  analysisId: string,
  customizations?: TemplateUpdate
): Promise<TemplateData> => {
  const response = await api.post<ApiResponse<TemplateData>>('/api/generate-template', {
    analysis_id: analysisId,
    customizations,
  });

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Template generation failed');
  }

  return response.data.data;
};

// Template Update API
export const updateTemplate = async (
  templateId: string,
  updates: TemplateUpdate
): Promise<TemplateData> => {
  const response = await api.put<ApiResponse<TemplateData>>(`/api/template/${templateId}`, {
    updates,
  });

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Template update failed');
  }

  return response.data.data;
};

// Preview Generation API
export const generatePreview = async (
  templateId: string,
  options?: PreviewOptions
): Promise<string> => {
  const response = await api.post<ApiResponse<{ preview_url: string }>>(
    `/api/generate-preview/${templateId}`,
    { options }
  );

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Preview generation failed');
  }

  return response.data.data.preview_url;
};

// Download Template API
export const downloadTemplate = async (templateId: string): Promise<Blob> => {
  const response = await api.get(`/api/download/template/${templateId}`, {
    responseType: 'blob',
  });

  return response.data;
};

// Download Preview API
export const downloadPreview = async (templateId: string): Promise<Blob> => {
  const response = await api.get(`/api/download/preview/${templateId}`, {
    responseType: 'blob',
  });

  return response.data;
};

// Font Management APIs
export const uploadFont = async (
  file: File,
  onProgress?: (percentage: number) => void
): Promise<FontUploadResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<ApiResponse<FontUploadResult>>('/api/fonts/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent: AxiosProgressEvent) => {
      if (progressEvent.total && onProgress) {
        const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentage);
      }
    },
  });

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Font upload failed');
  }

  return response.data.data;
};

export const listFonts = async (): Promise<FontInfo[]> => {
  const response = await api.get<ApiResponse<FontInfo[]>>('/api/fonts');

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to fetch fonts');
  }

  return response.data.data;
};

export const deleteFont = async (fontId: string): Promise<void> => {
  const response = await api.delete<ApiResponse<void>>(`/api/fonts/${fontId}`);

  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to delete font');
  }
};

export const getFontInfo = async (fontId: string): Promise<FontInfo> => {
  const response = await api.get<ApiResponse<FontInfo>>(`/api/fonts/${fontId}`);

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to fetch font info');
  }

  return response.data.data;
};

// Health Check API
export const healthCheck = async (): Promise<{ status: string; timestamp: string }> => {
  const response = await api.get<{ status: string; timestamp: string }>('/health');
  return response.data;
};

// Utility functions
export const createDownloadUrl = (blob: Blob, filename: string): string => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  return url;
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const validateImageFile = (file: File): { valid: boolean; error?: string } => {
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];

  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Please upload a JPEG, PNG, or WebP image'
    };
  }

  if (file.size > maxSize) {
    return {
      valid: false,
      error: `File size must be less than ${maxSize / (1024 * 1024)}MB`
    };
  }

  return { valid: true };
};

export const validateFontFile = (file: File): { valid: boolean; error?: string } => {
  const maxSize = 5 * 1024 * 1024; // 5MB
  const allowedExtensions = ['.ttf', '.otf', '.woff', '.woff2'];
  const fileName = file.name.toLowerCase();

  const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
  
  if (!hasValidExtension) {
    return {
      valid: false,
      error: 'Please upload a TTF, OTF, WOFF, or WOFF2 font file'
    };
  }

  if (file.size > maxSize) {
    return {
      valid: false,
      error: `Font file size must be less than ${maxSize / (1024 * 1024)}MB`
    };
  }

  return { valid: true };
};

// Error handling utility
export const handleApiError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

export default api;