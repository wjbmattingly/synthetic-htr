"""
Contextual alternates engine for sophisticated medieval typography.

This module implements the contextual substitution system inspired by the Cerne font,
where letters are dynamically modified based on their context to create authentic
cursive connections and medieval scribal variations.
"""

import re
import random
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class SubstitutionRule:
    """Represents a contextual substitution rule."""
    pattern: str  # Regex pattern to match
    replacement: str  # Replacement text
    context_before: Optional[str] = None  # Required context before
    context_after: Optional[str] = None   # Required context after
    probability: float = 1.0  # Probability of applying rule
    priority: int = 0  # Higher priority rules are applied first


class ContextualAlternatesEngine:
    """
    Engine for applying contextual alternates and sophisticated ligatures.
    
    This implements the core concept from the Cerne font: instead of pre-designed
    ligatures, we use rules to dynamically modify letterforms based on context.
    """
    
    def __init__(self, medieval_style: str = "carolingian"):
        """
        Initialize the contextual alternates engine.
        
        Args:
            medieval_style: Medieval script style (carolingian, gothic, uncial)
        """
        self.medieval_style = medieval_style
        self.substitution_rules = []
        self.doubled_letter_alternates = {}
        self.contextual_forms = {}
        
        # Initialize rules based on medieval style
        self._init_substitution_rules()
        self._init_doubled_letter_alternates()
        self._init_contextual_forms()
    
    def _init_substitution_rules(self):
        """Initialize contextual substitution rules based on medieval scribal practices."""
        
        # Common medieval ligatures and contextual forms
        base_rules = [
            # Standard medieval ligatures
            SubstitutionRule("st", "ſt", probability=0.8, priority=10),
            SubstitutionRule("ct", "ct", probability=0.7, priority=9),
            SubstitutionRule("ff", "ﬀ", probability=0.9, priority=8),
            SubstitutionRule("fi", "ﬁ", probability=0.8, priority=8),
            SubstitutionRule("fl", "ﬂ", probability=0.8, priority=8),
            
            # Contextual t forms (inspired by Cerne's t variations)
            SubstitutionRule("t", "ꞇ", context_before="i", probability=0.6, priority=7),
            SubstitutionRule("t", "ţ", context_after="e", probability=0.5, priority=7),
            SubstitutionRule("tt", "ꞇt", probability=0.7, priority=8),
            
            # Contextual s forms
            SubstitutionRule("s", "ſ", context_after="[aeiou]", probability=0.7, priority=6),
            SubstitutionRule("ss", "ſs", probability=0.8, priority=8),
            
            # Contextual r forms (insular r)
            SubstitutionRule("r", "ꝛ", context_after="[aeiou]", probability=0.6, priority=6),
            SubstitutionRule("er", "eꝛ", probability=0.7, priority=7),
            
            # Medieval abbreviation marks
            SubstitutionRule("que", "q̄", probability=0.8, priority=9),
            SubstitutionRule("per", "p̄", probability=0.7, priority=9),
            SubstitutionRule("pro", "p̄o", probability=0.7, priority=9),
            SubstitutionRule("con", "cō", probability=0.6, priority=9),
            SubstitutionRule("com", "cō", probability=0.6, priority=9),
            
            # Word-final forms
            SubstitutionRule("s", "ſ", context_after="\\b", probability=0.5, priority=5),
            SubstitutionRule("m", "ɱ", context_after="\\b", probability=0.4, priority=5),
        ]
        
        # Style-specific rules
        if self.medieval_style == "gothic":
            gothic_rules = [
                # Gothic-specific forms
                SubstitutionRule("o", "ꝍ", context_before="[bcdfghjklmnpqrstvwxyz]", probability=0.3, priority=4),
                SubstitutionRule("a", "ꜽ", context_after="[mn]", probability=0.4, priority=5),
                SubstitutionRule("d", "ꝺ", probability=0.3, priority=4),
                
                # Gothic ligatures
                SubstitutionRule("ch", "ꝭ", probability=0.6, priority=8),
                SubstitutionRule("ck", "ꝃ", probability=0.5, priority=8),
            ]
            base_rules.extend(gothic_rules)
            
        elif self.medieval_style == "uncial":
            uncial_rules = [
                # Uncial-specific forms
                SubstitutionRule("a", "ⱥ", probability=0.2, priority=4),
                SubstitutionRule("d", "ꝺ", probability=0.4, priority=4),
                SubstitutionRule("h", "ꜧ", probability=0.3, priority=4),
                SubstitutionRule("n", "ꞥ", probability=0.2, priority=4),
            ]
            base_rules.extend(uncial_rules)
        
        # Sort rules by priority (higher first)
        self.substitution_rules = sorted(base_rules, key=lambda r: r.priority, reverse=True)
    
    def _init_doubled_letter_alternates(self):
        """
        Initialize alternates for doubled letters.
        
        This implements the Cerne concept where doubled letters automatically
        get different forms to simulate natural handwriting variation.
        """
        self.doubled_letter_alternates = {
            'a': ['a', 'ⱥ', 'ꜽ'],
            'e': ['e', 'ę', 'ꝫ'],
            'i': ['i', 'ı', 'ꝭ'],
            'o': ['o', 'ꝍ', 'ø'],
            'u': ['u', 'ꝸ', 'ꞷ'],
            's': ['s', 'ſ', 'ꞅ'],
            't': ['t', 'ꞇ', 'ţ'],
            'r': ['r', 'ꝛ', 'ꞃ'],
            'n': ['n', 'ꞥ', 'ɲ'],
            'm': ['m', 'ɱ', 'ꝳ'],
            'l': ['l', 'ł', 'ꝉ'],
            'c': ['c', 'ꞓ', 'ꝯ'],
            'd': ['d', 'ꝺ', 'đ'],
            'f': ['f', 'ꝼ', 'ſ'],
            'g': ['g', 'ꝿ', 'ǥ'],
            'p': ['p', 'ꝑ', 'ꝓ'],
            'b': ['b', 'ꞗ', 'ƀ'],
        }
    
    def _init_contextual_forms(self):
        """Initialize contextual letterforms based on surrounding characters."""
        self.contextual_forms = {
            # Forms when preceded by specific letters
            'preceded_by': {
                'i': {
                    't': 'ꞇ',  # t after i
                    'n': 'ɲ',  # n after i
                },
                'o': {
                    'r': 'ꝛ',  # r after o
                },
                'e': {
                    'r': 'ꝛ',  # r after e
                },
            },
            
            # Forms when followed by specific letters
            'followed_by': {
                'e': {
                    't': 'ţ',  # t before e
                    'r': 'ꝛ',  # r before e
                },
                'a': {
                    'r': 'ꝛ',  # r before a
                },
                'i': {
                    's': 'ſ',  # s before i
                },
                'o': {
                    's': 'ſ',  # s before o
                },
            },
            
            # Word-initial forms
            'word_initial': {
                's': 'ſ',
                'f': 'ꝼ',
                'r': 'ꞃ',
            },
            
            # Word-final forms
            'word_final': {
                's': 'ſ',
                'm': 'ɱ',
                'n': 'ꞥ',
                'd': 'ꝺ',
            }
        }
    
    def apply_contextual_alternates(
        self,
        text: str,
        enable_ligatures: bool = True,
        enable_doubled_alternates: bool = True,
        enable_contextual_forms: bool = True,
        variation_strength: float = 0.7
    ) -> str:
        """
        Apply contextual alternates to text.
        
        Args:
            text: Input text
            enable_ligatures: Whether to apply ligature substitutions
            enable_doubled_alternates: Whether to vary doubled letters
            enable_contextual_forms: Whether to apply contextual forms
            variation_strength: Strength of variation (0.0-1.0)
            
        Returns:
            Text with contextual alternates applied
        """
        if not text:
            return text
        
        result = text
        
        # Apply ligatures and substitution rules
        if enable_ligatures:
            result = self._apply_substitution_rules(result, variation_strength)
        
        # Apply doubled letter alternates
        if enable_doubled_alternates:
            result = self._apply_doubled_alternates(result, variation_strength)
        
        # Apply contextual forms
        if enable_contextual_forms:
            result = self._apply_contextual_forms(result, variation_strength)
        
        return result
    
    def _apply_substitution_rules(self, text: str, strength: float) -> str:
        """Apply substitution rules in priority order."""
        result = text
        
        for rule in self.substitution_rules:
            # Check if we should apply this rule based on probability and strength
            if random.random() > rule.probability * strength:
                continue
            
            # Build the full pattern with context
            pattern = rule.pattern
            if rule.context_before:
                pattern = f"(?<={rule.context_before}){pattern}"
            if rule.context_after:
                pattern = f"{pattern}(?={rule.context_after})"
            
            try:
                result = re.sub(pattern, rule.replacement, result)
            except re.error:
                # Skip invalid regex patterns
                continue
        
        return result
    
    def _apply_doubled_alternates(self, text: str, strength: float) -> str:
        """Apply alternates for doubled letters."""
        result = list(text)
        
        i = 0
        while i < len(result) - 1:
            current_char = result[i].lower()
            next_char = result[i + 1].lower()
            
            # Check for doubled letters
            if (current_char == next_char and 
                current_char in self.doubled_letter_alternates and
                random.random() < strength):
                
                alternates = self.doubled_letter_alternates[current_char]
                
                # Choose different alternates for the two instances
                if len(alternates) >= 2:
                    # Keep first letter as is, change second
                    if random.random() < 0.7:  # 70% chance to vary
                        alt_choices = [alt for alt in alternates if alt != current_char]
                        if alt_choices:
                            result[i + 1] = random.choice(alt_choices)
            
            i += 1
        
        return ''.join(result)
    
    def _apply_contextual_forms(self, text: str, strength: float) -> str:
        """Apply contextual letterforms based on surrounding characters."""
        result = list(text)
        words = text.split()
        
        for word_idx, word in enumerate(words):
            word_start = text.find(word, sum(len(w) + 1 for w in words[:word_idx]))
            
            for i, char in enumerate(word):
                char_pos = word_start + i
                if char_pos >= len(result):
                    continue
                
                char_lower = char.lower()
                
                # Skip if random check fails
                if random.random() > strength:
                    continue
                
                # Check word-initial forms
                if i == 0 and char_lower in self.contextual_forms['word_initial']:
                    if random.random() < 0.5:  # 50% chance for word-initial forms
                        result[char_pos] = self.contextual_forms['word_initial'][char_lower]
                        continue
                
                # Check word-final forms
                if i == len(word) - 1 and char_lower in self.contextual_forms['word_final']:
                    if random.random() < 0.4:  # 40% chance for word-final forms
                        result[char_pos] = self.contextual_forms['word_final'][char_lower]
                        continue
                
                # Check preceded-by forms
                if i > 0:
                    prev_char = word[i - 1].lower()
                    if (prev_char in self.contextual_forms['preceded_by'] and
                        char_lower in self.contextual_forms['preceded_by'][prev_char]):
                        if random.random() < 0.6:  # 60% chance for contextual forms
                            result[char_pos] = self.contextual_forms['preceded_by'][prev_char][char_lower]
                            continue
                
                # Check followed-by forms
                if i < len(word) - 1:
                    next_char = word[i + 1].lower()
                    if (next_char in self.contextual_forms['followed_by'] and
                        char_lower in self.contextual_forms['followed_by'][next_char]):
                        if random.random() < 0.6:  # 60% chance for contextual forms
                            result[char_pos] = self.contextual_forms['followed_by'][next_char][char_lower]
        
        return ''.join(result)
    
    def add_substitution_rule(
        self,
        pattern: str,
        replacement: str,
        context_before: Optional[str] = None,
        context_after: Optional[str] = None,
        probability: float = 1.0,
        priority: int = 0
    ):
        """Add a custom substitution rule."""
        rule = SubstitutionRule(
            pattern=pattern,
            replacement=replacement,
            context_before=context_before,
            context_after=context_after,
            probability=probability,
            priority=priority
        )
        
        self.substitution_rules.append(rule)
        # Re-sort by priority
        self.substitution_rules.sort(key=lambda r: r.priority, reverse=True)
    
    def add_doubled_alternate(self, letter: str, alternates: List[str]):
        """Add alternates for a doubled letter."""
        self.doubled_letter_alternates[letter.lower()] = alternates
    
    def get_available_alternates(self, letter: str) -> List[str]:
        """Get available alternates for a letter."""
        return self.doubled_letter_alternates.get(letter.lower(), [letter])
    
    def set_medieval_style(self, style: str):
        """Change the medieval style and reinitialize rules."""
        if style in ["carolingian", "gothic", "uncial"]:
            self.medieval_style = style
            self.substitution_rules.clear()
            self._init_substitution_rules()
        else:
            raise ValueError(f"Unknown medieval style: {style}")
    
    def create_variation_sample(
        self,
        text: str,
        num_variations: int = 5
    ) -> List[str]:
        """
        Create multiple variations of the same text to demonstrate alternates.
        
        Args:
            text: Input text
            num_variations: Number of variations to generate
            
        Returns:
            List of text variations
        """
        variations = []
        
        for i in range(num_variations):
            # Use different variation strengths for diversity
            strength = 0.3 + (i * 0.15)  # 0.3 to 0.9
            variation = self.apply_contextual_alternates(
                text,
                variation_strength=min(strength, 1.0)
            )
            variations.append(variation)
        
        return variations
    
    def analyze_text_features(self, text: str) -> Dict[str, int]:
        """
        Analyze text to show what features could be applied.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with counts of applicable features
        """
        features = {
            'doubled_letters': 0,
            'ligature_opportunities': 0,
            'contextual_opportunities': 0,
            'word_boundaries': 0
        }
        
        # Count doubled letters
        for i in range(len(text) - 1):
            if text[i].lower() == text[i + 1].lower() and text[i].isalpha():
                features['doubled_letters'] += 1
        
        # Count ligature opportunities
        for rule in self.substitution_rules:
            if rule.priority >= 7:  # High priority rules are typically ligatures
                matches = len(re.findall(rule.pattern, text, re.IGNORECASE))
                features['ligature_opportunities'] += matches
        
        # Count words (for word-initial/final forms)
        features['word_boundaries'] = len(text.split()) * 2  # Initial + final
        
        # Count contextual opportunities (simplified)
        for letter in 'aeiourtnslm':
            features['contextual_opportunities'] += text.lower().count(letter)
        
        return features
