#!/usr/bin/env python3
"""
Gradio Prototype for Pinmaker

This is a demonstration of how Pinmaker could work with Gradio interface.
It imports and uses your existing backend code without modifying any files.
"""

import gradio as gr
import asyncio
import os
import tempfile
from pathlib import Path
from PIL import Image
import json
from typing import Optional, List, Dict, Any

# Import your existing backend modules
from src.image_analyzer import ImageAnalyzer
from src.template_generator import TemplateGenerator
from src.preview_generator import PreviewGenerator
from src.stock_photo_service import StockPhotoService
from src.font_manager import FontManager


class PinmakerGradioApp:
    def __init__(self):
        """Initialize the Gradio app with your existing backend services"""
        # Initialize your existing services
        self.image_analyzer = ImageAnalyzer()
        self.stock_service = StockPhotoService()
        self.font_manager = FontManager()
        self.template_generator = TemplateGenerator()
        self.preview_generator = PreviewGenerator(self.stock_service)
        
        # Create necessary directories
        self.setup_directories()
        
        # Get available fonts and templates
        self.available_fonts = self.get_available_fonts()
        self.available_templates = self.get_available_templates()
        
    def setup_directories(self):
        """Create necessary directories for the prototype"""
        directories = ['uploads', 'templates', 'previews', 'fonts']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def get_available_fonts(self) -> List[str]:
        """Get list of available fonts from font manager"""
        try:
            fonts = self.font_manager.list_fonts()
            font_names = [font.get('family', 'Unknown') for font in fonts.get('fonts', [])]
            # Add some default fonts if none available
            if not font_names:
                font_names = ['Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Verdana']
            return font_names
        except Exception as e:
            print(f"Error getting fonts: {e}")
            return ['Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Verdana']
    
    def get_available_templates(self) -> List[str]:
        """Get list of available templates"""
        try:
            template_dir = Path('templates')
            if template_dir.exists():
                templates = [f.stem for f in template_dir.glob('*.svg')]
                if templates:
                    return templates
        except Exception as e:
            print(f"Error getting templates: {e}")
        
        # Return some sample template names if none found
        return ['Modern Card', 'Vintage Style', 'Bold Typography', 'Minimalist', 'Creative Layout']
    
    async def analyze_image_async(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze uploaded image using your existing image analyzer"""
        try:
            # Save image temporarily
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                image.save(tmp_file.name, 'JPEG')
                
                # Use your existing image analyzer
                analysis = await self.image_analyzer.analyze_image(tmp_file.name)
                
                # Clean up
                os.unlink(tmp_file.name)
                
                return analysis
        except Exception as e:
            return {'error': f'Image analysis failed: {str(e)}'}
    
    def analyze_image(self, image: Optional[Image.Image]) -> str:
        """Wrapper for async image analysis"""
        if image is None:
            return "No image uploaded"
        
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(self.analyze_image_async(image))
            loop.close()
            
            if 'error' in analysis:
                return f"❌ {analysis['error']}"
            
            # Format analysis results nicely
            result = "🎨 **Image Analysis Results:**\n\n"
            
            if 'colors' in analysis:
                result += f"**Dominant Colors:** {', '.join(analysis['colors'][:5])}\n"
            
            if 'style' in analysis:
                result += f"**Detected Style:** {analysis['style']}\n"
            
            if 'mood' in analysis:
                result += f"**Mood:** {analysis['mood']}\n"
            
            if 'composition' in analysis:
                result += f"**Composition:** {analysis['composition']}\n"
            
            if 'text_areas' in analysis:
                result += f"**Text Areas Detected:** {len(analysis['text_areas'])}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Analysis failed: {str(e)}"
    
    async def generate_pin_async(self, text: str, font: str, template: str, 
                                background_image: Optional[Image.Image]) -> Image.Image:
        """Generate pin using your existing backend logic"""
        try:
            # Analyze background image if provided
            analysis = {}
            if background_image:
                analysis = await self.analyze_image_async(background_image)
            
            # For prototype, create a simple preview
            # In real implementation, this would use your template generator
            preview_image = Image.new('RGB', (800, 600), 'white')
            
            # This is where you'd integrate with your actual template generation
            # template_path = await self.template_generator.generate_template(...)
            # preview = await self.preview_generator.create_preview(template_path, analysis, template)
            
            return preview_image
            
        except Exception as e:
            # Return error image
            error_image = Image.new('RGB', (800, 600), 'red')
            return error_image
    
    def generate_pin(self, text: str, font: str, template: str, 
                    background_image: Optional[Image.Image]) -> Image.Image:
        """Wrapper for async pin generation"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.generate_pin_async(text, font, template, background_image)
            )
            loop.close()
            return result
        except Exception as e:
            # Return error image
            error_image = Image.new('RGB', (800, 600), 'lightgray')
            return error_image
    
    def search_stock_photos(self, query: str) -> List[str]:
        """Search for stock photos using your existing service"""
        try:
            # This would use your actual stock photo service
            # results = await self.stock_service.search_photos(query)
            
            # For prototype, return placeholder URLs
            return [
                f"https://picsum.photos/400/300?random=1&query={query}",
                f"https://picsum.photos/400/300?random=2&query={query}",
                f"https://picsum.photos/400/300?random=3&query={query}"
            ]
        except Exception as e:
            return []
    
    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(title="Pinmaker - Gradio Prototype", theme=gr.themes.Soft()) as app:
            gr.Markdown(
                """
                # 🎨 Pinmaker - Gradio Prototype
                
                This is a demonstration of how Pinmaker could work with a Gradio interface.
                It uses your existing backend code without modifying any files.
                
                **Features:**
                - Image analysis using your existing ImageAnalyzer
                - Font selection from your FontManager
                - Template-based pin generation
                - Stock photo integration
                - Real-time preview generation
                """
            )
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📝 Pin Content")
                    
                    pin_text = gr.Textbox(
                        label="Pin Text",
                        placeholder="Enter your pin text here...",
                        lines=3
                    )
                    
                    font_choice = gr.Dropdown(
                        choices=self.available_fonts,
                        label="Font Family",
                        value=self.available_fonts[0] if self.available_fonts else "Arial"
                    )
                    
                    template_choice = gr.Dropdown(
                        choices=self.available_templates,
                        label="Template Style",
                        value=self.available_templates[0] if self.available_templates else "Modern Card"
                    )
                    
                    gr.Markdown("### 🖼️ Background Image")
                    
                    background_image = gr.Image(
                        label="Upload Background Image",
                        type="pil",
                        height=200
                    )
                    
                    analyze_btn = gr.Button("🔍 Analyze Image", variant="secondary")
                    
                    analysis_output = gr.Markdown(
                        label="Analysis Results",
                        value="Upload an image to see analysis results"
                    )
                    
                    gr.Markdown("### 📸 Stock Photos")
                    
                    stock_query = gr.Textbox(
                        label="Search Stock Photos",
                        placeholder="e.g., nature, business, food"
                    )
                    
                    search_btn = gr.Button("🔍 Search", variant="secondary")
                    
                    stock_gallery = gr.Gallery(
                        label="Stock Photos",
                        show_label=True,
                        elem_id="gallery",
                        columns=2,
                        rows=2,
                        height="auto"
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("### 🎨 Pin Preview")
                    
                    generate_btn = gr.Button(
                        "✨ Generate Pin", 
                        variant="primary",
                        size="lg"
                    )
                    
                    pin_output = gr.Image(
                        label="Generated Pin",
                        type="pil",
                        height=400
                    )
                    
                    download_btn = gr.DownloadButton(
                        "💾 Download Pin",
                        variant="secondary"
                    )
                    
                    gr.Markdown(
                        """
                        ### 💡 Tips:
                        - Upload a background image for better results
                        - Use the image analysis to understand colors and style
                        - Try different fonts and templates
                        - Search stock photos for inspiration
                        """
                    )
            
            # Event handlers
            analyze_btn.click(
                fn=self.analyze_image,
                inputs=[background_image],
                outputs=[analysis_output]
            )
            
            search_btn.click(
                fn=self.search_stock_photos,
                inputs=[stock_query],
                outputs=[stock_gallery]
            )
            
            generate_btn.click(
                fn=self.generate_pin,
                inputs=[pin_text, font_choice, template_choice, background_image],
                outputs=[pin_output]
            )
            
            # Auto-analyze when image is uploaded
            background_image.change(
                fn=self.analyze_image,
                inputs=[background_image],
                outputs=[analysis_output]
            )
        
        return app


def main():
    """Run the Gradio prototype"""
    print("🚀 Starting Pinmaker Gradio Prototype...")
    
    # Initialize the app
    pinmaker_app = PinmakerGradioApp()
    
    # Create the interface
    interface = pinmaker_app.create_interface()
    
    # Launch the app
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )


if __name__ == "__main__":
    main()