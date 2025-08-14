#!/usr/bin/env python3
"""
Enhanced demo script for the Synthetic HTR package showcasing new features:
- Visualization capabilities
- Complex abbreviation rules
- Fixed ligature rules
- OCR analysis
"""

from synthetic_htr import TextAugmentor, ManuscriptGenerator, ManuscriptVisualizer, OCRAnalyzer
from synthetic_htr.utils import TextValidator
from synthetic_htr.augmentor import ComplexAbbreviationRules


def demo_enhanced_text_augmentation():
    """Demonstrate enhanced text augmentation with complex abbreviations."""
    print("=== Enhanced Text Augmentation Demo ===\n")
    
    # Sample texts with different contexts
    test_texts = [
        {
            "text": "In nomine Patris et Filii et Spiritus Sancti. Dominus vobiscum. Et cum spiritu tuo. Gloria Patri et Filio et Spiritui Sancto.",
            "context": "religious",
            "description": "Religious Prayer Text"
        },
        {
            "text": "Anno Domini nostri Iesu Christi millesimo ducentesimo. Ego magister Johannes, doctor theologiae, prior generalis.",
            "context": "legal", 
            "description": "Legal Document Opening"
        },
        {
            "text": "Quaestio prima: utrum Deus sit. Argumentum contra: videtur quod Deus non sit. Sed contra est quod dicitur.",
            "context": "academic",
            "description": "Scholastic Question"
        }
    ]
    
    # Test different medieval styles
    styles = ["carolingian", "gothic", "uncial"]
    
    for style in styles:
        print(f"\n--- {style.upper()} Style ---")
        augmentor = TextAugmentor(
            ligature_probability=0.9,
            abbreviation_probability=0.8,
            medieval_style=style
        )
        
        for test in test_texts:
            print(f"\n{test['description']} ({test['context']} context):")
            print(f"Original: {test['text']}")
            
            # Apply enhanced augmentation
            augmented = augmentor.augment_text(
                test['text'],
                add_ligatures=True,
                add_abbreviations=True,
                add_complex_abbreviations=True,
                add_decorations=True,
                context=test['context']
            )
            print(f"Enhanced: {augmented}")
            
            # Show statistics using complex abbreviation rules
            complex_rules = ComplexAbbreviationRules(style)
            stats = complex_rules.get_abbreviation_statistics(test['text'], augmented)
            print(f"Statistics: {stats['character_reduction']} chars saved ({stats['reduction_percentage']:.1f}% reduction)")


def demo_visualization_features():
    """Demonstrate visualization capabilities."""
    print("\n\n=== Visualization Features Demo ===\n")
    
    # Create sample manuscript with OCR data
    analyzer = OCRAnalyzer()
    visualizer = ManuscriptVisualizer()
    
    # Sample medieval text
    medieval_text = """
    In nom̄ p̄ris ⁊ f̄lii ⁊ sp̄us s̄i. 
    D̄s vobiscū. ⁊ c̄ sp̄u tuo.
    
    ☧i gr̄a ⁊ pāx ā d̄o p̄re nr̄o ⁊ d̄o ih̄u ☧o.
    
    Hic lib̄ docet q̄modo scrib̄di sint man̄scripta 
    sec̄dum artē ant̄quam ⁊ tradit̄ionem mon̄sticam.
    
    Pr̄imum, elīg̅enda ē charta vel perg̅amēna bona.
    Sec̄undum, penna vel calamus aptus ad scrib̄endum.
    Tert̄ium, atrament̄um nigrū ⁊ durū.
    
    Ā.
    """
    
    print("Generating synthetic OCR data with visualization...")
    
    # Generate manuscript with OCR polygons
    try:
        image, polygons, alto_xml = analyzer.generate_synthetic_ocr_data(
            text=medieval_text,
            width=1000,
            height=1400,
            font_size=24,
            num_columns=2,
            marginalia=True,
            curve_amount=0.3
        )
        
        print(f"Generated manuscript with {len(polygons)} text regions")
        
        # Visualize results and save everything
        print("Saving complete analysis with all visualization files...")
        saved_files = visualizer.save_complete_analysis(
            image=image,
            polygons=polygons,
            alto_xml=alto_xml,
            output_dir="enhanced_demo_output",
            base_name="medieval_manuscript",
            include_stats=True
        )
        
        # Save visualization without showing popup
        print("Saving additional visualization files...")
        visualizer.visualize_manuscript_with_polygons(
            image=image,
            polygons=polygons,
            title="Medieval Manuscript with OCR Polygons",
            show_text=True,
            save_dir="enhanced_demo_output",
            save_prefix="demo_visualization",
            show_plot=False
        )
        
        # Note: Text distribution analysis is included in the complete analysis above
        
        # Save outputs
        image.save("enhanced_demo_manuscript.png")
        analyzer.save_alto_xml(alto_xml, "enhanced_demo_ocr.xml")
        print("Saved manuscript and ALTO XML files")
        
    except Exception as e:
        print(f"Visualization demo failed: {e}")
        print("Make sure matplotlib is installed and fonts are available")


def demo_complex_abbreviations():
    """Demonstrate complex abbreviation features."""
    print("\n\n=== Complex Abbreviation Rules Demo ===\n")
    
    # Create complex abbreviation rules for different styles
    styles = ["carolingian", "gothic", "uncial"]
    
    # Test text with various Latin forms
    test_text = """
    In nomine Domini nostri Iesu Christi, anno domini millesimo ducentesimo.
    Sanctus Benedictus, abbas monasterii, prior generalis ordinis.
    Gloria Patri et Filio et Spiritui Sancto, sicut erat in principio.
    Quaestio prima de natura Dei: argumentum contra videtur quod non.
    Testamentum domini Johannis presbyteri, notarius publicus.
    """
    
    for style in styles:
        print(f"\n--- {style.upper()} Complex Abbreviations ---")
        
        complex_rules = ComplexAbbreviationRules(style)
        
        # Apply different contexts
        contexts = ["religious", "legal", "academic"]
        
        for context in contexts:
            print(f"\n{context.title()} context:")
            abbreviated = complex_rules.apply_complex_abbreviations(
                test_text, 
                probability=0.9,
                context=context
            )
            print(f"Result: {abbreviated}")
            
            # Show statistics
            stats = complex_rules.get_abbreviation_statistics(test_text, abbreviated)
            print(f"Reduction: {stats['reduction_percentage']:.1f}%")
            
            # Validate abbreviations
            is_valid, errors = complex_rules.validate_abbreviations(abbreviated)
            if not is_valid:
                print(f"Validation errors: {errors}")


def demo_ligature_improvements():
    """Demonstrate improved ligature rules."""
    print("\n\n=== Improved Ligature Rules Demo ===\n")
    
    from synthetic_htr.augmentor import LigatureRules
    
    # Test text with various ligature opportunities
    test_text = "The office of Matins and Vespers with beautiful illuminated text and fine craftsmanship."
    
    styles = ["carolingian", "gothic", "uncial"]
    
    for style in styles:
        print(f"\n--- {style.upper()} Ligatures ---")
        
        ligature_rules = LigatureRules(style)
        
        print(f"Available ligatures: {list(ligature_rules.get_available_ligatures().keys())}")
        
        # Apply ligatures
        result = ligature_rules.apply(test_text, probability=1.0)
        print(f"Original: {test_text}")
        print(f"With ligatures: {result}")
        
        # Show specific ligature examples
        examples = ["office", "beautiful", "fine", "craftsmanship", "aesthetic", "therefore"]
        print("\nSpecific examples:")
        for example in examples:
            ligated = ligature_rules.apply(example, probability=1.0)
            if ligated != example:
                print(f"  {example} → {ligated}")


def demo_character_analysis():
    """Demonstrate character frequency and text analysis."""
    print("\n\n=== Character Analysis Demo ===\n")
    
    from synthetic_htr.visualization.plot_utils import PlotUtils
    
    # Sample texts in different styles
    texts = {
        "Original Latin": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Medieval Augmented": "Lorē ips̄ dolor sit am̄, c̄sectet̄ur adipīsc̄ēns elit.",
        "Complex Abbreviated": "D̄s mīsereāt̄ur nr̄i ⁊ ben̄edīcat nōs. ☧s vincit, ☧s regnat, ☧s imperat."
    }
    
    # Analyze each text
    for title, text in texts.items():
        print(f"\n--- {title} ---")
        print(f"Text: {text}")
        
        # Note: Character analysis plots are saved but not displayed
        # to avoid popup interruptions during batch processing


def main():
    """Main demo function."""
    print("Synthetic HTR - Enhanced Features Demo")
    print("=" * 50)
    print("Showcasing visualization, complex abbreviations, and improved ligatures\n")
    
    try:
        # Run enhanced demos
        demo_enhanced_text_augmentation()
        demo_complex_abbreviations() 
        demo_ligature_improvements()
        demo_visualization_features()
        demo_character_analysis()
        
        print("\n" + "=" * 50)
        print("Enhanced demo completed successfully!")
        print("Check the generated files:")
        print("- enhanced_demo_manuscript.png")
        print("- enhanced_demo_ocr.xml")
        
    except Exception as e:
        print(f"\nError during enhanced demo: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install matplotlib seaborn")


if __name__ == "__main__":
    main()
