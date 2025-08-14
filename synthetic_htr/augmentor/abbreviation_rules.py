"""
Abbreviation rules engine for applying medieval abbreviations to text.
"""

import re
import random
from typing import Dict, List, Tuple


class AbbreviationRules:
    """
    Applies medieval abbreviation rules to text based on historical manuscript conventions.
    """
    
    def __init__(self, style: str = "carolingian"):
        """
        Initialize abbreviation rules for a specific medieval style.
        
        Args:
            style: Medieval script style ("carolingian", "gothic", "uncial")
        """
        self.style = style
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize abbreviation rules based on the selected style."""
        # Common abbreviations used across medieval styles
        self.common_abbreviations = {
            # Suspension (omitting letters at the end)
            "dominus": "d̄s",
            "deus": "d̄s",
            "christus": "x̄s",
            "sanctus": "s̄",
            "beatus": "b̄s",
            "pater": "p̄",
            "mater": "m̄",
            "filius": "f̄s",
            "spiritus": "s̄s",
            "gloria": "ḡa",
            "amen": "ā",
            "et": "&",
            "est": "est",
            "que": "q̄",
            "pro": "p̄",
            "per": "p̄",
            "con": "c̄",
            "com": "c̄",
            "cum": "c̄",
            
            # Contraction (omitting letters in the middle)
            "omnium": "om̄um",
            "omnipotens": "om̄potens",
            "omniparens": "om̄parens",
            "omniformis": "om̄formis",
            
            # Superscript abbreviations
            "anno": "a°",
            "domini": "d°",
            "mense": "m°",
            "die": "d°",
            "tempore": "t°",
            "seculo": "s°",
            "anno": "a°",
        }
        
        # Style-specific abbreviation rules
        if self.style == "carolingian":
            self.style_abbreviations = {
                "salvator": "sal̄tor",
                "salvatoris": "sal̄toris",
                "salvatorum": "sal̄torum",
                "salvatoribus": "sal̄toribus",
                "salvatorum": "sal̄torum",
                "salvatoribus": "sal̄toribus",
                "salvatorum": "sal̄torum",
                "salvatoribus": "sal̄toribus",
            }
        elif self.style == "gothic":
            self.style_abbreviations = {
                "salvator": "sal̄tor",
                "salvatoris": "sal̄toris",
                "salvatorum": "sal̄torum",
                "salvatoribus": "sal̄toribus",
                "salvatorum": "sal̄torum",
                "salvatoribus": "sal̄toribus",
                "salvatorum": "sal̄torum",
                "salvatoribus": "sal̄toribus",
                "omnium": "om̄um",
                "omnipotens": "om̄potens",
            }
        elif self.style == "uncial":
            self.style_abbreviations = {
                "salvator": "sal̄tor",
                "salvatoris": "sal̄toris",
                "salvatorum": "sal̄torum",
                "salvatoribus": "sal̄toribus",
            }
        else:
            self.style_abbreviations = {}
        
        # Word ending patterns (regex-based abbreviations)
        self.ending_patterns = {
            r'(\w+)ibus\b': r'\1;',  # Words ending in 'ibus' get abbreviated with semicolon
        }
        
        # Combine all abbreviations
        self.all_abbreviations = {**self.common_abbreviations, **self.style_abbreviations}
        
        # Priority order for abbreviation application (longer patterns first)
        self.abbreviation_order = sorted(
            self.all_abbreviations.keys(),
            key=len,
            reverse=True
        )
        
        # Tironian notes (historical shorthand symbols)
        self.tironian_notes = {
            "et": "⁊",
            "est": "ꝛ",
            "que": "ꝝ",
            "pro": "ꝟ",
            "per": "ꝟ",
            "con": "ꝡ",
            "com": "ꝡ",
            "cum": "ꝡ",
            "dominus": "ꝣ",
            "deus": "Ꝥ",
            "christus": "ꝥ",
            "sanctus": "Ꝧ",
            "beatus": "ꝧ",
            "pater": "Ꝩ",
            "mater": "ꝩ",
            "filius": "Ꝫ",
            "spiritus": "ꝫ",
            "gloria": "Ꝭ",
            "amen": "ꝭ",
        }
    
    def apply(self, text: str, probability: float = 1.0) -> str:
        """
        Apply abbreviation rules to the text.
        
        Args:
            text: Input text
            probability: Probability of applying each abbreviation (0.0-1.0)
            
        Returns:
            Text with applied abbreviations
        """
        if probability <= 0:
            return text
        
        result = text
        
        # Apply abbreviations in priority order (longest first)
        for abbreviation_pattern in self.abbreviation_order:
            if random.random() <= probability:
                replacement = self.all_abbreviations[abbreviation_pattern]
                
                # Use word boundaries to avoid partial replacements
                pattern = r'\b' + re.escape(abbreviation_pattern) + r'\b'
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Apply word ending patterns
        for pattern, replacement in self.ending_patterns.items():
            if random.random() <= probability:
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Apply Tironian notes with lower probability
        if random.random() <= probability * 0.3:
            result = self._apply_tironian_notes(result, probability * 0.5)
        
        return result
    
    def _apply_tironian_notes(self, text: str, probability: float) -> str:
        """Apply Tironian notes (historical shorthand symbols)."""
        result = text
        
        for pattern, replacement in self.tironian_notes.items():
            if random.random() <= probability:
                # Use word boundaries to avoid partial replacements
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                result = re.sub(pattern_regex, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def set_style(self, style: str):
        """Change the medieval script style and reinitialize rules."""
        if style in ["carolingian", "gothic", "uncial"]:
            self.style = style
            self._initialize_rules()
        else:
            raise ValueError(f"Unknown style: {style}. Available styles: carolingian, gothic, uncial")
    
    def add_custom_abbreviation(self, pattern: str, replacement: str):
        """Add a custom abbreviation rule."""
        self.all_abbreviations[pattern] = replacement
        # Re-sort the order
        self.abbreviation_order = sorted(
            self.all_abbreviations.keys(),
            key=len,
            reverse=True
        )
    
    def add_tironian_note(self, pattern: str, replacement: str):
        """Add a custom Tironian note."""
        self.tironian_notes[pattern] = replacement
    
    def add_ending_pattern(self, pattern: str, replacement: str):
        """Add a custom word ending pattern."""
        self.ending_patterns[pattern] = replacement
    
    def get_available_abbreviations(self) -> Dict[str, str]:
        """Get all available abbreviations for the current style."""
        return self.all_abbreviations.copy()
    
    def get_style_abbreviations(self) -> Dict[str, str]:
        """Get style-specific abbreviations only."""
        return self.style_abbreviations.copy()
    
    def get_tironian_notes(self) -> Dict[str, str]:
        """Get all Tironian notes."""
        return self.tironian_notes.copy()
    
    def remove_abbreviation(self, pattern: str):
        """Remove an abbreviation rule."""
        if pattern in self.all_abbreviations:
            del self.all_abbreviations[pattern]
            if pattern in self.style_abbreviations:
                del self.style_abbreviations[pattern]
            # Re-sort the order
            self.abbreviation_order = sorted(
                self.all_abbreviations.keys(),
                key=len,
                reverse=True
            )
    
    def apply_selective_abbreviations(
        self,
        text: str,
        abbreviations: List[str],
        probability: float = 1.0
    ) -> str:
        """
        Apply only specific abbreviations to the text.
        
        Args:
            text: Input text
            abbreviations: List of abbreviation patterns to apply
            probability: Probability of applying each abbreviation
            
        Returns:
            Text with applied abbreviations
        """
        if probability <= 0:
            return text
        
        result = text
        
        for abbreviation_pattern in abbreviations:
            if abbreviation_pattern in self.all_abbreviations and random.random() <= probability:
                replacement = self.all_abbreviations[abbreviation_pattern]
                pattern = r'\b' + re.escape(abbreviation_pattern) + r'\b'
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def get_abbreviation_statistics(self, text: str) -> Dict[str, int]:
        """
        Get statistics about abbreviations that could be applied to the text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with abbreviation patterns and their counts in the text
        """
        stats = {}
        text_lower = text.lower()
        
        # Count standard abbreviations
        for pattern in self.all_abbreviations:
            count = len(re.findall(r'\b' + re.escape(pattern) + r'\b', text_lower))
            if count > 0:
                stats[pattern] = count
        
        # Count pattern-based abbreviations
        for pattern_regex in self.ending_patterns:
            matches = re.findall(pattern_regex, text_lower)
            if matches:
                stats[f"words_ending_in_{pattern_regex.split('(')[1].split(')')[0]}"] = len(matches)
        
        return stats
