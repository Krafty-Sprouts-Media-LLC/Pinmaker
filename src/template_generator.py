import xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import os
from typing import Dict, List, Any, Tuple
from pathlib import Path
import base64
from datetime import datetime

class TemplateGenerator:
    def __init__(self):
        self.placeholder_tags = [
            "{TITLE}", "{SUBTITLE}", "{DESCRIPTION}", "{AUTHOR}", "{DATE}", 
            "{CATEGORY}", "{TAG}", "{QUOTE}", "{CTA_TEXT}", "{PRICE}", 
            "{DOMAIN}", "{SITE_NAME}", "{BRAND_NAME}", "{URL}", "{LOGO}",
            "{IMAGE_URL}", "{IMAGE_1}", "{IMAGE_2}", "{IMAGE_3}", "{IMAGE_4}",
            "{IMAGE_5}", "{IMAGE_6}", "{IMAGE_7}", "{IMAGE_8}", "{IMAGE_9}",
            "{IMAGE_10}", "{AVATAR}", "{THUMBNAIL}", "{BACKGROUND_IMAGE}",
            "{USERNAME}", "{USER_HANDLE}", "{FOLLOWERS}", "{LIKES}", "{SHARES}",
            "{VIEWS}", "{RATING}", "{PERCENTAGE}", "{NUMBER}"
        ]
    
    async def create_template(self, image_path: str, template_name: str, content_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Create SVG template from analyzed image"""
        try:
            # Load and analyze the original image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            height, width = image.shape[:2]
            
            # Create SVG template
            svg_content = await self._create_svg_template(
                width, height, content_mapping, image
            )
            
            # Save template file
            template_filename = f"{self._sanitize_filename(template_name)}.svg"
            template_path = f"templates/{template_filename}"
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            # Create template metadata
            template_data = {
                "name": template_name,
                "filename": template_filename,
                "dimensions": {"width": width, "height": height},
                "placeholders": self._extract_placeholders_from_mapping(content_mapping),
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            return {
                "template_path": template_path,
                "template_data": template_data,
                "analysis": content_mapping,
                "status": "success"
            }
        
        except Exception as e:
            raise Exception(f"Template creation failed: {str(e)}")
    
    async def _create_svg_template(self, width: int, height: int, analysis: Dict[str, Any], original_image: np.ndarray) -> str:
        """Generate SVG template with high-accuracy visual recreation"""
        try:
            # Start SVG document
            svg_parts = []
            svg_parts.append(f'<?xml version="1.0" encoding="UTF-8"?>')
            svg_parts.append(f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">')
            
            # Add background
            background_info = analysis.get('background_info', {})
            bg_color = background_info.get('background_color', '#ffffff')
            svg_parts.append(f'<rect width="{width}" height="{height}" fill="{bg_color}"/>')
            
            # Add image placeholders first (behind text)
            image_regions = analysis.get('image_regions', [])
            for i, region in enumerate(image_regions):
                if 'bbox' in region:
                    x1, y1, x2, y2 = region['bbox']
                    img_width = x2 - x1
                    img_height = y2 - y1
                    
                    placeholder_tag = region.get('placeholder_tag', f'{{IMAGE_{i+1}}}')
                    
                    # Create image placeholder rectangle
                    svg_parts.append(
                        f'<rect x="{x1}" y="{y1}" width="{img_width}" height="{img_height}" '
                        f'fill="#e0e0e0" stroke="#cccccc" stroke-width="2" '
                        f'stroke-dasharray="5,5" opacity="0.8"/>'
                    )
                    
                    # Add placeholder text
                    text_x = x1 + img_width // 2
                    text_y = y1 + img_height // 2
                    font_size = min(16, img_height // 4)
                    
                    svg_parts.append(
                        f'<text x="{text_x}" y="{text_y}" '
                        f'font-family="Arial, sans-serif" font-size="{font_size}" '
                        f'fill="#666666" text-anchor="middle" dominant-baseline="middle">'
                        f'{placeholder_tag}</text>'
                    )
            
            # Add text elements with preserved styling
            text_elements = analysis.get('text_elements', [])
            fonts_info = analysis.get('fonts', {}).get('detected_fonts', [])
            colors = analysis.get('colors', {})
            
            for i, text_elem in enumerate(text_elements):
                if 'bbox' in text_elem and 'suggested_placeholder' in text_elem:
                    x1, y1, x2, y2 = text_elem['bbox']
                    placeholder = text_elem['suggested_placeholder']
                    
                    # Get font information for this text element
                    font_info = fonts_info[i] if i < len(fonts_info) else {}
                    font_size = font_info.get('estimated_size', 16)
                    
                    # Determine text color (use dominant color or black)
                    text_color = self._get_text_color(original_image, [x1, y1, x2, y2], colors)
                    
                    # Calculate text position
                    text_x = x1
                    text_y = y1 + font_size  # Baseline adjustment
                    
                    # Add text element
                    svg_parts.append(
                        f'<text x="{text_x}" y="{text_y}" '
                        f'font-family="Arial, sans-serif" font-size="{font_size}" '
                        f'fill="{text_color}" '
                        f'font-weight="{self._get_font_weight(font_info)}" '
                        f'text-anchor="start">'
                        f'{placeholder}</text>'
                    )
            
            # Add layout structure elements (decorative shapes, lines, etc.)
            layout_regions = analysis.get('layout_structure', {}).get('layout_regions', [])
            for region in layout_regions:
                if 'bbox' in region:
                    x1, y1, x2, y2 = region['bbox']
                    region_width = x2 - x1
                    region_height = y2 - y1
                    
                    # Only add decorative elements for larger regions
                    if region_width > 50 and region_height > 50:
                        # Check if this region doesn't overlap with text or images
                        if not self._overlaps_with_content(region['bbox'], text_elements, image_regions):
                            # Add subtle decorative border
                            svg_parts.append(
                                f'<rect x="{x1}" y="{y1}" width="{region_width}" height="{region_height}" '
                                f'fill="none" stroke="#f0f0f0" stroke-width="1" opacity="0.5"/>'
                            )
            
            # Close SVG
            svg_parts.append('</svg>')
            
            return '\n'.join(svg_parts)
        
        except Exception as e:
            raise Exception(f"SVG generation failed: {str(e)}")
    
    def _get_text_color(self, image: np.ndarray, bbox: List[int], colors: Dict[str, Any]) -> str:
        """Determine appropriate text color based on image analysis"""
        try:
            x1, y1, x2, y2 = bbox
            
            # Extract text region
            if y2 <= image.shape[0] and x2 <= image.shape[1] and y1 >= 0 and x1 >= 0:
                text_region = image[y1:y2, x1:x2]
                if text_region.size > 0:
                    # Calculate average color in text region
                    avg_color = np.mean(text_region, axis=(0, 1))
                    # Convert BGR to RGB and then to hex
                    rgb_color = (int(avg_color[2]), int(avg_color[1]), int(avg_color[0]))
                    return "#{:02x}{:02x}{:02x}".format(*rgb_color)
            
            # Fallback to dominant color or black
            dominant_color = colors.get('dominant_color', '#000000')
            return dominant_color
        
        except Exception:
            return '#000000'  # Default to black
    
    def _get_font_weight(self, font_info: Dict[str, Any]) -> str:
        """Determine font weight based on analysis"""
        text_type = font_info.get('text_type', 'body')
        
        if text_type == 'title':
            return 'bold'
        elif text_type == 'subtitle':
            return '600'
        else:
            return 'normal'
    
    def _overlaps_with_content(self, bbox: List[int], text_elements: List[Dict], image_regions: List[Dict]) -> bool:
        """Check if a region overlaps with existing content"""
        x1, y1, x2, y2 = bbox
        
        # Check overlap with text elements
        for text_elem in text_elements:
            if 'bbox' in text_elem:
                tx1, ty1, tx2, ty2 = text_elem['bbox']
                if not (x2 < tx1 or x1 > tx2 or y2 < ty1 or y1 > ty2):
                    return True
        
        # Check overlap with image regions
        for img_region in image_regions:
            if 'bbox' in img_region:
                ix1, iy1, ix2, iy2 = img_region['bbox']
                if not (x2 < ix1 or x1 > ix2 or y2 < iy1 or y1 > iy2):
                    return True
        
        return False
    
    def _extract_placeholders_from_mapping(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract all placeholder tags used in the template"""
        placeholders = set()
        
        # From text elements
        text_elements = analysis.get('text_elements', [])
        for elem in text_elements:
            placeholder = elem.get('suggested_placeholder')
            if placeholder:
                placeholders.add(placeholder)
        
        # From image regions
        image_regions = analysis.get('image_regions', [])
        for region in image_regions:
            placeholder = region.get('placeholder_tag')
            if placeholder:
                placeholders.add(placeholder)
        
        return sorted(list(placeholders))
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Replace spaces with hyphens and convert to lowercase
        filename = filename.replace(' ', '-').lower()
        
        # Remove multiple consecutive hyphens
        while '--' in filename:
            filename = filename.replace('--', '-')
        
        # Remove leading/trailing hyphens
        filename = filename.strip('-')
        
        # Ensure filename is not empty
        if not filename:
            filename = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return filename
    
    async def update_template(self, template_path: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing template with user modifications"""
        try:
            # Read existing template
            with open(template_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Parse SVG
            root = ET.fromstring(svg_content)
            
            # Apply updates
            if 'colors' in updates:
                await self._update_colors(root, updates['colors'])
            
            if 'fonts' in updates:
                await self._update_fonts(root, updates['fonts'])
            
            if 'positions' in updates:
                await self._update_positions(root, updates['positions'])
            
            if 'placeholders' in updates:
                await self._update_placeholders(root, updates['placeholders'])
            
            # Convert back to string
            updated_svg = ET.tostring(root, encoding='unicode')
            
            # Save updated template
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(updated_svg)
            
            return {
                "template_path": template_path,
                "analysis": updates,
                "status": "updated"
            }
        
        except Exception as e:
            raise Exception(f"Template update failed: {str(e)}")
    
    async def _update_colors(self, root: ET.Element, color_updates: Dict[str, str]):
        """Update colors in SVG template"""
        for element in root.iter():
            # Update fill colors
            if 'fill' in element.attrib:
                old_color = element.attrib['fill']
                if old_color in color_updates:
                    element.attrib['fill'] = color_updates[old_color]
            
            # Update stroke colors
            if 'stroke' in element.attrib:
                old_color = element.attrib['stroke']
                if old_color in color_updates:
                    element.attrib['stroke'] = color_updates[old_color]
    
    async def _update_fonts(self, root: ET.Element, font_updates: Dict[str, Any]):
        """Update font properties in SVG template"""
        for text_elem in root.iter('text'):
            if 'font-family' in font_updates:
                text_elem.attrib['font-family'] = font_updates['font-family']
            
            if 'font-size' in font_updates:
                text_elem.attrib['font-size'] = str(font_updates['font-size'])
            
            if 'font-weight' in font_updates:
                text_elem.attrib['font-weight'] = font_updates['font-weight']
    
    async def _update_positions(self, root: ET.Element, position_updates: Dict[str, Dict[str, float]]):
        """Update element positions in SVG template"""
        for element_id, new_pos in position_updates.items():
            # Find element by ID or content
            for element in root.iter():
                if (element.attrib.get('id') == element_id or 
                    element.text == element_id):
                    
                    if 'x' in new_pos:
                        element.attrib['x'] = str(new_pos['x'])
                    if 'y' in new_pos:
                        element.attrib['y'] = str(new_pos['y'])
                    if 'width' in new_pos:
                        element.attrib['width'] = str(new_pos['width'])
                    if 'height' in new_pos:
                        element.attrib['height'] = str(new_pos['height'])
    
    async def _update_placeholders(self, root: ET.Element, placeholder_updates: Dict[str, str]):
        """Update placeholder tags in SVG template"""
        for text_elem in root.iter('text'):
            if text_elem.text and text_elem.text in placeholder_updates:
                text_elem.text = placeholder_updates[text_elem.text]