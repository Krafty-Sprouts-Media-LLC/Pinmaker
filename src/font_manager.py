import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
import base64


class FontManager:
    def __init__(self):
        self.fonts_dir = Path("fonts")
        self.fonts_dir.mkdir(exist_ok=True)

        self.font_registry_file = self.fonts_dir / "font_registry.json"
        self.font_registry = self._load_font_registry()

        # Supported font formats
        self.supported_formats = [".ttf", ".otf", ".woff", ".woff2"]

        # Default web-safe fonts
        self.web_safe_fonts = {
            "Arial": {"family": "Arial", "type": "sans-serif", "web_safe": True},
            "Helvetica": {
                "family": "Helvetica",
                "type": "sans-serif",
                "web_safe": True,
            },
            "Times New Roman": {
                "family": "Times New Roman",
                "type": "serif",
                "web_safe": True,
            },
            "Georgia": {"family": "Georgia", "type": "serif", "web_safe": True},
            "Courier New": {
                "family": "Courier New",
                "type": "monospace",
                "web_safe": True,
            },
            "Verdana": {"family": "Verdana", "type": "sans-serif", "web_safe": True},
            "Trebuchet MS": {
                "family": "Trebuchet MS",
                "type": "sans-serif",
                "web_safe": True,
            },
            "Impact": {"family": "Impact", "type": "sans-serif", "web_safe": True},
        }

    def _load_font_registry(self) -> Dict[str, Any]:
        """Load font registry from file"""
        try:
            if self.font_registry_file.exists():
                with open(self.font_registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading font registry: {e}")
            return {}

    def _save_font_registry(self):
        """Save font registry to file"""
        try:
            with open(self.font_registry_file, "w", encoding="utf-8") as f:
                json.dump(self.font_registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving font registry: {e}")

    async def register_font(self, font_path: str) -> Dict[str, Any]:
        """Register a new font file and extract metadata"""
        try:
            font_path = Path(font_path)

            if not font_path.exists():
                raise FileNotFoundError(f"Font file not found: {font_path}")

            # Validate font format
            if font_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported font format: {font_path.suffix}")

            # Extract font metadata
            font_info = await self._extract_font_info(font_path)

            # Generate unique font ID
            font_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{font_path.stem}"

            # Store font info in registry
            self.font_registry[font_id] = {
                "id": font_id,
                "filename": font_path.name,
                "path": str(font_path),
                "format": font_path.suffix.lower(),
                "family_name": font_info["family_name"],
                "style_name": font_info["style_name"],
                "full_name": font_info["full_name"],
                "type": font_info["type"],
                "weight": font_info["weight"],
                "italic": font_info["italic"],
                "uploaded_at": datetime.now().isoformat(),
                "file_size": font_path.stat().st_size,
                "web_safe": False,
            }

            # Save registry
            self._save_font_registry()

            return self.font_registry[font_id]

        except Exception as e:
            raise Exception(f"Font registration failed: {str(e)}")

    async def _extract_font_info(self, font_path: Path) -> Dict[str, Any]:
        """Extract metadata from font file"""
        try:
            # Only process TTF and OTF files with fontTools
            if font_path.suffix.lower() in [".ttf", ".otf"]:
                font = TTFont(font_path)

                # Extract name table
                name_table = font["name"]

                # Get font names
                family_name = self._get_font_name(name_table, 1) or font_path.stem
                style_name = self._get_font_name(name_table, 2) or "Regular"
                full_name = (
                    self._get_font_name(name_table, 4) or f"{family_name} {style_name}"
                )

                # Determine font type
                font_type = self._determine_font_type(family_name, style_name)

                # Extract weight and style info
                weight = self._extract_weight(style_name)
                italic = (
                    "italic" in style_name.lower() or "oblique" in style_name.lower()
                )

                font.close()

                return {
                    "family_name": family_name,
                    "style_name": style_name,
                    "full_name": full_name,
                    "type": font_type,
                    "weight": weight,
                    "italic": italic,
                }

            else:
                # For WOFF/WOFF2, use filename-based extraction
                return self._extract_info_from_filename(font_path)

        except Exception as e:
            print(f"Error extracting font info: {e}")
            return self._extract_info_from_filename(font_path)

    def _get_font_name(self, name_table, name_id: int) -> Optional[str]:
        """Extract specific name from font name table"""
        try:
            for record in name_table.names:
                if record.nameID == name_id:
                    if record.platformID == 3:  # Microsoft platform
                        return record.toUnicode()
                    elif record.platformID == 1:  # Macintosh platform
                        return record.toUnicode()
            return None
        except Exception:
            return None

    def _determine_font_type(self, family_name: str, style_name: str) -> str:
        """Determine font type (serif, sans-serif, monospace, etc.)"""
        family_lower = family_name.lower()
        style_lower = style_name.lower()

        # Check for monospace indicators
        if any(
            keyword in family_lower
            for keyword in ["mono", "courier", "console", "code"]
        ):
            return "monospace"

        # Check for serif indicators
        if any(
            keyword in family_lower
            for keyword in ["times", "georgia", "serif", "garamond"]
        ):
            return "serif"

        # Check for script/decorative indicators
        if any(
            keyword in family_lower
            for keyword in ["script", "brush", "hand", "cursive"]
        ):
            return "cursive"

        # Default to sans-serif
        return "sans-serif"

    def _extract_weight(self, style_name: str) -> str:
        """Extract font weight from style name"""
        style_lower = style_name.lower()

        if "thin" in style_lower or "hairline" in style_lower:
            return "100"
        elif "extralight" in style_lower or "ultralight" in style_lower:
            return "200"
        elif "light" in style_lower:
            return "300"
        elif "medium" in style_lower:
            return "500"
        elif "semibold" in style_lower or "demibold" in style_lower:
            return "600"
        elif "bold" in style_lower:
            return "700"
        elif "extrabold" in style_lower or "ultrabold" in style_lower:
            return "800"
        elif "black" in style_lower or "heavy" in style_lower:
            return "900"
        else:
            return "400"  # Normal/Regular

    def _extract_info_from_filename(self, font_path: Path) -> Dict[str, Any]:
        """Extract font info from filename when fontTools can't be used"""
        filename = font_path.stem

        # Try to parse filename for font info
        parts = filename.replace("-", " ").replace("_", " ").split()

        family_name = parts[0] if parts else filename
        style_name = " ".join(parts[1:]) if len(parts) > 1 else "Regular"

        return {
            "family_name": family_name,
            "style_name": style_name,
            "full_name": f"{family_name} {style_name}",
            "type": self._determine_font_type(family_name, style_name),
            "weight": self._extract_weight(style_name),
            "italic": "italic" in style_name.lower(),
        }

    async def list_fonts(self) -> List[Dict[str, Any]]:
        """Get list of all available fonts (web-safe + uploaded)"""
        try:
            fonts = []

            # Add web-safe fonts
            for font_name, font_info in self.web_safe_fonts.items():
                fonts.append(
                    {
                        "id": f"web_safe_{font_name.lower().replace(' ', '_')}",
                        "family_name": font_name,
                        "style_name": "Regular",
                        "full_name": font_name,
                        "type": font_info["type"],
                        "weight": "400",
                        "italic": False,
                        "web_safe": True,
                        "format": "system",
                    }
                )

            # Add uploaded fonts
            for font_id, font_info in self.font_registry.items():
                # Check if font file still exists
                if Path(font_info["path"]).exists():
                    fonts.append(font_info)
                else:
                    # Remove from registry if file doesn't exist
                    del self.font_registry[font_id]

            # Save updated registry
            self._save_font_registry()

            return fonts

        except Exception as e:
            raise Exception(f"Failed to list fonts: {str(e)}")

    async def get_font_info(self, font_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific font"""
        try:
            # Check web-safe fonts
            if font_id.startswith("web_safe_"):
                font_name = font_id.replace("web_safe_", "").replace("_", " ").title()
                if font_name in self.web_safe_fonts:
                    return {
                        "id": font_id,
                        "family_name": font_name,
                        "web_safe": True,
                        **self.web_safe_fonts[font_name],
                    }

            # Check uploaded fonts
            return self.font_registry.get(font_id)

        except Exception as e:
            print(f"Error getting font info: {e}")
            return None

    async def delete_font(self, font_id: str) -> bool:
        """Delete an uploaded font"""
        try:
            if font_id not in self.font_registry:
                return False

            font_info = self.font_registry[font_id]
            font_path = Path(font_info["path"])

            # Delete font file
            if font_path.exists():
                font_path.unlink()

            # Remove from registry
            del self.font_registry[font_id]

            # Save updated registry
            self._save_font_registry()

            return True

        except Exception as e:
            print(f"Error deleting font: {e}")
            return False

    async def get_font_css(self, font_id: str) -> Optional[str]:
        """Generate CSS @font-face rule for uploaded font"""
        try:
            font_info = await self.get_font_info(font_id)

            if not font_info or font_info.get("web_safe", False):
                return None

            font_path = Path(font_info["path"])
            if not font_path.exists():
                return None

            # Read font file and encode as base64
            with open(font_path, "rb") as f:
                font_data = base64.b64encode(f.read()).decode("utf-8")

            # Determine MIME type
            format_map = {
                ".ttf": "font/ttf",
                ".otf": "font/otf",
                ".woff": "font/woff",
                ".woff2": "font/woff2",
            }

            mime_type = format_map.get(font_info["format"], "font/ttf")

            # Generate CSS
            css = f"""@font-face {{
    font-family: '{font_info['family_name']}';
    src: url('data:{mime_type};base64,{font_data}') format('{font_info['format'][1:]}');
    font-weight: {font_info['weight']};
    font-style: {'italic' if font_info['italic'] else 'normal'};
}}"""

            return css

        except Exception as e:
            print(f"Error generating font CSS: {e}")
            return None

    async def cleanup_unused_fonts(self) -> int:
        """Remove font files that are not in the registry"""
        try:
            removed_count = 0

            # Get all font files in directory
            font_files = []
            for ext in self.supported_formats:
                font_files.extend(self.fonts_dir.glob(f"*{ext}"))

            # Get registered font paths
            registered_paths = {
                Path(info["path"]) for info in self.font_registry.values()
            }

            # Remove unregistered files
            for font_file in font_files:
                if (
                    font_file not in registered_paths
                    and font_file.name != "font_registry.json"
                ):
                    try:
                        font_file.unlink()
                        removed_count += 1
                    except Exception as e:
                        print(f"Error removing {font_file}: {e}")

            return removed_count

        except Exception as e:
            print(f"Error during cleanup: {e}")
            return 0

    def get_font_stats(self) -> Dict[str, Any]:
        """Get font manager statistics"""
        try:
            total_fonts = len(self.font_registry) + len(self.web_safe_fonts)
            uploaded_fonts = len(self.font_registry)
            web_safe_fonts = len(self.web_safe_fonts)

            # Calculate total file size
            total_size = 0
            for font_info in self.font_registry.values():
                font_path = Path(font_info["path"])
                if font_path.exists():
                    total_size += font_path.stat().st_size

            # Group by type
            font_types = {}
            for font_info in self.font_registry.values():
                font_type = font_info.get("type", "unknown")
                font_types[font_type] = font_types.get(font_type, 0) + 1

            return {
                "total_fonts": total_fonts,
                "uploaded_fonts": uploaded_fonts,
                "web_safe_fonts": web_safe_fonts,
                "total_file_size_bytes": total_size,
                "total_file_size_mb": round(total_size / (1024 * 1024), 2),
                "font_types": font_types,
                "supported_formats": self.supported_formats,
            }

        except Exception as e:
            print(f"Error getting font stats: {e}")
            return {}
