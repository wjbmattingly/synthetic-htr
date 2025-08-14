#!/usr/bin/env python3
"""
Command-line interface for the Synthetic HTR package.
"""

import argparse
import sys
import os
from pathlib import Path

from synthetic_htr import TextAugmentor, ManuscriptGenerator
from synthetic_htr.utils import TextValidator
from synthetic_htr.config import config


def create_manuscript(args):
    """Create a manuscript from text input."""
    print("Creating synthetic medieval manuscript...")
    
    # Initialize text augmentor
    augmentor = TextAugmentor(
        ligature_probability=args.ligature_prob,
        abbreviation_probability=args.abbreviation_prob,
        medieval_style=args.style
    )
    
    # Read input text
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.text
    
    if not text:
        print("Error: No text provided")
        return 1
    
    # Augment text
    print("Applying medieval text augmentation...")
    medieval_text = augmentor.augment_text(
        text,
        add_ligatures=args.ligatures,
        add_abbreviations=args.abbreviations,
        add_decorations=args.decorations
    )
    
    # Validate text
    validator = TextValidator()
    is_valid, errors = validator.validate_text(medieval_text)
    
    if not is_valid:
        print("Warning: Text validation failed:")
        for error in errors:
            print(f"  - {error}")
    
    # Initialize manuscript generator
    generator = ManuscriptGenerator(
        page_size=args.page_size,
        font_family=args.font,
        texture=args.texture,
        margin_size=args.margins,
        line_spacing=args.line_spacing,
        font_size=args.font_size
    )
    
    # Generate manuscript
    print("Generating manuscript image...")
    manuscript = generator.generate(
        text=medieval_text,
        add_illuminations=args.illuminations,
        add_marginalia=args.marginalia,
        add_decorative_borders=args.borders,
        add_noise=args.noise,
        add_aging=args.aging
    )
    
    # Save manuscript
    output_path = args.output or "manuscript.png"
    manuscript.save(output_path)
    print(f"Manuscript saved to: {output_path}")
    
    return 0


def augment_text(args):
    """Augment text to medieval style."""
    print("Applying medieval text augmentation...")
    
    # Initialize text augmentor
    augmentor = TextAugmentor(
        ligature_probability=args.ligature_prob,
        abbreviation_probability=args.abbreviation_prob,
        medieval_style=args.style
    )
    
    # Read input text
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.text
    
    if not text:
        print("Error: No text provided")
        return 1
    
    # Augment text
    medieval_text = augmentor.augment_text(
        text,
        add_ligatures=args.ligatures,
        add_abbreviations=args.abbreviations,
        add_decorations=args.decorations
    )
    
    # Output result
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(medieval_text)
        print(f"Augmented text saved to: {args.output_file}")
    else:
        print("\nAugmented text:")
        print("-" * 50)
        print(medieval_text)
        print("-" * 50)
    
    return 0


def validate_text(args):
    """Validate text for medieval manuscript generation."""
    print("Validating text...")
    
    # Read input text
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.text
    
    if not text:
        print("Error: No text provided")
        return 1
    
    # Validate text
    validator = TextValidator()
    is_valid, errors = validator.validate_text(text)
    
    if is_valid:
        print("✓ Text validation passed")
    else:
        print("✗ Text validation failed:")
        for error in errors:
            print(f"  - {error}")
    
    # Check compatibility
    compatibility = validator.check_medieval_compatibility(text)
    print(f"\nMedieval compatibility score: {compatibility['compatibility_score']:.2f}")
    print(f"Latin character ratio: {compatibility['latin_ratio']:.2f}")
    print(f"Medieval symbols found: {compatibility['medieval_symbols']}")
    
    if compatibility['suggestions']:
        print("\nSuggestions for improvement:")
        for suggestion in compatibility['suggestions']:
            print(f"  - {suggestion}")
    
    return 0


def batch_process(args):
    """Process multiple texts in batch."""
    print("Processing texts in batch...")
    
    # Read input files
    input_files = []
    if args.input_dir:
        input_dir = Path(args.input_dir)
        input_files = list(input_dir.glob("*.txt"))
    elif args.input_files:
        input_files = [Path(f) for f in args.input_files]
    
    if not input_files:
        print("Error: No input files found")
        return 1
    
    print(f"Found {len(input_files)} input files")
    
    # Initialize components
    augmentor = TextAugmentor(
        ligature_probability=args.ligature_prob,
        abbreviation_probability=args.abbreviation_prob,
        medieval_style=args.style
    )
    
    generator = ManuscriptGenerator(
        page_size=args.page_size,
        font_family=args.font,
        texture=args.texture,
        margin_size=args.margins,
        line_spacing=args.line_spacing,
        font_size=args.font_size
    )
    
    # Process each file
    output_dir = Path(args.output_dir or "output")
    output_dir.mkdir(exist_ok=True)
    
    for i, input_file in enumerate(input_files):
        print(f"Processing {input_file.name}...")
        
        # Read text
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Augment text
        medieval_text = augmentor.augment_text(
            text,
            add_ligatures=args.ligatures,
            add_abbreviations=args.abbreviations,
            add_decorations=args.decorations
        )
        
        # Generate manuscript
        manuscript = generator.generate(
            text=medieval_text,
            add_illuminations=args.illuminations,
            add_marginalia=args.marginalia,
            add_decorative_borders=args.borders,
            add_noise=args.noise,
            add_aging=args.aging
        )
        
        # Save manuscript
        output_name = f"{input_file.stem}_manuscript.png"
        output_path = output_dir / output_name
        manuscript.save(output_path)
        
        print(f"  Saved to: {output_path}")
    
    print(f"\nBatch processing completed. Output saved to: {output_dir}")
    return 0


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Synthetic HTR - Medieval Manuscript Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a manuscript from text
  synthetic-htr create "In nomine Domini nostri Iesu Christi" -o manuscript.png
  
  # Augment text to medieval style
  synthetic-htr augment "Hello world" --style gothic
  
  # Validate text
  synthetic-htr validate "Sample text" --input-file text.txt
  
  # Batch process multiple files
  synthetic-htr batch --input-dir texts/ --output-dir manuscripts/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create manuscript command
    create_parser = subparsers.add_parser('create', help='Create a manuscript')
    create_parser.add_argument('text', nargs='?', help='Input text')
    create_parser.add_argument('-i', '--input-file', help='Input text file')
    create_parser.add_argument('-o', '--output', help='Output image file')
    create_parser.add_argument('--style', choices=['carolingian', 'gothic', 'uncial'], 
                              default='carolingian', help='Medieval style')
    create_parser.add_argument('--font', choices=['medieval', 'gothic', 'uncial', 'serif', 'decorative'],
                              default='medieval', help='Font family')
    create_parser.add_argument('--texture', choices=['parchment', 'paper', 'vellum'],
                              default='parchment', help='Page texture')
    create_parser.add_argument('--page-size', nargs=2, type=int, default=[1200, 1600],
                              help='Page size (width height)')
    create_parser.add_argument('--margins', type=int, default=100, help='Margin size')
    create_parser.add_argument('--line-spacing', type=float, default=1.5, help='Line spacing')
    create_parser.add_argument('--font-size', type=int, default=24, help='Font size')
    create_parser.add_argument('--ligature-prob', type=float, default=0.7, help='Ligature probability')
    create_parser.add_argument('--abbreviation-prob', type=float, default=0.5, help='Abbreviation probability')
    create_parser.add_argument('--ligatures', action='store_true', help='Add ligatures')
    create_parser.add_argument('--abbreviations', action='store_true', help='Add abbreviations')
    create_parser.add_argument('--decorations', action='store_true', help='Add decorations')
    create_parser.add_argument('--illuminations', action='store_true', help='Add illuminations')
    create_parser.add_argument('--marginalia', action='store_true', help='Add marginalia')
    create_parser.add_argument('--borders', action='store_true', help='Add decorative borders')
    create_parser.add_argument('--noise', action='store_true', help='Add noise')
    create_parser.add_argument('--aging', action='store_true', help='Add aging effects')
    create_parser.set_defaults(func=create_manuscript)
    
    # Augment text command
    augment_parser = subparsers.add_parser('augment', help='Augment text to medieval style')
    augment_parser.add_argument('text', nargs='?', help='Input text')
    augment_parser.add_argument('-i', '--input-file', help='Input text file')
    augment_parser.add_argument('-o', '--output-file', help='Output text file')
    augment_parser.add_argument('--style', choices=['carolingian', 'gothic', 'uncial'],
                               default='carolingian', help='Medieval style')
    augment_parser.add_argument('--ligature-prob', type=float, default=0.7, help='Ligature probability')
    augment_parser.add_argument('--abbreviation-prob', type=float, default=0.5, help='Abbreviation probability')
    augment_parser.add_argument('--ligatures', action='store_true', help='Add ligatures')
    augment_parser.add_argument('--abbreviations', action='store_true', help='Add abbreviations')
    augment_parser.add_argument('--decorations', action='store_true', help='Add decorations')
    augment_parser.set_defaults(func=augment_text)
    
    # Validate text command
    validate_parser = subparsers.add_parser('validate', help='Validate text for medieval generation')
    validate_parser.add_argument('text', nargs='?', help='Input text')
    validate_parser.add_argument('-i', '--input-file', help='Input text file')
    validate_parser.set_defaults(func=validate_text)
    
    # Batch process command
    batch_parser = subparsers.add_parser('batch', help='Process multiple texts in batch')
    batch_parser.add_argument('--input-dir', help='Input directory containing text files')
    batch_parser.add_argument('--input-files', nargs='+', help='Input text files')
    batch_parser.add_argument('--output-dir', help='Output directory for manuscripts')
    batch_parser.add_argument('--style', choices=['carolingian', 'gothic', 'uncial'],
                             default='carolingian', help='Medieval style')
    batch_parser.add_argument('--font', choices=['medieval', 'gothic', 'uncial', 'serif', 'decorative'],
                             default='medieval', help='Font family')
    batch_parser.add_argument('--texture', choices=['parchment', 'paper', 'vellum'],
                             default='parchment', help='Page texture')
    batch_parser.add_argument('--page-size', nargs=2, type=int, default=[1200, 1600],
                             help='Page size (width height)')
    batch_parser.add_argument('--margins', type=int, default=100, help='Margin size')
    batch_parser.add_argument('--line-spacing', type=float, default=1.5, help='Line spacing')
    batch_parser.add_argument('--font-size', type=int, default=24, help='Font size')
    batch_parser.add_argument('--ligature-prob', type=float, default=0.7, help='Ligature probability')
    batch_parser.add_argument('--abbreviation-prob', type=float, default=0.5, help='Abbreviation probability')
    batch_parser.add_argument('--ligatures', action='store_true', help='Add ligatures')
    batch_parser.add_argument('--abbreviations', action='store_true', help='Add abbreviations')
    batch_parser.add_argument('--decorations', action='store_true', help='Add decorations')
    batch_parser.add_argument('--illuminations', action='store_true', help='Add illuminations')
    batch_parser.add_argument('--marginalia', action='store_true', help='Add marginalia')
    batch_parser.add_argument('--borders', action='store_true', help='Add decorative borders')
    batch_parser.add_argument('--noise', action='store_true', help='Add noise')
    batch_parser.add_argument('--aging', action='store_true', help='Add aging effects')
    batch_parser.set_defaults(func=batch_process)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
