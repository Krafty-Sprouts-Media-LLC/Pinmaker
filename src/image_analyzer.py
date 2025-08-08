import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time


@dataclass
class ImageAnalysisResult:
    """Container for image analysis results"""

    dominant_colors: List[str]
    color_palette: List[str]
    brightness: float
    contrast: float
    saturation: float
    sharpness: float
    noise_level: float
    composition_score: float
    objects_detected: List[Dict[str, Any]]
    faces_detected: List[Dict[str, Any]]
    text_regions: List[Dict[str, Any]]
    image_regions: List[Dict[str, Any]]
    background_analysis: Dict[str, Any]
    technical_quality: Dict[str, Any]
    aesthetic_score: float
    processing_time: float
    metadata: Dict[str, Any]


class ImageAnalyzer:
    """Advanced image analysis with computer vision techniques"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Initialize OpenCV cascades
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
        except Exception as e:
            self.logger.warning(f"Could not load face cascade: {e}")
            self.face_cascade = None

    async def analyze_image(self, image_path: str) -> ImageAnalysisResult:
        """Comprehensive image analysis"""
        start_time = time.time()

        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")

            # Run analysis tasks concurrently
            tasks = [
                self._analyze_colors(image),
                self._analyze_technical_quality(image),
                self._detect_objects(image),
                self._detect_faces(image),
                self._detect_text_regions(image),
                self._analyze_composition(image),
                self._segment_image_regions(image),
                self._analyze_background(image),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            (
                color_analysis,
                technical_analysis,
                objects,
                faces,
                text_regions,
                composition,
                image_regions,
                background,
            ) = results

            # Handle exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Analysis task {i} failed: {result}")
                    results[i] = {"error": str(result)}

            # Calculate aesthetic score
            aesthetic_score = self._calculate_aesthetic_score(
                technical_analysis, composition, color_analysis
            )

            processing_time = time.time() - start_time

            return ImageAnalysisResult(
                dominant_colors=color_analysis.get("dominant_colors", []),
                color_palette=color_analysis.get("color_palette", []),
                brightness=technical_analysis.get("brightness", 0.0),
                contrast=technical_analysis.get("contrast", 0.0),
                saturation=color_analysis.get("saturation", 0.0),
                sharpness=technical_analysis.get("sharpness", 0.0),
                noise_level=technical_analysis.get("noise_level", 0.0),
                composition_score=composition.get("score", 0.0),
                objects_detected=objects if isinstance(objects, list) else [],
                faces_detected=faces if isinstance(faces, list) else [],
                text_regions=text_regions if isinstance(text_regions, list) else [],
                image_regions=image_regions if isinstance(image_regions, list) else [],
                background_analysis=background if isinstance(background, dict) else {},
                technical_quality=(
                    technical_analysis if isinstance(technical_analysis, dict) else {}
                ),
                aesthetic_score=aesthetic_score,
                processing_time=processing_time,
                metadata={"image_path": image_path, "image_shape": image.shape},
            )

        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            return ImageAnalysisResult(
                dominant_colors=[],
                color_palette=[],
                brightness=0.0,
                contrast=0.0,
                saturation=0.0,
                sharpness=0.0,
                noise_level=0.0,
                composition_score=0.0,
                objects_detected=[],
                faces_detected=[],
                text_regions=[],
                image_regions=[],
                background_analysis={},
                technical_quality={},
                aesthetic_score=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)},
            )

    async def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color properties of the image"""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

            # Calculate dominant colors using K-means
            pixels = image.reshape(-1, 3)
            pixels = np.float32(pixels)

            # K-means clustering for dominant colors
            k = 5
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(
                pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
            )

            # Convert centers to hex colors
            dominant_colors = []
            for center in centers:
                color_hex = "#{:02x}{:02x}{:02x}".format(
                    int(center[2]), int(center[1]), int(center[0])  # BGR to RGB
                )
                dominant_colors.append(color_hex)

            # Calculate color statistics
            saturation = np.mean(hsv[:, :, 1]) / 255.0
            value = np.mean(hsv[:, :, 2]) / 255.0

            # Generate color palette (simplified)
            color_palette = dominant_colors[:3]  # Top 3 colors

            return {
                "dominant_colors": dominant_colors,
                "color_palette": color_palette,
                "saturation": float(saturation),
                "value": float(value),
                "color_diversity": len(np.unique(labels)),
            }

        except Exception as e:
            return {"error": f"Color analysis failed: {str(e)}"}

    async def _analyze_technical_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze technical quality metrics"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Brightness
            brightness = np.mean(gray) / 255.0

            # Contrast (standard deviation)
            contrast = np.std(gray) / 255.0

            # Sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)

            # Noise level (using high-frequency components)
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            noise = cv2.filter2D(gray, -1, kernel)
            noise_level = np.std(noise)

            # Exposure analysis
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            underexposed = np.sum(hist[:25]) / gray.size
            overexposed = np.sum(hist[230:]) / gray.size

            return {
                "brightness": float(brightness),
                "contrast": float(contrast),
                "sharpness": float(sharpness),
                "noise_level": float(noise_level),
                "underexposed_ratio": float(underexposed),
                "overexposed_ratio": float(overexposed),
            }

        except Exception as e:
            return {"error": f"Technical quality analysis failed: {str(e)}"}

    async def _detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects in the image using basic computer vision"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Find contours
            contours, _ = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            objects = []
            for i, contour in enumerate(contours[:10]):  # Limit to 10 largest
                area = cv2.contourArea(contour)
                if area > 1000:  # Filter small objects
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append(
                        {
                            "id": i,
                            "bbox": [x, y, w, h],
                            "area": float(area),
                            "confidence": min(
                                area / 10000, 1.0
                            ),  # Simplified confidence
                            "type": "object",  # Generic type
                        }
                    )

            return objects

        except Exception as e:
            return [{"error": f"Object detection failed: {str(e)}"}]

    async def _detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces in the image"""
        try:
            if self.face_cascade is None:
                return [{"error": "Face cascade not available"}]

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            face_list = []
            for i, (x, y, w, h) in enumerate(faces):
                face_list.append(
                    {
                        "id": i,
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "confidence": 0.8,  # Simplified confidence
                        "type": "face",
                    }
                )

            return face_list

        except Exception as e:
            return [{"error": f"Face detection failed: {str(e)}"}]

    async def _detect_text_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect potential text regions"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Use MSER (Maximally Stable Extremal Regions) for text detection
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)

            text_regions = []
            for i, region in enumerate(regions[:20]):  # Limit to 20 regions
                if len(region) > 10:  # Filter very small regions
                    x, y, w, h = cv2.boundingRect(region)
                    aspect_ratio = w / h if h > 0 else 0

                    # Filter based on text-like properties
                    if 0.1 < aspect_ratio < 10 and w > 10 and h > 5:
                        text_regions.append(
                            {
                                "id": i,
                                "bbox": [x, y, w, h],
                                "confidence": 0.6,  # Simplified confidence
                                "type": "text_region",
                                "aspect_ratio": float(aspect_ratio),
                            }
                        )

            return text_regions[:10]  # Limit to 10 text regions

        except Exception as e:
            return [{"error": f"Text detection failed: {str(e)}"}]

    async def _analyze_composition(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image composition"""
        try:
            height, width = image.shape[:2]
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Rule of thirds analysis
            third_h, third_w = height // 3, width // 3
            roi_points = [
                (third_w, third_h),
                (2 * third_w, third_h),
                (third_w, 2 * third_h),
                (2 * third_w, 2 * third_h),
            ]

            # Calculate interest points near rule of thirds intersections
            interest_score = 0
            for x, y in roi_points:
                roi = gray[
                    max(0, y - 20) : min(height, y + 20),
                    max(0, x - 20) : min(width, x + 20),
                ]
                if roi.size > 0:
                    interest_score += np.std(roi)

            # Symmetry analysis
            left_half = gray[:, : width // 2]
            right_half = cv2.flip(gray[:, width // 2 :], 1)
            min_width = min(left_half.shape[1], right_half.shape[1])
            symmetry_score = (
                1.0
                - np.mean(
                    np.abs(
                        left_half[:, :min_width].astype(float)
                        - right_half[:, :min_width].astype(float)
                    )
                )
                / 255.0
            )

            # Overall composition score
            composition_score = (interest_score / 1000 + symmetry_score) / 2
            composition_score = min(composition_score, 1.0)

            return {
                "score": float(composition_score),
                "rule_of_thirds_score": float(interest_score / 1000),
                "symmetry_score": float(symmetry_score),
                "aspect_ratio": float(width / height),
            }

        except Exception as e:
            return {"error": f"Composition analysis failed: {str(e)}"}

    async def _segment_image_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Segment image into distinct regions"""
        try:
            height, width = image.shape[:2]
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply threshold to find distinct regions
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Find connected components
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
                thresh, connectivity=8
            )

            image_regions = []
            for i in range(1, num_labels):  # Skip background (label 0)
                area = stats[i, cv2.CC_STAT_AREA]
                if area > width * height * 0.01:  # At least 1% of image
                    x = stats[i, cv2.CC_STAT_LEFT]
                    y = stats[i, cv2.CC_STAT_TOP]
                    w = stats[i, cv2.CC_STAT_WIDTH]
                    h = stats[i, cv2.CC_STAT_HEIGHT]

                    # Calculate region properties
                    region_mask = (labels == i).astype(np.uint8)
                    region_pixels = image[region_mask == 1]
                    avg_color = (
                        np.mean(region_pixels, axis=0)
                        if len(region_pixels) > 0
                        else [0, 0, 0]
                    )

                    image_regions.append(
                        {
                            "id": i - 1,
                            "bbox": [int(x), int(y), int(w), int(h)],
                            "area": int(area),
                            "centroid": [
                                float(centroids[i][0]),
                                float(centroids[i][1]),
                            ],
                            "avg_color": [
                                int(avg_color[2]),
                                int(avg_color[1]),
                                int(avg_color[0]),
                            ],  # BGR to RGB
                            "area_ratio": float(area / (width * height)),
                            "type": "region",
                            "placeholder_tag": f"{{IMAGE_{i}}}",
                        }
                    )
            return image_regions[:10]  # Limit to 10 image regions
        except Exception as e:
            return [{"error": f"Segmentation detection failed: {str(e)}"}]

    async def _analyze_background(self, image: np.ndarray) -> Dict[str, Any]:
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

    def _calculate_aesthetic_score(
        self,
        technical: Dict[str, Any],
        composition: Dict[str, Any],
        colors: Dict[str, Any],
    ) -> float:
        """Calculate overall aesthetic score"""
        try:
            # Weight different factors
            tech_score = (
                technical.get("sharpness", 0) / 1000
                + technical.get("contrast", 0)
                + (1 - technical.get("noise_level", 1000) / 1000)
            ) / 3

            comp_score = composition.get("score", 0)
            color_score = (
                colors.get("saturation", 0) * colors.get("color_diversity", 1) / 10
            )

            # Combine scores
            aesthetic_score = tech_score * 0.4 + comp_score * 0.4 + color_score * 0.2
            return min(max(aesthetic_score, 0.0), 1.0)

        except Exception:
            return 0.5  # Default neutral score
