// Core data types for the Pinterest Template Generator

export interface ColorInfo {
  hex: string;
  rgb: [number, number, number];
  percentage: number;
  name?: string;
}

export interface FontInfo {
  id: string;
  family_name: string;
  style_name: string;
  full_name: string;
  type: 'serif' | 'sans-serif' | 'monospace' | 'cursive' | 'fantasy';
  weight: string;
  italic: boolean;
  web_safe: boolean;
  format?: string;
  file_size?: number;
  uploaded_at?: string;
}

export interface TextElement {
  id: string;
  text: string;
  x: number;
  y: number;
  width: number;
  height: number;
  font_family: string;
  font_size: number;
  font_weight: string;
  color: string;
  alignment: 'left' | 'center' | 'right';
  line_height: number;
  letter_spacing: number;
  confidence: number;
  placeholder?: string;
}

export interface ImageRegion {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  type: 'photo' | 'illustration' | 'logo' | 'icon';
  confidence: number;
  placeholder?: string;
  description?: string;
}

export interface LayoutStructure {
  type: 'grid' | 'freeform' | 'centered' | 'asymmetric';
  columns: number;
  rows: number;
  sections: {
    id: string;
    x: number;
    y: number;
    width: number;
    height: number;
    type: 'header' | 'body' | 'footer' | 'sidebar' | 'content';
  }[];
}

export interface BackgroundInfo {
  type: 'solid' | 'gradient' | 'image' | 'pattern';
  primary_color: string;
  secondary_color?: string;
  gradient_direction?: number;
  texture?: string;
  opacity: number;
}

export interface AnalysisResult {
  id: string;
  filename: string;
  dimensions: {
    width: number;
    height: number;
  };
  colors: ColorInfo[];
  fonts: {
    detected: string[];
    suggested: FontInfo[];
  };
  text_elements: TextElement[];
  image_regions: ImageRegion[];
  layout: LayoutStructure;
  background: BackgroundInfo;
  analysis_time: number;
  confidence_score: number;
}

export interface TemplateData {
  id: string;
  svg_content: string;
  placeholders: {
    text: string[];
    images: string[];
  };
  editable_elements: {
    text_elements: TextElement[];
    image_regions: ImageRegion[];
    background: BackgroundInfo;
  };
  metadata: {
    width: number;
    height: number;
    created_at: string;
    based_on: string;
  };
}

export interface TemplateUpdate {
  colors?: {
    [elementId: string]: string;
  };
  fonts?: {
    [elementId: string]: {
      family: string;
      size?: number;
      weight?: string;
    };
  };
  positions?: {
    [elementId: string]: {
      x: number;
      y: number;
      width?: number;
      height?: number;
    };
  };
  content?: {
    text?: {
      [elementId: string]: string;
    };
    placeholders?: {
      [placeholder: string]: string;
    };
  };
}

export interface PreviewOptions {
  sample_text?: {
    [placeholder: string]: string;
  };
  sample_images?: {
    [placeholder: string]: string;
  };
  format: 'jpeg' | 'png';
  quality: number;
  width?: number;
  height?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface FontUploadResult {
  font_info: FontInfo;
  css_url?: string;
}

// Component Props Types
export interface ImageUploadProps {
  onImageAnalyzed: (result: AnalysisResult) => void;
  isLoading: boolean;
  onLoadingChange: (loading: boolean) => void;
}

export interface TemplateEditorProps {
  analysisResult: AnalysisResult;
  fonts: FontInfo[];
  onTemplateGenerated: (template: TemplateData) => void;
  onBack: () => void;
  isLoading: boolean;
  onLoadingChange: (loading: boolean) => void;
}

export interface PreviewPanelProps {
  templateData: TemplateData;
  previewUrl: string | null;
  onPreviewGenerated: (url: string) => void;
  onBack: () => void;
  onStartOver: () => void;
  isLoading: boolean;
  onLoadingChange: (loading: boolean) => void;
}

export interface FontManagerProps {
  fonts: FontInfo[];
  onFontsUpdated: (fonts: FontInfo[]) => void;
  onClose: () => void;
}

export interface ColorPickerProps {
  color: string;
  onChange: (color: string) => void;
  label?: string;
}

export interface FontSelectorProps {
  fonts: FontInfo[];
  selectedFont: string;
  onChange: (fontId: string) => void;
  label?: string;
}

export interface ElementEditorProps {
  element: TextElement | ImageRegion;
  fonts: FontInfo[];
  onUpdate: (updates: Partial<TextElement | ImageRegion>) => void;
  onDelete: () => void;
}

// API Endpoint Types
export interface AnalyzeImageRequest {
  file: File;
}

export interface GenerateTemplateRequest {
  analysis_id: string;
  customizations?: TemplateUpdate;
}

export interface UpdateTemplateRequest {
  template_id: string;
  updates: TemplateUpdate;
}

export interface GeneratePreviewRequest {
  template_id: string;
  options?: PreviewOptions;
}

export interface UploadFontRequest {
  file: File;
}

// Error Types
export interface ValidationError {
  field: string;
  message: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: ValidationError[];
}

// Utility Types
export type ElementType = 'text' | 'image' | 'background';
export type EditMode = 'select' | 'text' | 'image' | 'color';
export type ExportFormat = 'svg' | 'png' | 'jpeg' | 'pdf';

// Constants
export const SUPPORTED_IMAGE_FORMATS = ['image/jpeg', 'image/png', 'image/webp'] as const;
export const SUPPORTED_FONT_FORMATS = ['.ttf', '.otf', '.woff', '.woff2'] as const;
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const MAX_FONT_SIZE = 5 * 1024 * 1024; // 5MB

export type SupportedImageFormat = typeof SUPPORTED_IMAGE_FORMATS[number];
export type SupportedFontFormat = typeof SUPPORTED_FONT_FORMATS[number];