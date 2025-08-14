"""
Text augmentor for converting modern text to medieval Latin style with ligatures and abbreviations.
"""

import re
import random
from typing import Dict, List, Optional, Tuple
from .ligature_rules import LigatureRules
from .abbreviation_rules import AbbreviationRules
from .complex_abbreviation_rules import ComplexAbbreviationRules


class TextAugmentor:
    """
    Converts modern text to medieval Latin style with authentic ligatures, 
    abbreviations, and historical writing conventions.
    """
    
    def __init__(
        self,
        ligature_probability: float = 0.7,
        abbreviation_probability: float = 0.5,
        medieval_style: str = "carolingian",
        random_seed: Optional[int] = None
    ):
        """
        Initialize the text augmentor.
        
        Args:
            ligature_probability: Probability of applying ligatures (0.0-1.0)
            abbreviation_probability: Probability of applying abbreviations (0.0-1.0)
            medieval_style: Style of medieval script ("carolingian", "gothic", "uncial")
            random_seed: Random seed for reproducible results
        """
        if random_seed is not None:
            random.seed(random_seed)
            
        self.ligature_probability = ligature_probability
        self.abbreviation_probability = abbreviation_probability
        self.medieval_style = medieval_style
        
        # Initialize rule engines
        self.ligature_rules = LigatureRules(medieval_style)
        self.abbreviation_rules = AbbreviationRules(medieval_style)
        self.complex_abbreviation_rules = ComplexAbbreviationRules(medieval_style)
        
        # Common medieval word replacements
        self.medieval_replacements = {
            "et": "&",
            "est": "est",
            "que": "q̄",
            "pro": "p̄",
            "per": "p̄",
            "con": "c̄",
            "com": "c̄",
            "cum": "c̄",
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
        }
        
        # Medieval punctuation and symbols
        self.medieval_symbols = {
            "christ": "☧",  # Chi-Rho symbol
            "jesus": "ihs",  # IHS abbreviation
            "maria": "ma",   # MA abbreviation
        }
    
    def augment_text(
        self,
        text: str,
        add_ligatures: bool = True,
        add_abbreviations: bool = True,
        add_complex_abbreviations: bool = True,
        add_decorations: bool = False,
        preserve_case: bool = False,
        context: Optional[str] = None
    ) -> str:
        """
        Convert modern text to medieval Latin style.
        
        Args:
            text: Input text to convert
            add_ligatures: Whether to apply ligatures
            add_abbreviations: Whether to apply basic abbreviations
            add_complex_abbreviations: Whether to apply complex contextual abbreviations
            add_decorations: Whether to add decorative elements
            preserve_case: Whether to preserve original case
            context: Text context for contextual abbreviations ("religious", "legal", "academic")
            
        Returns:
            Medieval-style text with ligatures and abbreviations
        """
        if not text:
            return text
            
        # Convert to lowercase for processing (unless preserving case)
        if not preserve_case:
            text = text.lower()
        
        # Apply medieval word replacements
        text = self._apply_medieval_replacements(text)
        
        # Apply ligatures
        if add_ligatures:
            text = self._apply_ligatures(text)
        
        # Apply abbreviations
        if add_abbreviations:
            text = self._apply_abbreviations(text)
        
        # Apply complex abbreviations
        if add_complex_abbreviations:
            text = self._apply_complex_abbreviations(text, context)
        
        # Add decorative elements
        if add_decorations:
            text = self._add_decorations(text)
        
        # Clean up and format
        text = self._cleanup_text(text)
        
        return text
    
    def _apply_medieval_replacements(self, text: str) -> str:
        """Apply common medieval word replacements."""
        for modern, medieval in self.medieval_replacements.items():
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(modern) + r'\b'
            text = re.sub(pattern, medieval, text, flags=re.IGNORECASE)
        
        # Apply medieval symbols
        for word, symbol in self.medieval_symbols.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            text = re.sub(pattern, symbol, text, flags=re.IGNORECASE)
        
        return text
    
    def _apply_ligatures(self, text: str) -> str:
        """Apply ligature rules to the text."""
        return self.ligature_rules.apply(text, self.ligature_probability)
    
    def _apply_abbreviations(self, text: str) -> str:
        """Apply abbreviation rules to the text."""
        return self.abbreviation_rules.apply(text, self.abbreviation_probability)
    
    def _apply_complex_abbreviations(self, text: str, context: Optional[str] = None) -> str:
        """Apply complex abbreviation rules to the text."""
        return self.complex_abbreviation_rules.apply_complex_abbreviations(
            text, self.abbreviation_probability, context
        )
    
    def _add_decorations(self, text: str) -> str:
        """Add decorative elements to the text."""
        # Add decorative initials for sentences
        sentences = re.split(r'([.!?]+)', text)
        decorated_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i % 2 == 0 and sentence.strip():  # This is a sentence (not punctuation)
                # Add decorative initial for sentences starting with letters
                if sentence and sentence[0].isalpha():
                    decorated_sentences.append(f"❦{sentence}")
                else:
                    decorated_sentences.append(sentence)
            else:
                decorated_sentences.append(sentence)
        
        return ''.join(decorated_sentences)
    
    def _cleanup_text(self, text: str) -> str:
        """Clean up and format the final text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper spacing around medieval symbols
        text = re.sub(r'([&̄])', r' \1 ', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing spaces
        text = text.strip()
        
        return text
    
    def get_medieval_vocabulary(self) -> Dict[str, str]:
        """Get the current medieval vocabulary mappings."""
        return self.medieval_replacements.copy()
    
    def add_medieval_replacement(self, modern: str, medieval: str):
        """Add a custom medieval replacement rule."""
        self.medieval_replacements[modern] = medieval
    
    def set_style(self, style: str):
        """Change the medieval script style."""
        if style in ["carolingian", "gothic", "uncial"]:
            self.medieval_style = style
            self.ligature_rules.set_style(style)
            self.abbreviation_rules.set_style(style)
        else:
            raise ValueError(f"Unknown style: {style}. Available styles: carolingian, gothic, uncial")
    
    def batch_augment(
        self,
        texts: List[str],
        **kwargs
    ) -> List[str]:
        """Apply augmentation to a batch of texts."""
        return [self.augment_text(text, **kwargs) for text in texts]
