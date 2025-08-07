#!/usr/bin/env python3
"""
Simple Gradio Demo for Pinmaker

This shows how Pinmaker could work with a beautiful web interface
using Gradio - no React build process needed!
"""

import gradio as gr
import os
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional
import tempfile
import json


class GradioPinmaker:
    def __init__(self):
        self.templates = [
            "Modern Card",
            "Bold Typography", 
            "Vintage Style",
            "Minimalist",
            "Creative Burst"
        ]
        
        self.fonts = [
            "Arial",
            "Helvetica",
            "Times New Roman",
            "Georgia",
            "Verdana"
        ]
        
        self.color_schemes = {
            "Energetic": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
            "Professional": ["#2C3E50", "#3498DB", "#ECF0F1"],
            "Warm": ["#E74C3C", "#F39C12", "#F1C40F"],
            "Cool": ["#3498DB", "#9B59B6", "#1ABC9C"],
            "Nature": ["#27AE60", "#2ECC71", "#F39C12"],
            "Sunset": ["#E67E22", "#E74C3C", "#F39C12"]
        }
    
    def analyze_image(self, image) -> str:
        """Mock image analysis"""
        if image is None:
            return "No image uploaded"
        
        # Mock analysis
        analysis = {
            "dominant_colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
            "style": "Modern",
            "mood": "Energetic", 
            "suggested_text_color": "White",
            "recommended_template": "Modern Card",
            "composition": "Centered"
        }
        
        return json.dumps(analysis, indent=2)
    
    def create_pin(self, 
                   text: str,
                   template: str,
                   font: str,
                   color_scheme: str,
                   background_image=None) -> Image.Image:
        """Create a pin with the given parameters"""
        
        # Get colors for the scheme
        colors = self.color_schemes.get(color_scheme, ["#FF6B6B", "#4ECDC4", "#45B7D1"])
        
        # Create pin
        width, height = 800, 600
        
        if background_image is not None:
            # Use uploaded background
            bg = Image.open(background_image).convert('RGB')
            bg = bg.resize((width, height), Image.Resampling.LANCZOS)
            image = bg.copy()
            
            # Add overlay for text readability
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 128))
            image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        else:
            # Create gradient background
            image = Image.new('RGB', (width, height), colors[0])
            draw_bg = ImageDraw.Draw(image)
            
            for i in range(height):
                alpha = i / height
                r1, g1, b1 = int(colors[0][1:3], 16), int(colors[0][3:5], 16), int(colors[0][5:7], 16)
                r2, g2, b2 = int(colors[1][1:3], 16), int(colors[1][3:5], 16), int(colors[1][5:7], 16)
                
                r = int(r1 * (1 - alpha) + r2 * alpha)
                g = int(g1 * (1 - alpha) + g2 * alpha)
                b = int(b1 * (1 - alpha) + b2 * alpha)
                
                draw_bg.line([(0, i), (width, i)], fill=(r, g, b))
        
        draw = ImageDraw.Draw(image)
        
        # Add template-specific decorations
        if template == "Modern Card":
            margin = 50
            draw.rounded_rectangle(
                [margin, margin, width-margin, height-margin],
                radius=20, outline='white', width=4
            )
        elif template == "Bold Typography":
            for i in range(0, width, 120):
                draw.line([(i, 0), (i+60, height)], fill=colors[2] if len(colors) > 2 else '#FFFFFF', width=3)
        elif template == "Vintage Style":
            for thickness in range(3):
                draw.rectangle(
                    [thickness*15, thickness*15, width-thickness*15, height-thickness*15],
                    outline='white', width=3
                )
        elif template == "Creative Burst":
            # Add radiating lines from center
            center_x, center_y = width//2, height//2
            for angle in range(0, 360, 30):
                import math
                end_x = center_x + int(200 * math.cos(math.radians(angle)))
                end_y = center_y + int(200 * math.sin(math.radians(angle)))
                draw.line([(center_x, center_y), (end_x, end_y)], 
                         fill=colors[2] if len(colors) > 2 else '#FFFFFF', width=2)
        
        # Add text
        if text:
            try:
                font_size = 52
                try:
                    if os.name == 'nt':  # Windows
                        font_path = f"C:/Windows/Fonts/{font.lower().replace(' ', '')}.ttf"
                        if not os.path.exists(font_path):
                            font_path = "C:/Windows/Fonts/arial.ttf"
                    else:
                        font_path = f"/usr/share/fonts/truetype/dejavu/DejaVu{font.replace(' ', '')}.ttf"
                        if not os.path.exists(font_path):
                            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                    
                    if os.path.exists(font_path):
                        pil_font = ImageFont.truetype(font_path, font_size)
                    else:
                        pil_font = ImageFont.load_default()
                except:
                    pil_font = ImageFont.load_default()
                
                # Process text
                text_lines = text.split('\n') if '\n' in text else [text]
                total_height = len(text_lines) * (font_size + 15)
                y_start = (height - total_height) // 2
                
                for i, line in enumerate(text_lines):
                    if not line.strip():
                        continue
                        
                    # Calculate position
                    bbox = draw.textbbox((0, 0), line, font=pil_font)
                    text_width = bbox[2] - bbox[0]
                    x = (width - text_width) // 2
                    y = y_start + i * (font_size + 15)
                    
                    # Draw text shadow
                    for dx in [-3, -2, -1, 0, 1, 2, 3]:
                        for dy in [-3, -2, -1, 0, 1, 2, 3]:
                            if dx != 0 or dy != 0:
                                draw.text((x + dx, y + dy), line, font=pil_font, fill='black')
                    
                    # Draw main text
                    draw.text((x, y), line, font=pil_font, fill='white')
                
            except Exception as e:
                # Fallback text
                draw.text((50, height//2), f"Text: {text}", fill='white')
        
        return image
    
    def search_stock_photos(self, query: str) -> str:
        """Mock stock photo search"""
        if not query:
            return "Enter a search term"
        
        results = [
            f"📸 Professional {query} photo - High resolution",
            f"🎨 Creative {query} illustration - Vector format", 
            f"🌟 Premium {query} image - Commercial license",
            f"💼 Business {query} photo - Corporate style",
            f"🎯 Modern {query} design - Minimalist approach"
        ]
        
        return "\n".join(results)


def create_interface():
    """Create the Gradio interface"""
    pinmaker = GradioPinmaker()
    
    with gr.Blocks(title="Pinmaker - Python Edition", theme=gr.themes.Soft()) as interface:
        gr.Markdown(
            """
            # 🎨 Pinmaker - Python Edition
            
            **Create beautiful pins with pure Python - no React build process needed!**
            
            This demonstrates how Pinmaker could work with a modern web interface using Gradio.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Pin Content")
                
                text_input = gr.Textbox(
                    label="Pin Text",
                    placeholder="Enter your pin text here...\nUse line breaks for multiple lines",
                    lines=3,
                    value="Create\nAmazing\nPins!"
                )
                
                template_dropdown = gr.Dropdown(
                    choices=pinmaker.templates,
                    label="Template Style",
                    value="Modern Card"
                )
                
                font_dropdown = gr.Dropdown(
                    choices=pinmaker.fonts,
                    label="Font Family",
                    value="Arial"
                )
                
                color_dropdown = gr.Dropdown(
                    choices=list(pinmaker.color_schemes.keys()),
                    label="Color Scheme",
                    value="Energetic"
                )
                
                background_upload = gr.Image(
                    label="Background Image (Optional)",
                    type="filepath"
                )
                
                generate_btn = gr.Button(
                    "🎨 Generate Pin",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 🖼️ Pin Preview")
                
                pin_output = gr.Image(
                    label="Generated Pin",
                    type="pil"
                )
                
                gr.Markdown("### 🔍 Image Analysis")
                
                analysis_upload = gr.Image(
                    label="Upload Image to Analyze",
                    type="filepath"
                )
                
                analyze_btn = gr.Button("🔍 Analyze Image")
                
                analysis_output = gr.Textbox(
                    label="Analysis Results",
                    lines=8,
                    interactive=False
                )
                
                gr.Markdown("### 📸 Stock Photos")
                
                stock_query = gr.Textbox(
                    label="Search Query",
                    placeholder="e.g., business, nature, technology"
                )
                
                search_btn = gr.Button("🔍 Search Stock Photos")
                
                stock_results = gr.Textbox(
                    label="Search Results",
                    lines=6,
                    interactive=False
                )
        
        # Event handlers
        generate_btn.click(
            fn=pinmaker.create_pin,
            inputs=[text_input, template_dropdown, font_dropdown, color_dropdown, background_upload],
            outputs=pin_output
        )
        
        analyze_btn.click(
            fn=pinmaker.analyze_image,
            inputs=analysis_upload,
            outputs=analysis_output
        )
        
        search_btn.click(
            fn=pinmaker.search_stock_photos,
            inputs=stock_query,
            outputs=stock_results
        )
        
        # Auto-generate on parameter change
        for input_component in [text_input, template_dropdown, font_dropdown, color_dropdown]:
            input_component.change(
                fn=pinmaker.create_pin,
                inputs=[text_input, template_dropdown, font_dropdown, color_dropdown, background_upload],
                outputs=pin_output
            )
        
        gr.Markdown(
            """
            ---
            
            ### 🚀 Advantages of Python-Only Approach:
            
            - ✅ **No Build Process**: Just run Python - no npm, webpack, or React compilation
            - ✅ **Single Technology**: Everything in Python - easier to maintain
            - ✅ **Rapid Development**: Changes are immediately visible
            - ✅ **Simple Deployment**: One Python app instead of frontend + backend
            - ✅ **Beautiful UI**: Gradio provides modern, responsive interface
            - ✅ **Real-time Updates**: Interface updates as you type
            - ✅ **Easy Integration**: Direct access to your existing Python code
            
            **This is just a demo - your existing code remains completely untouched!**
            """
        )
    
    return interface


if __name__ == "__main__":
    # Check if gradio is available
    try:
        import gradio as gr
        interface = create_interface()
        print("\n🎨 Starting Pinmaker Gradio Demo...")
        print("📱 This will open a beautiful web interface in your browser!")
        print("🔗 The interface will be available at: http://localhost:7860")
        print("\n✨ Features:")
        print("  - Real-time pin generation")
        print("  - Image analysis simulation")
        print("  - Stock photo search mock")
        print("  - Multiple templates and color schemes")
        print("  - Background image upload")
        print("\n🚀 No React, no build process - just pure Python!")
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )
    except ImportError:
        print("❌ Gradio not installed. Install with: pip install gradio")
        print("\n💡 This demo shows how Pinmaker could work with a beautiful web interface")
        print("   using Gradio - no React build process needed!")