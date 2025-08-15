"""
Text augmentor for converting modern text to medieval Latin style with ligatures and abbreviations.
Enhanced with advanced typography features inspired by the Cerne font project.
"""

import re
import random
from typing import Dict, List, Optional, Tuple
from .ligature_rules import LigatureRules
from .abbreviation_rules import AbbreviationRules
from .complex_abbreviation_rules import ComplexAbbreviationRules

# Import new advanced typography modules
try:
    from ..typography import ContextualAlternatesEngine, LetterformVariationEngine
    ADVANCED_TYPOGRAPHY_AVAILABLE = True
except ImportError:
    ADVANCED_TYPOGRAPHY_AVAILABLE = False
    print("Advanced typography features not available. Install typography module for enhanced features.")


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
        random_seed: Optional[int] = None,
        use_advanced_typography: bool = True,
        variation_strength: float = 0.5
    ):
        """
        Initialize the text augmentor.
        
        Args:
            ligature_probability: Probability of applying ligatures (0.0-1.0)
            abbreviation_probability: Probability of applying abbreviations (0.0-1.0)
            medieval_style: Style of medieval script ("carolingian", "gothic", "uncial")
            random_seed: Random seed for reproducible results
            use_advanced_typography: Whether to use advanced typography features
            variation_strength: Strength of letterform variations (0.0-1.0)
        """
        if random_seed is not None:
            random.seed(random_seed)
            
        self.ligature_probability = ligature_probability
        self.abbreviation_probability = abbreviation_probability
        self.medieval_style = medieval_style
        self.use_advanced_typography = use_advanced_typography and ADVANCED_TYPOGRAPHY_AVAILABLE
        self.variation_strength = variation_strength
        
        # Initialize rule engines
        self.ligature_rules = LigatureRules(medieval_style)
        self.abbreviation_rules = AbbreviationRules(medieval_style)
        self.complex_abbreviation_rules = ComplexAbbreviationRules(medieval_style)
        
        # Initialize advanced typography engines if available
        if self.use_advanced_typography:
            self.contextual_engine = ContextualAlternatesEngine(medieval_style)
            self.variation_engine = LetterformVariationEngine(medieval_style, variation_strength)
        else:
            self.contextual_engine = None
            self.variation_engine = None
        
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
        context: Optional[str] = None,
        use_contextual_alternates: bool = True,
        use_letterform_variations: bool = True,
        writing_speed: str = "normal",
        formality: str = "formal",
        fatigue_level: str = "fresh"
    ) -> str:
        """
        Convert modern text to medieval Latin style with advanced typography.
        
        Args:
            text: Input text to convert
            add_ligatures: Whether to apply ligatures
            add_abbreviations: Whether to apply basic abbreviations
            add_complex_abbreviations: Whether to apply complex contextual abbreviations
            add_decorations: Whether to add decorative elements
            preserve_case: Whether to preserve original case
            context: Text context for contextual abbreviations ("religious", "legal", "academic")
            use_contextual_alternates: Whether to apply contextual alternates (Cerne-style)
            use_letterform_variations: Whether to apply letterform variations
            writing_speed: Speed of writing ("careful", "normal", "hasty")
            formality: Level of formality ("formal", "informal")
            fatigue_level: Scribe fatigue level ("fresh", "tired", "exhausted")
            
        Returns:
            Medieval-style text with advanced typography features
        """
        if not text:
            return text
            
        # Convert to lowercase for processing (unless preserving case)
        if not preserve_case:
            text = text.lower()
        
        # Apply medieval word replacements
        text = self._apply_medieval_replacements(text)
        
        # Apply traditional ligatures and abbreviations first
        if add_ligatures:
            text = self._apply_ligatures(text)
        
        if add_abbreviations:
            text = self._apply_abbreviations(text)
        
        if add_complex_abbreviations:
            text = self._apply_complex_abbreviations(text, context)
        
        # Apply advanced typography features if available
        if self.use_advanced_typography:
            # Apply contextual alternates (Cerne-style sophisticated ligatures)
            if use_contextual_alternates and self.contextual_engine:
                text = self.contextual_engine.apply_contextual_alternates(
                    text,
                    enable_ligatures=True,
                    enable_doubled_alternates=True,
                    enable_contextual_forms=True,
                    variation_strength=self.variation_strength
                )
            
            # Apply letterform variations for natural handwriting look
            if use_letterform_variations and self.variation_engine:
                text = self.variation_engine.apply_letterform_variations(
                    text,
                    context=context or "normal",
                    writing_speed=writing_speed,
                    fatigue_level=fatigue_level,
                    formality=formality
                )
        
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
    
    def create_text_variations(
        self,
        text: str,
        num_variations: int = 5,
        **kwargs
    ) -> List[str]:
        """
        Create multiple variations of the same text for diversity.
        
        Args:
            text: Input text
            num_variations: Number of variations to create
            **kwargs: Arguments passed to augment_text
            
        Returns:
            List of text variations
        """
        if not self.use_advanced_typography or not self.contextual_engine:
            # Fallback to basic variations
            return [self.augment_text(text, **kwargs) for _ in range(num_variations)]
        
        # Use advanced typography to create sophisticated variations
        return self.contextual_engine.create_variation_sample(text, num_variations)
    
    def get_typography_analysis(self, text: str) -> Dict[str, any]:
        """
        Analyze text for typography features.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'basic_features': {
                'character_count': len(text),
                'word_count': len(text.split()),
                'medieval_replacements': 0,
                'ligature_opportunities': 0
            }
        }
        
        # Count medieval replacement opportunities
        for modern_word in self.medieval_replacements.keys():
            analysis['basic_features']['medieval_replacements'] += text.lower().count(modern_word)
        
        # Add advanced analysis if available
        if self.use_advanced_typography:
            if self.contextual_engine:
                analysis['contextual_features'] = self.contextual_engine.analyze_text_features(text)
            
            if self.variation_engine:
                analysis['variation_features'] = self.variation_engine.get_variation_statistics(text)
        
        return analysis
    
    def get_layout_information(
        self,
        text: str,
        font_size: int = 24,
        line_width: int = 600,
        **typography_kwargs
    ) -> Dict[str, any]:
        """
        Get natural text layout information with variations.
        
        Args:
            text: Input text
            font_size: Base font size
            line_width: Maximum line width
            **typography_kwargs: Typography parameters
            
        Returns:
            Dictionary with layout information
        """
        if not self.use_advanced_typography or not self.variation_engine:
            # Basic layout fallback
            return {
                'original_text': text,
                'augmented_text': self.augment_text(text, **typography_kwargs),
                'lines': text.split('\n'),
                'advanced_features_available': False
            }
        
        # Get advanced layout with variations
        return self.variation_engine.create_natural_text_layout(
            text,
            base_font_size=font_size,
            line_width=line_width,
            context=typography_kwargs.get('context', 'normal'),
            writing_speed=typography_kwargs.get('writing_speed', 'normal'),
            fatigue_level=typography_kwargs.get('fatigue_level', 'fresh'),
            formality=typography_kwargs.get('formality', 'formal')
        )
    
    def set_variation_strength(self, strength: float):
        """Set the variation strength for advanced typography."""
        self.variation_strength = max(0.0, min(1.0, strength))
        if self.variation_engine:
            self.variation_engine.set_variation_strength(strength)
    
    def is_advanced_typography_available(self) -> bool:
        """Check if advanced typography features are available."""
        return self.use_advanced_typography
