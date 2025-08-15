"""
Color font renderer for medieval manuscripts.

This module implements multi-layer color font rendering inspired by the Cerne font's
COLR table approach, allowing for authentic medieval illuminated text with multiple
colors per glyph.
"""

import random
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
import numpy as np


@dataclass
class ColorLayer:
    """Represents a single color layer in a color font."""
    color: Tuple[int, int, int]  # RGB color
    opacity: float = 1.0  # Opacity (0.0-1.0)
    offset: Tuple[int, int] = (0, 0)  # X, Y offset for this layer
    blend_mode: str = "normal"  # Blend mode (normal, multiply, overlay, etc.)


@dataclass
class GlyphColorInfo:
    """Color information for a specific glyph."""
    base_layer: ColorLayer  # Base text layer
    decoration_layers: List[ColorLayer]  # Additional decorative layers
    has_illumination: bool = False  # Whether this glyph has illuminated decoration


class ColorFontRenderer:
    """
    Renders text with multiple color layers to simulate medieval illuminated manuscripts.
    
    This class implements the concept from color fonts like Cerne, where each character
    can have multiple colored layers that are composited together.
    """
    
    def __init__(self):
        """Initialize the color font renderer."""
        self.color_schemes = {}
        self.glyph_color_rules = {}
        self.illumination_patterns = {}
        
        # Initialize default color schemes
        self._init_color_schemes()
        self._init_glyph_rules()
        self._init_illumination_patterns()
    
    def _init_color_schemes(self):
        """Initialize medieval color schemes based on historical manuscripts."""
        
        # Cerne-inspired scheme (based on Book of Cerne pigments)
        self.color_schemes["cerne"] = {
            "text": (101, 67, 33),      # Dark reddish brown (iron gall ink)
            "red": (184, 92, 92),       # Red lead (minium)
            "yellow": (218, 165, 32),   # Orpiment
            "green": (107, 142, 35),    # Verdigris
            "blue": (70, 130, 180),     # Woad/lapis lazuli
            "gold": (255, 215, 0),      # Gold leaf
            "background": (245, 245, 220)  # Parchment
        }
        
        # Book of Kells inspired
        self.color_schemes["kells"] = {
            "text": (40, 40, 40),       # Dark charcoal
            "red": (139, 0, 0),         # Deep red
            "blue": (0, 0, 139),        # Deep blue
            "green": (0, 100, 0),       # Deep green
            "yellow": (255, 215, 0),    # Gold
            "purple": (75, 0, 130),     # Royal purple
            "background": (250, 248, 240)
        }
        
        # Lindisfarne Gospels inspired
        self.color_schemes["lindisfarne"] = {
            "text": (51, 51, 51),       # Charcoal
            "red": (178, 34, 34),       # Firebrick
            "blue": (25, 25, 112),      # Midnight blue
            "orange": (255, 140, 0),    # Dark orange
            "green": (34, 139, 34),     # Forest green
            "gold": (255, 215, 0),      # Gold
            "background": (255, 253, 250)
        }
        
        # Winchester Bible inspired
        self.color_schemes["winchester"] = {
            "text": (61, 43, 31),       # Dark brown
            "red": (165, 42, 42),       # Brown-red
            "blue": (72, 61, 139),      # Dark slate blue
            "green": (85, 107, 47),     # Dark olive green
            "purple": (106, 90, 205),   # Slate blue
            "gold": (218, 165, 32),     # Goldenrod
            "background": (248, 248, 255)
        }
    
    def _init_glyph_rules(self):
        """Initialize rules for which glyphs get which colors."""
        
        # Rules for capital letters (often illuminated)
        self.glyph_color_rules["capitals"] = {
            # Vowels often get red
            "AEIOU": ["red", "gold"],
            # Consonants get various colors
            "BCDFGHJKLMNPQRSTVWXYZ": ["blue", "green", "purple", "red"],
            # Special letters
            "ILMNR": ["blue", "red"],  # Often used in religious contexts
        }
        
        # Rules for specific letters in religious contexts
        self.glyph_color_rules["religious"] = {
            "I": ["gold", "red"],      # Jesus, In nomine
            "C": ["red", "blue"],      # Christus
            "D": ["blue", "purple"],   # Deus, Dominus
            "S": ["red", "green"],     # Sanctus, Spiritus
            "M": ["blue", "red"],      # Maria, Mater
            "P": ["purple", "gold"],   # Pater
        }
        
        # Rules for decorative elements
        self.glyph_color_rules["decorative"] = {
            "borders": ["gold", "red", "blue"],
            "flourishes": ["green", "red", "blue"],
            "backgrounds": ["yellow", "gold"],
        }
    
    def _init_illumination_patterns(self):
        """Initialize patterns for illuminated letters."""
        
        self.illumination_patterns = {
            "simple": {
                "background_shape": "circle",
                "decoration_type": "dots",
                "color_layers": 2,
            },
            "ornate": {
                "background_shape": "square",
                "decoration_type": "flourishes",
                "color_layers": 3,
            },
            "historiated": {
                "background_shape": "complex",
                "decoration_type": "interlace",
                "color_layers": 4,
            }
        }
    
    def create_color_layers_for_glyph(
        self,
        glyph: str,
        color_scheme: str = "cerne",
        illumination_level: str = "simple",
        is_capital: bool = False,
        context: str = "general"
    ) -> GlyphColorInfo:
        """
        Create color layer information for a specific glyph.
        
        Args:
            glyph: The character/glyph
            color_scheme: Color scheme to use
            illumination_level: Level of illumination (simple, ornate, historiated)
            is_capital: Whether this is a capital letter
            context: Context (religious, secular, academic)
            
        Returns:
            GlyphColorInfo with layer specifications
        """
        colors = self.color_schemes.get(color_scheme, self.color_schemes["cerne"])
        
        # Base text layer (always present)
        base_layer = ColorLayer(
            color=colors["text"],
            opacity=1.0,
            offset=(0, 0)
        )
        
        decoration_layers = []
        has_illumination = False
        
        # Add decoration layers for capitals
        if is_capital:
            has_illumination = True
            
            # Choose primary decoration color based on glyph
            if glyph.upper() in "AEIOU":
                primary_color = colors["red"]
            elif glyph.upper() in "BCDFG":
                primary_color = colors["blue"]
            elif glyph.upper() in "HJKLM":
                primary_color = colors["green"]
            elif glyph.upper() in "NOPQR":
                primary_color = colors["purple"] if "purple" in colors else colors["blue"]
            else:
                primary_color = colors["yellow"]
            
            # Background decoration layer
            decoration_layers.append(ColorLayer(
                color=primary_color,
                opacity=0.3,
                offset=(-1, -1),
                blend_mode="multiply"
            ))
            
            # Highlight layer
            if illumination_level in ["ornate", "historiated"]:
                decoration_layers.append(ColorLayer(
                    color=colors["gold"],
                    opacity=0.6,
                    offset=(1, 1),
                    blend_mode="overlay"
                ))
            
            # Additional ornate decorations
            if illumination_level == "historiated":
                decoration_layers.append(ColorLayer(
                    color=colors.get("purple", colors["blue"]),
                    opacity=0.4,
                    offset=(0, -2),
                    blend_mode="normal"
                ))
        
        # Context-specific adjustments
        if context == "religious":
            if glyph.upper() in "IHS":  # Jesus abbreviation
                decoration_layers.append(ColorLayer(
                    color=colors["gold"],
                    opacity=0.8,
                    offset=(0, 0),
                    blend_mode="overlay"
                ))
        
        return GlyphColorInfo(
            base_layer=base_layer,
            decoration_layers=decoration_layers,
            has_illumination=has_illumination
        )
    
    def render_color_text(
        self,
        draw: ImageDraw.Draw,
        text: str,
        position: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        color_scheme: str = "cerne",
        illumination_level: str = "simple",
        context: str = "general",
        add_backgrounds: bool = True
    ) -> List[Tuple[int, int, int, int]]:
        """
        Render text with color layers.
        
        Args:
            draw: PIL ImageDraw object
            text: Text to render
            position: Starting position (x, y)
            font: Font to use
            color_scheme: Color scheme name
            illumination_level: Level of illumination
            context: Text context
            add_backgrounds: Whether to add background decorations
            
        Returns:
            List of bounding boxes for rendered text
        """
        x, y = position
        bboxes = []
        
        # Process each character
        for i, char in enumerate(text):
            if not char.strip():  # Skip whitespace
                # Get space width
                try:
                    space_bbox = draw.textbbox((x, y), " ", font=font)
                    char_width = space_bbox[2] - space_bbox[0]
                except AttributeError:
                    char_width, _ = draw.textsize(" ", font=font)
                x += char_width
                continue
            
            # Determine if this should be illuminated
            is_capital = char.isupper()
            should_illuminate = (
                is_capital and 
                (i == 0 or text[i-1] in ". !?")  # First letter or after sentence
            )
            
            # Get color information for this glyph
            color_info = self.create_color_layers_for_glyph(
                char,
                color_scheme=color_scheme,
                illumination_level=illumination_level if should_illuminate else "simple",
                is_capital=is_capital,
                context=context
            )
            
            # Get character dimensions
            try:
                char_bbox = draw.textbbox((x, y), char, font=font)
                char_width = char_bbox[2] - char_bbox[0]
                char_height = char_bbox[3] - char_bbox[1]
            except AttributeError:
                char_width, char_height = draw.textsize(char, font=font)
                char_bbox = (x, y, x + char_width, y + char_height)
            
            # Render background decorations first
            if add_backgrounds and color_info.has_illumination:
                self._render_background_decoration(
                    draw, char, (x, y), char_width, char_height, 
                    color_info, illumination_level
                )
            
            # Render decoration layers (behind text)
            for layer in color_info.decoration_layers:
                layer_x = x + layer.offset[0]
                layer_y = y + layer.offset[1]
                
                # Apply opacity by modifying color
                layer_color = self._apply_opacity(layer.color, layer.opacity)
                
                draw.text((layer_x, layer_y), char, font=font, fill=layer_color)
            
            # Render base text layer
            draw.text((x, y), char, font=font, fill=color_info.base_layer.color)
            
            # Add to bounding boxes
            bboxes.append(char_bbox)
            
            # Move to next character position
            x += char_width
        
        return bboxes
    
    def _render_background_decoration(
        self,
        draw: ImageDraw.Draw,
        char: str,
        position: Tuple[int, int],
        width: int,
        height: int,
        color_info: GlyphColorInfo,
        illumination_level: str
    ):
        """Render background decorations for illuminated letters."""
        x, y = position
        
        # Get decoration color (first decoration layer)
        if color_info.decoration_layers:
            bg_color = color_info.decoration_layers[0].color
        else:
            bg_color = (200, 200, 200)  # Default gray
        
        # Expand the decoration area
        margin = max(width, height) // 4
        bg_x = x - margin
        bg_y = y - margin
        bg_width = width + 2 * margin
        bg_height = height + 2 * margin
        
        if illumination_level == "simple":
            # Simple circular background
            draw.ellipse(
                [bg_x, bg_y, bg_x + bg_width, bg_y + bg_height],
                fill=self._apply_opacity(bg_color, 0.2),
                outline=self._apply_opacity(bg_color, 0.5),
                width=2
            )
        
        elif illumination_level == "ornate":
            # Square background with corner decorations
            draw.rectangle(
                [bg_x, bg_y, bg_x + bg_width, bg_y + bg_height],
                fill=self._apply_opacity(bg_color, 0.15),
                outline=self._apply_opacity(bg_color, 0.6),
                width=2
            )
            
            # Add corner dots
            dot_size = 3
            corners = [
                (bg_x, bg_y),
                (bg_x + bg_width, bg_y),
                (bg_x, bg_y + bg_height),
                (bg_x + bg_width, bg_y + bg_height)
            ]
            
            for corner_x, corner_y in corners:
                draw.ellipse(
                    [corner_x - dot_size, corner_y - dot_size,
                     corner_x + dot_size, corner_y + dot_size],
                    fill=bg_color
                )
        
        elif illumination_level == "historiated":
            # Complex background with multiple elements
            # Outer circle
            draw.ellipse(
                [bg_x - 5, bg_y - 5, bg_x + bg_width + 5, bg_y + bg_height + 5],
                outline=self._apply_opacity(bg_color, 0.8),
                width=3
            )
            
            # Inner square
            inner_margin = margin // 2
            draw.rectangle(
                [bg_x + inner_margin, bg_y + inner_margin,
                 bg_x + bg_width - inner_margin, bg_y + bg_height - inner_margin],
                fill=self._apply_opacity(bg_color, 0.1),
                outline=self._apply_opacity(bg_color, 0.4),
                width=1
            )
            
            # Decorative cross pattern
            center_x = bg_x + bg_width // 2
            center_y = bg_y + bg_height // 2
            cross_size = min(bg_width, bg_height) // 3
            
            # Horizontal line
            draw.line(
                [center_x - cross_size, center_y, center_x + cross_size, center_y],
                fill=self._apply_opacity(bg_color, 0.6),
                width=2
            )
            
            # Vertical line
            draw.line(
                [center_x, center_y - cross_size, center_x, center_y + cross_size],
                fill=self._apply_opacity(bg_color, 0.6),
                width=2
            )
    
    def _apply_opacity(self, color: Tuple[int, int, int], opacity: float) -> Tuple[int, int, int]:
        """Apply opacity to a color by blending with white background."""
        if opacity >= 1.0:
            return color
        
        # Blend with white background
        r, g, b = color
        white = 255
        
        new_r = int(r * opacity + white * (1 - opacity))
        new_g = int(g * opacity + white * (1 - opacity))
        new_b = int(b * opacity + white * (1 - opacity))
        
        return (new_r, new_g, new_b)
    
    def create_illuminated_initial(
        self,
        char: str,
        size: int,
        color_scheme: str = "cerne",
        illumination_level: str = "ornate"
    ) -> Image.Image:
        """
        Create a standalone illuminated initial.
        
        Args:
            char: Character to illuminate
            size: Size of the initial in pixels
            color_scheme: Color scheme to use
            illumination_level: Level of illumination
            
        Returns:
            PIL Image of the illuminated initial
        """
        # Create image with padding
        padding = size // 2
        img_size = size + 2 * padding
        image = Image.new('RGBA', (img_size, img_size), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # Load a decorative font (fallback to default)
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except:
            font = ImageFont.load_default()
        
        # Render the illuminated character
        position = (padding, padding)
        self.render_color_text(
            draw, char, position, font,
            color_scheme=color_scheme,
            illumination_level=illumination_level,
            context="religious",
            add_backgrounds=True
        )
        
        return image
    
    def get_available_color_schemes(self) -> List[str]:
        """Get list of available color schemes."""
        return list(self.color_schemes.keys())
    
    def add_color_scheme(self, name: str, colors: Dict[str, Tuple[int, int, int]]):
        """Add a custom color scheme."""
        self.color_schemes[name] = colors
    
    def create_color_palette_sample(
        self,
        color_scheme: str = "cerne",
        sample_text: str = "ABCDEFGHIJKLM",
        output_path: Optional[str] = None
    ) -> Image.Image:
        """
        Create a sample showing the color palette in use.
        
        Args:
            color_scheme: Color scheme to demonstrate
            sample_text: Text to use for the sample
            output_path: Optional path to save the image
            
        Returns:
            PIL Image of the color palette sample
        """
        # Create image
        img_width, img_height = 800, 300
        image = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Load font
        try:
            font = ImageFont.truetype("arial.ttf", 36)
            title_font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Draw title
        colors = self.color_schemes.get(color_scheme, self.color_schemes["cerne"])
        draw.text((50, 30), f"Color Scheme: {color_scheme}", font=title_font, fill=colors["text"])
        
        # Draw sample text with color rendering
        self.render_color_text(
            draw, sample_text, (50, 100), font,
            color_scheme=color_scheme,
            illumination_level="ornate",
            add_backgrounds=True
        )
        
        # Draw color swatches
        swatch_y = 200
        swatch_size = 30
        swatch_x = 50
        
        for color_name, color_value in colors.items():
            if color_name != "background":
                # Draw color swatch
                draw.rectangle(
                    [swatch_x, swatch_y, swatch_x + swatch_size, swatch_y + swatch_size],
                    fill=color_value,
                    outline=(0, 0, 0),
                    width=1
                )
                
                # Draw color name
                draw.text(
                    (swatch_x, swatch_y + swatch_size + 5),
                    color_name,
                    font=title_font,
                    fill=colors["text"]
                )
                
                swatch_x += swatch_size + 80
        
        if output_path:
            image.save(output_path)
            print(f"Color palette sample saved to: {output_path}")
        
        return image
