#!/usr/bin/env python3
"""
Create a completely clean HuggingFace dataset that avoids Arrow/Parquet issues.

This version creates the dataset without any problematic internal metadata.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

try:
    from datasets import Dataset, Features, Value, Image as ImageFeature
    import datasets
except ImportError:
    print("Error: datasets library not found. Install with: pip install datasets")
    sys.exit(1)


class CleanDatasetConverter:
    """
    Creates a clean HuggingFace dataset without metadata issues.
    """
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
    
    def extract_text_from_xml(self, xml_path: Path) -> Dict[str, str]:
        """Extract original and abbreviated text from ALTO XML file."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Find all String elements
            namespace = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
            strings = root.findall('.//alto:String', namespace)
            
            if not strings:
                strings = root.findall('.//String')
            
            abbreviated_parts = []
            original_parts = []
            
            for string_elem in strings:
                abbreviated_content = string_elem.get('CONTENT', '')
                abbreviated_parts.append(abbreviated_content)
                
                original_content = string_elem.get('ORIGINAL_CONTENT')
                if original_content:
                    original_parts.append(original_content)
                else:
                    original_parts.append(abbreviated_content)
            
            return {
                'original': ' '.join(original_parts),
                'abbreviated': ' '.join(abbreviated_parts)
            }
            
        except Exception as e:
            print(f"Warning: Failed to parse XML {xml_path}: {e}")
            return {'original': '', 'abbreviated': ''}
    
    def collect_all_data(self) -> List[Dict[str, Any]]:
        """Collect all manuscript data."""
        print(f"Scanning directory: {self.input_dir}")
        
        all_data = []
        letter_dirs = sorted([d for d in self.input_dir.iterdir() if d.is_dir()])
        
        print(f"Found {len(letter_dirs)} letter directories")
        
        for i, letter_dir in enumerate(letter_dirs):
            if i % 100 == 0:
                print(f"Processing letter {i}/{len(letter_dirs)}: {letter_dir.name}")
            
            try:
                original_images = sorted(letter_dir.glob("page_*_original.png"))
                
                for img_path in original_images:
                    page_name = img_path.stem.replace('_original', '')
                    xml_path = letter_dir / f"{page_name}.xml"
                    
                    if not xml_path.exists():
                        continue
                    
                    text_data = self.extract_text_from_xml(xml_path)
                    
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
        
        print(f"Collected {len(all_data)} total pages")
        return all_data
    
    def create_clean_dataset(self, data: List[Dict[str, Any]]) -> Dataset:
        """Create a clean dataset without problematic metadata."""
        print("Creating clean HuggingFace dataset...")
        
        # Create dataset directly without complex features that might cause issues
        dataset = Dataset.from_list(data)
        
        # Cast to proper types
        dataset = dataset.cast_column('image', ImageFeature())
        
        print(f"Dataset created with {len(dataset)} samples")
        return dataset
    
    def save_clean_dataset(self, dataset: Dataset):
        """Save dataset in a clean format."""
        print(f"Saving clean dataset to: {self.output_dir}")
        
        # Remove existing directory
        if self.output_dir.exists():
            import shutil
            shutil.rmtree(self.output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save dataset without any custom formatting
        dataset.save_to_disk(str(self.output_dir))
        
        print(f"✅ Clean dataset saved!")
        print(f"   Location: {self.output_dir}")
        print(f"   Samples: {len(dataset)}")
    
    def convert(self):
        """Main conversion process."""
        print("🧹 Clean Medieval Letters Dataset Converter")
        print("=" * 50)
        
        all_data = self.collect_all_data()
        
        if not all_data:
            print("❌ No data found!")
            return
        
        dataset = self.create_clean_dataset(all_data)
        self.save_clean_dataset(dataset)
        
        print("\n🎉 Clean conversion completed!")


def main():
    parser = argparse.ArgumentParser(description="Create clean HuggingFace dataset")
    parser.add_argument("--input-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic",
                       help="Input directory")
    parser.add_argument("--output-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic-dataset",
                       help="Output directory")
    
    args = parser.parse_args()
    
    try:
        converter = CleanDatasetConverter(args.input_dir, args.output_dir)
        converter.convert()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
