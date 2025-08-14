#!/usr/bin/env python3
"""
Test script to demonstrate loading and using the Medieval Letters Synthetic Dataset.
"""

from datasets import load_from_disk
import matplotlib.pyplot as plt

def test_dataset():
    """Test loading and displaying samples from the dataset."""
    
    # Load the dataset
    print("Loading dataset...")
    dataset = load_from_disk("/Users/wjm55/data/medieval-letters-synthetic-dataset")
    
    print(f"Dataset loaded: {len(dataset)} samples")
    print(f"Features: {list(dataset.features.keys())}")
    
    # Get a sample
    sample = dataset[0]
    
    print("\nSample 0:")
    print(f"Letter ID: {sample['letter_id']}")
    print(f"Page: {sample['page_number']}")
    print(f"Image size: {sample['image'].size}")
    print(f"Original text: {sample['text'][:100]}...")
    print(f"Abbreviated text: {sample['abbreviated'][:100]}...")
    
    # Display the image
    plt.figure(figsize=(10, 8))
    plt.imshow(sample['image'])
    plt.title(f"Letter {sample['letter_id']}, Page {sample['page_number']}")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('sample_manuscript.png', dpi=150, bbox_inches='tight')
    print("\nSample image saved as 'sample_manuscript.png'")
    
    # Show some statistics
    print(f"\nDataset Statistics:")
    print(f"Total samples: {len(dataset)}")
    
    letter_ids = set(sample['letter_id'] for sample in dataset)
    print(f"Unique letters: {len(letter_ids)}")
    
    avg_text_length = sum(len(sample['text']) for sample in dataset) / len(dataset)
    print(f"Average text length: {avg_text_length:.1f} characters")
    
    print("\nDataset ready for training!")

if __name__ == "__main__":
    test_dataset()
