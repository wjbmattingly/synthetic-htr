#!/usr/bin/env python3
"""
Demo script showing how to use the Medieval Letters Synthetic Dataset.
"""

from datasets import load_from_disk
import matplotlib.pyplot as plt
import numpy as np

def demonstrate_dataset_usage():
    """Demonstrate various ways to use the dataset."""
    
    print("🏰 Medieval Letters Synthetic Dataset Demo")
    print("=" * 50)
    
    # Load the dataset
    dataset_path = "/Users/wjm55/data/medieval-letters-synthetic-dataset"
    dataset = load_from_disk(dataset_path)
    
    print(f"📚 Dataset loaded: {len(dataset)} samples")
    print(f"🏷️  Features: {list(dataset.features.keys())}")
    
    # Show some basic statistics
    print(f"\n📊 Dataset Statistics:")
    letter_ids = [sample['letter_id'] for sample in dataset]
    unique_letters = set(letter_ids)
    print(f"   Unique letters: {len(unique_letters)}")
    
    text_lengths = [len(sample['text']) for sample in dataset]
    abbrev_lengths = [len(sample['abbreviated']) for sample in dataset]
    
    print(f"   Average original text length: {np.mean(text_lengths):.1f} chars")
    print(f"   Average abbreviated text length: {np.mean(abbrev_lengths):.1f} chars")
    print(f"   Average compression ratio: {(1 - np.mean(abbrev_lengths) / np.mean(text_lengths)) * 100:.1f}%")
    
    # Show sample data
    print(f"\n🔍 Sample Examples:")
    for i in range(min(3, len(dataset))):
        sample = dataset[i]
        print(f"\n   Sample {i+1}:")
        print(f"     Letter: {sample['letter_id']}, Page: {sample['page_number']}")
        print(f"     Image: {sample['image'].size}, {sample['image'].mode}")
        print(f"     Original: \"{sample['text'][:80]}...\"")
        print(f"     Abbreviated: \"{sample['abbreviated'][:80]}...\"")
    
    # Demonstrate filtering
    print(f"\n🔎 Dataset Filtering Examples:")
    
    # Filter by letter ID
    letter_0000_pages = dataset.filter(lambda x: x['letter_id'] == '0000')
    print(f"   Letter 0000 has {len(letter_0000_pages)} pages")
    
    # Filter by text length
    long_texts = dataset.filter(lambda x: len(x['text']) > 1000)
    print(f"   {len(long_texts)} pages have >1000 characters")
    
    # Demonstrate mapping
    print(f"\n🔄 Dataset Mapping Examples:")
    
    # Add computed fields
    enhanced_dataset = dataset.map(lambda x: {
        **x,
        'text_length': len(x['text']),
        'abbreviated_length': len(x['abbreviated']),
        'compression_ratio': 1 - len(x['abbreviated']) / len(x['text']) if len(x['text']) > 0 else 0
    })
    
    sample_enhanced = enhanced_dataset[0]
    print(f"   Added computed fields: text_length={sample_enhanced['text_length']}, compression_ratio={sample_enhanced['compression_ratio']:.3f}")
    
    # Demonstrate train/test split
    print(f"\n📊 Train/Test Split Example:")
    split_dataset = dataset.train_test_split(test_size=0.2, seed=42)
    print(f"   Train: {len(split_dataset['train'])} samples")
    print(f"   Test: {len(split_dataset['test'])} samples")
    
    # Demonstrate batching
    print(f"\n📦 Batching Example:")
    dataloader = dataset.select(range(5)).iter(batch_size=2)
    for i, batch in enumerate(dataloader):
        print(f"   Batch {i+1}: {len(batch['image'])} images, {len(batch['text'])} texts")
        if i >= 1:  # Just show first 2 batches
            break
    
    # Create a visualization
    print(f"\n🎨 Creating visualization...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Medieval Letters Synthetic Dataset Samples', fontsize=16)
    
    for i, ax in enumerate(axes.flat):
        if i < len(dataset):
            sample = dataset[i]
            ax.imshow(sample['image'])
            ax.set_title(f"Letter {sample['letter_id']}, Page {sample['page_number']}", fontsize=10)
            ax.axis('off')
        else:
            ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('dataset_samples.png', dpi=150, bbox_inches='tight')
    print(f"   📸 Visualization saved as 'dataset_samples.png'")
    
    print(f"\n✅ Demo completed! The dataset is ready for:")
    print(f"   • Handwritten Text Recognition (HTR) training")
    print(f"   • OCR model fine-tuning")
    print(f"   • Medieval text analysis")
    print(f"   • Abbreviation expansion research")
    print(f"   • Historical document processing")

if __name__ == "__main__":
    demonstrate_dataset_usage()
