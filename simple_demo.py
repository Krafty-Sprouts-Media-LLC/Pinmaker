#!/usr/bin/env python3
"""
Simple Demo of Pinmaker with Python-only Interface

This demonstrates how Pinmaker could work with a simple Python interface
without requiring React/Node.js build processes.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
from typing import Optional, List, Dict, Any

# Import your existing backend modules
try:
    from src.image_analyzer import ImageAnalyzer
    from src.template_generator import TemplateGenerator
    from src.preview_generator import PreviewGenerator
    from src.stock_photo_service import StockPhotoService
    from src.font_manager import FontManager
except ImportError as e:
    print(f"Note: Some modules not available: {e}")
    print("This is just a demonstration of the concept.")


class SimplePinmakerDemo:
    def __init__(self):
        """Initialize the demo with mock services if real ones aren't available"""
        self.setup_directories()
        
        # Try to initialize real services, fall back to mocks
        try:
            self.image_analyzer = ImageAnalyzer()
            self.stock_service = StockPhotoService()
            self.font_manager = FontManager()
            self.template_generator = TemplateGenerator()
            self.preview_generator = PreviewGenerator(self.stock_service)
            self.real_services = True
            print("✅ Real backend services initialized")
        except Exception as e:
            print(f"⚠️  Using mock services: {e}")
            self.real_services = False
            self.setup_mock_services()
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['demo_uploads', 'demo_outputs', 'demo_templates']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def setup_mock_services(self):
        """Setup mock services for demonstration"""
        self.available_fonts = ['Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Verdana']
        self.available_templates = ['Modern Card', 'Vintage Style', 'Bold Typography', 'Minimalist']
    
    def analyze_image_mock(self, image_path: str) -> Dict[str, Any]:
        """Mock image analysis"""
        return {
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
            'style': 'Modern',
            'mood': 'Energetic',
            'composition': 'Centered',
            'text_areas': 2,
            'dominant_color': '#FF6B6B',
            'contrast': 'High',
            'brightness': 'Medium'
        }
    
    def create_sample_pin(self, text: str, font: str, template: str, 
                         colors: List[str] = None) -> Image.Image:
        """Create a sample pin image"""
        # Create a 800x600 pin image
        width, height = 800, 600
        
        # Use provided colors or defaults
        if not colors:
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        # Create image with gradient background
        image = Image.new('RGB', (width, height), colors[0])
        draw = ImageDraw.Draw(image)
        
        # Create a simple gradient effect
        for i in range(height):
            alpha = i / height
            r1, g1, b1 = int(colors[0][1:3], 16), int(colors[0][3:5], 16), int(colors[0][5:7], 16)
            r2, g2, b2 = int(colors[1][1:3], 16), int(colors[1][3:5], 16), int(colors[1][5:7], 16)
            
            r = int(r1 * (1 - alpha) + r2 * alpha)
            g = int(g1 * (1 - alpha) + g2 * alpha)
            b = int(b1 * (1 - alpha) + b2 * alpha)
            
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Add text
        try:
            # Try to use a system font
            font_size = 48
            try:
                if os.name == 'nt':  # Windows
                    font_path = f"C:/Windows/Fonts/{font.lower().replace(' ', '')}.ttf"
                    if not os.path.exists(font_path):
                        font_path = "C:/Windows/Fonts/arial.ttf"
                else:  # Linux/Mac
                    font_path = f"/usr/share/fonts/truetype/dejavu/DejaVu{font.replace(' ', '')}.ttf"
                    if not os.path.exists(font_path):
                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                
                pil_font = ImageFont.truetype(font_path, font_size)
            except:
                pil_font = ImageFont.load_default()
            
            # Add text with outline for better visibility
            text_lines = text.split('\n') if text else ['Sample Pin Text']
            y_offset = height // 2 - (len(text_lines) * font_size) // 2
            
            for line in text_lines:
                # Get text size
                bbox = draw.textbbox((0, 0), line, font=pil_font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                
                # Draw text outline
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y_offset + dy), line, font=pil_font, fill='black')
                
                # Draw main text
                draw.text((x, y_offset), line, font=pil_font, fill='white')
                y_offset += font_size + 10
            
            # Add template style indicator
            style_text = f"Template: {template}"
            bbox = draw.textbbox((0, 0), style_text, font=pil_font)
            style_width = bbox[2] - bbox[0]
            draw.text((width - style_width - 20, height - 40), style_text, 
                     font=pil_font, fill='white')
            
        except Exception as e:
            print(f"Error adding text: {e}")
        
        return image
    
    def run_demo(self):
        """Run the interactive demo"""
        print("\n" + "="*60)
        print("🎨 PINMAKER - PYTHON-ONLY DEMO")
        print("="*60)
        print("\nThis demonstrates how Pinmaker could work with pure Python.")
        print("No React, no Node.js, no build processes - just Python!\n")
        
        while True:
            print("\n📋 MENU:")
            print("1. 🖼️  Analyze Image")
            print("2. ✨ Generate Pin")
            print("3. 📊 Show Available Resources")
            print("4. 🔍 Mock Stock Photo Search")
            print("5. 🎨 Create Sample Pin Collection")
            print("6. ❌ Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                self.demo_image_analysis()
            elif choice == '2':
                self.demo_pin_generation()
            elif choice == '3':
                self.show_resources()
            elif choice == '4':
                self.demo_stock_search()
            elif choice == '5':
                self.create_sample_collection()
            elif choice == '6':
                print("\n👋 Thanks for trying the Pinmaker demo!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def demo_image_analysis(self):
        """Demo image analysis functionality"""
        print("\n🔍 IMAGE ANALYSIS DEMO")
        print("-" * 30)
        
        if self.real_services:
            image_path = input("Enter image path (or press Enter for mock): ").strip()
            if image_path and os.path.exists(image_path):
                try:
                    # Use real image analyzer
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    analysis = loop.run_until_complete(
                        self.image_analyzer.analyze_image(image_path)
                    )
                    loop.close()
                except Exception as e:
                    print(f"❌ Analysis failed: {e}")
                    analysis = self.analyze_image_mock(image_path)
            else:
                analysis = self.analyze_image_mock("mock_image.jpg")
        else:
            analysis = self.analyze_image_mock("mock_image.jpg")
        
        print("\n📊 ANALYSIS RESULTS:")
        for key, value in analysis.items():
            print(f"  {key.title()}: {value}")
    
    def demo_pin_generation(self):
        """Demo pin generation"""
        print("\n✨ PIN GENERATION DEMO")
        print("-" * 30)
        
        # Get user input
        text = input("Enter pin text (or press Enter for sample): ").strip()
        if not text:
            text = "Amazing\nContent\nHere!"
        
        print("\nAvailable fonts:", ', '.join(self.available_fonts[:5]))
        font = input("Choose font (or press Enter for Arial): ").strip()
        if not font:
            font = "Arial"
        
        print("\nAvailable templates:", ', '.join(self.available_templates))
        template = input("Choose template (or press Enter for Modern Card): ").strip()
        if not template:
            template = "Modern Card"
        
        # Generate pin
        print("\n🎨 Generating pin...")
        pin_image = self.create_sample_pin(text, font, template)
        
        # Save the pin
        output_path = f"demo_outputs/pin_{int(asyncio.get_event_loop().time())}.jpg"
        pin_image.save(output_path, 'JPEG', quality=90)
        
        print(f"✅ Pin generated and saved to: {output_path}")
        print(f"📏 Dimensions: {pin_image.size[0]}x{pin_image.size[1]}")
    
    def show_resources(self):
        """Show available resources"""
        print("\n📊 AVAILABLE RESOURCES")
        print("-" * 30)
        
        if self.real_services:
            try:
                fonts = self.font_manager.list_fonts()
                print(f"📝 Fonts: {len(fonts.get('fonts', []))} available")
                for font in fonts.get('fonts', [])[:5]:
                    print(f"  - {font.get('family', 'Unknown')}")
                if len(fonts.get('fonts', [])) > 5:
                    print(f"  ... and {len(fonts.get('fonts', [])) - 5} more")
            except Exception as e:
                print(f"❌ Error loading fonts: {e}")
        else:
            print(f"📝 Mock Fonts: {len(self.available_fonts)} available")
            for font in self.available_fonts:
                print(f"  - {font}")
        
        print(f"\n🎨 Templates: {len(self.available_templates)} available")
        for template in self.available_templates:
            print(f"  - {template}")
    
    def demo_stock_search(self):
        """Demo stock photo search"""
        print("\n🔍 STOCK PHOTO SEARCH DEMO")
        print("-" * 30)
        
        query = input("Enter search query (e.g., 'nature', 'business'): ").strip()
        if not query:
            query = "nature"
        
        print(f"\n🔍 Searching for '{query}'...")
        
        # Mock search results
        results = [
            {"title": f"Beautiful {query} photo 1", "url": f"https://picsum.photos/400/300?random=1"},
            {"title": f"Stunning {query} image 2", "url": f"https://picsum.photos/400/300?random=2"},
            {"title": f"Amazing {query} picture 3", "url": f"https://picsum.photos/400/300?random=3"},
        ]
        
        print(f"✅ Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']}")
            print(f"     URL: {result['url']}")
    
    def create_sample_collection(self):
        """Create a collection of sample pins"""
        print("\n🎨 CREATING SAMPLE PIN COLLECTION")
        print("-" * 40)
        
        samples = [
            {"text": "Motivational\nQuote\nDaily", "template": "Bold Typography", "colors": ['#FF6B6B', '#4ECDC4']},
            {"text": "Recipe\nOf The\nDay", "template": "Modern Card", "colors": ['#45B7D1', '#96CEB4']},
            {"text": "Travel\nTips &\nTricks", "template": "Vintage Style", "colors": ['#FFEAA7', '#DDA0DD']},
            {"text": "Business\nSuccess\nSecrets", "template": "Minimalist", "colors": ['#2C3E50', '#3498DB']},
        ]
        
        for i, sample in enumerate(samples, 1):
            print(f"\n📌 Creating pin {i}/4: {sample['template']}")
            
            pin_image = self.create_sample_pin(
                sample['text'], 
                'Arial', 
                sample['template'], 
                sample['colors']
            )
            
            output_path = f"demo_outputs/sample_pin_{i}_{sample['template'].lower().replace(' ', '_')}.jpg"
            pin_image.save(output_path, 'JPEG', quality=90)
            
            print(f"   ✅ Saved: {output_path}")
        
        print(f"\n🎉 Collection complete! Check the 'demo_outputs' folder.")


def main():
    """Run the demo"""
    demo = SimplePinmakerDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()