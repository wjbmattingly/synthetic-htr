"""
Synthetic HTR - Medieval Manuscript Generator

A Python package for generating synthetic medieval manuscripts with HTR capabilities.
Enhanced with advanced typography features inspired by the Cerne font project.
"""

__version__ = "0.2.0"  # Updated with advanced typography
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .augmentor.text_augmentor import TextAugmentor
from .generator.manuscript_generator import ManuscriptGenerator
from .visualization.visualizer import ManuscriptVisualizer
from .visualization.ocr_analyzer import OCRAnalyzer

# Import advanced typography features if available
try:
    from .typography import (
        AdvancedFontManager,
        ContextualAlternatesEngine,
        ColorFontRenderer,
        LetterformVariationEngine
    )
    ADVANCED_TYPOGRAPHY_AVAILABLE = True
    
    __all__ = [
        "TextAugmentor",
        "ManuscriptGenerator",
        "ManuscriptVisualizer",
        "OCRAnalyzer",
        "AdvancedFontManager",
        "ContextualAlternatesEngine",
        "ColorFontRenderer",
        "LetterformVariationEngine",
        "__version__",
        "__author__",
        "__email__",
    ]
    
except ImportError:
    ADVANCED_TYPOGRAPHY_AVAILABLE = False
    
    __all__ = [
        "TextAugmentor",
        "ManuscriptGenerator",
        "ManuscriptVisualizer",
        "OCRAnalyzer",
        "__version__",
        "__author__",
        "__email__",
    ]
