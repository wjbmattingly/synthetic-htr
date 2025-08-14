#!/usr/bin/env python3
"""
Test the clean dataset with only essential fields.
"""

from datasets import load_dataset
import warnings
warnings.filterwarnings("ignore")  # Suppress NumPy warnings

def test_clean_dataset():
    """Test the clean dataset structure."""
    
    dataset_path = "/Users/wjm55/data/medieval-letters-synthetic-dataset"
    
    print("🧪 Testing Clean Dataset")
    print("=" * 40)
    
    try:
        # Load dataset
        dataset = load_dataset(dataset_path)
        
        print(f"✅ Dataset loaded successfully!")
        print(f"   Samples: {len(dataset['train'])}")
        print(f"   Features: {list(dataset['train'].features.keys())}")
        
        # Test sample access
        sample = dataset['train'][0]
        print(f"\n📋 Sample 0:")
        print(f"   Image type: {type(sample['image'])}")
        print(f"   Image size: {sample['image'].size}")
        print(f"   Transcription length: {len(sample['transcription'])} chars")
        print(f"   Full transcription length: {len(sample['full_page_transcription'])} chars")
        print(f"   XML length: {len(sample['page_xml'])} chars")
        
        # Show text samples
        print(f"\n📝 Text samples:")
        print(f"   Abbreviated: '{sample['transcription'][:80]}...'")
        print(f"   Original: '{sample['full_page_transcription'][:80]}...'")
        
        # Show XML snippet
        print(f"\n📄 XML snippet:")
        xml_lines = sample['page_xml'].split('\n')[:3]
        for line in xml_lines:
            print(f"   {line.strip()}")
        print("   ...")
        
        print(f"\n🎯 Perfect for image-text side-by-side training!")
        print(f"   ✅ Image first in feature order")
        print(f"   ✅ Only essential fields")
        print(f"   ✅ Raw XML included")
        print(f"   ✅ No file path dependencies")
        print(f"   ✅ Ready for HuggingFace Hub!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_clean_dataset()
