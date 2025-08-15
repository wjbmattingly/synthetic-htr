"""
Cerne Color Font Renderer using BlackRenderer for proper COLR table support.

This module provides proper color font rendering for the Cerne font, which uses
OpenType COLR tables that PIL cannot handle natively.
"""

import os
import io
from typing import Tuple, Optional, List
from PIL import Image, ImageDraw
import numpy as np

try:
    from blackrenderer.font import BlackRendererFont
    from blackrenderer.backends import getSurfaceClass
    BLACKRENDERER_AVAILABLE = True
except ImportError:
    BLACKRENDERER_AVAILABLE = False
    print("BlackRenderer not available. Install with: pip install blackrenderer")


class CerneColorRenderer:
    """
    Renderer for Cerne color font using BlackRenderer.
    
    This class handles the proper rendering of the Cerne font's color features
    that are stored in COLR tables and cannot be rendered by PIL alone.
    """
    
    def __init__(self):
        """Initialize the Cerne color renderer."""
        self.blackrenderer_available = BLACKRENDERER_AVAILABLE
        self.cerne_font = None
        self.surface_class = None
        
        if self.blackrenderer_available:
            # Try available backends (based on listBackends output)
            for backend in ["cairo", "skia", "coregraphics", "svg"]:
                try:
                    self.surface_class = getSurfaceClass(backend)
                    if self.surface_class is not None:
                        print(f"Using BlackRenderer backend: {backend}")
                        break
                except (KeyError, ImportError) as e:
                    print(f"Backend {backend} not available: {e}")
                    continue
    
    def load_cerne_font(self, font_path: Optional[str] = None) -> bool:
        """
        Load the Cerne font for color rendering.
        
        Args:
            font_path: Path to Cerne font file
            
        Returns:
            True if font loaded successfully, False otherwise
        """
        if not self.blackrenderer_available:
            return False
        
        # Try to find Cerne font
        cerne_paths = [
            font_path,
            "/Users/wjm55/yale/Cerne-font/fonts/Cerne.otf",
            "/Users/wjm55/yale/synthetic-htr/synthetic_htr/fonts/Cerne.otf",
            "synthetic_htr/fonts/Cerne.otf"
        ]
        
        for path in cerne_paths:
            if path and os.path.exists(path):
                try:
                    self.cerne_font = BlackRendererFont(path)
                    print(f"✅ Loaded Cerne color font from: {path}")
                    return True
                except Exception as e:
                    print(f"Failed to load Cerne font from {path}: {e}")
                    continue
        
        print("❌ Could not load Cerne font for color rendering")
        return False
    
    def render_text_with_colors(
        self,
        text: str,
        font_size: int,
        width: int = None,
        height: int = None,
        x_offset: int = 0,
        y_offset: int = 0,
        background_color: Tuple[int, int, int] = (255, 255, 255)
    ) -> Optional[Image.Image]:
        """
        Render text with Cerne font colors using BlackRenderer SVG backend.
        
        Args:
            text: Text to render
            font_size: Font size in pixels
            width: Image width (optional, auto-calculated if None)
            height: Image height (optional, auto-calculated if None)
            x_offset: X offset for text positioning
            y_offset: Y offset for text positioning
            background_color: Background color (R, G, B)
            
        Returns:
            PIL Image with color font rendering, or None if failed
        """
        if not self.blackrenderer_available:
            return None
        
        try:
            import tempfile
            import subprocess
            
            # Find Cerne font path
            cerne_paths = [
                "/Users/wjm55/yale/Cerne-font/fonts/Cerne.otf",
                "/Users/wjm55/yale/synthetic-htr/synthetic_htr/fonts/Cerne.otf",
                "synthetic_htr/fonts/Cerne.otf"
            ]
            
            cerne_font_path = None
            for path in cerne_paths:
                if os.path.exists(path):
                    cerne_font_path = path
                    break
            
            if not cerne_font_path:
                print("❌ Could not find Cerne font")
                return None
            
            # Create temporary SVG file
            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_svg:
                svg_path = tmp_svg.name
            
            # Use BlackRenderer command line to create SVG
            cmd = [
                'blackrenderer',
                cerne_font_path,
                text,
                svg_path,
                '--font-size', str(font_size),
                '--backend', 'svg'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ BlackRenderer failed: {result.stderr}")
                return None
            
            # Convert SVG to PNG using PIL and cairosvg (if available) or other method
            if os.path.exists(svg_path):
                try:
                    # Try to use cairosvg if available
                    try:
                        import cairosvg
                        png_data = cairosvg.svg2png(url=svg_path)
                        image = Image.open(io.BytesIO(png_data))
                    except ImportError:
                        # Fallback: use subprocess to convert with system tools
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
                            png_path = tmp_png.name
                        
                        # Try using rsvg-convert (librsvg)
                        convert_cmd = ['rsvg-convert', '-o', png_path, svg_path]
                        convert_result = subprocess.run(convert_cmd, capture_output=True)
                        
                        if convert_result.returncode == 0:
                            image = Image.open(png_path)
                            os.unlink(png_path)
                        else:
                            print("❌ Could not convert SVG to PNG")
                            return None
                    
                    # Clean up SVG file
                    os.unlink(svg_path)
                    
                    # Convert to RGB if needed and apply background
                    if image.mode == 'RGBA':
                        rgb_image = Image.new('RGB', image.size, background_color)
                        rgb_image.paste(image, mask=image.split()[3])
                        return rgb_image
                    
                    return image
                    
                except Exception as e:
                    print(f"❌ Error converting SVG: {e}")
                    return None
            else:
                print("❌ BlackRenderer did not create SVG file")
                return None
            
        except Exception as e:
            print(f"❌ Error rendering color text: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def render_text_line(
        self,
        text: str,
        font_size: int,
        max_width: int = 800
    ) -> Optional[Image.Image]:
        """
        Render a single line of text with automatic sizing.
        
        Args:
            text: Text to render
            font_size: Font size
            max_width: Maximum width for the text
            
        Returns:
            PIL Image with the rendered text line
        """
        if not self.blackrenderer_available or not self.cerne_font:
            return None
        
        # Estimate dimensions (rough calculation)
        estimated_width = min(len(text) * font_size * 0.6, max_width)
        estimated_height = int(font_size * 1.5)
        
        return self.render_text_with_colors(
            text,
            font_size,
            int(estimated_width),
            estimated_height,
            x_offset=10,
            y_offset=10
        )
    
    def is_available(self) -> bool:
        """Check if color font rendering is available."""
        return self.blackrenderer_available and self.cerne_font is not None


def test_cerne_color_rendering():
    """Test function to verify Cerne color font rendering."""
    print("🎨 Testing Cerne Color Font Rendering")
    print("=" * 50)
    
    renderer = CerneColorRenderer()
    
    if not renderer.blackrenderer_available:
        print("❌ BlackRenderer not available")
        return False
    
    if not renderer.load_cerne_font():
        print("❌ Could not load Cerne font")
        return False
    
    # Test texts that should show color features
    test_texts = [
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # Capitals should show colors
        "In principio erat Verbum",
        "Sanctus Sanctus Sanctus",
        "The quick brown fox jumps"
    ]
    
    for i, text in enumerate(test_texts):
        print(f"Rendering: {text}")
        
        image = renderer.render_text_line(text, font_size=36)
        
        if image:
            output_path = f"cerne_color_test_{i+1}.png"
            image.save(output_path)
            print(f"✅ Saved: {output_path}")
        else:
            print(f"❌ Failed to render: {text}")
            return False
    
    print("🎉 Color font rendering test completed!")
    return True


if __name__ == "__main__":
    test_cerne_color_rendering()
