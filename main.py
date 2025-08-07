#!/usr/bin/env python3
"""
Pinterest Template Generator - Main FastAPI Application

This application serves both the React frontend and provides API endpoints
for image analysis, template generation, and preview creation.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
import uvicorn

# Import our custom modules
from src.image_analyzer import ImageAnalyzer
from src.template_generator import TemplateGenerator
from src.preview_generator import PreviewGenerator
from src.stock_photo_service import StockPhotoService
from src.font_manager import FontManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/opt/Pinmaker/logs/app.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# Application configuration
class Config:
    # Paths
    BASE_DIR = Path("/opt/Pinmaker")
    UPLOAD_DIR = BASE_DIR / "uploads"
    TEMPLATE_DIR = BASE_DIR / "templates"
    PREVIEW_DIR = BASE_DIR / "previews"
    FONT_DIR = BASE_DIR / "fonts"
    # FRONTEND_DIR removed - frontend now served by Netlify
    LOG_DIR = BASE_DIR / "logs"

    # File limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
    ALLOWED_FONT_TYPES = {
        "font/ttf",
        "font/otf",
        "application/font-woff",
        "application/font-woff2",
    }

    # API settings
    API_PREFIX = "/api/v1"
    CORS_ORIGINS = [
        "https://pinmaker.kraftysprouts.com",
        "http://localhost:3000",
        "https://*.netlify.app",  # Allow Netlify preview deployments
        "https://pinmaker-frontend.netlify.app",  # Your Netlify domain (update this)
    ]

    # Stock photo API keys (from environment)
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")


config = Config()

# Ensure directories exist
for directory in [
    config.UPLOAD_DIR,
    config.TEMPLATE_DIR,
    config.PREVIEW_DIR,
    config.FONT_DIR,
    config.LOG_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Global service instances
image_analyzer: Optional[ImageAnalyzer] = None
template_generator: Optional[TemplateGenerator] = None
preview_generator: Optional[PreviewGenerator] = None
stock_photo_service: Optional[StockPhotoService] = None
font_manager: Optional[FontManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Pinterest Template Generator...")

    global image_analyzer, template_generator, preview_generator, stock_photo_service, font_manager

    try:
        # Initialize services
        logger.info("Initializing AI services...")
        image_analyzer = ImageAnalyzer()
        template_generator = TemplateGenerator()

        stock_photo_service = StockPhotoService(
            unsplash_key=config.UNSPLASH_ACCESS_KEY,
            pexels_key=config.PEXELS_API_KEY,
            pixabay_key=config.PIXABAY_API_KEY,
        )

        preview_generator = PreviewGenerator(stock_photo_service)
        font_manager = FontManager(str(config.FONT_DIR))

        # Test API connections
        logger.info("Testing stock photo API connections...")
        await stock_photo_service.test_apis()

        logger.info("Application startup complete")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Pinterest Template Generator...")

    # Cleanup temporary files older than 1 hour
    try:
        import time

        current_time = time.time()
        for directory in [config.UPLOAD_DIR, config.TEMPLATE_DIR, config.PREVIEW_DIR]:
            for file_path in directory.glob("*"):
                if (
                    file_path.is_file()
                    and (current_time - file_path.stat().st_mtime) > 3600
                ):
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path}")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Pinterest Template Generator",
    description="AI-powered Pinterest template generation from images",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "pinmaker.kraftysprouts.com",
        "localhost",
        "*.netlify.app",
        "pinmaker-frontend.netlify.app",
        "pinmaker.netlify.app",
    ],
)


# Pydantic models for API requests/responses
class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    colors: list
    fonts: list
    text_elements: list
    image_regions: list
    layout_structure: dict
    background_info: dict
    message: str = ""


class TemplateRequest(BaseModel):
    analysis_id: str
    style: str = "modern"
    color_scheme: str = "original"


class TemplateResponse(BaseModel):
    success: bool
    template_id: str
    svg_content: str
    placeholders: list
    message: str = ""


class PreviewRequest(BaseModel):
    template_id: str
    sample_text: dict = {}
    stock_keywords: list = []
    style: str = "modern"
    format: str = "jpeg"
    quality: int = 85


class PreviewResponse(BaseModel):
    success: bool
    preview_id: str
    preview_url: str
    message: str = ""


# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "image_analyzer": image_analyzer is not None,
            "template_generator": template_generator is not None,
            "preview_generator": preview_generator is not None,
            "stock_photo_service": stock_photo_service is not None,
            "font_manager": font_manager is not None,
        },
    }


@app.post(f"{config.API_PREFIX}/analyze", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Analyze uploaded image and extract design elements."""
    try:
        # Validate file
        if file.content_type not in config.ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Read and save file
        content = await file.read()
        if len(content) > config.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        # Generate unique filename
        import uuid

        analysis_id = str(uuid.uuid4())
        file_path = config.UPLOAD_DIR / f"{analysis_id}.{file.filename.split('.')[-1]}"

        with open(file_path, "wb") as f:
            f.write(content)

        # Analyze image
        logger.info(f"Analyzing image: {file_path}")
        analysis_result = await asyncio.to_thread(
            image_analyzer.analyze_image, str(file_path)
        )

        return AnalysisResponse(
            success=True, analysis_id=analysis_id, **analysis_result
        )

    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{config.API_PREFIX}/generate-template", response_model=TemplateResponse)
async def generate_template(request: TemplateRequest):
    """Generate SVG template from analysis results."""
    try:
        # Load analysis results
        analysis_file = config.UPLOAD_DIR / f"{request.analysis_id}.json"
        if not analysis_file.exists():
            raise HTTPException(status_code=404, detail="Analysis not found")

        import json

        with open(analysis_file, "r") as f:
            analysis_data = json.load(f)

        # Generate template
        logger.info(f"Generating template for analysis: {request.analysis_id}")
        template_result = await asyncio.to_thread(
            template_generator.create_template,
            analysis_data,
            request.style,
            request.color_scheme,
        )

        # Save template
        import uuid

        template_id = str(uuid.uuid4())
        template_path = config.TEMPLATE_DIR / f"{template_id}.svg"

        with open(template_path, "w") as f:
            f.write(template_result["svg_content"])

        return TemplateResponse(
            success=True, template_id=template_id, **template_result
        )

    except Exception as e:
        logger.error(f"Error generating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{config.API_PREFIX}/generate-preview", response_model=PreviewResponse)
async def generate_preview(request: PreviewRequest):
    """Generate preview image from template."""
    try:
        # Load template
        template_path = config.TEMPLATE_DIR / f"{request.template_id}.svg"
        if not template_path.exists():
            raise HTTPException(status_code=404, detail="Template not found")

        with open(template_path, "r") as f:
            svg_content = f.read()

        # Generate preview
        logger.info(f"Generating preview for template: {request.template_id}")
        preview_result = await asyncio.to_thread(
            preview_generator.generate_preview,
            svg_content,
            request.sample_text,
            request.stock_keywords,
            request.style,
            request.format,
            request.quality,
        )

        # Save preview
        import uuid

        preview_id = str(uuid.uuid4())
        preview_path = config.PREVIEW_DIR / f"{preview_id}.{request.format}"

        with open(preview_path, "wb") as f:
            f.write(preview_result["image_data"])

        preview_url = f"/previews/{preview_id}.{request.format}"

        return PreviewResponse(
            success=True, preview_id=preview_id, preview_url=preview_url
        )

    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Font management endpoints
@app.post(f"{config.API_PREFIX}/fonts/upload")
async def upload_font(file: UploadFile = File(...)):
    """Upload custom font file."""
    try:
        if file.content_type not in config.ALLOWED_FONT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid font file type")

        content = await file.read()
        if len(content) > config.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Font file too large")

        result = await asyncio.to_thread(
            font_manager.register_font, file.filename, content
        )
        return {"success": True, **result}

    except Exception as e:
        logger.error(f"Error uploading font: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{config.API_PREFIX}/fonts")
async def list_fonts():
    """List available fonts."""
    try:
        fonts = await asyncio.to_thread(font_manager.list_fonts)
        return {"success": True, "fonts": fonts}
    except Exception as e:
        logger.error(f"Error listing fonts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# File serving endpoints
@app.get("/uploads/{filename}")
async def serve_upload(filename: str):
    """Serve uploaded files."""
    file_path = config.UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/templates/{filename}")
async def serve_template(filename: str):
    """Serve template files."""
    file_path = config.TEMPLATE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    return FileResponse(file_path, media_type="image/svg+xml")


@app.get("/previews/{filename}")
async def serve_preview(filename: str):
    """Serve preview files."""
    file_path = config.PREVIEW_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Preview not found")
    return FileResponse(file_path)


@app.get("/fonts/{filename}")
async def serve_font(filename: str):
    """Serve font files."""
    file_path = config.FONT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Font not found")
    return FileResponse(file_path)


# API-only backend - frontend served by Netlify
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Pinterest Template Generator API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "frontend": "https://pinmaker-frontend.netlify.app",  # Update with your Netlify URL
    }


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
    )
