#!/usr/bin/env python3
"""
Demo script showcasing the advanced typography features inspired by the Cerne font project.

This script demonstrates:
1. Contextual alternates and sophisticated ligatures
2. Automatic letterform variations
3. Color font rendering with multiple layers
4. Natural handwriting simulation
5. Medieval color schemes
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.abspath('.'))

try:
    from synthetic_htr.augmentor import TextAugmentor
    from synthetic_htr.visualization import OCRAnalyzer
    from synthetic_htr.typography import (
        AdvancedFontManager, 
        ContextualAlternatesEngine, 
        ColorFontRenderer, 
        LetterformVariationEngine
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure the synthetic_htr package is properly installed.")
    sys.exit(1)


def demo_contextual_alternates():
    """Demonstrate contextual alternates and sophisticated ligatures."""
    print("\n🔗 Contextual Alternates Demo")
    print("=" * 50)
    
    engine = ContextualAlternatesEngine("carolingian")
    
    sample_text = "litteris sanctus dominus christus beatus"
    print(f"Original text: {sample_text}")
    
    # Generate multiple variations
    variations = engine.create_variation_sample(sample_text, 5)
    
    for i, variation in enumerate(variations, 1):
        print(f"Variation {i}: {variation}")
    
    # Show analysis
    analysis = engine.analyze_text_features(sample_text)
    print(f"\nText analysis: {analysis}")


def demo_letterform_variations():
    """Demonstrate letterform variations for natural handwriting."""
    print("\n✍️  Letterform Variations Demo")
    print("=" * 50)
    
    engine = LetterformVariationEngine("carolingian", variation_strength=0.7)
    
    sample_text = "In principio erat Verbum"
    print(f"Original text: {sample_text}")
    
    # Different writing contexts
    contexts = [
        ("careful", "formal", "fresh"),
        ("normal", "formal", "fresh"),
        ("hasty", "informal", "tired"),
        ("normal", "formal", "exhausted")
    ]
    
    for writing_speed, formality, fatigue in contexts:
        varied = engine.apply_letterform_variations(
            sample_text,
            writing_speed=writing_speed,
            formality=formality,
            fatigue_level=fatigue
        )
        print(f"{writing_speed:8} + {formality:8} + {fatigue:9}: {varied}")


def demo_color_schemes():
    """Demonstrate different medieval color schemes."""
    print("\n🎨 Color Schemes Demo")
    print("=" * 50)
    
    renderer = ColorFontRenderer()
    
    schemes = renderer.get_available_color_schemes()
    print(f"Available color schemes: {', '.join(schemes)}")
    
    for scheme in schemes:
        colors = renderer.get_color_palette(scheme)
        print(f"\n{scheme.upper()} palette:")
        for color_name, rgb in colors.items():
            print(f"  {color_name:12}: RGB{rgb}")


def demo_advanced_text_augmentation():
    """Demonstrate advanced text augmentation with all features."""
    print("\n✨ Advanced Text Augmentation Demo")
    print("=" * 50)
    
    augmentor = TextAugmentor(
        medieval_style="carolingian",
        use_advanced_typography=True,
        variation_strength=0.6
    )
    
    sample_texts = [
        "Sanctus Sanctus Sanctus Dominus Deus Sabaoth",
        "In nomine Patris et Filii et Spiritus Sancti",
        "Gloria in excelsis Deo et in terra pax hominibus",
        "The quick brown fox jumps over the lazy dog"
    ]
    
    for text in sample_texts:
        print(f"\nOriginal: {text}")
        
        # Basic augmentation
        basic = augmentor.augment_text(
            text,
            use_contextual_alternates=False,
            use_letterform_variations=False
        )
        print(f"Basic:    {basic}")
        
        # Advanced augmentation
        advanced = augmentor.augment_text(
            text,
            use_contextual_alternates=True,
            use_letterform_variations=True,
            writing_speed="normal",
            formality="formal"
        )
        print(f"Advanced: {advanced}")


def demo_typography_analysis():
    """Demonstrate typography analysis features."""
    print("\n📊 Typography Analysis Demo")
    print("=" * 50)
    
    augmentor = TextAugmentor(
        medieval_style="carolingian",
        use_advanced_typography=True
    )
    
    sample_text = "Dominus vobiscum et cum spiritu tuo amen"
    
    analysis = augmentor.get_typography_analysis(sample_text)
    
    print(f"Text: {sample_text}")
    print(f"Analysis:")
    
    for category, data in analysis.items():
        print(f"\n{category.upper()}:")
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {data}")


def demo_manuscript_generation():
    """Demonstrate manuscript generation with advanced typography."""
    print("\n📜 Manuscript Generation Demo")
    print("=" * 50)
    
    analyzer = OCRAnalyzer(use_advanced_typography=True)
    
    sample_text = """Incipit Evangelium secundum Iohannem.
    
In principio erat Verbum et Verbum erat apud Deum et Deus erat Verbum. Hoc erat in principio apud Deum. Omnia per ipsum facta sunt et sine ipso factum est nihil quod factum est."""
    
    print("Generating manuscript with advanced typography...")
    
    try:
        image, polygons, alto_xml = analyzer.generate_synthetic_ocr_data(
            text=sample_text,
            width=800,
            height=600,
            font_size=24,
            medieval_font="cerne",
            color_scheme="cerne",
            use_color_layers=True,
            use_letterform_variations=True,
            writing_speed="normal",
            formality="formal",
            illumination_level="ornate"
        )
        
        # Save the generated manuscript
        output_path = "demo_advanced_manuscript.png"
        image.save(output_path)
        print(f"✅ Manuscript saved to: {output_path}")
        print(f"   Text regions detected: {len(polygons)}")
        print(f"   Image size: {image.size}")
        
    except Exception as e:
        print(f"❌ Error generating manuscript: {e}")
        print("This might be due to missing font files or dependencies.")


def main():
    """Run all typography demos."""
    print("🏰 Advanced Medieval Typography Demo")
    print("Inspired by the Cerne Font Project")
    print("=" * 60)
    
    # Check if advanced typography is available
    try:
        augmentor = TextAugmentor(use_advanced_typography=True)
        if not augmentor.is_advanced_typography_available():
            print("⚠️  Advanced typography features are not available.")
            print("Some demos may not work as expected.")
        else:
            print("✅ Advanced typography features are available!")
    except Exception as e:
        print(f"❌ Error checking typography availability: {e}")
        return 1
    
    try:
        # Run all demos
        demo_contextual_alternates()
        demo_letterform_variations()
        demo_color_schemes()
        demo_advanced_text_augmentation()
        demo_typography_analysis()
        demo_manuscript_generation()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print("\nTo use these features in your workflow:")
        print("1. Use TextAugmentor with use_advanced_typography=True")
        print("2. Use OCRAnalyzer with use_advanced_typography=True")
        print("3. Specify medieval_font, color_scheme, and other parameters")
        print("4. Run medieval-letters.py with advanced typography enabled")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
