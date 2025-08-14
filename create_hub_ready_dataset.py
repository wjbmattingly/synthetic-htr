#!/usr/bin/env python3
"""
Create HuggingFace Hub-ready dataset using streaming approach.

This version creates the dataset in a way that's optimized for HuggingFace Hub upload
and avoids Parquet conversion issues.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Iterator
import xml.etree.ElementTree as ET

try:
    from datasets import Dataset, Features, Value, Image as ImageFeature, DatasetDict
    from PIL import Image
except ImportError:
    print("Error: datasets library not found. Install with: pip install datasets pillow")
    sys.exit(1)


class HubReadyDatasetConverter:
    """
    Creates a HuggingFace Hub-ready dataset.
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
    
    def data_generator(self) -> Iterator[Dict[str, Any]]:
        """Generator that yields data samples one by one."""
        letter_dirs = sorted([d for d in self.input_dir.iterdir() if d.is_dir()])
        
        print(f"Found {len(letter_dirs)} letter directories")
        
        count = 0
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
                    
                    # Load image as PIL Image
                    try:
                        pil_image = Image.open(img_path)
                    except Exception as e:
                        print(f"Warning: Failed to load image {img_path}: {e}")
                        continue
                    
                    text_data = self.extract_text_from_xml(xml_path)
                    
                    page_data = {
                        'image': pil_image,  # Direct PIL Image
                        'text': text_data['original'],
                        'abbreviated': text_data['abbreviated'],
                        'letter_id': letter_dir.name,
                        'page_number': page_name.split('_')[1],
                    }
                    
                    count += 1
                    yield page_data
                    
            except Exception as e:
                print(f"Warning: Failed to process {letter_dir}: {e}")
                continue
        
        print(f"Generated {count} total samples")
    
    def create_hub_ready_dataset(self) -> Dataset:
        """Create Hub-ready dataset."""
        print("Creating Hub-ready dataset...")
        
        # Define features
        features = Features({
            'image': ImageFeature(),
            'text': Value('string'),
            'abbreviated': Value('string'),
            'letter_id': Value('string'),
            'page_number': Value('string'),
        })
        
        # Create dataset from generator
        dataset = Dataset.from_generator(
            self.data_generator,
            features=features
        )
        
        print(f"Dataset created with {len(dataset)} samples")
        return dataset
    
    def save_hub_ready_dataset(self, dataset: Dataset):
        """Save Hub-ready dataset."""
        print(f"Saving Hub-ready dataset to: {self.output_dir}")
        
        # Remove existing directory
        if self.output_dir.exists():
            import shutil
            shutil.rmtree(self.output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save dataset
        dataset.save_to_disk(str(self.output_dir))
        
        print(f"✅ Hub-ready dataset saved!")
        print(f"   Location: {self.output_dir}")
        print(f"   Samples: {len(dataset)}")
        
        # Create a simple README
        readme_content = f"""# Medieval Letters Synthetic Dataset

A synthetic dataset of medieval manuscript images with transcriptions.

## Dataset Description

This dataset contains {len(dataset)} synthetic medieval manuscript pages with:
- **Image**: Manuscript page image (375x500px)
- **Text**: Original transcription 
- **Abbreviated**: Abbreviated form (as shown on image)
- **Letter ID**: Unique letter identifier
- **Page Number**: Page number within letter

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("path/to/medieval-letters-synthetic-dataset")
```

## Features

- Synthetic medieval handwriting with realistic textures
- Original and abbreviated text pairs
- Multiple abbreviation styles (ligatures, contractions, etc.)
- Perfect for HTR/OCR model training
"""
        
        with open(self.output_dir / 'README.md', 'w') as f:
            f.write(readme_content)
        
        print("   📝 README.md created")
    
    def convert(self):
        """Main conversion process."""
        print("🚀 Hub-Ready Medieval Letters Dataset Converter")
        print("=" * 50)
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print()
        
        dataset = self.create_hub_ready_dataset()
        self.save_hub_ready_dataset(dataset)
        
        print("\n🎉 Hub-ready conversion completed!")
        print("   ✅ Optimized for HuggingFace Hub")
        print("   ✅ Parquet-compatible format")
        print("   ✅ Ready for upload!")


def main():
    parser = argparse.ArgumentParser(description="Create Hub-ready HuggingFace dataset")
    parser.add_argument("--input-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic",
                       help="Input directory")
    parser.add_argument("--output-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic-dataset",
                       help="Output directory")
    
    args = parser.parse_args()
    
    try:
        converter = HubReadyDatasetConverter(args.input_dir, args.output_dir)
        converter.convert()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
