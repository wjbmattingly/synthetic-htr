"""
Advanced font manager with support for contextual alternates and medieval typography features.

Inspired by the Cerne font project's sophisticated approach to medieval script rendering.
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class AdvancedFontManager:
    """
    Advanced font manager that handles contextual alternates, color fonts, and medieval typography.
    
    This class implements concepts from the Cerne font project:
    - Contextual alternates for authentic cursive connections
    - Automatic letterform variation for doubled letters
    - Color font support with multiple layers
    - Font feature settings (OpenType features)
    """
    
    def __init__(self, fonts_dir: Optional[str] = None):
        """
        Initialize the advanced font manager.
        
        Args:
            fonts_dir: Directory containing font files
        """
        if fonts_dir is None:
            fonts_dir = os.path.join(os.path.dirname(__file__), "..", "fonts")
        
        self.fonts_dir = Path(fonts_dir)
        self.loaded_fonts = {}
        self.font_features = {}
        self.color_palettes = {}
        
        # Initialize medieval color palettes (inspired by Cerne)
        self._init_medieval_colors()
        
        # Load font configurations
        self._load_font_configs()
        
        # Medieval font mappings with feature support
        self.medieval_fonts = {
            "cerne": {
                "file": "Cerne.otf",
                "features": {
                    "hist": False,  # Historical mode
                    "ss02": False,  # Alternate colors for caps
                    "ss03": False,  # No color for caps
                    "ss04": False,  # Word-final forms
                    "ss05": False,  # Miscellaneous alternates
                    "ss06": False,  # User color
                    "dlig": False,  # Discretionary ligatures
                    "calt": True,   # Contextual alternates (default on)
                    "liga": True,   # Standard ligatures
                },
                "supports_color": True,
                "supports_contextual": True
            },
            "junicode": {
                "file": "JunicodeTwoBeta-Regular.ttf",
                "features": {
                    "hist": False,
                    "liga": True,
                    "calt": True,
                    "smcp": False,  # Small caps
                    "onum": False,  # Old-style numerals
                },
                "supports_color": False,
                "supports_contextual": True
            },
            "medieval": {
                "file": "medieval.otf",
                "features": {
                    "liga": True,
                    "calt": True,
                },
                "supports_color": False,
                "supports_contextual": False
            },
            "vitor": {
                "file": "vitor.ttf",
                "features": {
                    "liga": True,
                },
                "supports_color": False,
                "supports_contextual": False
            }
        }
    
    def _init_medieval_colors(self):
        """Initialize medieval color palettes based on historical pigments."""
        # Cerne-inspired color palette
        self.color_palettes["cerne"] = {
            "text": (101, 67, 33),      # Dark reddish brown (main text)
            "red": (184, 92, 92),      # Red lead
            "yellow": (218, 165, 32),   # Orpiment
            "green": (107, 142, 35),    # Verdigris
            "blue": (70, 130, 180),     # Woad
            "background": (245, 245, 220)  # Parchment
        }
        
        # Traditional medieval palette
        self.color_palettes["traditional"] = {
            "text": (40, 40, 40),       # Dark gray-black
            "red": (139, 0, 0),         # Dark red
            "blue": (0, 0, 139),        # Dark blue
            "gold": (255, 215, 0),      # Gold
            "green": (0, 100, 0),       # Dark green
            "background": (250, 248, 240)  # Off-white
        }
        
        # Carolingian manuscript colors
        self.color_palettes["carolingian"] = {
            "text": (51, 51, 51),       # Charcoal
            "red": (178, 34, 34),       # Firebrick
            "blue": (25, 25, 112),      # Midnight blue
            "purple": (75, 0, 130),     # Indigo
            "brown": (139, 69, 19),     # Saddle brown
            "background": (255, 253, 250)  # Snow
        }
    
    def _load_font_configs(self):
        """Load font configuration files if they exist."""
        config_path = self.fonts_dir / "font_configs.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    configs = json.load(f)
                    self.medieval_fonts.update(configs)
            except Exception as e:
                print(f"Warning: Could not load font configs: {e}")
    
    def load_font(self, font_name: str, size: int, features: Optional[Dict[str, bool]] = None) -> ImageFont.FreeTypeFont:
        """
        Load a font with specified features.
        
        Args:
            font_name: Name of the medieval font
            size: Font size in pixels
            features: Dictionary of OpenType features to enable/disable
            
        Returns:
            Loaded PIL font object
        """
        cache_key = f"{font_name}_{size}_{str(features)}"
        
        if cache_key in self.loaded_fonts:
            return self.loaded_fonts[cache_key]
        
        if font_name not in self.medieval_fonts:
            raise ValueError(f"Unknown font: {font_name}. Available: {list(self.medieval_fonts.keys())}")
        
        font_info = self.medieval_fonts[font_name]
        font_path = self.fonts_dir / font_info["file"]
        
        if not font_path.exists():
            print(f"Warning: Font file not found: {font_path}")
            # Try fallback fonts
            fallback_path = self._find_fallback_font()
            if fallback_path:
                font_path = fallback_path
            else:
                raise FileNotFoundError(f"Font file not found: {font_path}")
        
        try:
            font = ImageFont.truetype(str(font_path), size)
            
            # Store font features for later use
            if features is None:
                features = font_info["features"].copy()
            else:
                # Merge with default features
                merged_features = font_info["features"].copy()
                merged_features.update(features)
                features = merged_features
            
            self.font_features[cache_key] = features
            self.loaded_fonts[cache_key] = font
            
            return font
            
        except Exception as e:
            print(f"Error loading font {font_path}: {e}")
            # Return default font as fallback
            return ImageFont.load_default()
    
    def _find_fallback_font(self) -> Optional[Path]:
        """Find a fallback font if the requested font is not available."""
        fallback_names = ["JunicodeTwoBeta-Regular.ttf", "medieval.otf", "cmr10.ttf"]
        
        for fallback in fallback_names:
            fallback_path = self.fonts_dir / fallback
            if fallback_path.exists():
                return fallback_path
        
        return None
    
    def get_font_features(self, font_name: str, size: int) -> Dict[str, bool]:
        """Get the current font features for a loaded font."""
        cache_key = f"{font_name}_{size}_None"
        return self.font_features.get(cache_key, {})
    
    def set_font_features(self, font_name: str, size: int, features: Dict[str, bool]):
        """Set font features for a font (requires reloading)."""
        cache_key = f"{font_name}_{size}_{str(features)}"
        if cache_key in self.loaded_fonts:
            del self.loaded_fonts[cache_key]
        
        # Reload with new features
        self.load_font(font_name, size, features)
    
    def supports_color_font(self, font_name: str) -> bool:
        """Check if a font supports color rendering."""
        if font_name not in self.medieval_fonts:
            return False
        return self.medieval_fonts[font_name].get("supports_color", False)
    
    def supports_contextual_alternates(self, font_name: str) -> bool:
        """Check if a font supports contextual alternates."""
        if font_name not in self.medieval_fonts:
            return False
        return self.medieval_fonts[font_name].get("supports_contextual", False)
    
    def get_color_palette(self, palette_name: str = "cerne") -> Dict[str, Tuple[int, int, int]]:
        """Get a medieval color palette."""
        return self.color_palettes.get(palette_name, self.color_palettes["cerne"])
    
    def render_text_with_features(
        self,
        draw: ImageDraw.Draw,
        text: str,
        position: Tuple[int, int],
        font_name: str,
        font_size: int,
        features: Optional[Dict[str, bool]] = None,
        color_palette: str = "cerne",
        use_color_layers: bool = True
    ) -> List[Tuple[int, int, int, int]]:
        """
        Render text with advanced typography features.
        
        Args:
            draw: PIL ImageDraw object
            text: Text to render
            position: (x, y) position
            font_name: Name of the font to use
            font_size: Size of the font
            features: OpenType features to apply
            color_palette: Color palette to use
            use_color_layers: Whether to use color font rendering
            
        Returns:
            List of bounding boxes for rendered text
        """
        font = self.load_font(font_name, font_size, features)
        colors = self.get_color_palette(color_palette)
        
        # Check if we should use color rendering
        if use_color_layers and self.supports_color_font(font_name):
            return self._render_color_text(draw, text, position, font, colors)
        else:
            return self._render_standard_text(draw, text, position, font, colors["text"])
    
    def _render_standard_text(
        self,
        draw: ImageDraw.Draw,
        text: str,
        position: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int]
    ) -> List[Tuple[int, int, int, int]]:
        """Render text with standard single-color rendering."""
        x, y = position
        
        # Get text bounding box
        try:
            bbox = draw.textbbox((x, y), text, font=font)
        except AttributeError:
            # Fallback for older PIL versions
            w, h = draw.textsize(text, font=font)
            bbox = (x, y, x + w, y + h)
        
        # Render the text
        draw.text(position, text, font=font, fill=color)
        
        return [bbox]
    
    def _render_color_text(
        self,
        draw: ImageDraw.Draw,
        text: str,
        position: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        colors: Dict[str, Tuple[int, int, int]]
    ) -> List[Tuple[int, int, int, int]]:
        """
        Render text with color font layers (simulating COLR table behavior).
        
        This is a simplified implementation of color font rendering.
        In a full implementation, this would parse COLR/CPAL tables.
        """
        x, y = position
        bboxes = []
        
        # For now, we'll simulate color font behavior by:
        # 1. Rendering base text in main color
        # 2. Adding colored highlights for capitals
        
        # Get text bounding box
        try:
            bbox = draw.textbbox((x, y), text, font=font)
        except AttributeError:
            w, h = draw.textsize(text, font=font)
            bbox = (x, y, x + w, y + h)
        
        # Render base text
        draw.text(position, text, font=font, fill=colors["text"])
        bboxes.append(bbox)
        
        # Add colored highlights for capital letters (simulating color layers)
        char_x = x
        for char in text:
            if char.isupper():
                # Get character width
                try:
                    char_bbox = draw.textbbox((char_x, y), char, font=font)
                    char_width = char_bbox[2] - char_bbox[0]
                except AttributeError:
                    char_width, _ = draw.textsize(char, font=font)
                
                # Choose color based on character
                if char in 'AEIOU':
                    highlight_color = colors.get("red", colors["text"])
                elif char in 'BCDFG':
                    highlight_color = colors.get("blue", colors["text"])
                elif char in 'HJKLM':
                    highlight_color = colors.get("green", colors["text"])
                else:
                    highlight_color = colors.get("yellow", colors["text"])
                
                # Render colored version with slight offset for layering effect
                draw.text((char_x, y), char, font=font, fill=highlight_color)
                
                char_x += char_width
            else:
                # Get character width for spacing
                try:
                    char_bbox = draw.textbbox((char_x, y), char, font=font)
                    char_width = char_bbox[2] - char_bbox[0]
                except AttributeError:
                    char_width, _ = draw.textsize(char, font=font)
                char_x += char_width
        
        return bboxes
    
    def get_available_fonts(self) -> List[str]:
        """Get list of available medieval fonts."""
        return list(self.medieval_fonts.keys())
    
    def get_font_info(self, font_name: str) -> Dict[str, Any]:
        """Get detailed information about a font."""
        if font_name not in self.medieval_fonts:
            raise ValueError(f"Unknown font: {font_name}")
        
        info = self.medieval_fonts[font_name].copy()
        font_path = self.fonts_dir / info["file"]
        info["path"] = str(font_path)
        info["exists"] = font_path.exists()
        
        return info
    
    def create_font_specimen(
        self,
        font_name: str,
        sample_text: str = "The quick brown fox jumps over the lazy dog",
        size: int = 36,
        output_path: Optional[str] = None
    ) -> Image.Image:
        """
        Create a font specimen showing the font's capabilities.
        
        Args:
            font_name: Name of the font
            sample_text: Text to display
            size: Font size
            output_path: Optional path to save the specimen
            
        Returns:
            PIL Image of the font specimen
        """
        # Create image
        img_width, img_height = 800, 400
        image = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Load font
        font = self.load_font(font_name, size)
        colors = self.get_color_palette("cerne")
        
        # Draw title
        title_font = self.load_font(font_name, size + 10)
        draw.text((50, 30), f"Font: {font_name}", font=title_font, fill=colors["text"])
        
        # Draw sample text
        y_pos = 100
        
        # Normal text
        draw.text((50, y_pos), sample_text, font=font, fill=colors["text"])
        y_pos += size + 20
        
        # With different features if supported
        if self.supports_contextual_alternates(font_name):
            features = {"hist": True, "calt": True}
            hist_font = self.load_font(font_name, size, features)
            draw.text((50, y_pos), f"Historical: {sample_text}", font=hist_font, fill=colors["text"])
            y_pos += size + 20
        
        # Color rendering if supported
        if self.supports_color_font(font_name):
            self.render_text_with_features(
                draw, f"Color: {sample_text}", (50, y_pos),
                font_name, size, use_color_layers=True
            )
        
        if output_path:
            image.save(output_path)
            print(f"Font specimen saved to: {output_path}")
        
        return image
