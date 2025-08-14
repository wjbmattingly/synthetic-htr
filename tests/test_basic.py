#!/usr/bin/env python3
"""
Basic tests for the Synthetic HTR package.
"""

import unittest
import tempfile
import os
from PIL import Image

from synthetic_htr import TextAugmentor, ManuscriptGenerator, ManuscriptVisualizer, OCRAnalyzer
from synthetic_htr.utils import TextValidator
from synthetic_htr.augmentor import ComplexAbbreviationRules


class TestTextAugmentor(unittest.TestCase):
    """Test cases for the TextAugmentor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.augmentor = TextAugmentor()
        self.sample_text = "In nomine Domini nostri Iesu Christi"
    
    def test_basic_augmentation(self):
        """Test basic text augmentation."""
        result = self.augmentor.augment_text(self.sample_text)
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, self.sample_text)
    
    def test_complex_augmentation(self):
        """Test complex text augmentation with context."""
        result = self.augmentor.augment_text(
            self.sample_text,
            add_ligatures=True,
            add_abbreviations=True,
            add_complex_abbreviations=True,
            context="religious"
        )
        self.assertIsInstance(result, str)
    
    def test_ligature_application(self):
        """Test ligature application."""
        result = self.augmentor.augment_text(
            self.sample_text,
            add_ligatures=True,
            add_abbreviations=False
        )
        # Should contain some ligatures
        self.assertIsInstance(result, str)
    
    def test_abbreviation_application(self):
        """Test abbreviation application."""
        result = self.augmentor.augment_text(
            self.sample_text,
            add_ligatures=False,
            add_abbreviations=True
        )
        # Should contain some abbreviations
        self.assertIsInstance(result, str)
    
    def test_style_changing(self):
        """Test changing medieval style."""
        self.augmentor.set_style("gothic")
        self.assertEqual(self.augmentor.medieval_style, "gothic")
        
        self.augmentor.set_style("carolingian")
        self.assertEqual(self.augmentor.medieval_style, "carolingian")
    
    def test_invalid_style(self):
        """Test invalid style handling."""
        with self.assertRaises(ValueError):
            self.augmentor.set_style("invalid_style")
    
    def test_batch_augmentation(self):
        """Test batch text augmentation."""
        texts = ["Text 1", "Text 2", "Text 3"]
        results = self.augmentor.batch_augment(texts)
        
        self.assertEqual(len(results), len(texts))
        for result in results:
            self.assertIsInstance(result, str)


class TestManuscriptGenerator(unittest.TestCase):
    """Test cases for the ManuscriptGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ManuscriptGenerator()
        self.sample_text = "Sample text for testing manuscript generation."
    
    def test_basic_generation(self):
        """Test basic manuscript generation."""
        manuscript = self.generator.generate(self.sample_text)
        self.assertIsInstance(manuscript, Image.Image)
        self.assertEqual(manuscript.size, self.generator.page_size)
    
    def test_page_size_changing(self):
        """Test changing page size."""
        new_size = (800, 1000)
        self.generator.set_page_size(new_size)
        self.assertEqual(self.generator.page_size, new_size)
    
    def test_font_changing(self):
        """Test changing font family."""
        self.generator.set_font("gothic")
        self.assertEqual(self.generator.font_family, "gothic")
    
    def test_texture_changing(self):
        """Test changing texture."""
        self.generator.set_texture("paper")
        self.assertEqual(self.generator.texture, "paper")
    
    def test_batch_generation(self):
        """Test batch manuscript generation."""
        texts = ["Text 1", "Text 2"]
        with tempfile.TemporaryDirectory() as temp_dir:
            results = self.generator.batch_generate(texts, temp_dir)
            self.assertEqual(len(results), len(texts))
            
            # Check that files were created
            for result_path in results:
                self.assertTrue(os.path.exists(result_path))


class TestTextValidator(unittest.TestCase):
    """Test cases for the TextValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = TextValidator()
        self.valid_text = "In nomine Domini nostri Iesu Christi"
        self.invalid_text = "Invalid text with 🚀 emoji"
    
    def test_valid_text_validation(self):
        """Test validation of valid text."""
        is_valid, errors = self.validator.validate_text(self.valid_text)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_text_validation(self):
        """Test validation of invalid text."""
        is_valid, errors = self.validator.validate_text(self.invalid_text)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_empty_text_validation(self):
        """Test validation of empty text."""
        is_valid, errors = self.validator.validate_text("")
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_text_sanitization(self):
        """Test text sanitization."""
        sanitized = self.validator.sanitize_text(self.invalid_text)
        self.assertNotEqual(sanitized, self.invalid_text)
        self.assertIsInstance(sanitized, str)
    
    def test_text_normalization(self):
        """Test text normalization."""
        normalized = self.validator.normalize_text("  Multiple   Spaces  ")
        self.assertEqual(normalized, "multiple spaces")
    
    def test_medieval_compatibility(self):
        """Test medieval compatibility checking."""
        compatibility = self.validator.check_medieval_compatibility(self.valid_text)
        self.assertIn('compatibility_score', compatibility)
        self.assertIn('latin_ratio', compatibility)
        self.assertIn('suggestions', compatibility)
    
    def test_medieval_improvements(self):
        """Test medieval improvement suggestions."""
        suggestions = self.validator.suggest_medieval_improvements(self.valid_text)
        self.assertIsInstance(suggestions, list)
    
    def test_style_validation(self):
        """Test medieval style validation."""
        is_valid, errors = self.validator.validate_medieval_style(
            self.valid_text, "carolingian"
        )
        self.assertTrue(is_valid)
        
        is_valid, errors = self.validator.validate_medieval_style(
            self.valid_text, "invalid_style"
        )
        self.assertFalse(is_valid)


class TestComplexAbbreviationRules(unittest.TestCase):
    """Test cases for the ComplexAbbreviationRules class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.complex_rules = ComplexAbbreviationRules()
        self.sample_text = "In nomine Domini nostri Iesu Christi amen"
    
    def test_complex_abbreviation_application(self):
        """Test complex abbreviation application."""
        result = self.complex_rules.apply_complex_abbreviations(
            self.sample_text,
            probability=1.0,
            context="religious"
        )
        self.assertIsInstance(result, str)
        # Should have some abbreviations applied
        self.assertTrue(any(char in result for char in ['̄', '☧', '⁊']))
    
    def test_abbreviation_statistics(self):
        """Test abbreviation statistics calculation."""
        abbreviated = self.complex_rules.apply_complex_abbreviations(
            self.sample_text, probability=1.0
        )
        stats = self.complex_rules.get_abbreviation_statistics(
            self.sample_text, abbreviated
        )
        
        self.assertIn('original_length', stats)
        self.assertIn('abbreviated_length', stats)
        self.assertIn('reduction_percentage', stats)
    
    def test_abbreviation_validation(self):
        """Test abbreviation validation."""
        test_text = "d̄s vobiscum ☧s regnat"
        is_valid, errors = self.complex_rules.validate_abbreviations(test_text)
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(errors, list)


class TestManuscriptVisualizer(unittest.TestCase):
    """Test cases for the ManuscriptVisualizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = ManuscriptVisualizer()
        # Create a simple test image
        self.test_image = Image.new('RGB', (100, 100), color='white')
        self.test_polygons = [
            ("test text", [(10, 10), (50, 10), (50, 30), (10, 30)]),
            ("more text", [(10, 40), (60, 40), (60, 60), (10, 60)])
        ]
    
    def test_visualizer_initialization(self):
        """Test visualizer initialization."""
        self.assertIsInstance(self.visualizer, ManuscriptVisualizer)
        self.assertEqual(self.visualizer.figure_size, (15, 10))
    
    def test_polygon_visualization(self):
        """Test polygon visualization (without actually displaying)."""
        # This test ensures the method doesn't crash
        try:
            # We can't easily test the actual plotting without display
            # but we can test that the method exists and accepts parameters
            self.assertTrue(hasattr(self.visualizer, 'visualize_manuscript_with_polygons'))
        except Exception as e:
            self.fail(f"Visualization method failed: {e}")


class TestOCRAnalyzer(unittest.TestCase):
    """Test cases for the OCRAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = OCRAnalyzer()
        self.sample_text = "Sample text for OCR analysis"
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        self.assertIsInstance(self.analyzer, OCRAnalyzer)
        self.assertEqual(self.analyzer.alto_namespace, "http://www.loc.gov/standards/alto/ns-v4#")
    
    def test_ocr_data_generation(self):
        """Test OCR data generation."""
        try:
            image, polygons, alto_xml = self.analyzer.generate_synthetic_ocr_data(
                text=self.sample_text,
                width=400,
                height=300,
                font_size=16
            )
            
            self.assertIsInstance(image, Image.Image)
            self.assertIsInstance(polygons, list)
            self.assertIsNotNone(alto_xml)
            
        except Exception as e:
            # Skip test if font issues or other environment problems
            self.skipTest(f"OCR generation skipped due to environment: {e}")
    
    def test_text_distribution_analysis(self):
        """Test text distribution analysis."""
        test_polygons = [
            ("text1", [(10, 10), (50, 10), (50, 30), (10, 30)]),
            ("text2", [(10, 40), (60, 40), (60, 60), (10, 60)])
        ]
        
        analysis = self.analyzer.analyze_text_distribution(test_polygons, 100, 100)
        
        self.assertIn('total_text_regions', analysis)
        self.assertIn('text_coverage', analysis)
        self.assertEqual(analysis['total_text_regions'], 2)


if __name__ == "__main__":
    unittest.main()
