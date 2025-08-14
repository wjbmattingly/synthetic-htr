#!/usr/bin/env python3
"""
Validate that the dataset follows proper HuggingFace format and will work with the Hub.
"""

from datasets import load_from_disk
import json
from pathlib import Path

def validate_dataset():
    """Validate the dataset format and structure."""
    
    dataset_path = "/Users/wjm55/data/medieval-letters-synthetic-dataset"
    
    print("🔍 HuggingFace Dataset Format Validation")
    print("=" * 50)
    
    # Check required files exist
    required_files = ['data-00000-of-00001.arrow', 'dataset_info.json', 'state.json']
    missing_files = []
    
    for file in required_files:
        file_path = Path(dataset_path) / file
        if not file_path.exists():
            missing_files.append(file)
        else:
            print(f"✅ {file} exists ({file_path.stat().st_size:,} bytes)")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    # Check dataset_info.json format
    print(f"\n📋 Checking dataset_info.json format...")
    with open(Path(dataset_path) / 'dataset_info.json', 'r') as f:
        dataset_info = json.load(f)
    
    required_keys = ['features']
    for key in required_keys:
        if key in dataset_info:
            print(f"✅ {key} present")
        else:
            print(f"❌ {key} missing")
            return False
    
    # Check features format
    features = dataset_info['features']
    expected_features = ['image', 'text', 'abbreviated', 'letter_id', 'page_number']
    
    print(f"\n🏷️  Checking features...")
    for feature in expected_features:
        if feature in features:
            feature_type = features[feature].get('_type', 'Unknown')
            print(f"✅ {feature}: {feature_type}")
        else:
            print(f"❌ {feature} missing")
            return False
    
    # Load and test dataset
    print(f"\n📚 Loading dataset...")
    try:
        dataset = load_from_disk(dataset_path)
        print(f"✅ Dataset loaded successfully")
        print(f"   Samples: {len(dataset)}")
        print(f"   Features: {list(dataset.features.keys())}")
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return False
    
    # Test sample access
    print(f"\n🔍 Testing sample access...")
    try:
        sample = dataset[0]
        print(f"✅ Sample access works")
        print(f"   Image type: {type(sample['image'])}")
        print(f"   Image size: {sample['image'].size}")
        print(f"   Text length: {len(sample['text'])}")
        print(f"   Letter ID: {sample['letter_id']}")
    except Exception as e:
        print(f"❌ Error accessing sample: {e}")
        return False
    
    # Test iteration
    print(f"\n🔄 Testing dataset iteration...")
    try:
        count = 0
        for i, item in enumerate(dataset):
            count += 1
            if i >= 2:  # Just test first 3
                break
        print(f"✅ Iteration works ({count} samples tested)")
    except Exception as e:
        print(f"❌ Error during iteration: {e}")
        return False
    
    # Test slicing
    print(f"\n📏 Testing dataset slicing...")
    try:
        subset = dataset[:5]
        print(f"✅ Slicing works (subset size: {len(subset['image'])})")
    except Exception as e:
        print(f"❌ Error during slicing: {e}")
        return False
    
    # Check for any unusual files
    print(f"\n📁 Checking for unexpected files...")
    dataset_dir = Path(dataset_path)
    all_files = list(dataset_dir.iterdir())
    expected_files = {'.cache', 'data-00000-of-00001.arrow', 'dataset_info.json', 'state.json'}
    
    unexpected_files = []
    for file in all_files:
        if file.name not in expected_files:
            unexpected_files.append(file.name)
    
    if unexpected_files:
        print(f"⚠️  Unexpected files found: {unexpected_files}")
        print("   (These might cause issues with HuggingFace Hub)")
    else:
        print(f"✅ No unexpected files found")
    
    print(f"\n🎉 Validation Summary:")
    print(f"   ✅ All required files present")
    print(f"   ✅ dataset_info.json format correct")
    print(f"   ✅ Features properly defined")
    print(f"   ✅ Dataset loads successfully")
    print(f"   ✅ Sample access works")
    print(f"   ✅ Iteration and slicing work")
    print(f"   ✅ Ready for HuggingFace Hub upload!")
    
    print(f"\n📤 To upload to HuggingFace Hub:")
    print(f"   1. Install huggingface_hub: pip install huggingface_hub")
    print(f"   2. Login: huggingface-cli login")
    print(f"   3. Upload: huggingface-cli upload your-username/medieval-letters-synthetic {dataset_path}")
    
    return True

if __name__ == "__main__":
    validate_dataset()
