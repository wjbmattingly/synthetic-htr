#!/usr/bin/env python3
"""
Basic usage example for the Synthetic HTR package.

This script demonstrates how to use the text augmentor and manuscript generator
to create synthetic medieval manuscripts.
"""

from synthetic_htr import TextAugmentor, ManuscriptGenerator, ManuscriptVisualizer, OCRAnalyzer
from synthetic_htr.utils import TextValidator
from synthetic_htr.augmentor import ComplexAbbreviationRules


def main():
    """Main function demonstrating basic usage."""
    print("=== Synthetic HTR - Basic Usage Example ===\n")
    
    # Sample Latin text
    sample_text = """
    In nomine Domini nostri Iesu Christi. 
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
    
    print("Original text:")
    print(sample_text)
    print("-" * 50)
    
    # Initialize text augmentor
    print("Initializing text augmentor...")
    augmentor = TextAugmentor(
        ligature_probability=0.8,
        abbreviation_probability=0.7,
        medieval_style="carolingian"
    )
    
    # Augment the text with enhanced features
    print("Applying medieval text augmentation with complex abbreviations...")
    medieval_text = augmentor.augment_text(
        sample_text,
        add_ligatures=True,
        add_abbreviations=True,
        add_complex_abbreviations=True,
        add_decorations=True,
        context="religious"  # Specify context for better abbreviations
    )
    
    print("Medieval text:")
    print(medieval_text)
    print("-" * 50)
    
    # Validate the text
    print("Validating medieval text...")
    validator = TextValidator()
    is_valid, errors = validator.validate_text(medieval_text)
    
    if is_valid:
        print("✓ Text validation passed")
    else:
        print("✗ Text validation failed:")
        for error in errors:
            print(f"  - {error}")
    
    # Check compatibility
    compatibility = validator.check_medieval_compatibility(medieval_text)
    print(f"\nMedieval compatibility score: {compatibility['compatibility_score']:.2f}")
    print(f"Latin character ratio: {compatibility['latin_ratio']:.2f}")
    print(f"Medieval symbols found: {compatibility['medieval_symbols']}")
    
    if compatibility['suggestions']:
        print("\nSuggestions for improvement:")
        for suggestion in compatibility['suggestions']:
            print(f"  - {suggestion}")
    
    print("-" * 50)
    
    # Initialize manuscript generator
    print("Initializing manuscript generator...")
    generator = ManuscriptGenerator(
        page_size=(1200, 1600),
        font_family="medieval",
        texture="parchment",
        margin_size=100,
        line_spacing=1.8,
        font_size=28
    )
    
    # Generate manuscript image
    print("Generating manuscript image...")
    manuscript_image = generator.generate(
        text=medieval_text,
        add_illuminations=True,
        add_marginalia=True,
        add_decorative_borders=True,
        add_noise=True,
        add_aging=True
    )
    
    # Save the manuscript
    output_path = "example_manuscript.png"
    manuscript_image.save(output_path)
    print(f"Manuscript saved to: {output_path}")
    
    # Demonstrate visualization features
    print("Generating visualization with OCR analysis...")
    analyzer = OCRAnalyzer()
    visualizer = ManuscriptVisualizer()
    
    try:
        # Generate OCR data
        ocr_image, polygons, alto_xml = analyzer.generate_synthetic_ocr_data(
            text=medieval_text,
            width=1200,
            height=1600,
            font_size=28,
            num_columns=1,
            marginalia=True,
            curve_amount=0.2
        )
        
        # Save complete analysis with all visualizations
        saved_files = visualizer.save_complete_analysis(
            image=ocr_image,
            polygons=polygons,
            alto_xml=alto_xml,
            output_dir="example_output",
            base_name="example_manuscript",
            include_stats=True
        )
        
        # Save visualization without popup
        visualizer.visualize_manuscript_with_polygons(
            image=ocr_image,
            polygons=polygons,
            title="Example Manuscript with Text Detection",
            save_dir="example_output",
            save_prefix="basic_example",
            show_plot=False
        )
        
    except Exception as e:
        print(f"Visualization demo skipped (install matplotlib): {e}")
    
    # Display manuscript information
    print(f"\nManuscript details:")
    print(f"  - Page size: {manuscript_image.size}")
    print(f"  - Font family: {generator.font_family}")
    print(f"  - Texture: {generator.texture}")
    print(f"  - Margins: {generator.margin_size}px")
    
    # Show abbreviation statistics
    complex_rules = ComplexAbbreviationRules("carolingian")
    stats = complex_rules.get_abbreviation_statistics(sample_text, medieval_text)
    print(f"\nText transformation statistics:")
    print(f"  - Character reduction: {stats['reduction_percentage']:.1f}%")
    print(f"  - Suspension marks: {stats.get('suspension_marks', 0)}")
    print(f"  - Tironian notes: {stats.get('tironian_notes', 0)}")
    print(f"  - Chi-rho symbols: {stats.get('chi_rho_symbols', 0)}")
    
    print("\n=== Enhanced example completed successfully! ===")


if __name__ == "__main__":
    main()
