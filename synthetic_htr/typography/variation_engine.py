"""
Letterform variation engine for authentic medieval handwriting simulation.

This module implements automatic letterform variation inspired by the Cerne font's
approach to simulating natural handwriting variability through contextual alternates
and pseudo-random variation.
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import numpy as np


@dataclass
class LetterVariation:
    """Represents a variation of a letter."""
    base_letter: str
    variant_form: str
    variation_type: str  # 'size', 'shape', 'position', 'style'
    probability: float = 0.5
    context_dependent: bool = False
    context_rules: Optional[Dict[str, any]] = None


class LetterformVariationEngine:
    """
    Engine for applying natural letterform variations to simulate authentic handwriting.
    
    This implements the concept from medieval manuscripts where scribes naturally
    varied letterforms due to writing speed, mood, fatigue, and stylistic preferences.
    """
    
    def __init__(self, medieval_style: str = "carolingian", variation_strength: float = 0.5):
        """
        Initialize the letterform variation engine.
        
        Args:
            medieval_style: Medieval script style
            variation_strength: Overall strength of variations (0.0-1.0)
        """
        self.medieval_style = medieval_style
        self.variation_strength = variation_strength
        self.letter_variations = {}
        self.size_variations = {}
        self.position_variations = {}
        self.style_variations = {}
        
        # Initialize variation rules
        self._init_letter_variations()
        self._init_size_variations()
        self._init_position_variations()
        self._init_style_variations()
    
    def _init_letter_variations(self):
        """Initialize letter shape variations based on medieval scribal practices."""
        
        # Common medieval letter variants
        base_variations = {
            'a': ['a', 'ⱥ', 'ꜽ'],  # Various 'a' forms
            'e': ['e', 'ę', 'ꝫ'],  # Various 'e' forms
            'g': ['g', 'ꝿ', 'ǥ'],  # Insular and continental 'g'
            'r': ['r', 'ꝛ', 'ꞃ'],  # Round 'r' and insular 'r'
            's': ['s', 'ſ', 'ꞅ'],  # Long 's' and variants
            't': ['t', 'ꞇ', 'ţ'],  # Various 't' forms
            'd': ['d', 'ꝺ', 'đ'],  # Insular 'd' and variants
            'f': ['f', 'ꝼ', 'ſ'],  # Various 'f' forms
            'n': ['n', 'ꞥ', 'ɲ'],  # Various 'n' forms
            'm': ['m', 'ɱ', 'ꝳ'],  # Various 'm' forms
            'u': ['u', 'ꝸ', 'ꞷ'],  # Various 'u' forms
            'v': ['v', 'ꝟ', 'ꝩ'],  # Various 'v' forms
            'w': ['w', 'ƿ', 'ꝡ'],  # Wynn and variants
            'y': ['y', 'ẏ', 'ỿ'],  # Various 'y' forms
            'z': ['z', 'ꝣ', 'ʒ'],  # Various 'z' forms
        }
        
        # Style-specific variations
        if self.medieval_style == "gothic":
            # Gothic script has more angular variations
            gothic_additions = {
                'o': ['o', 'ꝍ', 'ø'],
                'i': ['i', 'ı', 'ꝭ'],
                'c': ['c', 'ꞓ', 'ꝯ'],
                'b': ['b', 'ꞗ', 'ƀ'],
                'p': ['p', 'ꝑ', 'ꝓ'],
                'h': ['h', 'ꜧ', 'ħ'],
                'l': ['l', 'ł', 'ꝉ'],
                'k': ['k', 'ꝃ', 'ꝁ'],
            }
            base_variations.update(gothic_additions)
            
        elif self.medieval_style == "uncial":
            # Uncial has distinctive rounded forms
            uncial_additions = {
                'a': ['a', 'ⱥ', 'Ⱥ'],
                'd': ['d', 'ꝺ', 'Ꝺ'],
                'h': ['h', 'ꜧ', 'Ꜧ'],
                'n': ['n', 'ꞥ', 'Ꞥ'],
                'r': ['r', 'ꞃ', 'Ꞃ'],
                'f': ['f', 'ꝼ', 'Ꝼ'],
            }
            base_variations.update(uncial_additions)
        
        # Convert to LetterVariation objects
        for base_letter, variants in base_variations.items():
            self.letter_variations[base_letter] = []
            for variant in variants[1:]:  # Skip the base form
                variation = LetterVariation(
                    base_letter=base_letter,
                    variant_form=variant,
                    variation_type='shape',
                    probability=0.3 + random.random() * 0.4,  # 0.3-0.7
                    context_dependent=True
                )
                self.letter_variations[base_letter].append(variation)
    
    def _init_size_variations(self):
        """Initialize size variation rules."""
        self.size_variations = {
            # Letters that can be slightly larger
            'ascenders': {
                'letters': 'bdfhklt',
                'size_multiplier_range': (1.0, 1.2),
                'probability': 0.3
            },
            
            # Letters that can be slightly smaller
            'minims': {
                'letters': 'imnuv',
                'size_multiplier_range': (0.9, 1.0),
                'probability': 0.2
            },
            
            # Descenders can vary in length
            'descenders': {
                'letters': 'gjpqy',
                'size_multiplier_range': (1.0, 1.3),
                'probability': 0.25
            },
            
            # Wide letters can be compressed
            'wide_letters': {
                'letters': 'mwAMW',
                'size_multiplier_range': (0.8, 1.1),
                'probability': 0.2
            }
        }
    
    def _init_position_variations(self):
        """Initialize position variation rules for natural irregularity."""
        self.position_variations = {
            # Baseline variations (letters sitting slightly high/low)
            'baseline_shift': {
                'max_shift': 2,  # pixels
                'probability': 0.4,
                'affected_letters': 'abcdefghijklmnopqrstuvwxyz'
            },
            
            # Horizontal spacing variations
            'letter_spacing': {
                'spacing_range': (-1, 2),  # pixels
                'probability': 0.3,
                'context_dependent': True
            },
            
            # Slight rotation for natural look
            'rotation': {
                'angle_range': (-2, 2),  # degrees
                'probability': 0.2,
                'affected_letters': 'abcdefghijklmnopqrstuvwxyz'
            },
            
            # Kerning adjustments for specific letter pairs
            'kerning_pairs': {
                'AV': -1, 'AW': -1, 'AY': -1,
                'FA': -1, 'TA': -1, 'VA': -1,
                'WA': -1, 'YA': -1, 'To': -1,
                'Tr': -1, 'Tu': -1, 'Tw': -1,
                'Ty': -1, 'Ya': -1, 'Ye': -1,
                'Yo': -1, 'Yu': -1
            }
        }
    
    def _init_style_variations(self):
        """Initialize stylistic variations for different contexts."""
        self.style_variations = {
            # Formal vs informal variations
            'formality': {
                'formal': {
                    'letter_spacing_multiplier': 1.1,
                    'size_consistency': 0.9,  # More consistent sizing
                    'variation_probability': 0.2  # Less variation
                },
                'informal': {
                    'letter_spacing_multiplier': 0.9,
                    'size_consistency': 0.6,  # Less consistent sizing
                    'variation_probability': 0.6  # More variation
                }
            },
            
            # Speed variations (fast vs careful writing)
            'writing_speed': {
                'careful': {
                    'position_variation': 0.3,
                    'size_variation': 0.2,
                    'shape_variation': 0.3
                },
                'normal': {
                    'position_variation': 0.5,
                    'size_variation': 0.4,
                    'shape_variation': 0.5
                },
                'hasty': {
                    'position_variation': 0.8,
                    'size_variation': 0.7,
                    'shape_variation': 0.7
                }
            },
            
            # Fatigue effects (writing gets more irregular over time)
            'fatigue': {
                'fresh': {
                    'consistency': 0.9,
                    'baseline_drift': 0.1
                },
                'tired': {
                    'consistency': 0.6,
                    'baseline_drift': 0.4
                },
                'exhausted': {
                    'consistency': 0.4,
                    'baseline_drift': 0.7
                }
            }
        }
    
    def apply_letterform_variations(
        self,
        text: str,
        context: str = "normal",
        writing_speed: str = "normal",
        fatigue_level: str = "fresh",
        formality: str = "formal"
    ) -> str:
        """
        Apply letterform variations to text.
        
        Args:
            text: Input text
            context: Writing context
            writing_speed: Speed of writing (careful, normal, hasty)
            fatigue_level: Level of scribe fatigue (fresh, tired, exhausted)
            formality: Level of formality (formal, informal)
            
        Returns:
            Text with letterform variations applied
        """
        if not text:
            return text
        
        # Get style parameters
        speed_params = self.style_variations['writing_speed'].get(writing_speed, 
                                                                self.style_variations['writing_speed']['normal'])
        fatigue_params = self.style_variations['fatigue'].get(fatigue_level,
                                                            self.style_variations['fatigue']['fresh'])
        formal_params = self.style_variations['formality'].get(formality,
                                                             self.style_variations['formality']['formal'])
        
        # Calculate effective variation strength
        effective_strength = (
            self.variation_strength * 
            speed_params['shape_variation'] * 
            (2.0 - fatigue_params['consistency']) *
            formal_params['variation_probability']
        )
        
        result = list(text)
        
        # Apply shape variations
        for i, char in enumerate(result):
            char_lower = char.lower()
            
            # Skip if no variations available
            if char_lower not in self.letter_variations:
                continue
            
            # Check if we should apply variation
            if random.random() > effective_strength:
                continue
            
            # Choose a variation
            variations = self.letter_variations[char_lower]
            if variations:
                chosen_variation = random.choice(variations)
                
                # Apply context-dependent rules if needed
                if chosen_variation.context_dependent:
                    if self._should_apply_contextual_variation(text, i, chosen_variation):
                        result[i] = chosen_variation.variant_form
                else:
                    if random.random() < chosen_variation.probability:
                        result[i] = chosen_variation.variant_form
        
        return ''.join(result)
    
    def _should_apply_contextual_variation(
        self,
        text: str,
        position: int,
        variation: LetterVariation
    ) -> bool:
        """Determine if a contextual variation should be applied."""
        
        # Get surrounding context
        before_char = text[position - 1] if position > 0 else ''
        after_char = text[position + 1] if position < len(text) - 1 else ''
        
        # Apply some basic contextual rules
        base_letter = variation.base_letter
        
        # Don't vary letters at word boundaries as much
        if before_char in ' \t\n' or after_char in ' \t\n':
            return random.random() < variation.probability * 0.5
        
        # Vary doubled letters more often (like Cerne)
        if before_char.lower() == base_letter or after_char.lower() == base_letter:
            return random.random() < variation.probability * 1.5
        
        # Some letters vary more in certain contexts
        if base_letter == 's':
            # Long s more likely before vowels
            if after_char.lower() in 'aeiou':
                return random.random() < variation.probability * 1.3
        
        if base_letter == 'r':
            # Insular r more likely after certain letters
            if before_char.lower() in 'eo':
                return random.random() < variation.probability * 1.2
        
        return random.random() < variation.probability
    
    def generate_position_variations(
        self,
        text: str,
        font_size: int,
        writing_speed: str = "normal",
        fatigue_level: str = "fresh"
    ) -> List[Tuple[int, int, float]]:
        """
        Generate position variations for each character.
        
        Args:
            text: Input text
            font_size: Base font size
            writing_speed: Speed of writing
            fatigue_level: Level of fatigue
            
        Returns:
            List of (x_offset, y_offset, rotation) tuples for each character
        """
        speed_params = self.style_variations['writing_speed'].get(writing_speed,
                                                                self.style_variations['writing_speed']['normal'])
        fatigue_params = self.style_variations['fatigue'].get(fatigue_level,
                                                            self.style_variations['fatigue']['fresh'])
        
        variations = []
        baseline_drift = 0  # Cumulative baseline drift
        
        for i, char in enumerate(text):
            x_offset = 0
            y_offset = 0
            rotation = 0
            
            # Apply baseline variations
            if random.random() < self.position_variations['baseline_shift']['probability']:
                max_shift = self.position_variations['baseline_shift']['max_shift']
                y_offset = random.randint(-max_shift, max_shift)
            
            # Apply fatigue-based baseline drift
            if fatigue_level != 'fresh':
                drift_amount = fatigue_params['baseline_drift'] * font_size * 0.1
                baseline_drift += random.uniform(-drift_amount, drift_amount)
                y_offset += int(baseline_drift)
            
            # Apply letter spacing variations
            if i > 0 and random.random() < self.position_variations['letter_spacing']['probability']:
                spacing_range = self.position_variations['letter_spacing']['spacing_range']
                x_offset = random.randint(spacing_range[0], spacing_range[1])
            
            # Apply rotation variations
            if (char.lower() in self.position_variations['rotation']['affected_letters'] and
                random.random() < self.position_variations['rotation']['probability']):
                angle_range = self.position_variations['rotation']['angle_range']
                rotation = random.uniform(angle_range[0], angle_range[1])
            
            # Apply speed-based position variations
            position_var = speed_params['position_variation']
            x_offset += int(random.uniform(-position_var, position_var))
            y_offset += int(random.uniform(-position_var, position_var))
            
            variations.append((x_offset, y_offset, rotation))
        
        return variations
    
    def generate_size_variations(
        self,
        text: str,
        base_font_size: int,
        writing_speed: str = "normal",
        formality: str = "formal"
    ) -> List[int]:
        """
        Generate size variations for each character.
        
        Args:
            text: Input text
            base_font_size: Base font size
            writing_speed: Speed of writing
            formality: Level of formality
            
        Returns:
            List of font sizes for each character
        """
        speed_params = self.style_variations['writing_speed'].get(writing_speed,
                                                                self.style_variations['writing_speed']['normal'])
        formal_params = self.style_variations['formality'].get(formality,
                                                             self.style_variations['formality']['formal'])
        
        size_variations = []
        
        for char in text:
            char_size = base_font_size
            char_lower = char.lower()
            
            # Apply category-based size variations
            for category, rules in self.size_variations.items():
                if char_lower in rules['letters']:
                    if random.random() < rules['probability']:
                        min_mult, max_mult = rules['size_multiplier_range']
                        multiplier = random.uniform(min_mult, max_mult)
                        char_size = int(base_font_size * multiplier)
                        break
            
            # Apply speed and formality adjustments
            size_consistency = formal_params['size_consistency']
            size_variation = speed_params['size_variation']
            
            # Add random variation based on consistency
            if random.random() > size_consistency:
                variation_amount = size_variation * base_font_size * 0.1
                size_adjustment = random.uniform(-variation_amount, variation_amount)
                char_size = max(int(char_size + size_adjustment), base_font_size // 2)
            
            size_variations.append(char_size)
        
        return size_variations
    
    def create_natural_text_layout(
        self,
        text: str,
        base_font_size: int = 24,
        line_width: int = 600,
        context: str = "normal",
        writing_speed: str = "normal",
        fatigue_level: str = "fresh",
        formality: str = "formal"
    ) -> Dict[str, any]:
        """
        Create a natural text layout with all variations applied.
        
        Args:
            text: Input text
            base_font_size: Base font size
            line_width: Maximum line width
            context: Writing context
            writing_speed: Speed of writing
            fatigue_level: Level of fatigue
            formality: Level of formality
            
        Returns:
            Dictionary with layout information
        """
        # Apply letterform variations
        varied_text = self.apply_letterform_variations(
            text, context, writing_speed, fatigue_level, formality
        )
        
        # Generate position and size variations
        position_vars = self.generate_position_variations(
            varied_text, base_font_size, writing_speed, fatigue_level
        )
        size_vars = self.generate_size_variations(
            varied_text, base_font_size, writing_speed, formality
        )
        
        # Break text into lines (simplified)
        words = varied_text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_width = len(word) * base_font_size * 0.6  # Rough estimate
            if current_width + word_width > line_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width + base_font_size * 0.3  # Space width
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return {
            'original_text': text,
            'varied_text': varied_text,
            'lines': lines,
            'position_variations': position_vars,
            'size_variations': size_vars,
            'parameters': {
                'context': context,
                'writing_speed': writing_speed,
                'fatigue_level': fatigue_level,
                'formality': formality
            }
        }
    
    def set_variation_strength(self, strength: float):
        """Set the overall variation strength (0.0-1.0)."""
        self.variation_strength = max(0.0, min(1.0, strength))
    
    def add_custom_variation(
        self,
        base_letter: str,
        variant_form: str,
        variation_type: str = 'shape',
        probability: float = 0.5,
        context_dependent: bool = False
    ):
        """Add a custom letter variation."""
        if base_letter not in self.letter_variations:
            self.letter_variations[base_letter] = []
        
        variation = LetterVariation(
            base_letter=base_letter,
            variant_form=variant_form,
            variation_type=variation_type,
            probability=probability,
            context_dependent=context_dependent
        )
        
        self.letter_variations[base_letter].append(variation)
    
    def get_variation_statistics(self, text: str) -> Dict[str, any]:
        """Get statistics about potential variations in text."""
        stats = {
            'total_characters': len(text),
            'letters_with_variations': 0,
            'doubled_letters': 0,
            'potential_variations': 0,
            'variation_opportunities': {}
        }
        
        for i, char in enumerate(text):
            char_lower = char.lower()
            
            if char_lower in self.letter_variations:
                stats['letters_with_variations'] += 1
                stats['potential_variations'] += len(self.letter_variations[char_lower])
                
                if char_lower not in stats['variation_opportunities']:
                    stats['variation_opportunities'][char_lower] = 0
                stats['variation_opportunities'][char_lower] += 1
            
            # Count doubled letters
            if i > 0 and text[i-1].lower() == char_lower and char.isalpha():
                stats['doubled_letters'] += 1
        
        return stats
