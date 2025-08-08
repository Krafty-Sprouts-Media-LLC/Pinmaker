import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from sklearn.cluster import KMeans
import webcolors
from typing import Dict, List, Tuple, Any, Optional
import logging
import os
from collections import Counter
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """Comprehensive image analysis for Pinterest pin optimization."""
    
    def __init__(self):
        """Initialize the ImageAnalyzer with default settings."""
        self.tesseract_config = '--oem 3 --psm 6'
        
        # Font detection patterns
        self.serif_patterns = [
            r'times', r'georgia', r'garamond', r'baskerville', 
            r'minion', r'caslon', r'palatino'
        ]
        
        self.sans_serif_patterns = [
            r'arial', r'helvetica', r'calibri', r'verdana', 
            r'tahoma', r'trebuchet', r'futura', r'avenir'
        ]
        
        self.script_patterns = [
            r'script', r'brush', r'handwriting', r'cursive',
            r'calligraphy', r'signature'
        ]
        
        self.display_patterns = [
            r'impact', r'bebas', r'oswald', r'montserrat',
            r'roboto', r'open sans', r'lato'
        ]

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Perform comprehensive image analysis.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing all analysis results
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Convert to RGB for PIL operations
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Perform all analyses
            results = {
                'image_info': self._get_image_info(pil_image),
                'color_analysis': self._analyze_colors(image_rgb),
                'text_analysis': self._analyze_text(pil_image),
                'layout_analysis': self._analyze_layout(image),
                'background_analysis': self._analyze_background(image),
                'visual_elements': self._analyze_visual_elements(image),
                'pinterest_optimization': self._get_pinterest_recommendations(image_rgb, pil_image)
            }
            
            logger.info(f"Successfully analyzed image: {image_path}")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {str(e)}")
            raise

    def _get_image_info(self, image: Image.Image) -> Dict[str, Any]:
        """Get basic image information."""
        width, height = image.size
        aspect_ratio = width / height
        
        # Determine orientation
        if aspect_ratio > 1.2:
            orientation = "landscape"
        elif aspect_ratio < 0.8:
            orientation = "portrait"
        else:
            orientation = "square"
        
        # Check Pinterest optimal ratios
        pinterest_ratios = {
            "2:3": abs(aspect_ratio - (2/3)) < 0.1,
            "1:1.5": abs(aspect_ratio - (1/1.5)) < 0.1,
            "9:16": abs(aspect_ratio - (9/16)) < 0.1
        }
        
        optimal_ratio = any(pinterest_ratios.values())
        
        return {
            "width": width,
            "height": height,
            "aspect_ratio": round(aspect_ratio, 2),
            "orientation": orientation,
            "pinterest_optimal": optimal_ratio,
            "pinterest_ratios": pinterest_ratios,
            "total_pixels": width * height
        }

    def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color composition and palette."""
        # Reshape image for clustering
        pixels = image.reshape(-1, 3)
        
        # Remove very dark and very light pixels for better color analysis
        mask = np.logical_and(
            np.mean(pixels, axis=1) > 20,
            np.mean(pixels, axis=1) < 235
        )
        filtered_pixels = pixels[mask]
        
        if len(filtered_pixels) == 0:
            filtered_pixels = pixels
        
        # Perform K-means clustering to find dominant colors
        n_colors = min(8, len(filtered_pixels))
        if n_colors > 1:
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(filtered_pixels)
            
            # Get colors and their frequencies
            colors = kmeans.cluster_centers_.astype(int)
            labels = kmeans.labels_
            color_counts = Counter(labels)
            
            # Sort colors by frequency
            dominant_colors = []
            for i, count in color_counts.most_common():
                color_rgb = tuple(colors[i])
                percentage = (count / len(labels)) * 100
                
                # Convert to hex
                color_hex = '#{:02x}{:02x}{:02x}'.format(*color_rgb)
                
                # Try to get color name
                try:
                    color_name = webcolors.rgb_to_name(color_rgb)
                except ValueError:
                    color_name = self._get_closest_color_name(color_rgb)
                
                dominant_colors.append({
                    "rgb": color_rgb,
                    "hex": color_hex,
                    "name": color_name,
                    "percentage": round(percentage, 1)
                })
        else:
            # Fallback for single color
            avg_color = np.mean(filtered_pixels, axis=0).astype(int)
            color_hex = '#{:02x}{:02x}{:02x}'.format(*avg_color)
            dominant_colors = [{
                "rgb": tuple(avg_color),
                "hex": color_hex,
                "name": self._get_closest_color_name(tuple(avg_color)),
                "percentage": 100.0
            }]
        
        # Analyze color temperature and mood
        avg_color = np.mean(pixels, axis=0)
        color_temp = self._analyze_color_temperature(avg_color)
        color_mood = self._analyze_color_mood(dominant_colors)
        
        return {
            "dominant_colors": dominant_colors,
            "color_temperature": color_temp,
            "color_mood": color_mood,
            "average_brightness": float(np.mean(pixels)),
            "color_diversity": len(dominant_colors)
        }

    def _get_closest_color_name(self, rgb_color: Tuple[int, int, int]) -> str:
        """Get the closest named color for an RGB value."""
        min_colors = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - rgb_color[0]) ** 2
            gd = (g_c - rgb_color[1]) ** 2
            bd = (b_c - rgb_color[2]) ** 2
            min_colors[(rd + gd + bd)] = name
        return min_colors[min(min_colors.keys())]

    def _analyze_color_temperature(self, avg_color: np.ndarray) -> str:
        """Analyze if colors are warm, cool, or neutral."""
        r, g, b = avg_color
        
        # Simple color temperature analysis
        if r > g and r > b:
            return "warm"
        elif b > r and b > g:
            return "cool"
        else:
            return "neutral"

    def _analyze_color_mood(self, dominant_colors: List[Dict]) -> str:
        """Analyze the overall mood based on colors."""
        if not dominant_colors:
            return "neutral"
        
        # Analyze based on dominant color
        primary_color = dominant_colors[0]["rgb"]
        r, g, b = primary_color
        
        # Simple mood analysis based on color psychology
        if r > 150 and g < 100 and b < 100:
            return "energetic"
        elif g > 150 and r < 100 and b < 100:
            return "natural"
        elif b > 150 and r < 100 and g < 100:
            return "calm"
        elif r > 150 and g > 150 and b < 100:
            return "cheerful"
        elif r < 100 and g < 100 and b < 100:
            return "sophisticated"
        else:
            return "balanced"

    def _analyze_text(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze text content and typography."""
        try:
            # Extract text using OCR
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            
            # Get detailed text information
            text_data = pytesseract.image_to_data(image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
            
            # Filter out low confidence detections
            confident_text = []
            text_regions = []
            
            for i in range(len(text_data['text'])):
                if int(text_data['conf'][i]) > 30:  # Confidence threshold
                    word = text_data['text'][i].strip()
                    if word:
                        confident_text.append(word)
                        text_regions.append({
                            "text": word,
                            "confidence": int(text_data['conf'][i]),
                            "bbox": {
                                "x": text_data['left'][i],
                                "y": text_data['top'][i],
                                "width": text_data['width'][i],
                                "height": text_data['height'][i]
                            }
                        })
            
            # Analyze text content
            full_text = ' '.join(confident_text)
            word_count = len(confident_text)
            
            # Detect potential fonts (basic heuristics)
            font_analysis = self._analyze_fonts(text_regions, image)
            
            # Analyze text layout
            text_layout = self._analyze_text_layout(text_regions, image.size)
            
            return {
                "extracted_text": full_text,
                "word_count": word_count,
                "text_regions": text_regions,
                "font_analysis": font_analysis,
                "text_layout": text_layout,
                "has_text": len(confident_text) > 0
            }
            
        except Exception as e:
            logger.warning(f"Text analysis failed: {str(e)}")
            return {
                "extracted_text": "",
                "word_count": 0,
                "text_regions": [],
                "font_analysis": {},
                "text_layout": {},
                "has_text": False
            }

    def _analyze_fonts(self, text_regions: List[Dict], image: Image.Image) -> Dict[str, Any]:
        """Analyze font characteristics from text regions."""
        if not text_regions:
            return {"detected_fonts": [], "font_categories": []}
        
        font_sizes = []
        font_categories = []
        
        for region in text_regions:
            # Estimate font size based on bounding box height
            font_size = region["bbox"]["height"]
            font_sizes.append(font_size)
            
            # Basic font category detection (would need more sophisticated analysis)
            text_lower = region["text"].lower()
            
            # Check for font indicators in text (if any)
            if any(re.search(pattern, text_lower) for pattern in self.serif_patterns):
                font_categories.append("serif")
            elif any(re.search(pattern, text_lower) for pattern in self.sans_serif_patterns):
                font_categories.append("sans-serif")
            elif any(re.search(pattern, text_lower) for pattern in self.script_patterns):
                font_categories.append("script")
            elif any(re.search(pattern, text_lower) for pattern in self.display_patterns):
                font_categories.append("display")
            else:
                font_categories.append("unknown")
        
        avg_font_size = np.mean(font_sizes) if font_sizes else 0
        font_category_counts = Counter(font_categories)
        
        return {
            "average_font_size": round(avg_font_size, 1),
            "font_size_range": [min(font_sizes), max(font_sizes)] if font_sizes else [0, 0],
            "font_categories": dict(font_category_counts),
            "primary_font_category": font_category_counts.most_common(1)[0][0] if font_category_counts else "unknown"
        }

    def _analyze_text_layout(self, text_regions: List[Dict], image_size: Tuple[int, int]) -> Dict[str, Any]:
        """Analyze text layout and positioning."""
        if not text_regions:
            return {"text_coverage": 0, "text_distribution": "none"}
        
        width, height = image_size
        
        # Calculate text coverage
        total_text_area = sum(
            region["bbox"]["width"] * region["bbox"]["height"]
            for region in text_regions
        )
        text_coverage = (total_text_area / (width * height)) * 100
        
        # Analyze text distribution
        y_positions = [region["bbox"]["y"] for region in text_regions]
        
        top_third = height / 3
        middle_third = 2 * height / 3
        
        top_count = sum(1 for y in y_positions if y < top_third)
        middle_count = sum(1 for y in y_positions if top_third <= y < middle_third)
        bottom_count = sum(1 for y in y_positions if y >= middle_third)
        
        if top_count > middle_count and top_count > bottom_count:
            distribution = "top-heavy"
        elif bottom_count > middle_count and bottom_count > top_count:
            distribution = "bottom-heavy"
        elif middle_count > top_count and middle_count > bottom_count:
            distribution = "center-focused"
        else:
            distribution = "distributed"
        
        return {
            "text_coverage": round(text_coverage, 2),
            "text_distribution": distribution,
            "text_regions_count": len(text_regions)
        }

    def _analyze_layout(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image layout and composition."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Detect edges for composition analysis
        edges = cv2.Canny(gray, 50, 150)
        
        # Analyze rule of thirds
        thirds_analysis = self._analyze_rule_of_thirds(edges)
        
        # Detect main subject/focal points
        focal_points = self._detect_focal_points(gray)
        
        # Analyze symmetry
        symmetry = self._analyze_symmetry(gray)
        
        # Analyze visual weight distribution
        weight_distribution = self._analyze_visual_weight(gray)
        
        return {
            "rule_of_thirds": thirds_analysis,
            "focal_points": focal_points,
            "symmetry": symmetry,
            "visual_weight": weight_distribution,
            "edge_density": float(np.sum(edges > 0) / (width * height))
        }

    def _analyze_rule_of_thirds(self, edges: np.ndarray) -> Dict[str, Any]:
        """Analyze adherence to rule of thirds."""
        height, width = edges.shape
        
        # Define thirds lines
        v_line1 = width // 3
        v_line2 = 2 * width // 3
        h_line1 = height // 3
        h_line2 = 2 * height // 3
        
        # Check edge density along thirds lines
        v1_density = np.sum(edges[:, v_line1-2:v_line1+3]) / (height * 5)
        v2_density = np.sum(edges[:, v_line2-2:v_line2+3]) / (height * 5)
        h1_density = np.sum(edges[h_line1-2:h_line1+3, :]) / (width * 5)
        h2_density = np.sum(edges[h_line2-2:h_line2+3, :]) / (width * 5)
        
        avg_density = (v1_density + v2_density + h1_density + h2_density) / 4
        
        # Check intersection points
        intersections = [
            (v_line1, h_line1), (v_line1, h_line2),
            (v_line2, h_line1), (v_line2, h_line2)
        ]
        
        intersection_scores = []
        for x, y in intersections:
            region = edges[max(0, y-10):min(height, y+11), max(0, x-10):min(width, x+11)]
            score = np.sum(region) / (region.shape[0] * region.shape[1])
            intersection_scores.append(float(score))
        
        return {
            "line_alignment_score": float(avg_density),
            "intersection_scores": intersection_scores,
            "follows_rule": avg_density > 0.1 or max(intersection_scores) > 0.2
        }

    def _detect_focal_points(self, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Detect potential focal points in the image."""
        # Use corner detection to find interesting points
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=10, qualityLevel=0.01, minDistance=30)
        
        focal_points = []
        if corners is not None:
            for corner in corners:
                x, y = corner.ravel()
                focal_points.append({
                    "x": int(x),
                    "y": int(y),
                    "strength": float(gray[int(y), int(x)])
                })
        
        return focal_points

    def _analyze_symmetry(self, gray: np.ndarray) -> Dict[str, Any]:
        """Analyze image symmetry."""
        height, width = gray.shape
        
        # Vertical symmetry
        left_half = gray[:, :width//2]
        right_half = np.fliplr(gray[:, width//2:])
        
        # Resize to match if needed
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]
        
        vertical_symmetry = float(np.corrcoef(left_half.flatten(), right_half.flatten())[0, 1])
        
        # Horizontal symmetry
        top_half = gray[:height//2, :]
        bottom_half = np.flipud(gray[height//2:, :])
        
        min_height = min(top_half.shape[0], bottom_half.shape[0])
        top_half = top_half[:min_height, :]
        bottom_half = bottom_half[:min_height, :]
        
        horizontal_symmetry = float(np.corrcoef(top_half.flatten(), bottom_half.flatten())[0, 1])
        
        return {
            "vertical_symmetry": vertical_symmetry if not np.isnan(vertical_symmetry) else 0.0,
            "horizontal_symmetry": horizontal_symmetry if not np.isnan(horizontal_symmetry) else 0.0,
            "is_symmetric": max(vertical_symmetry, horizontal_symmetry) > 0.7
        }

    def _analyze_visual_weight(self, gray: np.ndarray) -> Dict[str, Any]:
        """Analyze visual weight distribution."""
        height, width = gray.shape
        
        # Divide image into quadrants
        mid_h, mid_w = height // 2, width // 2
        
        quadrants = {
            "top_left": gray[:mid_h, :mid_w],
            "top_right": gray[:mid_h, mid_w:],
            "bottom_left": gray[mid_h:, :mid_w],
            "bottom_right": gray[mid_h:, mid_w:]
        }
        
        # Calculate visual weight (inverse of brightness - darker areas have more weight)
        weights = {}
        for name, quadrant in quadrants.items():
            avg_brightness = np.mean(quadrant)
            visual_weight = 255 - avg_brightness  # Invert so darker = heavier
            weights[name] = float(visual_weight)
        
        # Find dominant quadrant
        dominant_quadrant = max(weights, key=weights.get)
        
        return {
            "quadrant_weights": weights,
            "dominant_quadrant": dominant_quadrant,
            "weight_balance": float(np.std(list(weights.values())))
        }

    def _analyze_background(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze background characteristics."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Sample edges for background analysis
        height, width = gray.shape
        edge_width = min(50, width // 10)
        edge_height = min(50, height // 10)
        
        # Sample from edges
        edges_sample = np.concatenate([
            gray[:edge_height, :].flatten(),  # Top edge
            gray[-edge_height:, :].flatten(),  # Bottom edge
            gray[:, :edge_width].flatten(),  # Left edge
            gray[:, -edge_width:].flatten()  # Right edge
        ])
        
        # Background color (mode of edge samples)
        bg_color = np.median(edges_sample)
        bg_hex = '#{:02x}{:02x}{:02x}'.format(int(bg_color), int(bg_color), int(bg_color))
        
        # Background complexity
        bg_variance = np.var(gray)
        
        bg_type = (
            "solid"
            if bg_variance < 1000
            else "gradient" if bg_variance < 5000 else "pattern"
        )
        
        return {
            "background_color": bg_hex,
            "background_type": bg_type,
            "background_complexity": float(bg_variance),
            "is_simple_background": bg_variance < 2000
        }

    def _analyze_visual_elements(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze visual elements like shapes, objects, etc."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect contours for shape analysis
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze shapes
        shapes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small contours
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Classify shape based on number of vertices
                vertices = len(approx)
                if vertices == 3:
                    shape_type = "triangle"
                elif vertices == 4:
                    shape_type = "rectangle"
                elif vertices > 8:
                    shape_type = "circle"
                else:
                    shape_type = "polygon"
                
                shapes.append({
                    "type": shape_type,
                    "area": float(area),
                    "vertices": vertices
                })
        
        # Count shape types
        shape_counts = Counter(shape["type"] for shape in shapes)
        
        return {
            "total_shapes": len(shapes),
            "shape_distribution": dict(shape_counts),
            "largest_shape": max(shapes, key=lambda x: x["area"]) if shapes else None,
            "visual_complexity": len(contours)
        }

    def _get_pinterest_recommendations(self, image_rgb: np.ndarray, pil_image: Image.Image) -> Dict[str, Any]:
        """Generate Pinterest-specific optimization recommendations."""
        width, height = pil_image.size
        aspect_ratio = width / height
        
        recommendations = []
        score = 100  # Start with perfect score
        
        # Aspect ratio recommendations
        if not (0.5 <= aspect_ratio <= 0.8):  # Pinterest prefers vertical
            recommendations.append("Consider using a vertical aspect ratio (2:3 or 1:1.5) for better Pinterest performance")
            score -= 15
        
        # Size recommendations
        if width < 600:
            recommendations.append("Increase image width to at least 600px for better quality")
            score -= 10
        
        if height < 900:
            recommendations.append("Increase image height to at least 900px for vertical pins")
            score -= 10
        
        # Text analysis for Pinterest
        avg_brightness = np.mean(image_rgb)
        if avg_brightness < 50:
            recommendations.append("Image appears too dark - consider brightening for better visibility")
            score -= 10
        elif avg_brightness > 200:
            recommendations.append("Image appears too bright - consider adjusting contrast")
            score -= 5
        
        # Color recommendations
        unique_colors = len(np.unique(image_rgb.reshape(-1, 3), axis=0))
        if unique_colors < 100:
            recommendations.append("Consider adding more color variety to make the pin more engaging")
            score -= 5
        
        # Final score calculation
        pinterest_score = max(0, min(100, score))
        
        return {
            "pinterest_score": pinterest_score,
            "recommendations": recommendations,
            "optimal_for_pinterest": pinterest_score >= 80,
            "suggested_improvements": {
                "aspect_ratio": "2:3 or 1:1.5",
                "minimum_size": "600x900px",
                "recommended_size": "1000x1500px"
            }
        }

    def get_analysis_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the analysis."""
        summary_parts = []
        
        # Image info
        info = analysis_results.get('image_info', {})
        summary_parts.append(f"Image: {info.get('width', 'Unknown')}x{info.get('height', 'Unknown')} ({info.get('orientation', 'unknown')} orientation)")
        
        # Colors
        colors = analysis_results.get('color_analysis', {})
        if colors.get('dominant_colors'):
            primary_color = colors['dominant_colors'][0]
            summary_parts.append(f"Primary color: {primary_color.get('name', 'Unknown')} ({primary_color.get('percentage', 0):.1f}%)")
        
        # Text
        text = analysis_results.get('text_analysis', {})
        if text.get('has_text'):
            summary_parts.append(f"Contains text: {text.get('word_count', 0)} words detected")
        else:
            summary_parts.append("No readable text detected")
        
        # Pinterest optimization
        pinterest = analysis_results.get('pinterest_optimization', {})
        score = pinterest.get('pinterest_score', 0)
        summary_parts.append(f"Pinterest optimization score: {score}/100")
        
        return ". ".join(summary_parts) + "."
