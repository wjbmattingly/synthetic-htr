"""
Complex abbreviation rules engine for applying medieval abbreviations with contextual patterns.
"""

import re
import random
from typing import Dict, List, Tuple, Optional, Pattern


class ComplexAbbreviationRules:
    """
    Advanced abbreviation rules that handle contextual patterns, inflections,
    and complex medieval abbreviation conventions.
    """
    
    def __init__(self, style: str = "carolingian"):
        """
        Initialize complex abbreviation rules for a specific medieval style.
        
        Args:
            style: Medieval script style ("carolingian", "gothic", "uncial")
        """
        self.style = style
        self._initialize_complex_rules()
    
    def _initialize_complex_rules(self):
        """Initialize complex abbreviation rules based on the selected style."""
        
        # Religious terms with full declensional patterns
        self.religious_terms = {
            # Dominus (Lord) - complete declension
            "dominus": {"nom": "d̄s", "gen": "d̄i", "dat": "d̄o", "acc": "d̄m", "abl": "d̄o"},
            "domini": {"gen": "d̄i", "nom_pl": "d̄i", "voc": "d̄e"},
            "dominum": {"acc": "d̄m"},
            "domino": {"dat": "d̄o", "abl": "d̄o"},
            "dominorum": {"gen_pl": "d̄orum"},
            "dominis": {"dat_pl": "d̄is", "abl_pl": "d̄is"},
            "dominos": {"acc_pl": "d̄os"},
            
            # Deus (God) - complete declension
            "deus": {"nom": "d̄s", "voc": "d̄s"},
            "dei": {"gen": "d̄i", "nom_pl": "d̄i"},
            "deo": {"dat": "d̄o", "abl": "d̄o"},
            "deum": {"acc": "d̄m"},
            "deorum": {"gen_pl": "d̄orum"},
            "deis": {"dat_pl": "d̄is", "abl_pl": "d̄is"},
            "deos": {"acc_pl": "d̄os"},
            
            # Christus (Christ) - with Chi-Rho symbol
            "christus": {"nom": "☧", "voc": "☧"},
            "christi": {"gen": "☧i", "voc": "☧e"},
            "christo": {"dat": "☧o", "abl": "☧o"},
            "christum": {"acc": "☧m"},
            
            # Jesus - with IHS monogram
            "jesus": {"nom": "ih̄s", "voc": "ih̄s"},
            "iesu": {"voc": "ih̄u", "abl": "ih̄u"},
            "iesum": {"acc": "ih̄m"},
            
            # Sanctus (Saint/Holy) - with gender variations
            "sanctus": {"nom_m": "s̄s", "voc_m": "s̄e"},
            "sancta": {"nom_f": "s̄a", "voc_f": "s̄a"},
            "sanctum": {"nom_n": "s̄m", "acc_m": "s̄m", "acc_n": "s̄m"},
            "sancti": {"gen_m": "s̄i", "nom_pl_m": "s̄i", "voc_pl_m": "s̄i"},
            "sanctae": {"gen_f": "s̄ae", "dat_f": "s̄ae", "nom_pl_f": "s̄ae", "voc_pl_f": "s̄ae"},
            "sancto": {"dat_m": "s̄o", "abl_m": "s̄o", "dat_n": "s̄o", "abl_n": "s̄o"},
            "sanctam": {"acc_f": "s̄am"},
            "sancta": {"abl_f": "s̄a", "nom_pl_n": "s̄a", "acc_pl_n": "s̄a", "voc_pl_n": "s̄a"},
            "sanctorum": {"gen_pl_m": "s̄orum", "gen_pl_n": "s̄orum"},
            "sanctarum": {"gen_pl_f": "s̄arum"},
            "sanctis": {"dat_pl": "s̄is", "abl_pl": "s̄is"},
            "sanctos": {"acc_pl_m": "s̄os"},
            "sanctas": {"acc_pl_f": "s̄as"},
        }
        
        # Contextual abbreviation patterns
        self.contextual_patterns = [
            # Religious contexts
            {
                "pattern": r"\b(in nomine) (domini|dei|patris|filii|spiritus)\b",
                "replacement": r"in nom̄ \2",
                "context": "religious_invocation"
            },
            {
                "pattern": r"\b(anno domini)\s+(\d+)\b",
                "replacement": r"a°d° \2",
                "context": "dating"
            },
            {
                "pattern": r"\b(gloria) (patri) (et) (filio) (et) (spiritui) (sancto)\b",
                "replacement": r"ḡa p̄ri ⁊ f̄lio ⁊ sp̄ui s̄o",
                "context": "doxology"
            },
            {
                "pattern": r"\b(pater noster) (qui) (es) (in) (caelis)\b",
                "replacement": r"p̄r nr̄ q̄ ē in cælis",
                "context": "prayer"
            },
            {
                "pattern": r"\b(ave maria) (gratia) (plena)\b",
                "replacement": r"ave mā grāa plēa",
                "context": "prayer"
            },
            
            # Legal and administrative contexts
            {
                "pattern": r"\b(anno) (domini) (nostri) (iesu) (christi)\b",
                "replacement": r"a° d̄i nr̄i ih̄u ☧i",
                "context": "legal_dating"
            },
            {
                "pattern": r"\b(testamentum) (domini) (nostri)\b",
                "replacement": r"test̄m d̄i nr̄i",
                "context": "legal"
            },
            {
                "pattern": r"\b(privilegium) (apostolicum)\b",
                "replacement": r"privil̄ ap̄licum",
                "context": "ecclesiastical_legal"
            },
            
            # Academic and scholarly contexts
            {
                "pattern": r"\b(quaestio) (prima|secunda|tertia|quarta|quinta)\b",
                "replacement": r"q̄tio \2",
                "context": "scholastic"
            },
            {
                "pattern": r"\b(argumentum) (contra|pro)\b",
                "replacement": r"argum̄ \2",
                "context": "scholastic"
            },
            {
                "pattern": r"\b(sed) (contra)\b",
                "replacement": r"sed c̄tra",
                "context": "scholastic"
            },
            {
                "pattern": r"\b(respondeo) (dicendum) (quod)\b",
                "replacement": r"resp̄ dic̄ q̄d",
                "context": "scholastic"
            },
        ]
        
        # Compound abbreviations (multiple words abbreviated together)
        self.compound_abbreviations = {
            # Religious compounds
            "in nomine patris": "in nom̄ p̄ris",
            "et filii et": "⁊ f̄lii ⁊",
            "spiritus sancti": "sp̄us s̄i",
            "per dominum nostrum": "p̄ d̄m nr̄m",
            "iesum christum": "ih̄m ☧m",
            "filium tuum": "f̄lium tuum",
            "qui tecum vivit": "q̄ tecū vivit",
            "et regnat": "⁊ regnat",
            "in unitate": "in unitāte",
            "eiusdem spiritus": "eiusd̄ sp̄us",
            "per omnia saecula": "p̄ omnia sæcula",
            "saeculorum amen": "sæculorū am̄",
            
            # Calendar and dating
            "kalendas ianuarii": "kal° ian°",
            "idus martii": "id° mart°",
            "nonas aprilis": "non° apr°",
            "anno incarnationis": "a° incarnat̄onis",
            "domini nostri": "d̄i nr̄i",
            "tempore domini": "t̄e d̄i",
            
            # Administrative
            "capitulum generale": "cap̄ gen̄le",
            "prior generalis": "pr̄ gen̄lis",
            "abbas monasterii": "abb̄s mon̄ii",
            "frater ordinis": "fr̄ ord̄inis",
            "ecclesiae sanctae": "eccl̄ae s̄ae",
            "episcopus civitatis": "ep̄s civitātis",
            
            # Legal
            "instrumentum publicum": "instr̄m publ̄",
            "notarius publicus": "not̄ publ̄",
            "testamentum ultimum": "test̄m ult̄",
            "voluntas ultima": "vol̄tas ult̄a",
            "carta donationis": "carta donat̄onis",
            "privilegium confirmationis": "privil̄ confirm̄onis",
        }
        
        # Style-specific advanced patterns
        if self.style == "carolingian":
            self.style_specific_rules = {
                "nomina_sacra": True,  # Use nomina sacra extensively
                "tironian_notes": True,  # Use Tironian notes
                "suspension_marks": True,  # Use suspension marks
                "complex_ligatures": False,  # Limited complex ligatures
            }
        elif self.style == "gothic":
            self.style_specific_rules = {
                "nomina_sacra": True,
                "tironian_notes": False,  # Less common in Gothic
                "suspension_marks": True,
                "complex_ligatures": True,  # More complex abbreviations
                "rotunda_forms": True,  # Use rotunda letter forms
            }
        elif self.style == "uncial":
            self.style_specific_rules = {
                "nomina_sacra": True,
                "tironian_notes": False,  # Not typically used
                "suspension_marks": True,
                "complex_ligatures": False,
                "simple_forms": True,  # Prefer simpler abbreviations
            }
    
    def apply_complex_abbreviations(
        self,
        text: str,
        probability: float = 1.0,
        context: Optional[str] = None
    ) -> str:
        """
        Apply complex abbreviation rules with contextual awareness.
        
        Args:
            text: Input text
            probability: Overall probability of applying abbreviations
            context: Text context ("religious", "legal", "academic", etc.)
            
        Returns:
            Text with applied complex abbreviations
        """
        if probability <= 0:
            return text
        
        result = text
        
        # Apply contextual patterns first
        result = self._apply_contextual_patterns(result, probability, context)
        
        # Apply compound abbreviations
        result = self._apply_compound_abbreviations(result, probability)
        
        # Apply religious term declensions
        result = self._apply_religious_declensions(result, probability)
        
        # Apply style-specific rules
        result = self._apply_style_specific_rules(result, probability)
        
        return result
    
    def _apply_contextual_patterns(
        self,
        text: str,
        probability: float,
        context: Optional[str] = None
    ) -> str:
        """Apply contextual abbreviation patterns."""
        result = text
        
        for pattern_info in self.contextual_patterns:
            # Apply context filtering if specified
            if context and pattern_info["context"] != context:
                continue
            
            if random.random() <= probability:
                pattern = pattern_info["pattern"]
                replacement = pattern_info["replacement"]
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _apply_compound_abbreviations(self, text: str, probability: float) -> str:
        """Apply compound abbreviations (multi-word phrases)."""
        result = text
        
        # Sort by length (longest first) to avoid partial replacements
        sorted_compounds = sorted(
            self.compound_abbreviations.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        for compound, abbreviation in sorted_compounds:
            if random.random() <= probability:
                # Use word boundaries to ensure complete phrase matching
                pattern = r'\b' + re.escape(compound) + r'\b'
                result = re.sub(pattern, abbreviation, result, flags=re.IGNORECASE)
        
        return result
    
    def _apply_religious_declensions(self, text: str, probability: float) -> str:
        """Apply religious term abbreviations with proper declensional forms."""
        result = text
        
        for base_form, declensions in self.religious_terms.items():
            if random.random() <= probability:
                for case_form, abbreviation in declensions.items():
                    # Create pattern that matches word boundaries
                    pattern = r'\b' + re.escape(base_form) + r'\b'
                    result = re.sub(pattern, abbreviation, result, flags=re.IGNORECASE)
        
        return result
    
    def _apply_style_specific_rules(self, text: str, probability: float) -> str:
        """Apply style-specific abbreviation rules."""
        result = text
        rules = self.style_specific_rules
        
        if rules.get("nomina_sacra", False) and random.random() <= probability:
            # Apply nomina sacra (sacred names) with overlines
            nomina_sacra = {
                "deus": "d̄s",
                "dominus": "d̄s", 
                "jesus": "ih̄s",
                "christus": "☧s",
                "spiritus": "sp̄s",
                "filius": "f̄s",
                "pater": "p̄r",
                "mater": "m̄r",
            }
            
            for word, abbreviation in nomina_sacra.items():
                pattern = r'\b' + re.escape(word) + r'\b'
                result = re.sub(pattern, abbreviation, result, flags=re.IGNORECASE)
        
        if rules.get("rotunda_forms", False) and random.random() <= probability:
            # Apply rotunda letter forms (Gothic style)
            rotunda_replacements = {
                "rum": "ꝝ",  # Latin small letter rum rotunda
                "ur": "ꝛ",   # Latin small letter r rotunda
                "us": "ꝰ",   # Modifier letter us
                "est": "ꝑ",  # Latin letter p with stroke (est abbreviation)
            }
            
            for pattern, replacement in rotunda_replacements.items():
                result = re.sub(pattern, replacement, result)
        
        return result
    
    def get_abbreviation_statistics(self, original: str, abbreviated: str) -> Dict[str, int]:
        """
        Get statistics about the abbreviations applied.
        
        Args:
            original: Original text
            abbreviated: Text after abbreviation
            
        Returns:
            Dictionary with abbreviation statistics
        """
        stats = {
            "original_length": len(original),
            "abbreviated_length": len(abbreviated),
            "character_reduction": len(original) - len(abbreviated),
            "reduction_percentage": ((len(original) - len(abbreviated)) / len(original)) * 100 if original else 0,
            "abbreviations_applied": 0,
            "compound_abbreviations": 0,
            "religious_abbreviations": 0,
            "contextual_abbreviations": 0
        }
        
        # Count different types of abbreviations by looking for characteristic marks
        overline_count = abbreviated.count('̄')  # Combining overline
        stats["suspension_marks"] = overline_count
        
        tironian_count = abbreviated.count('⁊')  # Tironian et
        stats["tironian_notes"] = tironian_count
        
        chi_rho_count = abbreviated.count('☧')  # Chi-rho
        stats["chi_rho_symbols"] = chi_rho_count
        
        # Estimate total abbreviations by counting marked abbreviations
        stats["abbreviations_applied"] = overline_count + tironian_count + chi_rho_count
        
        return stats
    
    def validate_abbreviations(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate that abbreviations are properly formed.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for malformed overlines (combining character issues)
        if '̄' in text:
            # Look for overlines not attached to letters
            malformed_overlines = re.findall(r'[^a-zA-Z]̄|̄[^a-zA-Z]', text)
            if malformed_overlines:
                errors.append(f"Malformed overlines found: {malformed_overlines}")
        
        # Check for inconsistent abbreviation patterns
        if 'd̄s' in text and 'dominus' in text:
            errors.append("Inconsistent abbreviation: both 'd̄s' and 'dominus' found")
        
        if '☧' in text and 'christus' in text.lower():
            errors.append("Inconsistent abbreviation: both '☧' and 'christus' found")
        
        # Check for proper context of abbreviations
        # Religious abbreviations should appear in religious contexts
        religious_abbrevs = ['d̄s', 'x̄s', '☧', 'ih̄s', 's̄s']
        has_religious_abbrev = any(abbrev in text for abbrev in religious_abbrevs)
        has_religious_context = any(word in text.lower() for word in 
                                  ['ecclesia', 'monastery', 'divine', 'sacred', 'holy', 'prayer'])
        
        if has_religious_abbrev and not has_religious_context:
            errors.append("Religious abbreviations found without religious context")
        
        return len(errors) == 0, errors
