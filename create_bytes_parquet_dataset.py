#!/usr/bin/env python3
"""
Create HuggingFace dataset with images as bytes (not paths).

This version explicitly converts images to bytes to ensure no file paths are stored.
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


class BytesParquetDatasetConverter:
    """
    Creates HuggingFace dataset with images as raw bytes.
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
    
    def pil_to_bytes(self, pil_image: Image.Image) -> bytes:
        """Convert PIL Image to bytes."""
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def collect_all_data(self) -> List[Dict[str, Any]]:
        """Collect all manuscript data with images as bytes."""
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
                    
                    text_data = self.extract_text_from_xml(xml_path)
                    page_number = page_name.split('_')[1]
                    
                    # Create record with image as bytes
                    record = {
                        'id': f"{letter_dir.name}_{page_number}",
                        'manuscript_id': letter_dir.name,
                        'page_id': page_number,
                        'line_id': "full_page",
                        'transcription': text_data['abbreviated'],
                        'full_page_transcription': text_data['original'],
                        'xml_line_id': f"{letter_dir.name}_{page_number}_line_1",
                        'xml_transcription': text_data['abbreviated'],
                        'bbox_x': 0,
                        'bbox_y': 0,
                        'bbox_width': pil_image.size[0],
                        'bbox_height': pil_image.size[1],
                        'baseline': "",
                        'language': "latin",
                        'script': "gothic",
                        'type': "synthetic",
                        'dataset_name': "medieval-letters-synthetic",
                        'license': "cc-by-4.0",
                        'source_url': "",
                        'description': "Synthetic medieval manuscript page with abbreviations",
                        'shelfmark': f"synthetic_{letter_dir.name}",
                        'origin': "synthetic_generation",
                        'date': "medieval_style",
                        'library': "synthetic",
                        'url': "",
                        'iiif': "",
                        'rdf': "",
                        'image': {"bytes": image_bytes},  # Image as bytes dict
                        'full_page_image': {"bytes": image_bytes},  # Same image
                    }
                    
                    all_data.append(record)
                    
            except Exception as e:
                print(f"Warning: Failed to process {letter_dir}: {e}")
                continue
        
        print(f"Collected {len(all_data)} total pages")
        return all_data
    
    def create_dataset(self, data: List[Dict[str, Any]]) -> Dataset:
        """Create dataset with proper image features."""
        print("Creating dataset with embedded images...")
        
        # Define features - images will be automatically handled as bytes
        features = Features({
            'id': Value('string'),
            'manuscript_id': Value('string'),
            'page_id': Value('string'),
            'line_id': Value('string'),
            'transcription': Value('string'),
            'full_page_transcription': Value('string'),
            'xml_line_id': Value('string'),
            'xml_transcription': Value('string'),
            'bbox_x': Value('int32'),
            'bbox_y': Value('int32'),
            'bbox_width': Value('int32'),
            'bbox_height': Value('int32'),
            'baseline': Value('string'),
            'language': Value('string'),
            'script': Value('string'),
            'type': Value('string'),
            'dataset_name': Value('string'),
            'license': Value('string'),
            'source_url': Value('string'),
            'description': Value('string'),
            'shelfmark': Value('string'),
            'origin': Value('string'),
            'date': Value('string'),
            'library': Value('string'),
            'url': Value('string'),
            'iiif': Value('string'),
            'rdf': Value('string'),
            'image': ImageFeature(),  # Will handle bytes automatically
            'full_page_image': ImageFeature(),
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
  - name: id
    dtype: string
  - name: manuscript_id
    dtype: string
  - name: page_id
    dtype: string
  - name: line_id
    dtype: string
  - name: transcription
    dtype: string
  - name: full_page_transcription
    dtype: string
  - name: xml_line_id
    dtype: string
  - name: xml_transcription
    dtype: string
  - name: bbox_x
    dtype: int32
  - name: bbox_y
    dtype: int32
  - name: bbox_width
    dtype: int32
  - name: bbox_height
    dtype: int32
  - name: baseline
    dtype: string
  - name: language
    dtype: string
  - name: script
    dtype: string
  - name: type
    dtype: string
  - name: dataset_name
    dtype: string
  - name: license
    dtype: string
  - name: source_url
    dtype: string
  - name: description
    dtype: string
  - name: shelfmark
    dtype: string
  - name: origin
    dtype: string
  - name: date
    dtype: string
  - name: library
    dtype: string
  - name: url
    dtype: string
  - name: iiif
    dtype: string
  - name: rdf
    dtype: string
  - name: image
    dtype: image
  - name: full_page_image
    dtype: image
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

A synthetic dataset of {num_examples} medieval manuscript pages with original and abbreviated transcriptions.

## Dataset Description

This dataset contains high-quality synthetic medieval manuscript pages featuring:

- **Synthetic manuscript images** (375x500px) with realistic textures and ink variations
- **Original transcriptions** before abbreviation rules were applied  
- **Abbreviated transcriptions** as they appear on the manuscripts (e.g., "omn;" for "omnibus")
- **Medieval Latin text** with authentic abbreviation patterns
- **Gothic script styling** with natural handwriting variations

## Key Features

- `transcription`: Text as it appears on the manuscript with abbreviations
- `full_page_transcription`: Original text before abbreviations
- `image`: The synthetic manuscript page image (embedded as bytes)
- `manuscript_id`: Unique identifier for each letter (0000, 0001, etc.)
- `page_id`: Page number within the manuscript

## Usage

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("path/to/medieval-letters-synthetic")

# Access a sample
sample = dataset['train'][0]
print(f"Original: {{sample['full_page_transcription'][:100]}}...")
print(f"Abbreviated: {{sample['transcription'][:100]}}...")

# Display the image
sample['image'].show()
```

## Applications

Perfect for:
- **Handwritten Text Recognition (HTR)** model training
- **OCR development** for historical documents  
- **Medieval paleography** research
- **Abbreviation expansion** studies
- **Document digitization** benchmarks

## Technical Details

- **Image format**: PNG, 375x500px resolution, embedded as bytes
- **Text encoding**: UTF-8
- **Language**: Medieval Latin
- **Script**: Gothic/medieval style
- **Abbreviations**: Includes ligatures, contractions, and Tironian notes

## License

CC-BY-4.0

## Citation

```bibtex
@dataset{{medieval_letters_synthetic,
  title={{Medieval Letters Synthetic Dataset}},
  year={{2024}},
  description={{Synthetic medieval manuscript dataset with {num_examples} pages}},
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
        print("🔒 Bytes-Based Parquet Dataset Converter")
        print("=" * 50)
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print()
        
        all_data = self.collect_all_data()
        
        if not all_data:
            print("❌ No data found!")
            return
        
        dataset = self.create_dataset(all_data)
        self.save_parquet_dataset(dataset, num_shards=5)
        
        print("\n🎉 Bytes-based Parquet dataset creation completed!")
        print("   ✅ Images embedded as bytes (no file paths)")
        print("   ✅ No external file dependencies")
        print("   ✅ Ready for HuggingFace Hub!")


def main():
    parser = argparse.ArgumentParser(description="Create Parquet dataset with images as bytes")
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
        converter = BytesParquetDatasetConverter(args.input_dir, args.output_dir)
        converter.convert()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
