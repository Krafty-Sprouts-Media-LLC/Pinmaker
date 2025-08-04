# Pinterest Template Generator - API Documentation

This document provides comprehensive documentation for the Pinterest Template Generator API.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Common Headers](#common-headers)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
- [Data Models](#data-models)
- [Examples](#examples)
- [SDKs and Libraries](#sdks-and-libraries)

## Overview

The Pinterest Template Generator API is a RESTful API built with FastAPI that provides endpoints for:

- Image analysis and template generation
- Stock photo search and integration
- Custom font management
- Template preview and export
- Health monitoring

### API Features

- **Async Processing**: All endpoints support asynchronous processing
- **File Upload**: Support for image uploads up to 10MB
- **Real-time Preview**: Generate previews in real-time
- **Multiple Formats**: Support for various image and font formats
- **Error Handling**: Comprehensive error responses with details
- **Rate Limiting**: Built-in rate limiting for API protection

## Authentication

Currently, the API does not require authentication for public endpoints. However, admin endpoints require an API key.

### Admin API Key

For admin endpoints, include the API key in the header:

```http
X-API-Key: your-admin-api-key
```

## Base URL

```
Production: https://pinmaker.kraftysprouts.com
Development: http://localhost:8000
```

## Common Headers

```http
Content-Type: application/json
Accept: application/json
User-Agent: YourApp/1.0
```

For file uploads:

```http
Content-Type: multipart/form-data
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `413` - Payload Too Large
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error
- `503` - Service Unavailable

### Common Error Codes

- `INVALID_FILE_TYPE` - Unsupported file format
- `FILE_TOO_LARGE` - File exceeds size limit
- `ANALYSIS_FAILED` - Image analysis failed
- `TEMPLATE_GENERATION_FAILED` - Template generation failed
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INVALID_API_KEY` - Invalid or missing API key

## Rate Limiting

### Limits

- **General API**: 100 requests per minute per IP
- **File Upload**: 10 uploads per minute per IP
- **Template Generation**: 20 generations per minute per IP

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## Endpoints

### Health Check

#### GET /health

Check the health status of the API.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "ai_models": "loaded",
    "storage": "available",
    "external_apis": "connected"
  }
}
```

### Image Analysis

#### POST /api/analyze

Analyze an uploaded image to extract text, colors, and layout information.

**Request:**

```http
POST /api/analyze
Content-Type: multipart/form-data

image: [binary file data]
options: {"detect_language": "en", "extract_colors": true}
```

**Parameters:**

- `image` (file, required): Image file (JPEG, PNG, WebP)
- `options` (JSON, optional): Analysis options

**Response:**

```json
{
  "analysis_id": "analysis_123456789",
  "image_info": {
    "width": 1080,
    "height": 1080,
    "format": "JPEG",
    "size_bytes": 245760
  },
  "text_elements": [
    {
      "id": "text_1",
      "text": "Hello World",
      "bbox": [100, 50, 300, 100],
      "confidence": 0.95,
      "font_size": 24,
      "font_weight": "bold",
      "color": "#000000"
    }
  ],
  "colors": {
    "dominant": "#FF6B6B",
    "palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
    "harmony": "complementary"
  },
  "layout": {
    "type": "grid",
    "regions": [
      {
        "id": "region_1",
        "bbox": [0, 0, 540, 540],
        "type": "text_area",
        "background_color": "#FFFFFF"
      }
    ],
    "grid": {
      "rows": 2,
      "columns": 2
    }
  },
  "confidence": 0.87,
  "processing_time": 2.34
}
```

### Template Generation

#### POST /api/generate-template

Generate a template based on analysis results and customizations.

**Request:**

```json
{
  "analysis_id": "analysis_123456789",
  "customizations": {
    "title": "Custom Title",
    "subtitle": "Custom Subtitle",
    "colors": {
      "primary": "#FF6B6B",
      "secondary": "#4ECDC4",
      "background": "#FFFFFF",
      "text": "#333333"
    },
    "fonts": {
      "title": "Roboto-Bold",
      "body": "Roboto-Regular"
    },
    "layout": {
      "style": "modern",
      "spacing": "comfortable"
    }
  },
  "stock_photos": [
    {
      "id": "photo_123",
      "url": "https://example.com/photo.jpg",
      "position": "background"
    }
  ],
  "dimensions": {
    "width": 1080,
    "height": 1080
  }
}
```

**Response:**

```json
{
  "template_id": "template_123456789",
  "svg_content": "<svg>...</svg>",
  "template_url": "/templates/template_123456789.svg",
  "preview_url": "/previews/template_123456789.png",
  "metadata": {
    "dimensions": {"width": 1080, "height": 1080},
    "elements_count": 5,
    "fonts_used": ["Roboto-Bold", "Roboto-Regular"],
    "colors_used": ["#FF6B6B", "#4ECDC4", "#FFFFFF"],
    "file_size": 15420
  },
  "generation_time": 1.23
}
```

### Preview Generation

#### POST /api/generate-preview

Generate a preview image of the template.

**Request:**

```json
{
  "template_id": "template_123456789",
  "format": "png",
  "quality": 90,
  "dimensions": {
    "width": 540,
    "height": 540
  }
}
```

**Response:**

```json
{
  "preview_id": "preview_123456789",
  "preview_url": "/previews/preview_123456789.png",
  "metadata": {
    "format": "PNG",
    "dimensions": {"width": 540, "height": 540},
    "file_size": 89432
  },
  "generation_time": 0.45
}
```

### Stock Photo Search

#### GET /api/stock-photos

Search for stock photos from multiple providers.

**Parameters:**

- `q` (string, required): Search query
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Results per page (default: 20, max: 50)
- `orientation` (string, optional): Image orientation (landscape, portrait, square)
- `category` (string, optional): Image category
- `color` (string, optional): Dominant color filter

**Example:**

```http
GET /api/stock-photos?q=nature&page=1&per_page=20&orientation=square
```

**Response:**

```json
{
  "query": "nature",
  "page": 1,
  "per_page": 20,
  "total_results": 1500,
  "total_pages": 75,
  "photos": [
    {
      "id": "photo_123",
      "url": "https://example.com/photo.jpg",
      "thumbnail_url": "https://example.com/thumb.jpg",
      "width": 1080,
      "height": 1080,
      "photographer": "John Doe",
      "source": "unsplash",
      "tags": ["nature", "forest", "green"],
      "color": "#4A7C59"
    }
  ]
}
```

### Font Management

#### POST /api/fonts/upload

Upload a custom font file.

**Request:**

```http
POST /api/fonts/upload
Content-Type: multipart/form-data

font: [binary font file]
name: "Custom Font"
category: "sans-serif"
```

**Response:**

```json
{
  "font_id": "font_123456789",
  "name": "Custom Font",
  "filename": "custom-font.ttf",
  "category": "sans-serif",
  "format": "TTF",
  "file_size": 45678,
  "font_url": "/fonts/custom-font.ttf",
  "metadata": {
    "family_name": "Custom Font",
    "style": "Regular",
    "weight": 400,
    "supported_characters": 256
  }
}
```

#### GET /api/fonts

List all available fonts.

**Parameters:**

- `category` (string, optional): Filter by category
- `search` (string, optional): Search by name

**Response:**

```json
{
  "fonts": [
    {
      "font_id": "font_123456789",
      "name": "Roboto",
      "category": "sans-serif",
      "variants": ["Regular", "Bold", "Italic"],
      "font_url": "/fonts/roboto.ttf",
      "preview_url": "/fonts/previews/roboto.png"
    }
  ],
  "total_count": 25
}
```

### Static File Serving

#### GET /uploads/{filename}

Serve uploaded image files.

#### GET /templates/{filename}

Serve generated template files.

#### GET /previews/{filename}

Serve preview image files.

#### GET /fonts/{filename}

Serve font files.

## Data Models

### AnalysisRequest

```typescript
interface AnalysisRequest {
  image: File;
  options?: {
    detect_language?: string;
    extract_colors?: boolean;
    analyze_layout?: boolean;
    confidence_threshold?: number;
  };
}
```

### TemplateRequest

```typescript
interface TemplateRequest {
  analysis_id: string;
  customizations?: {
    title?: string;
    subtitle?: string;
    colors?: {
      primary?: string;
      secondary?: string;
      background?: string;
      text?: string;
    };
    fonts?: {
      title?: string;
      body?: string;
    };
    layout?: {
      style?: 'modern' | 'classic' | 'minimal';
      spacing?: 'tight' | 'comfortable' | 'loose';
    };
  };
  stock_photos?: StockPhoto[];
  dimensions?: {
    width: number;
    height: number;
  };
}
```

### TextElement

```typescript
interface TextElement {
  id: string;
  text: string;
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
  confidence: number;
  font_size: number;
  font_weight?: string;
  font_style?: string;
  color: string;
  background_color?: string;
}
```

### ColorPalette

```typescript
interface ColorPalette {
  dominant: string;
  palette: string[];
  harmony: 'monochromatic' | 'analogous' | 'complementary' | 'triadic';
  temperature: 'warm' | 'cool' | 'neutral';
}
```

### Layout

```typescript
interface Layout {
  type: 'grid' | 'freeform' | 'centered' | 'asymmetric';
  regions: Region[];
  grid?: {
    rows: number;
    columns: number;
  };
  alignment: 'left' | 'center' | 'right';
}
```

### Region

```typescript
interface Region {
  id: string;
  bbox: [number, number, number, number];
  type: 'text_area' | 'image_area' | 'decoration';
  background_color?: string;
  border?: {
    width: number;
    color: string;
    style: 'solid' | 'dashed' | 'dotted';
  };
}
```

### StockPhoto

```typescript
interface StockPhoto {
  id: string;
  url: string;
  thumbnail_url: string;
  width: number;
  height: number;
  photographer: string;
  source: 'unsplash' | 'pexels' | 'pixabay';
  tags: string[];
  color: string;
  license: string;
}
```

### Font

```typescript
interface Font {
  font_id: string;
  name: string;
  filename: string;
  category: 'serif' | 'sans-serif' | 'monospace' | 'display' | 'handwriting';
  format: 'TTF' | 'OTF' | 'WOFF' | 'WOFF2';
  file_size: number;
  font_url: string;
  preview_url?: string;
  metadata: {
    family_name: string;
    style: string;
    weight: number;
    supported_characters: number;
  };
}
```

## Examples

### Complete Workflow Example

```javascript
// 1. Analyze an image
const formData = new FormData();
formData.append('image', imageFile);
formData.append('options', JSON.stringify({
  detect_language: 'en',
  extract_colors: true
}));

const analysisResponse = await fetch('/api/analyze', {
  method: 'POST',
  body: formData
});
const analysis = await analysisResponse.json();

// 2. Search for stock photos
const stockResponse = await fetch('/api/stock-photos?q=nature&orientation=square');
const stockPhotos = await stockResponse.json();

// 3. Generate template
const templateRequest = {
  analysis_id: analysis.analysis_id,
  customizations: {
    title: 'My Custom Title',
    colors: {
      primary: '#FF6B6B',
      secondary: '#4ECDC4'
    }
  },
  stock_photos: [stockPhotos.photos[0]]
};

const templateResponse = await fetch('/api/generate-template', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(templateRequest)
});
const template = await templateResponse.json();

// 4. Generate preview
const previewRequest = {
  template_id: template.template_id,
  format: 'png',
  dimensions: { width: 540, height: 540 }
};

const previewResponse = await fetch('/api/generate-preview', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(previewRequest)
});
const preview = await previewResponse.json();

console.log('Template URL:', template.template_url);
console.log('Preview URL:', preview.preview_url);
```

### Error Handling Example

```javascript
try {
  const response = await fetch('/api/analyze', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    
    switch (error.error_code) {
      case 'INVALID_FILE_TYPE':
        console.error('Please upload a valid image file');
        break;
      case 'FILE_TOO_LARGE':
        console.error('File is too large. Maximum size is 10MB');
        break;
      case 'RATE_LIMIT_EXCEEDED':
        console.error('Too many requests. Please try again later');
        break;
      default:
        console.error('An error occurred:', error.detail);
    }
    return;
  }
  
  const analysis = await response.json();
  // Process successful response
  
} catch (error) {
  console.error('Network error:', error);
}
```

### Rate Limiting Handling

```javascript
class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.requestQueue = [];
    this.isProcessing = false;
  }
  
  async makeRequest(endpoint, options) {
    return new Promise((resolve, reject) => {
      this.requestQueue.push({ endpoint, options, resolve, reject });
      this.processQueue();
    });
  }
  
  async processQueue() {
    if (this.isProcessing || this.requestQueue.length === 0) {
      return;
    }
    
    this.isProcessing = true;
    
    while (this.requestQueue.length > 0) {
      const { endpoint, options, resolve, reject } = this.requestQueue.shift();
      
      try {
        const response = await fetch(`${this.baseURL}${endpoint}`, options);
        
        if (response.status === 429) {
          // Rate limited, wait and retry
          const retryAfter = response.headers.get('Retry-After') || 60;
          await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
          this.requestQueue.unshift({ endpoint, options, resolve, reject });
          continue;
        }
        
        resolve(response);
      } catch (error) {
        reject(error);
      }
      
      // Add delay between requests
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    this.isProcessing = false;
  }
}
```

## SDKs and Libraries

### JavaScript/TypeScript SDK

```javascript
class PinmakerAPI {
  constructor(baseURL, apiKey = null) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
  }
  
  async analyzeImage(imageFile, options = {}) {
    const formData = new FormData();
    formData.append('image', imageFile);
    if (Object.keys(options).length > 0) {
      formData.append('options', JSON.stringify(options));
    }
    
    return this.makeRequest('/api/analyze', {
      method: 'POST',
      body: formData
    });
  }
  
  async generateTemplate(request) {
    return this.makeRequest('/api/generate-template', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
  }
  
  async searchStockPhotos(query, options = {}) {
    const params = new URLSearchParams({ q: query, ...options });
    return this.makeRequest(`/api/stock-photos?${params}`);
  }
  
  async makeRequest(endpoint, options = {}) {
    const headers = {
      ...options.headers
    };
    
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    
    return response.json();
  }
}

// Usage
const api = new PinmakerAPI('https://pinmaker.kraftysprouts.com');

// Analyze image
const analysis = await api.analyzeImage(imageFile, {
  detect_language: 'en',
  extract_colors: true
});

// Generate template
const template = await api.generateTemplate({
  analysis_id: analysis.analysis_id,
  customizations: {
    title: 'My Template'
  }
});
```

### Python SDK

```python
import requests
from typing import Dict, List, Optional

class PinmakerAPI:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def analyze_image(self, image_path: str, options: Optional[Dict] = None) -> Dict:
        """Analyze an image file."""
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {}
            
            if options:
                data['options'] = json.dumps(options)
            
            response = self.session.post(
                f'{self.base_url}/api/analyze',
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    def generate_template(self, request: Dict) -> Dict:
        """Generate a template."""
        response = self.session.post(
            f'{self.base_url}/api/generate-template',
            json=request
        )
        response.raise_for_status()
        return response.json()
    
    def search_stock_photos(self, query: str, **kwargs) -> Dict:
        """Search for stock photos."""
        params = {'q': query, **kwargs}
        response = self.session.get(
            f'{self.base_url}/api/stock-photos',
            params=params
        )
        response.raise_for_status()
        return response.json()

# Usage
api = PinmakerAPI('https://pinmaker.kraftysprouts.com')

# Analyze image
analysis = api.analyze_image('image.jpg', {
    'detect_language': 'en',
    'extract_colors': True
})

# Generate template
template = api.generate_template({
    'analysis_id': analysis['analysis_id'],
    'customizations': {
        'title': 'My Template'
    }
})
```

---

*This API documentation is automatically generated from the OpenAPI specification and is kept up-to-date with the latest API changes.*