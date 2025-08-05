import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
import requests
import os
import tempfile
from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime
from .stock_photo_service import StockPhotoService


class PreviewGenerator:
    def __init__(self):
        self.stock_service = StockPhotoService()
        self.sample_content = {
            "{TITLE}": "Sample Title",
            "{SUBTITLE}": "Sample Subtitle",
            "{DESCRIPTION}": "Sample Description Text",
            "{AUTHOR}": "Sample Author",
            "{DATE}": "Sample Date",
            "{CATEGORY}": "Sample Category",
            "{TAG}": "Sample Tag",
            "{QUOTE}": "Sample Quote",
            "{CTA_TEXT}": "Click Here",
            "{PRICE}": "$99",
            "{DOMAIN}": "sample.com",
            "{SITE_NAME}": "Sample Website",
            "{BRAND_NAME}": "Sample Brand",
            "{URL}": "www.sample.com",
            "{USERNAME}": "@sampleuser",
            "{USER_HANDLE}": "@sample",
            "{FOLLOWERS}": "1.2K",
            "{LIKES}": "456",
            "{SHARES}": "123",
            "{VIEWS}": "2.3K",
            "{RATING}": "4.5",
            "{PERCENTAGE}": "85%",
            "{NUMBER}": "42",
        }

    async def create_preview(
        self, template_path: str, analysis: Dict[str, Any], template_name: str
    ) -> Dict[str, Any]:
        """Create JPEG preview from SVG template with sample content"""
        try:
            # Read SVG template
            with open(template_path, "r", encoding="utf-8") as f:
                svg_content = f.read()

            # Parse SVG
            root = ET.fromstring(svg_content)

            # Get dimensions
            width = int(root.attrib.get("width", 800))
            height = int(root.attrib.get("height", 600))

            # Create preview image
            preview_image = await self._render_preview(root, width, height, analysis)

            # Save preview
            preview_filename = f"{self._sanitize_filename(template_name)}.jpg"
            preview_path = f"previews/{preview_filename}"

            preview_image.save(preview_path, "JPEG", quality=85, optimize=True)

            return {
                "preview_path": preview_path,
                "preview_filename": preview_filename,
                "dimensions": {"width": width, "height": height},
                "status": "success",
            }

        except Exception as e:
            raise Exception(f"Preview generation failed: {str(e)}")

    async def _render_preview(
        self, svg_root: ET.Element, width: int, height: int, analysis: Dict[str, Any]
    ) -> Image.Image:
        """Render SVG template as PIL Image with sample content"""
        try:
            # Create blank image
            preview = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(preview)

            # Get background color from SVG
            bg_color = self._extract_background_color(svg_root)
            if bg_color:
                preview = Image.new("RGB", (width, height), bg_color)
                draw = ImageDraw.Draw(preview)

            # Process image placeholders first
            await self._render_image_placeholders(draw, svg_root, analysis)

            # Process text elements
            await self._render_text_elements(draw, svg_root)

            # Process decorative elements
            await self._render_decorative_elements(draw, svg_root)

            return preview

        except Exception as e:
            raise Exception(f"Preview rendering failed: {str(e)}")

    def _extract_background_color(self, svg_root: ET.Element) -> Optional[str]:
        """Extract background color from SVG"""
        try:
            # Look for background rectangle
            for rect in svg_root.iter("rect"):
                # Check if this is likely the background (full width/height)
                rect_width = rect.attrib.get("width", "0")
                rect_height = rect.attrib.get("height", "0")
                rect_x = rect.attrib.get("x", "0")
                rect_y = rect.attrib.get("y", "0")

                if (
                    rect_x == "0"
                    and rect_y == "0"
                    and rect_width == svg_root.attrib.get("width")
                    and rect_height == svg_root.attrib.get("height")
                ):

                    fill_color = rect.attrib.get("fill")
                    if fill_color and fill_color.startswith("#"):
                        return fill_color

            return None

        except Exception:
            return None

    async def _render_image_placeholders(
        self, draw: ImageDraw.Draw, svg_root: ET.Element, analysis: Dict[str, Any]
    ):
        """Render image placeholders with stock photos or placeholder graphics"""
        try:
            image_regions = analysis.get("image_regions", [])

            for i, region in enumerate(image_regions):
                if "bbox" not in region:
                    continue

                x1, y1, x2, y2 = region["bbox"]
                img_width = x2 - x1
                img_height = y2 - y1

                # Determine if we should use stock photo or placeholder
                image_type = region.get("type", "unknown")

                if image_type == "real_photo":
                    # Try to get stock photo
                    stock_image = await self._get_stock_image(img_width, img_height)
                    if stock_image:
                        # Resize and paste stock image
                        stock_image = stock_image.resize(
                            (img_width, img_height), Image.Resampling.LANCZOS
                        )
                        # Convert to RGB if necessary
                        if stock_image.mode != "RGB":
                            stock_image = stock_image.convert("RGB")

                        # Paste onto preview (need to handle this differently with PIL)
                        # For now, we'll draw a colored rectangle as placeholder
                        draw.rectangle(
                            [x1, y1, x2, y2], fill="#4CAF50", outline="#45a049", width=2
                        )

                        # Add "Stock Photo" text
                        try:
                            font = ImageFont.truetype(
                                "arial.ttf", min(16, img_height // 4)
                            )
                        except:
                            font = ImageFont.load_default()

                        text = "Stock Photo"
                        text_bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]

                        text_x = x1 + (img_width - text_width) // 2
                        text_y = y1 + (img_height - text_height) // 2

                        draw.text((text_x, text_y), text, fill="white", font=font)
                    else:
                        # Fallback to colored placeholder
                        draw.rectangle(
                            [x1, y1, x2, y2], fill="#2196F3", outline="#1976D2", width=2
                        )
                else:
                    # Keep as placeholder icon (gray with dashed border)
                    draw.rectangle(
                        [x1, y1, x2, y2], fill="#e0e0e0", outline="#cccccc", width=2
                    )

                    # Draw dashed border effect (simplified)
                    dash_length = 5
                    for x in range(x1, x2, dash_length * 2):
                        draw.line(
                            [x, y1, min(x + dash_length, x2), y1],
                            fill="#cccccc",
                            width=2,
                        )
                        draw.line(
                            [x, y2, min(x + dash_length, x2), y2],
                            fill="#cccccc",
                            width=2,
                        )

                    for y in range(y1, y2, dash_length * 2):
                        draw.line(
                            [x1, y, x1, min(y + dash_length, y2)],
                            fill="#cccccc",
                            width=2,
                        )
                        draw.line(
                            [x2, y, x2, min(y + dash_length, y2)],
                            fill="#cccccc",
                            width=2,
                        )

                    # Add placeholder text
                    try:
                        font = ImageFont.truetype("arial.ttf", min(16, img_height // 4))
                    except:
                        font = ImageFont.load_default()

                    placeholder_tag = region.get("placeholder_tag", f"{{IMAGE_{i+1}}}")
                    text_bbox = draw.textbbox((0, 0), placeholder_tag, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]

                    text_x = x1 + (img_width - text_width) // 2
                    text_y = y1 + (img_height - text_height) // 2

                    draw.text(
                        (text_x, text_y), placeholder_tag, fill="#666666", font=font
                    )

        except Exception as e:
            print(f"Error rendering image placeholders: {e}")

    async def _render_text_elements(self, draw: ImageDraw.Draw, svg_root: ET.Element):
        """Render text elements with sample content"""
        try:
            for text_elem in svg_root.iter("text"):
                # Get text properties
                x = int(float(text_elem.attrib.get("x", 0)))
                y = int(float(text_elem.attrib.get("y", 0)))
                font_size = int(float(text_elem.attrib.get("font-size", 16)))
                fill_color = text_elem.attrib.get("fill", "#000000")
                font_weight = text_elem.attrib.get("font-weight", "normal")

                # Get placeholder text and replace with sample content
                placeholder_text = text_elem.text or ""
                sample_text = self.sample_content.get(
                    placeholder_text, placeholder_text
                )

                # Load font
                try:
                    if font_weight == "bold":
                        font = ImageFont.truetype("arialbd.ttf", font_size)
                    else:
                        font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()

                # Convert color
                if fill_color.startswith("#"):
                    color = fill_color
                else:
                    color = "#000000"

                # Draw text
                draw.text((x, y), sample_text, fill=color, font=font)

        except Exception as e:
            print(f"Error rendering text elements: {e}")

    async def _render_decorative_elements(
        self, draw: ImageDraw.Draw, svg_root: ET.Element
    ):
        """Render decorative elements like borders, shapes"""
        try:
            for rect in svg_root.iter("rect"):
                # Skip background and image placeholder rectangles
                if rect.attrib.get("fill") in [
                    "#e0e0e0",
                    "#4CAF50",
                    "#2196F3",
                ] or rect.attrib.get("stroke-dasharray"):
                    continue

                x = int(float(rect.attrib.get("x", 0)))
                y = int(float(rect.attrib.get("y", 0)))
                width = int(float(rect.attrib.get("width", 0)))
                height = int(float(rect.attrib.get("height", 0)))

                fill_color = rect.attrib.get("fill", "none")
                stroke_color = rect.attrib.get("stroke", "none")
                stroke_width = int(float(rect.attrib.get("stroke-width", 1)))

                # Draw filled rectangle
                if fill_color != "none" and fill_color:
                    draw.rectangle([x, y, x + width, y + height], fill=fill_color)

                # Draw border
                if stroke_color != "none" and stroke_color:
                    draw.rectangle(
                        [x, y, x + width, y + height],
                        outline=stroke_color,
                        width=stroke_width,
                    )

        except Exception as e:
            print(f"Error rendering decorative elements: {e}")

    async def _get_stock_image(self, width: int, height: int) -> Optional[Image.Image]:
        """Get stock image from APIs"""
        try:
            # Use stock photo service
            stock_image_url = await self.stock_service.get_random_image(width, height)

            if stock_image_url:
                response = requests.get(stock_image_url, timeout=10)
                if response.status_code == 200:
                    # Save to temporary file and load as PIL Image
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".jpg"
                    ) as tmp_file:
                        tmp_file.write(response.content)
                        tmp_file.flush()

                        image = Image.open(tmp_file.name)
                        # Clean up temp file
                        os.unlink(tmp_file.name)

                        return image

            return None

        except Exception as e:
            print(f"Error getting stock image: {e}")
            return None

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
            filename = f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return filename
