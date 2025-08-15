"""
Advanced typography module for medieval manuscript generation.

This module provides sophisticated typography features inspired by the Cerne font project,
including contextual alternates, automatic letterform variation, and color font support.
"""

from .font_manager import AdvancedFontManager
from .contextual_engine import ContextualAlternatesEngine
from .color_font import ColorFontRenderer
from .variation_engine import LetterformVariationEngine

__all__ = [
    'AdvancedFontManager',
    'ContextualAlternatesEngine', 
    'ColorFontRenderer',
    'LetterformVariationEngine'
]
