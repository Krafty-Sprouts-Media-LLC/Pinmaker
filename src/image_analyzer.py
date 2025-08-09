import cv2
import numpy as np
import easyocr
from colorthief import ColorThief
from PIL import Image, ImageFont, ImageDraw
import torch
from ultralytics import YOLO
from sklearn.cluster import KMeans
import os
import tempfile
from typing import Dict, List, Tuple, Any
import json
from pathlib import Path


class ImageAnalyzer:
    def __init__(self):
        self.ocr_reader = easyocr.Reader(["en"])
        # Initialize YOLO for object detection (helps with layout analysis)

        try:
            self.yolo_model = YOLO("yolov8n.pt")  # Lightweight model for speed
        except:
            self.yolo_model = None
            print("Warning: YOLO model not available, using fallback detection")

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Comprehensive image analysis for template generation"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Get image dimensions
            height, width = image.shape[:2]

            # Try lightweight analysis first (faster, less resource intensive)
            try:
                return self._analyze_image_lightweight(image_path, width, height)
            except Exception as light_error:
                print(f"Lightweight analysis failed, trying full analysis: {light_error}")
                # Fall back to full analysis
                return self._analyze_image_full(image_path, width, height)
                
        except Exception as e:
            raise Exception(f"Image analysis failed: {str(e)}")

    def _analyze_image_lightweight(self, image_path: str, width: int, height: int) -> Dict[str, Any]:
        """Lightweight analysis without heavy AI dependencies"""
        try:
            # Basic color extraction using PIL (faster than ColorThief)
            from PIL import Image
            import numpy as np
            
            pil_image = Image.open(image_path)
            pil_image = pil_image.resize((100, 100))  # Resize for speed
            img_array = np.array(pil_image)
            
            # Simple color analysis
            colors_list = []
            try:
                # Get dominant colors using simple method
                pixels = img_array.reshape(-1, 3)
                unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
                top_colors = unique_colors[np.argsort(counts)[-5:]]  # Top 5 colors
                
                for i, color in enumerate(top_colors):
                    hex_color = "#{:02x}{:02x}{:02x}".format(*color)
                    colors_list.append({"type": "dominant", "color": hex_color, "index": i})
            except:
                colors_list = [{"type": "fallback", "color": "#ffffff"}]

            # Basic font/text analysis (no OCR)
            fonts_list = []
            
            # Basic layout analysis
            layout_structure = {
                "layout_regions": [],
                "grid_analysis": {"grid_detected": False},
                "layout_type": "simple"
            }
            
            # Basic background analysis
            background_info = {
                "background_color": "#ffffff",
                "background_type": "solid",
                "background_variance": 0.0
            }
            
            return {
                "dimensions": {"width": width, "height": height},
                "colors": colors_list,
                "fonts": fonts_list,
                "text_elements": [],
                "layout_structure": layout_structure,
                "image_regions": [],
                "background_info": background_info,
                "analysis_complete": True,
            }
        except Exception as e:
            raise Exception(f"Lightweight analysis failed: {str(e)}")

    def _analyze_image_full(self, image_path: str, width: int, height: int) -> Dict[str, Any]:
        """Full analysis with all AI dependencies"""
        # Perform all analysis tasks (synchronously for thread execution)
        colors_data = self._extract_colors(image_path)
        fonts_data = self._detect_fonts(cv2.imread(image_path))
        text_elements = self._extract_text(cv2.imread(image_path))
        layout_structure = self._analyze_layout(cv2.imread(image_path))
        image_regions = self._detect_image_regions(cv2.imread(image_path))
        background_info = self._analyze_background(cv2.imread(image_path))

        # Convert to expected Pydantic format
        # colors should be a list, fonts should be a list
        colors_list = []
        if isinstance(colors_data, dict) and "error" not in colors_data:
            # Extract color information into list format
            if "dominant_color" in colors_data:
                colors_list.append({"type": "dominant", "color": colors_data["dominant_color"]})
            if "palette" in colors_data:
                for i, color in enumerate(colors_data["palette"]):
                    colors_list.append({"type": "palette", "color": color, "index": i})
            if "cluster_colors" in colors_data:
                for i, color in enumerate(colors_data["cluster_colors"]):
                    colors_list.append({"type": "cluster", "color": color, "index": i})
        else:
            # Fallback if color extraction failed
            colors_list = [{"type": "fallback", "color": "#ffffff"}]

        # Convert fonts data to list format
        fonts_list = []
        if isinstance(fonts_data, dict) and "error" not in fonts_data:
            if "detected_fonts" in fonts_data:
                fonts_list = fonts_data["detected_fonts"]
        else:
            # Fallback if font detection failed
            fonts_list = []

        return {
            "dimensions": {"width": width, "height": height},
            "colors": colors_list,
            "fonts": fonts_list,
            "text_elements": text_elements,
            "layout_structure": layout_structure,
            "image_regions": image_regions,
            "background_info": background_info,
            "analysis_complete": True,
        }

    def _extract_colors(self, image_path: str) -> Dict[str, Any]:
        """Extract dominant colors from the image"""
        try:
            # Use ColorThief for dominant colors

            color_thief = ColorThief(image_path)
            dominant_color = color_thief.get_color(quality=1)
            palette = color_thief.get_palette(color_count=8, quality=1)

            # Convert to hex

            dominant_hex = "#{:02x}{:02x}{:02x}".format(*dominant_color)
            palette_hex = ["#{:02x}{:02x}{:02x}".format(*color) for color in palette]

            # Additional color analysis using OpenCV

            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Reshape for clustering

            pixels = image_rgb.reshape(-1, 3)

            # Use KMeans to find color clusters

            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)

            cluster_colors = kmeans.cluster_centers_.astype(int)
            cluster_hex = [
                "#{:02x}{:02x}{:02x}".format(*color) for color in cluster_colors
            ]

            return {
                "dominant_color": dominant_hex,
                "palette": palette_hex,
                "cluster_colors": cluster_hex,
                "color_analysis": "high_accuracy",
            }
        except Exception as e:
            return {"error": f"Color extraction failed: {str(e)}"}

    def _detect_fonts(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect and analyze fonts in the image"""
        try:
            # Convert to grayscale for text analysis

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Use OCR to get text regions with confidence

            ocr_results = self.ocr_reader.readtext(gray, detail=1)

            font_info = []
            for bbox, text, confidence in ocr_results:
                if confidence > 0.5:  # Filter low confidence detections
                    # Extract text region

                    x1, y1 = int(min([point[0] for point in bbox])), int(
                        min([point[1] for point in bbox])
                    )
                    x2, y2 = int(max([point[0] for point in bbox])), int(
                        max([point[1] for point in bbox])
                    )

                    # Calculate text properties

                    text_height = y2 - y1
                    text_width = x2 - x1

                    # Estimate font size (rough approximation)

                    estimated_font_size = max(12, int(text_height * 0.8))

                    # Analyze text characteristics

                    char_density = len(text) / max(text_width, 1)

                    font_info.append(
                        {
                            "text": text,
                            "bbox": [x1, y1, x2, y2],
                            "estimated_size": estimated_font_size,
                            "confidence": confidence,
                            "char_density": char_density,
                            "text_type": self._classify_text_type(
                                text, estimated_font_size
                            ),
                        }
                    )
            return {
                "detected_fonts": font_info,
                "font_analysis": "high_accuracy",
                "total_text_regions": len(font_info),
            }
        except Exception as e:
            return {"error": f"Font detection failed: {str(e)}"}

    def _classify_text_type(self, text: str, font_size: int) -> str:
        """Classify text as title, subtitle, body, etc."""
        text_length = len(text.strip())

        if font_size > 24 and text_length < 50:
            return "title"
        elif font_size > 18 and text_length < 100:
            return "subtitle"
        elif text_length < 20:
            return "label"
        else:
            return "body"

    def _extract_text(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Extract all text elements with positioning"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ocr_results = self.ocr_reader.readtext(gray, detail=1)

            text_elements = []
            for i, (bbox, text, confidence) in enumerate(ocr_results):
                if confidence > 0.3:  # Lower threshold for text extraction
                    x1, y1 = int(min([point[0] for point in bbox])), int(
                        min([point[1] for point in bbox])
                    )
                    x2, y2 = int(max([point[0] for point in bbox])), int(
                        max([point[1] for point in bbox])
                    )

                    text_elements.append(
                        {
                            "id": f"text_{i}",
                            "content": text.strip(),
                            "bbox": [x1, y1, x2, y2],
                            "confidence": confidence,
                            "suggested_placeholder": self._suggest_placeholder(
                                text.strip()
                            ),
                        }
                    )
            return text_elements
        except Exception as e:
            return [{"error": f"Text extraction failed: {str(e)}"}]

    def _suggest_placeholder(self, text: str) -> str:
        """Suggest appropriate placeholder tag for detected text"""
        text_lower = text.lower().strip()

        # Common patterns for different placeholder types

        if any(word in text_lower for word in ["title", "heading", "main"]):
            return "{TITLE}"
        elif any(word in text_lower for word in ["subtitle", "subheading"]):
            return "{SUBTITLE}"
        elif any(word in text_lower for word in ["description", "desc", "about"]):
            return "{DESCRIPTION}"
        elif any(word in text_lower for word in ["author", "by", "creator"]):
            return "{AUTHOR}"
        elif any(word in text_lower for word in ["date", "time", "when"]):
            return "{DATE}"
        elif any(word in text_lower for word in ["category", "tag", "type"]):
            return "{CATEGORY}"
        elif any(word in text_lower for word in ["quote", "saying"]):
            return "{QUOTE}"
        elif any(word in text_lower for word in ["price", "$", "cost"]):
            return "{PRICE}"
        elif any(word in text_lower for word in ["website", "site", "url"]):
            return "{SITE_NAME}"
        elif len(text) > 50:
            return "{DESCRIPTION}"
        elif len(text) < 10:
            return "{TAG}"
        else:
            return "{TITLE}"

    def _analyze_layout(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze layout structure using computer vision"""
        try:
            height, width = image.shape[:2]
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Edge detection for layout analysis

            edges = cv2.Canny(gray, 50, 150)

            # Find contours for layout regions

            contours, _ = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Filter and analyze significant contours

            layout_regions = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > (width * height * 0.01):  # Filter small regions
                    x, y, w, h = cv2.boundingRect(contour)

                    layout_regions.append(
                        {
                            "id": f"region_{i}",
                            "bbox": [x, y, x + w, y + h],
                            "area": area,
                            "aspect_ratio": w / h if h > 0 else 1,
                        }
                    )
            # Analyze grid structure

            grid_analysis = self._analyze_grid_structure(layout_regions, width, height)

            return {
                "layout_regions": layout_regions,
                "grid_analysis": grid_analysis,
                "layout_type": self._classify_layout_type(
                    layout_regions, width, height
                ),
            }
        except Exception as e:
            return {"error": f"Layout analysis failed: {str(e)}"}

    def _analyze_grid_structure(
        self, regions: List[Dict], width: int, height: int
    ) -> Dict[str, Any]:
        """Analyze if layout follows a grid structure"""
        if not regions:
            return {"grid_detected": False}
        # Extract x and y coordinates

        x_coords = []
        y_coords = []

        for region in regions:
            x1, y1, x2, y2 = region["bbox"]
            x_coords.extend([x1, x2])
            y_coords.extend([y1, y2])
        # Find common alignment points

        x_coords = sorted(set(x_coords))
        y_coords = sorted(set(y_coords))

        # Detect grid lines (simplified)

        grid_cols = len(set([r["bbox"][0] for r in regions]))
        grid_rows = len(set([r["bbox"][1] for r in regions]))

        return {
            "grid_detected": grid_cols > 1 or grid_rows > 1,
            "estimated_columns": grid_cols,
            "estimated_rows": grid_rows,
            "alignment_points": {
                "x": x_coords[:5],
                "y": y_coords[:5],
            },  # Limit for response size
        }

    def _classify_layout_type(
        self, regions: List[Dict], width: int, height: int
    ) -> str:
        """Classify the overall layout type"""
        if not regions:
            return "simple"
        num_regions = len(regions)

        if num_regions == 1:
            return "single_focus"
        elif num_regions <= 3:
            return "minimal"
        elif num_regions <= 6:
            return "moderate"
        else:
            return "complex"

    def _detect_image_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect and classify image regions"""
        try:
            height, width = image.shape[:2]

            # Use YOLO if available for object detection

            image_regions = []

            if self.yolo_model:
                try:
                    results = self.yolo_model(image)
                    for i, result in enumerate(results[0].boxes.data):
                        x1, y1, x2, y2, conf, cls = result
                        if conf > 0.3:  # Confidence threshold
                            image_regions.append(
                                {
                                    "id": f"image_{i + 1}",
                                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                                    "confidence": float(conf),
                                    "type": self._classify_image_type(
                                        image, [int(x1), int(y1), int(x2), int(y2)]
                                    ),
                                    "placeholder_tag": f"{{IMAGE_{i + 1}}}",
                                }
                            )
                except Exception as e:
                    print(f"YOLO detection failed: {e}")
            # Fallback: Use color segmentation for image detection

            if not image_regions:
                image_regions = self._detect_images_by_segmentation(image)
            return image_regions
        except Exception as e:
            return [{"error": f"Image region detection failed: {str(e)}"}]

    def _classify_image_type(self, image: np.ndarray, bbox: List[int]) -> str:
        """Classify image region as placeholder_icon or real_photo"""
        try:
            x1, y1, x2, y2 = bbox
            roi = image[y1:y2, x1:x2]

            if roi.size == 0:
                return "unknown"
            # Convert to RGB for analysis

            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

            # Calculate color statistics

            mean_color = np.mean(roi_rgb, axis=(0, 1))
            std_color = np.std(roi_rgb, axis=(0, 1))

            # Check if colors are in grayscale range (placeholder icons)

            is_grayscale = np.allclose(mean_color, mean_color[0], atol=30)

            # Check color variance (low variance = placeholder)

            color_variance = np.mean(std_color)

            # Check if colors are in typical placeholder range (120-180 RGB)

            in_placeholder_range = all(120 <= c <= 180 for c in mean_color)

            if is_grayscale and color_variance < 50 and in_placeholder_range:
                return "placeholder_icon"
            else:
                return "real_photo"
        except Exception:
            return "unknown"

    def _detect_images_by_segmentation(
        self, image: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Fallback method to detect image regions using color segmentation"""
        try:
            height, width = image.shape[:2]
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply threshold to find distinct regions

            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Find contours

            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            image_regions = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > (width * height * 0.02):  # Filter small regions
                    x, y, w, h = cv2.boundingRect(contour)

                    # Check if region looks like an image placeholder

                    aspect_ratio = w / h if h > 0 else 1
                    if 0.5 <= aspect_ratio <= 2.0:  # Reasonable aspect ratio for images
                        image_regions.append(
                            {
                                "id": f"image_{i + 1}",
                                "bbox": [x, y, x + w, y + h],
                                "confidence": 0.7,  # Default confidence for segmentation
                                "type": self._classify_image_type(
                                    image, [x, y, x + w, y + h]
                                ),
                                "placeholder_tag": f"{{IMAGE_{i + 1}}}",
                            }
                        )
            return image_regions[:10]  # Limit to 10 image regions
        except Exception as e:
            return [{"error": f"Segmentation detection failed: {str(e)}"}]

    def _analyze_background(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze background properties"""
        try:
            height, width = image.shape[:2]

            # Sample background from corners and edges

            corner_size = min(50, width // 10, height // 10)

            corners = [
                image[0:corner_size, 0:corner_size],  # Top-left
                image[0:corner_size, -corner_size:],  # Top-right
                image[-corner_size:, 0:corner_size],  # Bottom-left
                image[-corner_size:, -corner_size:],  # Bottom-right
            ]

            # Calculate average background color

            bg_colors = []
            for corner in corners:
                if corner.size > 0:
                    mean_color = np.mean(corner, axis=(0, 1))
                    bg_colors.append(mean_color)
            if bg_colors:
                avg_bg_color = np.mean(bg_colors, axis=0)
                bg_hex = "#{:02x}{:02x}{:02x}".format(
                    int(avg_bg_color[2]),
                    int(avg_bg_color[1]),
                    int(avg_bg_color[0]),  # BGR to RGB
                )
            else:
                bg_hex = "#ffffff"
            # Detect if background has patterns or gradients

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            bg_variance = np.var(gray)

            bg_type = (
                "solid"
                if bg_variance < 1000
                else "gradient" if bg_variance < 5000 else "pattern"
            )

            return {
                "background_color": bg_hex,
                "background_type": bg_type,
                "background_variance": float(bg_variance),
            }
        except Exception as e:
            return {"error": f"Background analysis failed: {str(e)}"}
