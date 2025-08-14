"""
Ligature rules engine for applying medieval ligatures to text.
"""

import re
import random
from typing import Dict, List, Tuple


class LigatureRules:
    """
    Applies medieval ligature rules to text based on historical manuscript conventions.
    """
    
    def __init__(self, style: str = "carolingian"):
        """
        Initialize ligature rules for a specific medieval style.
        
        Args:
            style: Medieval script style ("carolingian", "gothic", "uncial")
        """
        self.style = style
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize ligature rules based on the selected style."""
        # Common ligatures used across medieval styles
        self.common_ligatures = {
            "ae": "æ",  # U+00E6 Latin Small Letter AE
            "oe": "œ",  # U+0153 Latin Small Letter OE
            "AE": "Æ",  # U+00C6 Latin Capital Letter AE
            "OE": "Œ",  # U+0152 Latin Capital Letter OE
            "ff": "ﬀ",  # U+FB00 Latin Small Ligature FF
            "fi": "ﬁ",  # U+FB01 Latin Small Ligature FI
            "fl": "ﬂ",  # U+FB02 Latin Small Ligature FL
            "ffi": "ﬃ", # U+FB03 Latin Small Ligature FFI
            "ffl": "ﬄ", # U+FB04 Latin Small Ligature FFL
            "ft": "ﬅ",  # U+FB05 Latin Small Ligature Long S T
            "st": "ﬆ",  # U+FB06 Latin Small Ligature ST
            # "ct": "ꜯ",  # U+A72F Latin Small Letter Cuatrillo
            "ss": "ß",  # U+00DF Latin Small Letter Sharp S (German eszett)
            "tz": "ꜩ",  # U+A729 Latin Small Letter TZ
        }
        
        # Style-specific ligature rules with proper medieval ligatures
        if self.style == "carolingian":
            self.style_ligatures = {
                "ch": "ch",   # Often written as single character in manuscripts
                "th": "þ",    # U+00FE Latin Small Letter Thorn
                "TH": "Þ",    # U+00DE Latin Capital Letter Thorn
                "et": "⁊",    # U+204A Tironian Sign Et
                "qu": "ꝗ",    # U+A757 Latin Small Letter Q With Stroke Through Descender
                "nt": "nt",   # Medieval nt ligature
                "nd": "nd",   # Medieval nd ligature
                "mp": "mp",   # Medieval mp ligature
                "ng": "ng",   # Medieval ng ligature
                "nk": "nk",   # Medieval nk ligature
                "rum": "ꝝ",   # U+A75D Latin Small Letter Rum Rotunda
                "us": "ꝰ",    # U+A770 Modifier Letter Us
            }
        elif self.style == "gothic":
            self.style_ligatures = {
                "ch": "ch",
                "th": "þ",    # U+00FE Latin Small Letter Thorn
                "TH": "Þ",    # U+00DE Latin Capital Letter Thorn
                "et": "⁊",    # U+204A Tironian Sign Et
                "qu": "ꝗ",    # U+A757 Latin Small Letter Q With Stroke
                "ck": "ck",   # Gothic ck ligature
                "tz": "ꜩ",    # U+A729 Latin Small Letter TZ
                "pf": "pf",   # Gothic pf ligature
                "nt": "nt",   # Gothic nt ligature
                "nd": "nd",   # Gothic nd ligature
                "mp": "mp",   # Gothic mp ligature
                "ng": "ng",   # Gothic ng ligature
                "nk": "nk",   # Gothic nk ligature
                "ll": "ll",   # Gothic double l
                "mm": "mm",   # Gothic double m
                "nn": "nn",   # Gothic double n
                "pp": "pp",   # Gothic double p
                "tt": "tt",   # Gothic double t
                "rum": "ꝝ",   # U+A75D Latin Small Letter Rum Rotunda
                "us": "ꝰ",    # U+A770 Modifier Letter Us
                "ur": "ꝛ",    # U+A75B Latin Small Letter R Rotunda
            }
        elif self.style == "uncial":
            self.style_ligatures = {
                "et": "⁊",    # U+204A Tironian Sign Et
                "th": "þ",    # U+00FE Latin Small Letter Thorn (less common in uncial)
                "TH": "Þ",    # U+00DE Latin Capital Letter Thorn
                "qu": "ꝗ",    # U+A757 Latin Small Letter Q With Stroke
                "nt": "nt",   # Uncial nt ligature
                "nd": "nd",   # Uncial nd ligature
                "ng": "ng",   # Uncial ng ligature
                "us": "ꝰ",    # U+A770 Modifier Letter Us
            }
        else:
            self.style_ligatures = {}
        
        # Combine all ligatures
        self.all_ligatures = {**self.common_ligatures, **self.style_ligatures}
        
        # Priority order for ligature application (longer patterns first)
        self.ligature_order = sorted(
            self.all_ligatures.keys(),
            key=len,
            reverse=True
        )
    
    def apply(self, text: str, probability: float = 1.0) -> str:
        """
        Apply ligature rules to the text with context awareness.
        
        Args:
            text: Input text
            probability: Probability of applying each ligature (0.0-1.0)
            
        Returns:
            Text with applied ligatures
        """
        if probability <= 0:
            return text
        
        result = text
        
        # Apply ligatures in priority order (longest first)
        for ligature_pattern in self.ligature_order:
            if random.random() <= probability:
                replacement = self.all_ligatures[ligature_pattern]
                
                # Special handling for different types of ligatures
                if ligature_pattern in ['et', 'ET']:
                    # Apply tironian et only when 'et' is a standalone word
                    pattern = r'\b' + re.escape(ligature_pattern) + r'\b'
                    result = re.sub(pattern, replacement, result)
                elif ligature_pattern in self.common_ligatures:
                    # Apply common ligatures within words, case-sensitive
                    if ligature_pattern.isupper():
                        # Only replace uppercase patterns at word beginnings
                        pattern = r'\b' + re.escape(ligature_pattern)
                        result = re.sub(pattern, replacement, result)
                    else:
                        # Apply lowercase ligatures anywhere in words
                        pattern = re.escape(ligature_pattern)
                        result = re.sub(pattern, replacement, result)
                else:
                    # Apply style-specific ligatures within words
                    pattern = re.escape(ligature_pattern)
                    result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def set_style(self, style: str):
        """Change the medieval script style and reinitialize rules."""
        if style in ["carolingian", "gothic", "uncial"]:
            self.style = style
            self._initialize_rules()
        else:
            raise ValueError(f"Unknown style: {style}. Available styles: carolingian, gothic, uncial")
    
    def add_custom_ligature(self, pattern: str, replacement: str):
        """Add a custom ligature rule."""
        self.all_ligatures[pattern] = replacement
        # Re-sort the order
        self.ligature_order = sorted(
            self.all_ligatures.keys(),
            key=len,
            reverse=True
        )
    
    def get_available_ligatures(self) -> Dict[str, str]:
        """Get all available ligatures for the current style."""
        return self.all_ligatures.copy()
    
    def get_style_ligatures(self) -> Dict[str, str]:
        """Get style-specific ligatures only."""
        return self.style_ligatures.copy()
    
    def remove_ligature(self, pattern: str):
        """Remove a ligature rule."""
        if pattern in self.all_ligatures:
            del self.all_ligatures[pattern]
            if pattern in self.style_ligatures:
                del self.style_ligatures[pattern]
            # Re-sort the order
            self.ligature_order = sorted(
                self.all_ligatures.keys(),
                key=len,
                reverse=True
            )
    
    def apply_selective_ligatures(
        self,
        text: str,
        ligatures: List[str],
        probability: float = 1.0
    ) -> str:
        """
        Apply only specific ligatures to the text.
        
        Args:
            text: Input text
            ligatures: List of ligature patterns to apply
            probability: Probability of applying each ligature
            
        Returns:
            Text with applied ligatures
        """
        if probability <= 0:
            return text
        
        result = text
        
        for ligature_pattern in ligatures:
            if ligature_pattern in self.all_ligatures and random.random() <= probability:
                replacement = self.all_ligatures[ligature_pattern]
                pattern = re.escape(ligature_pattern)
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
