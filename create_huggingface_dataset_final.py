#!/usr/bin/env python3
"""
Convert Medieval Letters Synthetic Manuscripts to Hugging Face Dataset (Final Version)

This version creates a clean HuggingFace dataset without any conflicting metadata 
that could cause Arrow schema issues.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

try:
    from datasets import Dataset, Features, Value, Image as ImageFeature
except ImportError:
    print("Error: datasets library not found. Install with: pip install datasets")
    sys.exit(1)


class ManuscriptDatasetConverter:
    """
    Converts synthetic manuscript data to Hugging Face dataset format.
    """
    
    def __init__(self, input_dir: str, output_dir: str):
        """
        Initialize the converter.
        
        Args:
            input_dir: Directory containing the synthetic manuscript data
            output_dir: Directory where the HF dataset will be saved
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
    
    def extract_text_from_xml(self, xml_path: Path) -> Dict[str, str]:
        """
        Extract original and abbreviated text from ALTO XML file.
        
        Args:
            xml_path: Path to the XML file
            
        Returns:
            Dictionary with 'original' and 'abbreviated' text
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Find all String elements
            namespace = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
            strings = root.findall('.//alto:String', namespace)
            
            if not strings:
                # Try without namespace
                strings = root.findall('.//String')
            
            abbreviated_parts = []
            original_parts = []
            
            for string_elem in strings:
                # Get abbreviated content (what's displayed)
                abbreviated_content = string_elem.get('CONTENT', '')
                abbreviated_parts.append(abbreviated_content)
                
                # Get original content (before abbreviations)
                original_content = string_elem.get('ORIGINAL_CONTENT')
                if original_content:
                    original_parts.append(original_content)
                else:
                    # If no original content, use abbreviated content
                    original_parts.append(abbreviated_content)
            
            return {
                'original': ' '.join(original_parts),
                'abbreviated': ' '.join(abbreviated_parts)
            }
            
        except Exception as e:
            print(f"Warning: Failed to parse XML {xml_path}: {e}")
            return {'original': '', 'abbreviated': ''}
    
    def collect_all_data(self) -> List[Dict[str, Any]]:
        """
        Collect all manuscript data from the input directory.
        
        Returns:
            List of all page data dictionaries with image paths
        """
        print(f"Scanning directory: {self.input_dir}")
        
        all_data = []
        letter_dirs = sorted([d for d in self.input_dir.iterdir() if d.is_dir()])
        
        print(f"Found {len(letter_dirs)} letter directories")
        
        for i, letter_dir in enumerate(letter_dirs):
            if i % 100 == 0:
                print(f"Processing letter {i}/{len(letter_dirs)}: {letter_dir.name}")
            
            try:
                # Find all original image files
                original_images = sorted(letter_dir.glob("page_*_original.png"))
                
                for img_path in original_images:
                    # Extract page number from filename
                    page_name = img_path.stem.replace('_original', '')
                    xml_path = letter_dir / f"{page_name}.xml"
                    
                    if not xml_path.exists():
                        print(f"Warning: XML file not found for {img_path}")
                        continue
                    
                    # Extract text from XML
                    text_data = self.extract_text_from_xml(xml_path)
                    
                    # Create page entry with image path
                    page_data = {
                        'image': str(img_path),
                        'text': text_data['original'],
                        'abbreviated': text_data['abbreviated'],
                        'letter_id': letter_dir.name,
                        'page_number': page_name.split('_')[1],
                    }
                    
                    all_data.append(page_data)
                    
            except Exception as e:
                print(f"Warning: Failed to process {letter_dir}: {e}")
                continue
        
        print(f"Collected {len(all_data)} total pages from {len(letter_dirs)} letters")
        return all_data
    
    def create_dataset(self, data: List[Dict[str, Any]]) -> Dataset:
        """
        Create a Hugging Face dataset from the collected data.
        
        Args:
            data: List of page data dictionaries
            
        Returns:
            Hugging Face Dataset object
        """
        print("Creating Hugging Face dataset...")
        
        # Define features explicitly
        features = Features({
            'image': ImageFeature(),
            'text': Value('string'),
            'abbreviated': Value('string'),
            'letter_id': Value('string'),
            'page_number': Value('string'),
        })
        
        # Create dataset from the data with explicit features
        dataset = Dataset.from_list(data, features=features)
        
        print(f"Dataset created with {len(dataset)} samples")
        print(f"Features: {list(dataset.features.keys())}")
        
        return dataset
    
    def save_dataset(self, dataset: Dataset):
        """
        Save the dataset to disk.
        
        Args:
            dataset: Hugging Face Dataset to save
        """
        print(f"Saving dataset to: {self.output_dir}")
        
        # Remove existing directory to avoid conflicts
        if self.output_dir.exists():
            import shutil
            shutil.rmtree(self.output_dir)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as Hugging Face dataset - this creates the proper format
        dataset.save_to_disk(str(self.output_dir))
        
        print(f"✅ Dataset saved successfully!")
        print(f"   Location: {self.output_dir}")
        print(f"   Samples: {len(dataset)}")
        print(f"   Features: {list(dataset.features.keys())}")
    
    def convert(self):
        """
        Main conversion process.
        """
        print("🏰 Medieval Letters Dataset Converter (Final)")
        print("=" * 50)
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print()
        
        # Collect all data
        all_data = self.collect_all_data()
        
        if not all_data:
            print("❌ No data found to convert!")
            return
        
        # Create dataset
        dataset = self.create_dataset(all_data)
        
        # Save dataset
        self.save_dataset(dataset)
        
        print("\n🎉 Conversion completed successfully!")
        print("   ✅ Clean HuggingFace format")
        print("   ✅ No conflicting metadata")
        print("   ✅ Ready for HuggingFace Hub!")


def main():
    """Main function to run the dataset converter."""
    parser = argparse.ArgumentParser(description="Convert synthetic manuscripts to Hugging Face dataset")
    parser.add_argument("--input-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic",
                       help="Input directory containing synthetic manuscript data")
    parser.add_argument("--output-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic-dataset",
                       help="Output directory for the Hugging Face dataset")
    
    args = parser.parse_args()
    
    try:
        converter = ManuscriptDatasetConverter(args.input_dir, args.output_dir)
        converter.convert()
    except KeyboardInterrupt:
        print("\n⏹️  Conversion interrupted by user.")
        return 1
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
