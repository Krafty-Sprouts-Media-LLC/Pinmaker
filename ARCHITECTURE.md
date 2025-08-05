# Pinterest Template Generator - System Architecture

This document provides a comprehensive overview of the Pinterest Template Generator's system architecture, design decisions, and implementation details.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Patterns](#architecture-patterns)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [AI/ML Pipeline](#aiml-pipeline)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Performance Considerations](#performance-considerations)
- [Deployment Architecture](#deployment-architecture)
- [Monitoring & Observability](#monitoring--observability)
- [Scalability Design](#scalability-design)
- [Technology Stack](#technology-stack)

## System Overview

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Mobile App    │    │  API Clients    │
│   (React SPA)   │    │   (Future)      │    │  (Third-party)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      Load Balancer        │
                    │       (Nginx)             │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │    FastAPI Application    │
                    │    (Python Backend)       │
                    └─────────────┬─────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
┌───────┴────────┐    ┌──────────┴──────────┐    ┌────────┴────────┐
│   AI/ML Engine │    │   File Storage      │    │   External APIs │
│   (Computer     │    │   (Local FS)       │    │   (Stock Photos)│
│    Vision)      │    │                     │    │                 │
└────────────────┘    └─────────────────────┘    └─────────────────┘
```

### Core Components

1. **Frontend Layer**: React TypeScript SPA with Tailwind CSS
2. **Backend Layer**: FastAPI Python application
3. **AI/ML Layer**: Computer vision and text analysis pipeline
4. **Storage Layer**: File-based storage for uploads, templates, and assets
5. **External Services**: Stock photo APIs and font services
6. **Infrastructure Layer**: Nginx, systemd, monitoring, and backup systems

## Architecture Patterns

### Design Patterns Used

1. **Model-View-Controller (MVC)**
   - Models: Pydantic models for data validation
   - Views: React components
   - Controllers: FastAPI route handlers

2. **Service Layer Pattern**
   - Separation of business logic from API endpoints
   - Dedicated services for AI, file handling, and external APIs

3. **Repository Pattern**
   - Abstraction layer for file storage operations
   - Easy to swap storage backends in the future

4. **Factory Pattern**
   - AI model initialization and management
   - Font loading and processing

5. **Observer Pattern**
   - Event-driven monitoring and logging
   - Real-time status updates

### Architectural Principles

- **Single Responsibility**: Each component has a clear, focused purpose
- **Dependency Injection**: Loose coupling between components
- **Configuration Management**: Environment-based configuration
- **Error Handling**: Comprehensive error handling and recovery
- **Logging & Monitoring**: Extensive observability throughout the system

## Backend Architecture

### FastAPI Application Structure

```
main.py
├── Application Configuration
├── Middleware Setup
├── Route Registration
├── Service Initialization
└── Static File Serving

Services/
├── ImageAnalyzer
│   ├── Computer Vision Pipeline
│   ├── Text Detection (EasyOCR)
│   ├── Color Analysis (ColorThief)
│   └── Layout Detection
├── TemplateGenerator
│   ├── SVG Generation
│   ├── Layout Recreation
│   └── Style Application
├── PreviewGenerator
│   ├── Real-time Rendering
│   └── Export Functionality
├── StockPhotoService
│   ├── Multi-provider Integration
│   └── Search & Caching
└── FontManager
    ├── Font Upload & Validation
    ├── Font Embedding
    └── Font Library Management
```

### API Design

#### RESTful Endpoints

```
GET  /health                    # Health check
POST /api/analyze              # Image analysis
POST /api/generate-template    # Template generation
POST /api/generate-preview     # Preview generation
GET  /api/stock-photos         # Stock photo search
POST /api/fonts/upload         # Font upload
GET  /api/fonts                # List fonts
GET  /uploads/{filename}       # Serve uploaded files
GET  /templates/{filename}     # Serve generated templates
GET  /previews/{filename}      # Serve preview images
GET  /fonts/{filename}         # Serve font files
```

#### Request/Response Models

```python
# Analysis Request
class AnalysisRequest(BaseModel):
    image_data: str  # Base64 encoded image
    options: Optional[Dict[str, Any]] = {}

# Template Request
class TemplateRequest(BaseModel):
    analysis_id: str
    customizations: Optional[Dict[str, Any]] = {}
    stock_photos: Optional[List[str]] = []
    fonts: Optional[List[str]] = []

# Response Models
class AnalysisResponse(BaseModel):
    analysis_id: str
    elements: List[ElementData]
    layout: LayoutData
    colors: ColorPalette
    fonts: List[FontData]
    confidence: float
```

### Service Layer Architecture

#### ImageAnalyzer Service

```python
class ImageAnalyzer:
    def __init__(self):
        self.text_detector = easyocr.Reader(['en'])
        self.color_extractor = ColorThief()
        self.layout_analyzer = LayoutAnalyzer()
    
    async def analyze_image(self, image_path: str) -> AnalysisResult:
        # Multi-stage analysis pipeline
        text_elements = await self.detect_text(image_path)
        colors = await self.extract_colors(image_path)
        layout = await self.analyze_layout(image_path)
        
        return AnalysisResult(
            text_elements=text_elements,
            colors=colors,
            layout=layout
        )
```

#### TemplateGenerator Service

```python
class TemplateGenerator:
    def __init__(self):
        self.svg_builder = SVGBuilder()
        self.layout_engine = LayoutEngine()
    
    async def generate_template(self, analysis: AnalysisResult, 
                              customizations: Dict) -> Template:
        # Template generation pipeline
        layout = self.layout_engine.create_layout(analysis.layout)
        elements = self.create_elements(analysis.text_elements)
        styles = self.apply_styles(analysis.colors, customizations)
        
        return self.svg_builder.build_template(layout, elements, styles)
```

## Frontend Architecture

### React Application Structure

```
src/
├── components/
│   ├── common/           # Reusable UI components
│   ├── upload/           # File upload components
│   ├── analysis/         # Analysis display components
│   ├── template/         # Template editing components
│   ├── preview/          # Preview components
│   └── fonts/            # Font management components
├── hooks/                # Custom React hooks
├── services/             # API service layer
├── stores/               # State management
├── types/                # TypeScript type definitions
├── utils/                # Utility functions
└── styles/               # Global styles and themes
```

### Component Architecture

#### State Management

```typescript
// Using React Context + useReducer for global state
interface AppState {
  currentImage: ImageData | null;
  analysisResult: AnalysisResult | null;
  template: Template | null;
  customizations: Customizations;
  fonts: Font[];
  stockPhotos: StockPhoto[];
  loading: LoadingState;
  errors: ErrorState;
}

// Actions for state updates
type AppAction = 
  | { type: 'SET_IMAGE'; payload: ImageData }
  | { type: 'SET_ANALYSIS'; payload: AnalysisResult }
  | { type: 'UPDATE_CUSTOMIZATIONS'; payload: Partial<Customizations> }
  | { type: 'SET_LOADING'; payload: LoadingState }
  | { type: 'SET_ERROR'; payload: ErrorState };
```

#### Component Hierarchy

```
App
├── Header
├── MainContent
│   ├── UploadSection
│   │   ├── ImageUploader
│   │   └── UploadProgress
│   ├── AnalysisSection
│   │   ├── AnalysisDisplay
│   │   ├── ElementList
│   │   └── ColorPalette
│   ├── CustomizationSection
│   │   ├── FontSelector
│   │   ├── ColorPicker
│   │   ├── StockPhotoSearch
│   │   └── LayoutAdjuster
│   └── PreviewSection
│       ├── TemplatePreview
│       ├── ExportOptions
│       └── DownloadButton
└── Footer
```

### API Service Layer

```typescript
class ApiService {
  private baseURL: string;
  private httpClient: AxiosInstance;
  
  async analyzeImage(imageFile: File): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await this.httpClient.post('/api/analyze', formData);
    return response.data;
  }
  
  async generateTemplate(request: TemplateRequest): Promise<Template> {
    const response = await this.httpClient.post('/api/generate-template', request);
    return response.data;
  }
  
  async searchStockPhotos(query: string): Promise<StockPhoto[]> {
    const response = await this.httpClient.get(`/api/stock-photos?q=${query}`);
    return response.data;
  }
}
```

## AI/ML Pipeline

### Computer Vision Pipeline

```
Input Image
    ↓
┌─────────────────┐
│ Preprocessing   │ ← Image resizing, normalization
└─────────┬───────┘
          ↓
┌─────────────────┐
│ Text Detection  │ ← EasyOCR for text recognition
└─────────┬───────┘
          ↓
┌─────────────────┐
│ Color Analysis  │ ← ColorThief for dominant colors
└─────────┬───────┘
          ↓
┌─────────────────┐
│ Layout Analysis │ ← Custom CV pipeline
└─────────┬───────┘
          ↓
┌─────────────────┐
│ Element         │ ← Combine all analysis results
│ Classification  │
└─────────┬───────┘
          ↓
    Analysis Result
```

### Text Detection Implementation

```python
class TextDetector:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
    
    def detect_text(self, image_path: str) -> List[TextElement]:
        results = self.reader.readtext(image_path)
        
        text_elements = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Filter low-confidence detections
                element = TextElement(
                    text=text,
                    bbox=self._normalize_bbox(bbox),
                    confidence=confidence,
                    font_size=self._estimate_font_size(bbox),
                    style=self._analyze_text_style(text)
                )
                text_elements.append(element)
        
        return text_elements
```

### Layout Analysis Algorithm

```python
class LayoutAnalyzer:
    def analyze_layout(self, image: np.ndarray, 
                      text_elements: List[TextElement]) -> Layout:
        # 1. Grid-based segmentation
        grid = self._create_grid(image.shape, grid_size=20)
        
        # 2. Color-based region detection
        regions = self._detect_regions_by_color(image, grid)
        
        # 3. Text-based element grouping
        text_groups = self._group_text_elements(text_elements)
        
        # 4. Spatial relationship analysis
        relationships = self._analyze_spatial_relationships(regions, text_groups)
        
        # 5. Layout classification
        layout_type = self._classify_layout(relationships)
        
        return Layout(
            type=layout_type,
            regions=regions,
            text_groups=text_groups,
            relationships=relationships
        )
```

### Color Analysis

```python
class ColorAnalyzer:
    def extract_color_palette(self, image_path: str) -> ColorPalette:
        color_thief = ColorThief(image_path)
        
        # Extract dominant colors
        dominant_color = color_thief.get_color(quality=1)
        palette = color_thief.get_palette(color_count=8, quality=1)
        
        # Analyze color harmony
        harmony = self._analyze_color_harmony(palette)
        
        # Generate complementary colors
        complementary = self._generate_complementary_colors(dominant_color)
        
        return ColorPalette(
            dominant=dominant_color,
            palette=palette,
            harmony=harmony,
            complementary=complementary
        )
```

## Data Flow

### Image Analysis Flow

```
1. User uploads image
   ↓
2. Frontend validates file
   ↓
3. Image sent to backend
   ↓
4. Backend saves to uploads/
   ↓
5. AI pipeline processes image
   ├── Text detection
   ├── Color analysis
   └── Layout analysis
   ↓
6. Analysis results returned
   ↓
7. Frontend displays results
```

### Template Generation Flow

```
1. User customizes template
   ↓
2. Frontend sends generation request
   ↓
3. Backend processes request
   ├── Applies customizations
   ├── Integrates stock photos
   └── Embeds custom fonts
   ↓
4. SVG template generated
   ↓
5. Template saved to templates/
   ↓
6. Template URL returned
   ↓
7. Frontend displays template
```

### Real-time Preview Flow

```
1. User makes changes
   ↓
2. Frontend debounces changes
   ↓
3. Preview request sent
   ↓
4. Backend generates preview
   ↓
5. Preview image created
   ↓
6. Preview URL returned
   ↓
7. Frontend updates preview
```

## Security Architecture

### Security Layers

1. **Network Security**
   - HTTPS/TLS encryption
   - Firewall configuration
   - DDoS protection

2. **Application Security**
   - Input validation
   - File type restrictions
   - Size limitations
   - CORS configuration

3. **Data Security**
   - Temporary file cleanup
   - Secure file storage
   - No persistent user data

4. **Infrastructure Security**
   - Fail2ban intrusion detection
   - Regular security updates
   - Monitoring and alerting

### Security Implementation

```python
# File validation
def validate_upload(file: UploadFile) -> bool:
    # Check file size
    if file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(413, "File too large")
    
    # Check file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "Invalid file type")
    
    # Check file extension
    ext = file.filename.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "File extension not allowed")
    
    return True

# Rate limiting
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    
    if await is_rate_limited(client_ip):
        raise HTTPException(429, "Rate limit exceeded")
    
    response = await call_next(request)
    return response
```

## Performance Considerations

### Backend Optimization

1. **Async Processing**
   - All I/O operations are async
   - Concurrent request handling
   - Non-blocking AI processing

2. **Caching Strategy**
   - In-memory caching for AI models
   - File-based caching for results
   - CDN for static assets

3. **Resource Management**
   - Connection pooling
   - Memory management
   - GPU utilization (when available)

### Frontend Optimization

1. **Code Splitting**
   - Lazy loading of components
   - Dynamic imports
   - Bundle optimization

2. **Asset Optimization**
   - Image compression
   - Font subsetting
   - CSS purging

3. **State Management**
   - Efficient re-rendering
   - Memoization
   - Virtual scrolling

### Performance Monitoring

```python
# Performance middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 5.0:
        logger.warning(f"Slow request: {request.url} took {process_time:.2f}s")
    
    return response
```

## Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Server                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Nginx     │  │  Gunicorn   │  │   Python    │        │
│  │ (Reverse    │  │ (WSGI       │  │ Application │        │
│  │  Proxy)     │  │  Server)    │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   systemd   │  │   Fail2ban  │  │  Monitoring │        │
│  │  (Service   │  │ (Security)  │  │   Scripts   │        │
│  │ Management) │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    File System                              │
│  /opt/Pinmaker/                                             │
│  ├── app/          (Application code)                      │
│  ├── uploads/      (User uploads)                          │
│  ├── templates/    (Generated templates)                   │
│  ├── previews/     (Preview images)                        │
│  ├── fonts/        (Custom fonts)                          │
│  ├── logs/         (Application logs)                      │
│  └── backups/      (System backups)                        │
└─────────────────────────────────────────────────────────────┘
```

### Service Configuration

```ini
# systemd service configuration
[Unit]
Description=Pinterest Template Generator
After=network.target

[Service]
Type=exec
User=pinmaker
Group=pinmaker
WorkingDirectory=/opt/Pinmaker
Environment=PATH=/opt/Pinmaker/venv/bin
ExecStart=/opt/Pinmaker/venv/bin/gunicorn main:app -c gunicorn.conf.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Monitoring & Observability

### Monitoring Stack

1. **System Monitoring**
   - CPU, memory, disk usage
   - Network performance
   - Service health checks

2. **Application Monitoring**
   - Request/response metrics
   - Error rates and types
   - Performance metrics

3. **Business Metrics**
   - Template generation success rate
   - User engagement metrics
   - AI model performance

### Logging Strategy

```python
# Structured logging
import structlog

logger = structlog.get_logger()

# Request logging
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    logger.info(
        "request_started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host
    )
    
    response = await call_next(request)
    
    logger.info(
        "request_completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration=time.time() - start_time
    )
    
    return response
```

### Alerting System

```bash
# Alert conditions
- CPU usage > 80% for 5 minutes
- Memory usage > 85% for 5 minutes
- Disk usage > 90%
- Service downtime > 1 minute
- Error rate > 5% for 10 minutes
- Response time > 10 seconds
```

## Scalability Design

### Horizontal Scaling Options

1. **Load Balancing**
   - Multiple application instances
   - Session-less design
   - Shared file storage

2. **Microservices Migration**
   - Separate AI processing service
   - Dedicated file storage service
   - Independent scaling

3. **Cloud Migration**
   - Container deployment
   - Auto-scaling groups
   - Managed services

### Vertical Scaling

1. **Resource Optimization**
   - GPU acceleration for AI
   - SSD storage for performance
   - Memory optimization

2. **Caching Layers**
   - Redis for session storage
   - CDN for static assets
   - Application-level caching

## Technology Stack

### Backend Technologies

- **Framework**: FastAPI 0.104+
- **Language**: Python 3.12+
- **AI/ML**: PyTorch, Ultralytics, EasyOCR, OpenCV
- **Image Processing**: Pillow, ColorThief, scikit-image
- **Font Handling**: fontTools, Wand
- **HTTP Client**: httpx, aiohttp
- **Validation**: Pydantic
- **Async**: asyncio, uvloop

### Frontend Technologies

- **Framework**: React 18+
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3+
- **Build Tool**: Vite 5+
- **State Management**: React Context + useReducer
- **HTTP Client**: Axios
- **UI Components**: Custom components

### Infrastructure Technologies

- **Web Server**: Nginx 1.20+
- **WSGI Server**: Gunicorn
- **Process Manager**: systemd
- **Security**: Fail2ban, UFW
- **SSL**: Let's Encrypt (Certbot)
- **Monitoring**: Custom scripts
- **Backup**: Custom backup system

### Development Tools

- **Version Control**: Git
- **Code Quality**: ESLint, Prettier, Black
- **Testing**: pytest, Jest
- **Documentation**: Markdown
- **Deployment**: Custom deployment scripts

---

*This architecture document is maintained alongside the codebase and should be updated when significant architectural changes are made.*