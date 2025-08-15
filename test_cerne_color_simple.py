#!/usr/bin/env python3
"""
Simple test of Cerne color font rendering using BlackRenderer SVG output.
"""

import os
import subprocess
import tempfile
from PIL import Image

def render_cerne_text_to_svg(text: str, font_size: int = 48) -> str:
    """
    Render text using Cerne font to SVG format.
    
    Args:
        text: Text to render
        font_size: Font size in pixels
        
    Returns:
        Path to generated SVG file, or None if failed
    """
    # Find Cerne font
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
    
    # Create output SVG file
    svg_path = f"cerne_render_{hash(text) % 10000}.svg"
    
    # Use BlackRenderer to create SVG
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
    
    if os.path.exists(svg_path):
        print(f"✅ Created SVG: {svg_path}")
        return svg_path
    else:
        print("❌ SVG file not created")
        return None

def test_cerne_color_rendering():
    """Test Cerne color font rendering with various texts."""
    print("🎨 Testing Cerne Color Font Rendering")
    print("=" * 50)
    
    test_texts = [
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "In principio erat Verbum",
        "Sanctus Sanctus Sanctus",
        "The quick brown fox jumps",
        "Medieval manuscript text with ligatures"
    ]
    
    for i, text in enumerate(test_texts):
        print(f"\n📝 Rendering: {text}")
        svg_path = render_cerne_text_to_svg(text, font_size=36)
        
        if svg_path:
            print(f"✅ Success! Check {svg_path} for color results")
            
            # Read a bit of the SVG to show colors
            with open(svg_path, 'r') as f:
                content = f.read()
                # Extract fill colors
                import re
                colors = re.findall(r'fill="(#[0-9A-Fa-f]{6})"', content)
                unique_colors = list(set(colors))
                if unique_colors:
                    print(f"🎨 Colors found: {', '.join(unique_colors[:5])}")
                else:
                    print("🎨 No explicit colors found (may be using default)")
        else:
            print(f"❌ Failed to render: {text}")
    
    print("\n🎉 Test completed! Check the generated SVG files.")
    print("💡 Tip: Open the SVG files in a web browser to see the full color effects.")

if __name__ == "__main__":
    test_cerne_color_rendering()
