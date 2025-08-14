#!/usr/bin/env python3
"""
Create a Parquet-safe HuggingFace dataset.

This version manually creates the metadata to avoid Arrow/Parquet conversion issues.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

try:
    from datasets import Dataset, Features, Value, Image as ImageFeature
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    print("Error: datasets library not found. Install with: pip install datasets pyarrow")
    sys.exit(1)


class ParquetSafeDatasetConverter:
    """
    Creates a Parquet-safe HuggingFace dataset.
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
    
    def create_dataset(self, data: List[Dict[str, Any]]) -> Dataset:
        """Create dataset."""
        print("Creating dataset...")
        
        dataset = Dataset.from_list(data)
        dataset = dataset.cast_column('image', ImageFeature())
        
        print(f"Dataset created with {len(dataset)} samples")
        return dataset
    
    def save_parquet_safe_dataset(self, dataset: Dataset):
        """Save dataset with manually created, safe metadata."""
        print(f"Saving Parquet-safe dataset to: {self.output_dir}")
        
        # Remove existing directory
        if self.output_dir.exists():
            import shutil
            shutil.rmtree(self.output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save dataset first
        dataset.save_to_disk(str(self.output_dir))
        
        # Create clean state.json without problematic fields
        clean_state = {
            "_data_files": [{"filename": "data-00000-of-00001.arrow"}],
            "_fingerprint": "clean_dataset_v1",
            "_format_columns": None,
            "_format_type": None,
            "_output_all_columns": False,
            "_split": None
        }
        
        # Write the clean state.json
        with open(self.output_dir / 'state.json', 'w') as f:
            json.dump(clean_state, f, indent=2)
        
        print(f"✅ Parquet-safe dataset saved!")
        print(f"   Location: {self.output_dir}")
        print(f"   Samples: {len(dataset)}")
    
    def convert(self):
        """Main conversion process."""
        print("🔒 Parquet-Safe Medieval Letters Dataset Converter")
        print("=" * 50)
        
        all_data = self.collect_all_data()
        
        if not all_data:
            print("❌ No data found!")
            return
        
        dataset = self.create_dataset(all_data)
        self.save_parquet_safe_dataset(dataset)
        
        print("\n🎉 Parquet-safe conversion completed!")


def main():
    parser = argparse.ArgumentParser(description="Create Parquet-safe HuggingFace dataset")
    parser.add_argument("--input-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic",
                       help="Input directory")
    parser.add_argument("--output-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic-dataset",
                       help="Output directory")
    
    args = parser.parse_args()
    
    try:
        converter = ParquetSafeDatasetConverter(args.input_dir, args.output_dir)
        converter.convert()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
