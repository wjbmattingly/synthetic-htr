#!/usr/bin/env python3
"""
Test script to verify Cerne font is working properly.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

def test_cerne_font():
    """Test if Cerne font can be loaded and used."""
    print("🧪 Testing Cerne Font")
    print("=" * 30)
    
    # Possible Cerne font locations
    cerne_paths = [
        "/Users/wjm55/yale/Cerne-font/fonts/Cerne.otf",
        "/Users/wjm55/yale/synthetic-htr/synthetic_htr/fonts/Cerne.otf",
        "synthetic_htr/fonts/Cerne.otf"
    ]
    
    cerne_font = None
    cerne_path_used = None
    
    # Try to load Cerne font
    for path in cerne_paths:
        if os.path.exists(path):
            try:
                cerne_font = ImageFont.truetype(path, 36)
                cerne_path_used = path
                print(f"✅ Successfully loaded Cerne font from: {path}")
                break
            except Exception as e:
                print(f"❌ Failed to load Cerne font from {path}: {e}")
    
    if cerne_font is None:
        print("❌ Could not load Cerne font from any location")
        return False
    
    # Test rendering
    print("\n📝 Testing text rendering...")
    
    # Create test image
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Test texts
    test_texts = [
        "The quick brown fox jumps over the lazy dog",
        "In principio erat Verbum et Verbum erat apud Deum",
        "Sanctus Sanctus Sanctus Dominus Deus Sabaoth"
    ]
    
    # Cerne-inspired brown color
    cerne_brown = (101, 67, 33)
    
    y_pos = 50
    for i, text in enumerate(test_texts):
        print(f"Rendering: {text[:30]}...")
        
        try:
            draw.text((50, y_pos), text, font=cerne_font, fill=cerne_brown)
            y_pos += 80
            print(f"✅ Successfully rendered text {i+1}")
        except Exception as e:
            print(f"❌ Failed to render text {i+1}: {e}")
            return False
    
    # Save test image
    output_path = "cerne_font_test.png"
    img.save(output_path)
    print(f"\n✅ Test image saved to: {output_path}")
    print(f"Font used: {cerne_path_used}")
    
    return True

def test_basic_generation():
    """Test basic manuscript generation with Cerne font."""
    print("\n📜 Testing Basic Manuscript Generation")
    print("=" * 40)
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.abspath('.'))
        
        from synthetic_htr.visualization import OCRAnalyzer
        
        analyzer = OCRAnalyzer(use_advanced_typography=False)  # Use simple mode
        
        sample_text = "In principio erat Verbum et Verbum erat apud Deum et Deus erat Verbum"
        
        print("Generating manuscript page...")
        
        image, polygons, alto_xml = analyzer.generate_synthetic_ocr_data(
            text=sample_text,
            width=600,
            height=400,
            font_size=24,
            medieval_font="cerne",
            use_color_layers=False,
            add_noise=False
        )
        
        # Save the result
        output_path = "cerne_manuscript_test.png"
        image.save(output_path)
        
        print(f"✅ Manuscript generated successfully!")
        print(f"   Output: {output_path}")
        print(f"   Text regions: {len(polygons)}")
        print(f"   Image size: {image.size}")
        
        return True
        
    except Exception as e:
        print(f"❌ Manuscript generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🏰 Cerne Font Integration Test")
    print("=" * 50)
    
    success = True
    
    # Test 1: Font loading
    if not test_cerne_font():
        success = False
    
    # Test 2: Basic manuscript generation
    if not test_basic_generation():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Cerne font integration is working.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
