from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
from PIL import Image
import io
import logging
from image_analyzer import ImageAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pinmaker API",
    description="AI-powered Pinterest template generator",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://pinmaker.netlify.app",
        "https://pinmaker.kraftysprouts.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the image analyzer
image_analyzer = ImageAnalyzer()

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    message: str

class ColorInfo(BaseModel):
    hex: str
    rgb: List[int]
    name: str
    percentage: float

class FontInfo(BaseModel):
    family: str
    size: int
    weight: str
    style: str
    color: str

class TextElement(BaseModel):
    text: str
    position: Dict[str, int]
    font: FontInfo
    confidence: float

class LayoutStructure(BaseModel):
    type: str
    position: Dict[str, int]
    size: Dict[str, int]
    content_type: str

class ImageRegion(BaseModel):
    type: str
    position: Dict[str, int]
    size: Dict[str, int]
    description: str
    confidence: float

class BackgroundInfo(BaseModel):
    type: str
    dominant_color: str
    pattern: Optional[str] = None
    texture: Optional[str] = None

class Dimensions(BaseModel):
    width: int
    height: int
    aspect_ratio: str

class AnalysisResponse(BaseModel):
    dimensions: Dimensions
    colors: List[ColorInfo]
    fonts: List[FontInfo]
    text_elements: List[TextElement]
    layout_structure: List[LayoutStructure]
    image_regions: List[ImageRegion]
    background: BackgroundInfo
    design_style: str
    complexity_score: float
    template_suggestions: List[str]

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        message="Pinmaker API is running"
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Pinmaker API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Image analysis endpoint
@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Validate file
        if not file:
            raise HTTPException(status_code=422, detail="No file provided")
        
        if not file.filename:
            raise HTTPException(status_code=422, detail="No file selected")
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read and validate image
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=422, detail="Empty file")
        
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()  # Verify it's a valid image
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # Reset file pointer and reopen for analysis
        image = Image.open(io.BytesIO(contents))
        
        # Analyze the image
        logger.info(f"Analyzing image: {file.filename}")
        analysis_result = image_analyzer.analyze_image(image)
        
        # Convert the analysis result to match AnalysisResponse format
        response_data = {
            "dimensions": analysis_result["dimensions"],
            "colors": list(analysis_result["colors"]) if isinstance(analysis_result["colors"], dict) else analysis_result["colors"],
            "fonts": list(analysis_result["fonts"]) if isinstance(analysis_result["fonts"], dict) else analysis_result["fonts"],
            "text_elements": analysis_result["text_elements"],
            "layout_structure": analysis_result["layout_structure"],
            "image_regions": analysis_result["image_regions"],
            "background": analysis_result["background"],
            "design_style": analysis_result["design_style"],
            "complexity_score": analysis_result["complexity_score"],
            "template_suggestions": analysis_result["template_suggestions"]
        }
        
        return AnalysisResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
