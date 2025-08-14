"""
Synthetic HTR - Medieval Manuscript Generator

A Python package for generating synthetic medieval manuscripts with HTR capabilities.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .augmentor.text_augmentor import TextAugmentor
from .generator.manuscript_generator import ManuscriptGenerator
from .visualization.visualizer import ManuscriptVisualizer
from .visualization.ocr_analyzer import OCRAnalyzer

__all__ = [
    "TextAugmentor",
    "ManuscriptGenerator",
    "ManuscriptVisualizer",
    "OCRAnalyzer",
    "__version__",
    "__author__",
    "__email__",
]
