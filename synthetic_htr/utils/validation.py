"""
Text validation utilities for medieval text processing.
"""

import re
from typing import List, Dict, Tuple, Optional


class TextValidator:
    """
    Validates and sanitizes text input for medieval manuscript generation.
    """
    
    def __init__(self):
        """Initialize the text validator."""
        # Common Latin characters and medieval symbols
        self.latin_chars = set(
            'abcdefghijklmnopqrstuvwxyz'
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'
            'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸ'
        )
        
        # Medieval symbols and ligatures
        self.medieval_symbols = set(
            'æœﬀﬁﬂftllttss'
            '&̄⁊ꝛꝝꝟꝡꝣꝤꝥꝦꝧꝨꝩꝪꝫꝬꝭ'
            '☧❦✝°'
        )
        
        # Punctuation and whitespace
        self.punctuation = set('.,;:!?\'"()[]{}')
        self.whitespace = set(' \t\n\r')
        
        # All valid characters
        self.valid_chars = (
            self.latin_chars | 
            self.medieval_symbols | 
            self.punctuation | 
            self.whitespace
        )
    
    def validate_text(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate text for medieval manuscript generation.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not text:
            errors.append("Text cannot be empty")
            return False, errors
        
        if len(text.strip()) == 0:
            errors.append("Text contains only whitespace")
            return False, errors
        
        # Check for invalid characters
        invalid_chars = []
        for char in text:
            if char not in self.valid_chars:
                invalid_chars.append(char)
        
        if invalid_chars:
            unique_invalid = list(set(invalid_chars))
            errors.append(f"Invalid characters found: {unique_invalid}")
        
        # Check text length
        if len(text) > 10000:
            errors.append("Text is too long (maximum 10,000 characters)")
        
        # Check for excessive whitespace
        if re.search(r'\s{5,}', text):
            errors.append("Excessive whitespace detected")
        
        # Check for mixed scripts (basic check)
        if self._has_mixed_scripts(text):
            errors.append("Mixed writing systems detected")
        
        return len(errors) == 0, errors
    
    def _has_mixed_scripts(self, text: str) -> bool:
        """Check if text contains mixed writing systems."""
        # Basic check for non-Latin characters
        non_latin = re.findall(r'[^\u0000-\u007F\u00C0-\u017F]', text)
        
        # Filter out medieval symbols we know about
        known_medieval = re.findall(r'[æœﬀﬁﬂ&̄⁊ꝛꝝꝟꝡꝣꝤꝥꝦꝧꝨꝩꝪꝫꝬꝭ☧❦✝°]', text)
        
        # If there are non-Latin characters that aren't known medieval symbols
        return len(non_latin) > len(known_medieval)
    
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text by removing or replacing invalid characters.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return text
        
        # Replace invalid characters with spaces
        sanitized = ''
        for char in text:
            if char in self.valid_chars:
                sanitized += char
            else:
                sanitized += ' '
        
        # Clean up multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove leading/trailing whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent processing.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return text
        
        # Convert to lowercase
        normalized = text.lower()
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove leading/trailing whitespace
        normalized = normalized.strip()
        
        # Basic punctuation normalization
        normalized = re.sub(r'[.!?]+', '.', normalized)  # Multiple punctuation to single
        normalized = re.sub(r'[,;:]+', ',', normalized)  # Multiple separators to comma
        
        return normalized
    
    def check_medieval_compatibility(self, text: str) -> Dict[str, any]:
        """
        Check how well the text is suited for medieval manuscript generation.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with compatibility metrics
        """
        if not text:
            return {
                'compatibility_score': 0.0,
                'latin_ratio': 0.0,
                'medieval_symbols': 0,
                'suggestions': ['Text is empty']
            }
        
        # Count character types
        total_chars = len(text)
        latin_chars = sum(1 for c in text if c in self.latin_chars)
        medieval_symbols = sum(1 for c in text if c in self.medieval_symbols)
        
        # Calculate ratios
        latin_ratio = latin_chars / total_chars if total_chars > 0 else 0.0
        
        # Calculate compatibility score (0.0-1.0)
        compatibility_score = latin_ratio * 0.8 + (medieval_symbols / total_chars) * 0.2
        
        # Generate suggestions
        suggestions = []
        
        if latin_ratio < 0.7:
            suggestions.append("Text contains many non-Latin characters")
        
        if medieval_symbols == 0:
            suggestions.append("Consider adding medieval symbols and ligatures")
        
        if len(text) < 50:
            suggestions.append("Text is quite short for a manuscript")
        
        if len(text) > 2000:
            suggestions.append("Text is very long, consider breaking into sections")
        
        return {
            'compatibility_score': compatibility_score,
            'latin_ratio': latin_ratio,
            'medieval_symbols': medieval_symbols,
            'total_characters': total_chars,
            'suggestions': suggestions
        }
    
    def suggest_medieval_improvements(self, text: str) -> List[str]:
        """
        Suggest improvements to make text more medieval-like.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Check for common modern words that could be medievalized
        modern_words = {
            'and': 'et',
            'with': 'cum',
            'for': 'pro',
            'by': 'per',
            'in': 'in',
            'of': 'de',
            'the': 'ille',
            'a': 'unus',
            'an': 'unus',
            'is': 'est',
            'are': 'sunt',
            'was': 'erat',
            'were': 'erant',
            'will': 'volo',
            'would': 'vellem',
            'could': 'possem',
            'should': 'debeo',
            'may': 'possum',
            'might': 'possim'
        }
        
        text_lower = text.lower()
        for modern, medieval in modern_words.items():
            if modern in text_lower:
                suggestions.append(f"Consider replacing '{modern}' with '{medieval}'")
        
        # Check for abbreviations
        if 'dominus' in text_lower:
            suggestions.append("Consider using 'd̄s' for 'dominus'")
        if 'deus' in text_lower:
            suggestions.append("Consider using 'd̄s' for 'deus'")
        if 'christus' in text_lower:
            suggestions.append("Consider using 'x̄s' for 'christus'")
        
        # Check for ligatures
        if 'ae' in text_lower:
            suggestions.append("Consider using 'æ' for 'ae'")
        if 'oe' in text_lower:
            suggestions.append("Consider using 'œ' for 'oe'")
        
        return suggestions
    
    def validate_medieval_style(self, text: str, style: str) -> Tuple[bool, List[str]]:
        """
        Validate text for a specific medieval style.
        
        Args:
            text: Text to validate
            style: Medieval style ("carolingian", "gothic", "uncial")
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if style not in ["carolingian", "gothic", "uncial"]:
            errors.append(f"Unknown medieval style: {style}")
            return False, errors
        
        # Style-specific validations
        if style == "carolingian":
            # Carolingian minuscule is more conservative
            if re.search(r'[ꝟꝡꝣꝤꝥꝦꝧꝨꝩꝪꝫꝬꝭ]', text):
                errors.append("Text contains Gothic-style symbols not suitable for Carolingian script")
        
        elif style == "gothic":
            # Gothic allows more abbreviations and symbols
            pass  # Most symbols are allowed
        
        elif style == "uncial":
            # Uncial is more formal and conservative
            if re.search(r'[ꝟꝡꝣꝤꝥꝦꝧꝨꝩꝪꝫꝬꝭ]', text):
                errors.append("Text contains Gothic-style symbols not suitable for Uncial script")
        
        return len(errors) == 0, errors
