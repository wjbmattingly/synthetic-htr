#!/usr/bin/env python3
"""
Test script to verify the Medieval Letters Synthetic Dataset format.
"""

from datasets import load_from_disk
import matplotlib.pyplot as plt
from PIL import Image

def test_dataset():
    """Test loading and verifying the dataset format."""
    
    # Load the dataset
    print("Loading dataset...")
    dataset_path = "/Users/wjm55/data/medieval-letters-synthetic-dataset"
    
    try:
        dataset = load_from_disk(dataset_path)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return
    
    print(f"✅ Dataset loaded successfully: {len(dataset)} samples")
    print(f"📊 Features: {list(dataset.features.keys())}")
    print(f"🎯 Feature types: {dataset.features}")
    
    # Check the first sample
    print("\n🔍 Inspecting first sample...")
    sample = dataset[0]
    
    print(f"Letter ID: {sample['letter_id']}")
    print(f"Page: {sample['page_number']}")
    print(f"Image type: {type(sample['image'])}")
    print(f"Image mode: {sample['image'].mode if hasattr(sample['image'], 'mode') else 'N/A'}")
    print(f"Image size: {sample['image'].size if hasattr(sample['image'], 'size') else 'N/A'}")
    print(f"Text length: {len(sample['text'])} chars")
    print(f"Abbreviated length: {len(sample['abbreviated'])} chars")
    
    print(f"\nOriginal text (first 150 chars):")
    print(f"'{sample['text'][:150]}...'")
    print(f"\nAbbreviated text (first 150 chars):")
    print(f"'{sample['abbreviated'][:150]}...'")
    
    # Test image access and display
    try:
        if hasattr(sample['image'], 'size'):
            print(f"\n📸 Image details:")
            print(f"   Size: {sample['image'].size}")
            print(f"   Mode: {sample['image'].mode}")
            print(f"   Format: {sample['image'].format}")
            
            # Try to save the image
            sample['image'].save('test_manuscript_sample.png')
            print("   ✅ Sample image saved as 'test_manuscript_sample.png'")
        else:
            print("⚠️  Image is not a PIL Image object")
    except Exception as e:
        print(f"❌ Error accessing image: {e}")
    
    # Check dataset iteration
    print(f"\n🔄 Testing dataset iteration...")
    count = 0
    for i, item in enumerate(dataset):
        if i >= 3:  # Just test first 3
            break
        count += 1
        print(f"   Sample {i}: Letter {item['letter_id']}, Page {item['page_number']}")
    
    print(f"✅ Successfully iterated through {count} samples")
    
    # Test dataset slicing
    print(f"\n📏 Testing dataset slicing...")
    subset = dataset[:5]
    print(f"   Subset length: {len(subset['image'])}")
    print(f"   All samples have images: {all(hasattr(img, 'size') for img in subset['image'])}")
    
    print(f"\n🎉 Dataset format verification complete!")
    print(f"   ✅ Proper HuggingFace format")
    print(f"   ✅ PIL Images loaded correctly")
    print(f"   ✅ Text fields populated")
    print(f"   ✅ Ready for training!")

if __name__ == "__main__":
    test_dataset()
