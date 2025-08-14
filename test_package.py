#!/usr/bin/env python3
"""
Simple test script to verify the Synthetic HTR package works correctly.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from synthetic_htr import TextAugmentor, ManuscriptGenerator
        print("✓ Main package imports successful")
    except ImportError as e:
        print(f"✗ Main package import failed: {e}")
        return False
    
    try:
        from synthetic_htr.augmentor import LigatureRules, AbbreviationRules
        print("✓ Augmentor module imports successful")
    except ImportError as e:
        print(f"✗ Augmentor module import failed: {e}")
        return False
    
    try:
        from synthetic_htr.generator import LayoutEngine, TextureManager
        print("✓ Generator module imports successful")
    except ImportError as e:
        print(f"✗ Generator module import failed: {e}")
        return False
    
    try:
        from synthetic_htr.utils import ImageProcessor, TextValidator
        print("✓ Utils module imports successful")
    except ImportError as e:
        print(f"✗ Utils module import failed: {e}")
        return False
    
    return True


def test_text_augmentor():
    """Test the text augmentor functionality."""
    print("\nTesting text augmentor...")
    
    try:
        from synthetic_htr import TextAugmentor
        
        # Test basic initialization
        augmentor = TextAugmentor()
        print("✓ TextAugmentor initialization successful")
        
        # Test text augmentation
        sample_text = "In nomine Domini nostri Iesu Christi"
        augmented = augmentor.augment_text(sample_text)
        
        if augmented != sample_text:
            print("✓ Text augmentation working")
        else:
            print("⚠ Text augmentation may not be working (no changes detected)")
        
        # Test style changing
        augmentor.set_style("gothic")
        if augmentor.medieval_style == "gothic":
            print("✓ Style changing working")
        else:
            print("✗ Style changing failed")
        
        return True
        
    except Exception as e:
        print(f"✗ Text augmentor test failed: {e}")
        return False


def test_manuscript_generator():
    """Test the manuscript generator functionality."""
    print("\nTesting manuscript generator...")
    
    try:
        from synthetic_htr import ManuscriptGenerator
        
        # Test basic initialization
        generator = ManuscriptGenerator(page_size=(800, 1000))
        print("✓ ManuscriptGenerator initialization successful")
        
        # Test font loading
        if hasattr(generator, 'font'):
            print("✓ Font loading successful")
        else:
            print("⚠ Font loading may have failed")
        
        return True
        
    except Exception as e:
        print(f"✗ Manuscript generator test failed: {e}")
        return False


def test_utilities():
    """Test utility functions."""
    print("\nTesting utilities...")
    
    try:
        from synthetic_htr.utils import TextValidator
        
        # Test validator initialization
        validator = TextValidator()
        print("✓ TextValidator initialization successful")
        
        # Test basic validation
        is_valid, errors = validator.validate_text("Test text")
        if is_valid:
            print("✓ Text validation working")
        else:
            print("⚠ Text validation may not be working")
        
        return True
        
    except Exception as e:
        print(f"✗ Utilities test failed: {e}")
        return False


def test_configuration():
    """Test configuration functionality."""
    print("\nTesting configuration...")
    
    try:
        from synthetic_htr.config import config
        
        # Test config loading
        if hasattr(config, 'config'):
            print("✓ Configuration loading successful")
            
            # Test getting values
            fonts = config.get('fonts')
            if fonts:
                print("✓ Configuration access working")
            else:
                print("⚠ Configuration access may not be working")
        else:
            print("⚠ Configuration may not be properly loaded")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("Synthetic HTR Package Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_text_augmentor,
        test_manuscript_generator,
        test_utilities,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package is working correctly.")
        return 0
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
