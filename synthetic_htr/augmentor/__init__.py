"""
Text augmentation module for converting modern text to medieval Latin style.
"""

from .text_augmentor import TextAugmentor
from .ligature_rules import LigatureRules
from .abbreviation_rules import AbbreviationRules
from .complex_abbreviation_rules import ComplexAbbreviationRules

__all__ = [
    "TextAugmentor",
    "LigatureRules", 
    "AbbreviationRules",
    "ComplexAbbreviationRules",
]
