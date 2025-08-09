import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
import os
import tempfile
from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime
from .font_manager import FontManager
from .stock_photo_service import StockPhotoService


class TemplateGenerator:
    def __init__(self, font_manager=None, stock_photo_service=None):
        self.font_manager = font_manager or FontManager()
        self.stock_service = stock_photo_service or StockPhotoService()

        # Template styles
        self.template_styles = {
            "modern": {
                "background_color": "#FFFFFF",
                "primary_color": "#2196F3",
                "secondary_color": "#FFC107",
                "text_color": "#333333",
                "font_family": "Arial",
                "border_radius": 8,
                "padding": 20,
            },
            "minimal": {
                "background_color": "#F8F9FA",
                "primary_color": "#6C757D",
                "secondary_color": "#E9ECEF",
                "text_color": "#212529",
                "font_family": "Helvetica",
                "border_radius": 0,
                "padding": 30,
            },
            "vibrant": {
                "background_color": "#FF6B6B",
                "primary_color": "#4ECDC4",
                "secondary_color": "#45B7D1",
                "text_color": "#FFFFFF",
                "font_family": "Impact",
                "border_radius": 15,
                "padding": 15,
            },
        }

    async def create_template(
        self, analysis: Dict[str, Any], style: str = "modern", dimensions: tuple = (800, 600)
    ) -> Dict[str, Any]:
        """Create SVG template from image analysis"""
        try:
            # Get style configuration
            style_config = self.template_styles.get(style, self.template_styles["modern"])

            # Create content mapping from analysis
            content_mapping = self._create_content_mapping(analysis)

            # Generate SVG template
            svg_content = await self._create_svg_template(
                content_mapping, style_config, dimensions
            )

            # Generate unique template ID
            template_id = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            template_filename = f"{template_id}.svg"
            template_path = f"templates/{template_filename}"

            # Ensure templates directory exists
            os.makedirs("templates", exist_ok=True)

            # Save SVG template
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            return {
                "template_path": template_path,
                "svg_content": svg_content,
                "template_data": svg_content,
                "analysis": content_mapping,
                "placeholders": self._extract_placeholders_from_mapping(content_mapping),
                "status": "success",
            }

        except Exception as e:
            raise Exception(f"Template generation failed: {str(e)}")

    def _create_content_mapping(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create content mapping from analysis results"""
        try:
            # Extract relevant information from analysis
            text_elements = analysis.get("text_elements", [])
            image_regions = analysis.get("image_regions", [])
            colors = analysis.get("colors", [])
            fonts = analysis.get("fonts", [])
            layout_structure = analysis.get("layout_structure", {})
            background_info = analysis.get("background_info", {})

            # Create structured content mapping
            content_mapping = {
                "text_elements": self._process_text_elements(text_elements),
                "image_regions": self._process_image_regions(image_regions),
                "color_palette": self._process_colors(colors),
                "font_suggestions": self._process_fonts(fonts),
                "layout_structure": layout_structure,
                "background_info": background_info,
                "placeholders": self._generate_placeholders(text_elements, image_regions),
            }

            return content_mapping

        except Exception as e:
            print(f"Error creating content mapping: {e}")
            return {}

    def _process_text_elements(self, text_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and enhance text elements"""
        processed_elements = []

        for i, element in enumerate(text_elements):
            processed_element = {
                "id": f"text_{i+1}",
                "content": element.get("content", f"Text Element {i+1}"),
                "bbox": element.get("bbox", [0, 0, 100, 20]),
                "confidence": element.get("confidence", 0.8),
                "font_size": self._estimate_font_size(element.get("bbox", [0, 0, 100, 20])),
                "placeholder_tag": f"{{TEXT_{i+1}}}",
                "suggested_placeholder": element.get("suggested_placeholder", f"{{TEXT_{i+1}}}"),
            }
            processed_elements.append(processed_element)

        return processed_elements

    def _process_image_regions(self, image_regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and enhance image regions"""
        processed_regions = []

        for i, region in enumerate(image_regions):
            processed_region = {
                "id": f"image_{i+1}",
                "bbox": region.get("bbox", [0, 0, 100, 100]),
                "type": region.get("type", "placeholder"),
                "placeholder_tag": f"{{IMAGE_{i+1}}}",
                "suggested_content": region.get("suggested_content", "Image placeholder"),
            }
            processed_regions.append(processed_region)

        return processed_regions

    def _process_colors(self, colors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process color information"""
        try:
            if not colors:
                return {
                    "dominant": "#2196F3",
                    "palette": ["#2196F3", "#FFC107", "#4CAF50"],
                    "background": "#FFFFFF",
                    "text": "#333333",
                }

            # Extract dominant color
            dominant_color = colors[0] if colors else "#2196F3"
            if isinstance(dominant_color, dict):
                dominant_color = dominant_color.get("hex", "#2196F3")

            # Create color palette
            palette = []
            for color in colors[:5]:  # Take first 5 colors
                if isinstance(color, dict):
                    palette.append(color.get("hex", "#000000"))
                else:
                    palette.append(str(color))

            return {
                "dominant": dominant_color,
                "palette": palette,
                "background": "#FFFFFF",
                "text": "#333333",
            }

        except Exception as e:
            print(f"Error processing colors: {e}")
            return {
                "dominant": "#2196F3",
                "palette": ["#2196F3", "#FFC107", "#4CAF50"],
                "background": "#FFFFFF",
                "text": "#333333",
            }

    def _process_fonts(self, fonts: List[Dict[str, Any]]) -> List[str]:
        """Process font information"""
        try:
            font_suggestions = []

            for font in fonts:
                if isinstance(font, dict):
                    font_name = font.get("name", "Arial")
                else:
                    font_name = str(font)

                if font_name not in font_suggestions:
                    font_suggestions.append(font_name)

            # Add default fonts if none found
            if not font_suggestions:
                font_suggestions = ["Arial", "Helvetica", "Times New Roman"]

            return font_suggestions[:3]  # Limit to 3 suggestions

        except Exception as e:
            print(f"Error processing fonts: {e}")
            return ["Arial", "Helvetica", "Times New Roman"]

    async def _create_svg_template(
        self, content_mapping: Dict[str, Any], style_config: Dict[str, Any], dimensions: tuple
    ) -> str:
        """Generate SVG template content"""
        try:
            width, height = dimensions
            svg_content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'

            # Add background
            svg_content += self._add_background(style_config, width, height)

            # Add image placeholders
            svg_content += self._add_image_placeholders(
                content_mapping.get("image_regions", []), style_config
            )

            # Add text elements
            svg_content += self._add_text_elements(
                content_mapping.get("text_elements", []), style_config
            )

            # Add layout structure elements
            svg_content += self._add_layout_elements(
                content_mapping.get("layout_structure", {}), style_config
            )

            svg_content += "</svg>"

            return svg_content

        except Exception as e:
            print(f"Error creating SVG template: {e}")
            return f'<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg"><rect width="800" height="600" fill="#FFFFFF"/><text x="400" y="300" text-anchor="middle" font-size="24" fill="#333333">Template Generation Error</text></svg>'

    def _add_background(self, style_config: Dict[str, Any], width: int, height: int) -> str:
        """Add background to SVG"""
        bg_color = style_config.get("background_color", "#FFFFFF")
        return f'  <rect width="{width}" height="{height}" fill="{bg_color}"/>\n'

    def _add_image_placeholders(self, image_regions: List[Dict[str, Any]], style_config: Dict[str, Any]) -> str:
        """Add image placeholders to SVG"""
        svg_content = ""

        for region in image_regions:
            bbox = region.get("bbox", [0, 0, 100, 100])
            x, y, x2, y2 = bbox
            width = x2 - x
            height = y2 - y
            placeholder_tag = region.get("placeholder_tag", "{IMAGE}")

            # Add placeholder rectangle
            svg_content += f'  <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#e0e0e0" stroke="#cccccc" stroke-width="2" stroke-dasharray="5,5"/>\n'

            # Add placeholder text
            text_x = x + width // 2
            text_y = y + height // 2
            font_size = min(16, height // 4)
            svg_content += f'  <text x="{text_x}" y="{text_y}" text-anchor="middle" font-size="{font_size}" fill="#666666">{placeholder_tag}</text>\n'

        return svg_content

    def _add_text_elements(self, text_elements: List[Dict[str, Any]], style_config: Dict[str, Any]) -> str:
        """Add text elements to SVG"""
        svg_content = ""
        font_family = style_config.get("font_family", "Arial")
        text_color = style_config.get("text_color", "#333333")

        for element in text_elements:
            bbox = element.get("bbox", [0, 0, 100, 20])
            x, y = bbox[0], bbox[1]
            font_size = element.get("font_size", 16)
            placeholder_tag = element.get("placeholder_tag", "{TEXT}")

            svg_content += f'  <text x="{x}" y="{y + font_size}" font-family="{font_family}" font-size="{font_size}" fill="{text_color}">{placeholder_tag}</text>\n'

        return svg_content

    def _add_layout_elements(self, layout_structure: Dict[str, Any], style_config: Dict[str, Any]) -> str:
        """Add layout structure elements to SVG"""
        svg_content = ""
        primary_color = style_config.get("primary_color", "#2196F3")
        border_radius = style_config.get("border_radius", 8)

        # Add decorative elements based on layout structure
        if layout_structure.get("has_border", False):
            svg_content += f'  <rect x="10" y="10" width="780" height="580" fill="none" stroke="{primary_color}" stroke-width="2" rx="{border_radius}"/>\n'

        return svg_content

    def _estimate_font_size(self, bbox: List[int]) -> int:
        """Estimate appropriate font size based on bounding box"""
        try:
            height = bbox[3] - bbox[1]
            # Estimate font size as 70% of height
            font_size = max(12, min(48, int(height * 0.7)))
            return font_size
        except:
            return 16

    def _generate_placeholders(self, text_elements: List[Dict[str, Any]], image_regions: List[Dict[str, Any]]) -> List[str]:
        """Generate list of all placeholders"""
        placeholders = set()

        # Add text placeholders
        for i, element in enumerate(text_elements):
            placeholders.add(f"{{TEXT_{i+1}}}")

        # Add image placeholders
        for i, region in enumerate(image_regions):
            placeholders.add(f"{{IMAGE_{i+1}}}")

        # Add common content placeholders
        common_placeholders = [
            "{TITLE}", "{SUBTITLE}", "{DESCRIPTION}", "{AUTHOR}", "{DATE}",
            "{CATEGORY}", "{TAG}", "{QUOTE}", "{CTA_TEXT}", "{PRICE}",
            "{DOMAIN}", "{SITE_NAME}", "{BRAND_NAME}", "{URL}", "{USERNAME}"
        ]
        placeholders.update(common_placeholders)

        return sorted(list(placeholders))

    def _update_placeholders(self, svg_content: str, analysis: Dict[str, Any]) -> str:
        """Update placeholder tags in SVG content"""
        try:
            # Replace text placeholders
            text_elements = analysis.get("text_elements", [])
            for i, element in enumerate(text_elements):
                placeholder = f"{{TEXT_{i+1}}}"
                content = element.get("content", "Sample Text")
                svg_content = svg_content.replace(placeholder, content)

            # Replace image placeholders
            image_regions = analysis.get("image_regions", [])
            for i, region in enumerate(image_regions):
                placeholder = f"{{IMAGE_{i+1}}}"
                # For now, keep as placeholder - will be handled by preview generator
                svg_content = svg_content.replace(placeholder, placeholder)

            return svg_content

        except Exception as e:
            print(f"Error updating placeholders: {e}")
            return svg_content

    def _extract_placeholders_from_mapping(self, content_mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract placeholders from content mapping"""
        try:
            placeholders = []
            
            # Extract text placeholders
            text_elements = content_mapping.get("text_elements", [])
            for i, element in enumerate(text_elements):
                placeholders.append({
                    "type": "text",
                    "id": f"TEXT_{i+1}",
                    "tag": f"{{TEXT_{i+1}}}",
                    "content": element.get("content", "Sample Text"),
                    "bbox": element.get("bbox", [0, 0, 100, 20])
                })
            
            # Extract image placeholders
            image_regions = content_mapping.get("image_regions", [])
            for i, region in enumerate(image_regions):
                placeholders.append({
                    "type": "image",
                    "id": f"IMAGE_{i+1}",
                    "tag": f"{{IMAGE_{i+1}}}",
                    "bbox": region.get("bbox", [0, 0, 100, 100])
                })
            
            return placeholders
            
        except Exception as e:
            print(f"Error extracting placeholders: {e}")
            return []

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        # Replace spaces with hyphens and convert to lowercase
        filename = filename.replace(" ", "-").lower()

        # Remove multiple consecutive hyphens
        while "--" in filename:
            filename = filename.replace("--", "-")

        # Remove leading/trailing hyphens
        filename = filename.strip("-")

        # Ensure filename is not empty
        if not filename:
            filename = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return filename