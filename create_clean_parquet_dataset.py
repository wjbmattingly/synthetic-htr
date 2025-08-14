#!/usr/bin/env python3
"""
Create clean HuggingFace dataset with only essential fields.

Features: image, transcription, full_page_transcription, page_xml
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
import math
import io

try:
    from datasets import Dataset, Features, Value, Image as ImageFeature
    import pandas as pd
    from PIL import Image
except ImportError:
    print("Error: Required libraries not found. Install with: pip install datasets pandas pillow")
    sys.exit(1)


class CleanParquetDatasetConverter:
    """
    Creates clean HuggingFace dataset with only essential fields.
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
    
    def read_xml_as_text(self, xml_path: Path) -> str:
        """Read XML file as raw text."""
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Failed to read XML {xml_path}: {e}")
            return ""
    
    def pil_to_bytes(self, pil_image: Image.Image) -> bytes:
        """Convert PIL Image to bytes."""
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def collect_all_data(self) -> List[Dict[str, Any]]:
        """Collect all manuscript data with only essential fields."""
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
                    
                    # Load image and convert to bytes
                    try:
                        pil_image = Image.open(img_path)
                        image_bytes = self.pil_to_bytes(pil_image)
                    except Exception as e:
                        print(f"Warning: Failed to load image {img_path}: {e}")
                        continue
                    
                    # Extract text data
                    text_data = self.extract_text_from_xml(xml_path)
                    
                    # Read raw XML
                    page_xml = self.read_xml_as_text(xml_path)
                    
                    # Create clean record with only essential fields
                    record = {
                        'image': {"bytes": image_bytes},  # Image first
                        'transcription': text_data['abbreviated'],  # What appears on image
                        'full_page_transcription': text_data['original'],  # Original text
                        'page_xml': page_xml,  # Raw XML content
                    }
                    
                    all_data.append(record)
                    
            except Exception as e:
                print(f"Warning: Failed to process {letter_dir}: {e}")
                continue
        
        print(f"Collected {len(all_data)} total pages")
        return all_data
    
    def create_dataset(self, data: List[Dict[str, Any]]) -> Dataset:
        """Create dataset with clean features."""
        print("Creating clean dataset...")
        
        # Define features in the order you want: image first
        features = Features({
            'image': ImageFeature(),  # First field
            'transcription': Value('string'),  # Abbreviated text (what's on the image)
            'full_page_transcription': Value('string'),  # Original text
            'page_xml': Value('string'),  # Raw XML content
        })
        
        dataset = Dataset.from_list(data, features=features)
        
        print(f"Dataset created with {len(dataset)} samples")
        return dataset
    
    def save_parquet_dataset(self, dataset: Dataset, num_shards: int = 5):
        """Save dataset as multiple Parquet files."""
        print(f"Saving dataset as {num_shards} Parquet files...")
        
        # Remove existing directory and create new structure
        if self.output_dir.exists():
            import shutil
            shutil.rmtree(self.output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        data_dir = self.output_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Calculate shard size
        total_samples = len(dataset)
        shard_size = math.ceil(total_samples / num_shards)
        
        total_bytes = 0
        actual_shards = 0
        
        for i in range(num_shards):
            start_idx = i * shard_size
            end_idx = min((i + 1) * shard_size, total_samples)
            
            if start_idx >= total_samples:
                break
            
            print(f"  Creating shard {i+1}/{num_shards} (samples {start_idx} to {end_idx-1})")
            
            shard = dataset.select(range(start_idx, end_idx))
            
            # Save as Parquet
            parquet_filename = f"train-{i:05d}-of-{num_shards:05d}.parquet"
            parquet_path = data_dir / parquet_filename
            
            shard.to_parquet(str(parquet_path))
            
            file_size = parquet_path.stat().st_size
            total_bytes += file_size
            actual_shards += 1
            
            print(f"     {parquet_filename}: {file_size / (1024*1024):.1f} MB ({end_idx - start_idx} samples)")
        
        # Create README.md
        self.create_readme(dataset, total_bytes, actual_shards)
        
        print(f"✅ Dataset saved to {self.output_dir}")
        print(f"   Total size: {total_bytes / (1024*1024):.1f} MB")
        print(f"   Samples: {len(dataset)}")
        print(f"   Shards: {actual_shards}")
    
    def create_readme(self, dataset: Dataset, total_bytes: int, num_shards: int):
        """Create README.md with dataset metadata."""
        num_examples = len(dataset)
        download_size = total_bytes
        
        readme_content = f"""---
dataset_info:
  features:
  - name: image
    dtype: image
  - name: transcription
    dtype: string
  - name: full_page_transcription
    dtype: string
  - name: page_xml
    dtype: string
  splits:
  - name: train
    num_bytes: {total_bytes}.0
    num_examples: {num_examples}
  download_size: {download_size}
  dataset_size: {total_bytes}.0
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
---

# Medieval Letters Synthetic Dataset

A clean synthetic dataset of {num_examples} medieval manuscript pages with transcriptions.

## Dataset Description

This dataset contains high-quality synthetic medieval manuscript pages featuring:

- **Synthetic manuscript images** (375x500px) with realistic textures and ink variations
- **Abbreviated transcriptions** as they appear on the manuscripts (e.g., "omn;" for "omnibus")
- **Original transcriptions** before abbreviation rules were applied  
- **Page XML** containing the full ALTO XML with layout and text information

## Features

- **`image`**: The synthetic manuscript page image (PNG, 375x500px)
- **`transcription`**: Text as it appears on the manuscript with medieval abbreviations
- **`full_page_transcription`**: Original text before abbreviations were applied
- **`page_xml`**: Raw ALTO XML containing layout and transcription data

## Usage

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("path/to/medieval-letters-synthetic")

# Access a sample
sample = dataset['train'][0]

# Display image and transcriptions side by side
print("Image size:", sample['image'].size)
print("Abbreviated:", sample['transcription'][:100], "...")
print("Original:", sample['full_page_transcription'][:100], "...")

# Show the image
sample['image'].show()

# Access XML data
xml_content = sample['page_xml']
print("XML length:", len(xml_content), "characters")
```

## Image and Text Side-by-Side

This dataset is perfect for training models that need to correlate visual manuscript content with textual transcriptions:

```python
import matplotlib.pyplot as plt

sample = dataset['train'][0]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Show image
ax1.imshow(sample['image'])
ax1.set_title('Manuscript Image')
ax1.axis('off')

# Show transcriptions
text_content = f"Abbreviated:\\n{{sample['transcription'][:200]}}...\\n\\nOriginal:\\n{{sample['full_page_transcription'][:200]}}..."
ax2.text(0.05, 0.95, text_content, transform=ax2.transAxes, fontsize=10, 
         verticalalignment='top', wrap=True)
ax2.set_title('Transcriptions')
ax2.axis('off')

plt.tight_layout()
plt.show()
```

## Applications

Perfect for:
- **Handwritten Text Recognition (HTR)** model training
- **OCR development** for historical documents  
- **Medieval paleography** research
- **Abbreviation expansion** studies
- **Image-to-text alignment** tasks

## Technical Details

- **Image format**: PNG, 375x500px resolution, embedded as bytes
- **Text encoding**: UTF-8
- **Language**: Medieval Latin
- **Script**: Gothic/medieval style
- **Abbreviations**: Includes ligatures, contractions, and Tironian notes
- **XML format**: ALTO XML with layout and transcription information

## License

CC-BY-4.0

## Citation

```bibtex
@dataset{{medieval_letters_synthetic,
  title={{Medieval Letters Synthetic Dataset}},
  year={{2024}},
  description={{Clean synthetic medieval manuscript dataset with {num_examples} pages}},
  license={{CC-BY-4.0}}
}}
```
"""
        
        readme_path = self.output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"   📝 README.md created")
    
    def convert(self):
        """Main conversion process."""
        print("🧹 Clean Parquet Dataset Converter")
        print("=" * 50)
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print()
        print("Features: image, transcription, full_page_transcription, page_xml")
        print()
        
        all_data = self.collect_all_data()
        
        if not all_data:
            print("❌ No data found!")
            return
        
        dataset = self.create_dataset(all_data)
        self.save_parquet_dataset(dataset, num_shards=5)
        
        print("\n🎉 Clean Parquet dataset creation completed!")
        print("   ✅ Only essential fields included")
        print("   ✅ Image first, then transcriptions")
        print("   ✅ Raw XML included")
        print("   ✅ No file path dependencies")
        print("   ✅ Ready for HuggingFace Hub!")


def main():
    parser = argparse.ArgumentParser(description="Create clean Parquet dataset with essential fields only")
    parser.add_argument("--input-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic",
                       help="Input directory")
    parser.add_argument("--output-dir", 
                       default="/Users/wjm55/data/medieval-letters-synthetic-dataset",
                       help="Output directory")
    parser.add_argument("--num-shards", 
                       type=int,
                       default=5,
                       help="Number of Parquet files to create")
    
    args = parser.parse_args()
    
    try:
        converter = CleanParquetDatasetConverter(args.input_dir, args.output_dir)
        converter.convert()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
