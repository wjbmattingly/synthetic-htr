#!/usr/bin/env python3
"""
Demo script for the Synthetic HTR package.

This script demonstrates the key features of the package:
1. Text augmentation with medieval ligatures and abbreviations
2. Manuscript image generation with authentic appearance
3. Various medieval styles and customization options
"""

from synthetic_htr import TextAugmentor, ManuscriptGenerator
from synthetic_htr.utils import TextValidator


def demo_text_augmentation():
    """Demonstrate text augmentation features."""
    print("=== Text Augmentation Demo ===\n")
    
    # Sample texts in different languages/styles
    texts = [
        "In nomine Domini nostri Iesu Christi. Amen.",
    ]
    
    # Initialize augmentor with different styles
    styles = ["carolingian", "gothic", "uncial"]
    
    for style in styles:
        print(f"\n--- {style.upper()} Style ---")
        augmentor = TextAugmentor(
            ligature_probability=0.8,
            abbreviation_probability=0.7,
            medieval_style=style
        )
        
        for i, text in enumerate(texts):
            print(f"\nOriginal {i+1}: {text}")
            augmented = augmentor.augment_text(
                text,
                add_ligatures=True,
                add_abbreviations=True,
                add_decorations=True
            )
            print(f"Medieval {i+1}: {augmented}")


def demo_manuscript_generation():
    """Demonstrate manuscript generation features."""
    print("\n\n=== Manuscript Generation Demo ===\n")
    
    # Sample medieval text
    medieval_text = """
    ❦In nomine Domini nostri Iesu Christi. 
    Incipit liber de arte scribendi manuscripta.
    
    Hic liber docet quomodo scribendi sint manuscripta 
    secundum artem antiquam et traditionem monasticam.
    
    Primum, eligenda est charta vel pergamena bona.
    Secundum, penna vel calamus aptus ad scribendum.
    Tertium, atramentum nigrum et durum.
    
    Deinde, scribendum est littera littera, 
    cum diligentia et reverentia.
    
    Amen.
    """
    
    print("Sample medieval text:")
    print(medieval_text)
    print("-" * 60)
    
    # Generate manuscripts with different styles
    styles = [
        ("carolingian", "medieval", "parchment"),
        ("gothic", "gothic", "paper"),
        ("uncial", "uncial", "vellum")
    ]
    
    for style_name, font_family, texture in styles:
        print(f"\nGenerating {style_name} manuscript...")
        
        generator = ManuscriptGenerator(
            page_size=(1000, 1400),
            font_family=font_family,
            texture=texture,
            margin_size=80,
            line_spacing=1.6,
            font_size=24
        )
        
        manuscript = generator.generate(
            text=medieval_text,
            add_illuminations=True,
            add_marginalia=True,
            add_decorative_borders=True,
            add_noise=True,
            add_aging=True
        )
        
        # Save manuscript
        output_path = f"demo_manuscript_{style_name}.png"
        manuscript.save(output_path)
        print(f"  Saved to: {output_path}")
        print(f"  Size: {manuscript.size}")
        print(f"  Font: {font_family}")
        print(f"  Texture: {texture}")


def demo_validation():
    """Demonstrate text validation features."""
    print("\n\n=== Text Validation Demo ===\n")
    
    # Sample texts for validation
    test_texts = [
        "Perfect Latin text: In nomine Domini nostri Iesu Christi.",
        "Mixed text with emojis: Hello world! 🚀 🌍",
        "Empty text: ",
        "Very long text: " + "Lorem ipsum " * 1000,
        "Text with medieval symbols: d̄s & x̄s æ œ"
    ]
    
    validator = TextValidator()
    
    for i, text in enumerate(test_texts):
        print(f"\n--- Test {i+1} ---")
        print(f"Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # Validate text
        is_valid, errors = validator.validate_text(text)
        if is_valid:
            print("✓ Validation: PASSED")
        else:
            print("✗ Validation: FAILED")
            for error in errors:
                print(f"  - {error}")
        
        # Check compatibility
        compatibility = validator.check_medieval_compatibility(text)
        print(f"  Compatibility score: {compatibility['compatibility_score']:.2f}")
        print(f"  Latin ratio: {compatibility['latin_ratio']:.2f}")
        
        # Get suggestions
        suggestions = validator.suggest_medieval_improvements(text)
        if suggestions:
            print("  Suggestions:")
            for suggestion in suggestions[:3]:  # Show first 3 suggestions
                print(f"    - {suggestion}")


def main():
    """Main demo function."""
    print("Synthetic HTR - Medieval Manuscript Generator")
    print("=" * 50)
    print("This demo showcases the key features of the package.\n")
    
    try:
        # Run demos
        demo_text_augmentation()
        demo_manuscript_generation()
        demo_validation()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("Check the generated manuscript images in the current directory.")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Make sure all dependencies are installed and fonts are available.")


if __name__ == "__main__":
    main()
