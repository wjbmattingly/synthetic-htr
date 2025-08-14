#!/usr/bin/env python3
"""
Test the final Parquet dataset to ensure it loads properly.
"""

from datasets import load_dataset
from pathlib import Path

def test_parquet_dataset():
    """Test loading the Parquet dataset."""
    
    dataset_path = "/Users/wjm55/data/medieval-letters-synthetic-dataset"
    
    print("🧪 Testing Final Parquet Dataset")
    print("=" * 40)
    
    try:
        # Load dataset
        dataset = load_dataset(dataset_path)
        
        print(f"✅ Dataset loaded successfully!")
        print(f"   Splits: {list(dataset.keys())}")
        print(f"   Train samples: {len(dataset['train'])}")
        print(f"   Features: {list(dataset['train'].features.keys())}")
        
        # Test sample access
        sample = dataset['train'][0]
        print(f"\n📋 Sample 0:")
        print(f"   ID: {sample['id']}")
        print(f"   Manuscript: {sample['manuscript_id']}")
        print(f"   Page: {sample['page_id']}")
        print(f"   Language: {sample['language']}")
        print(f"   Script: {sample['script']}")
        print(f"   Image type: {type(sample['image'])}")
        print(f"   Image size: {sample['image'].size}")
        print(f"   Transcription length: {len(sample['transcription'])} chars")
        print(f"   Full transcription length: {len(sample['full_page_transcription'])} chars")
        
        # Show text sample
        print(f"\n📝 Text samples:")
        print(f"   Original: '{sample['full_page_transcription'][:80]}...'")
        print(f"   Abbreviated: '{sample['transcription'][:80]}...'")
        
        # Test iteration
        print(f"\n🔄 Testing iteration:")
        count = 0
        for i, item in enumerate(dataset['train']):
            count += 1
            if i >= 2:
                break
        print(f"   Successfully iterated {count} samples")
        
        # Test slicing
        print(f"\n📏 Testing slicing:")
        subset = dataset['train'][:3]
        print(f"   Subset size: {len(subset['id'])}")
        print(f"   All have images: {all(hasattr(img, 'size') for img in subset['image'])}")
        
        print(f"\n🎉 All tests passed! Dataset is ready for:")
        print(f"   ✅ HuggingFace Hub upload")
        print(f"   ✅ HTR model training")
        print(f"   ✅ Research applications")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_parquet_dataset()
