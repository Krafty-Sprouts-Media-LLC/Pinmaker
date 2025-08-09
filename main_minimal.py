#!/usr/bin/env python3
"""
Pinterest Template Generator - Minimal FastAPI Application
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

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
    BASE_DIR = Path("/opt/Pinmaker")
    UPLOAD_DIR = BASE_DIR / "uploads"
    API_PREFIX = "/api/v1"
    CORS_ORIGINS = ["*"]
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

config = Config()

# Ensure directories exist
config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Global service instances (minimal)
image_analyzer = None
template_generator = None
preview_generator = None
stock_photo_service = None
font_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Pinterest Template Generator (Minimal)...")
    
    # Skip heavy dependencies for now
    logger.info("Skipping heavy AI dependencies for minimal startup")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pinterest Template Generator...")

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

# Pydantic models
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

# API Routes
@app.get(f"{config.API_PREFIX}/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "image_analyzer": False,  # Disabled for minimal version
            "template_generator": False,
            "preview_generator": False,
            "stock_photo_service": False,
            "font_manager": False,
        },
    }

@app.options(f"{config.API_PREFIX}/analyze")
async def analyze_options():
    """Handle CORS preflight requests for analyze endpoint."""
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        }
    )

@app.post(f"{config.API_PREFIX}/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Minimal image analysis endpoint."""
    try:
        # Validate file
        if file.content_type not in config.ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Read file
        content = await file.read()
        if len(content) > config.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        # Generate analysis ID
        import uuid
        analysis_id = str(uuid.uuid4())

        # Minimal analysis (no heavy dependencies)
        try:
            from PIL import Image
            import io
            
            # Load image
            image = Image.open(io.BytesIO(content))
            width, height = image.size
            
            # Basic color analysis
            img_array = image.resize((100, 100))
            img_array = img_array.convert('RGB')
            
            # Simple color extraction
            colors = []
            try:
                import numpy as np
                img_np = np.array(img_array)
                pixels = img_np.reshape(-1, 3)
                unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
                top_colors = unique_colors[np.argsort(counts)[-5:]]
                
                for i, color in enumerate(top_colors):
                    hex_color = "#{:02x}{:02x}{:02x}".format(*color)
                    colors.append({"type": "dominant", "color": hex_color, "index": i})
            except:
                colors = [{"type": "fallback", "color": "#ffffff"}]

            # Return minimal analysis
            return JSONResponse(
                content={
                    "success": True,
                    "analysis_id": analysis_id,
                    "colors": colors,
                    "fonts": [],
                    "text_elements": [],
                    "image_regions": [],
                    "layout_structure": {
                        "layout_regions": [],
                        "grid_analysis": {"grid_detected": False},
                        "layout_type": "simple"
                    },
                    "background_info": {
                        "background_color": "#ffffff",
                        "background_type": "solid",
                        "background_variance": 0.0
                    },
                    "dimensions": {"width": width, "height": height},
                    "analysis_complete": True,
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Pinterest Template Generator API (Minimal)",
        "version": "1.0.0",
        "docs": "/api/docs",
        "frontend": "https://pinmaker-frontend.netlify.app",
    }

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
    )
