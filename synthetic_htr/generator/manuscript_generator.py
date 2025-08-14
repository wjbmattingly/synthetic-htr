"""
Main manuscript generator for creating synthetic medieval manuscript images.
"""

import os
import random
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from .layout_engine import LayoutEngine
from .texture_manager import TextureManager


class ManuscriptGenerator:
    """
    Generates synthetic medieval manuscript images with authentic appearance.
    """
    
    def __init__(
        self,
        page_size: Tuple[int, int] = (1200, 1600),
        font_family: str = "medieval",
        texture: str = "parchment",
        margin_size: int = 100,
        line_spacing: float = 1.5,
        font_size: int = 24,
        random_seed: Optional[int] = None
    ):
        """
        Initialize the manuscript generator.
        
        Args:
            page_size: Size of the manuscript page (width, height)
            font_family: Font family to use ("medieval", "gothic", "uncial")
            texture: Texture to apply ("parchment", "paper", "vellum")
            margin_size: Size of page margins in pixels
            line_spacing: Spacing between text lines (multiplier)
            font_size: Base font size in pixels
            random_seed: Random seed for reproducible results
        """
        if random_seed is not None:
            random.seed(random_seed)
            
        self.page_size = page_size
        self.font_family = font_family
        self.texture = texture
        self.margin_size = margin_size
        self.line_spacing = line_spacing
        self.font_size = font_size
        
        # Initialize components
        self.layout_engine = LayoutEngine(
            page_size=page_size,
            margin_size=margin_size,
            line_spacing=line_spacing
        )
        
        self.texture_manager = TextureManager()
        
        # Font mapping
        self.font_mapping = {
            "medieval": "medieval.otf",
            "gothic": "vitor.ttf",
            "uncial": "JunicodeTwoBeta-Regular.ttf",
            "serif": "cmr10.ttf",
            "decorative": "HeavyRain-X3y9P.ttf"
        }
        
        # Load default font
        self._load_font()
    
    def _load_font(self):
        """Load the specified font."""
        font_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "fonts",
            self.font_mapping.get(self.font_family, "medieval.otf")
        )
        
        try:
            self.font = ImageFont.truetype(font_path, self.font_size)
        except Exception as e:
            print(f"Warning: Could not load font {font_path}: {e}")
            # Fallback to default system font
            self.font = ImageFont.load_default()
    
    def generate(
        self,
        text: str,
        add_illuminations: bool = False,
        add_marginalia: bool = False,
        add_decorative_borders: bool = False,
        add_noise: bool = True,
        add_aging: bool = True
    ) -> Image.Image:
        """
        Generate a synthetic medieval manuscript image.
        
        Args:
            text: Text content to render
            add_illuminations: Whether to add decorative initials
            add_marginalia: Whether to add marginal notes
            add_decorative_borders: Whether to add decorative borders
            add_noise: Whether to add realistic noise
            add_aging: Whether to add aging effects
            
        Returns:
            PIL Image of the generated manuscript
        """
        # Create base image
        image = Image.new('RGB', self.page_size, color='white')
        
        # Apply texture
        image = self.texture_manager.apply_texture(image, self.texture)
        
        # Create drawing context
        draw = ImageDraw.Draw(image)
        
        # Layout text
        text_layout = self.layout_engine.layout_text(text, self.font)
        
        # Render text
        self._render_text(draw, text_layout)
        
        # Add decorative elements
        if add_illuminations:
            self._add_illuminations(draw, text_layout)
        
        if add_marginalia:
            self._add_marginalia(draw)
        
        if add_decorative_borders:
            self._add_decorative_borders(draw)
        
        # Add realistic effects
        if add_noise:
            image = self._add_noise(image)
        
        if add_aging:
            image = self._add_aging_effects(image)
        
        return image
    
    def _render_text(self, draw: ImageDraw.Draw, text_layout: Dict[str, Any]):
        """Render the text according to the layout."""
        for line_info in text_layout['lines']:
            x, y = line_info['position']
            text = line_info['text']
            
            # Apply random variations for authenticity
            x_offset = random.randint(-2, 2)
            y_offset = random.randint(-1, 1)
            
            # Render text with slight variations
            draw.text(
                (x + x_offset, y + y_offset),
                text,
                font=self.font,
                fill='black'
            )
    
    def _add_illuminations(self, draw: ImageDraw.Draw, text_layout: Dict[str, Any]):
        """Add decorative initials and illuminations."""
        if not text_layout['lines']:
            return
            
        # Add decorative initial for first line
        first_line = text_layout['lines'][0]
        x, y = first_line['position']
        
        # Create decorative initial
        initial_size = self.font_size * 2
        initial_x = x - initial_size - 20
        initial_y = y - initial_size // 2
        
        # Draw decorative circle around initial
        draw.ellipse(
            [initial_x, initial_y, initial_x + initial_size, initial_y + initial_size],
            outline='gold',
            width=3
        )
        
        # Add decorative elements
        self._draw_decorative_elements(draw, initial_x, initial_y, initial_size)
    
    def _add_marginalia(self, draw: ImageDraw.Draw):
        """Add marginal notes and decorations."""
        # Add some random marginal notes
        margin_notes = [
            "Nota bene",
            "Vide supra",
            "Cf.",
            "✝",
            "❦",
            "☧"
        ]
        
        for i in range(random.randint(2, 5)):
            x = random.randint(20, self.margin_size - 50)
            y = random.randint(100, self.page_size[1] - 100)
            
            note = random.choice(margin_notes)
            draw.text((x, y), note, font=self.font, fill='brown')
    
    def _add_decorative_borders(self, draw: ImageDraw.Draw):
        """Add decorative borders around the page."""
        border_width = 3
        border_color = 'gold'
        
        # Outer border
        draw.rectangle(
            [0, 0, self.page_size[0] - 1, self.page_size[1] - 1],
            outline=border_color,
            width=border_width
        )
        
        # Inner border
        inner_margin = 50
        draw.rectangle(
            [inner_margin, inner_margin, 
             self.page_size[0] - inner_margin - 1, 
             self.page_size[1] - inner_margin - 1],
            outline=border_color,
            width=1
        )
        
        # Corner decorations
        corner_size = 30
        for corner in [(0, 0), (self.page_size[0] - corner_size, 0),
                       (0, self.page_size[1] - corner_size),
                       (self.page_size[0] - corner_size, self.page_size[1] - corner_size)]:
            x, y = corner
            draw.rectangle([x, y, x + corner_size, y + corner_size],
                          outline=border_color, width=2)
    
    def _draw_decorative_elements(self, draw: ImageDraw.Draw, x: int, y: int, size: int):
        """Draw decorative elements around initials."""
        # Add some simple decorative patterns
        center_x = x + size // 2
        center_y = y + size // 2
        
        # Draw small circles around the initial
        for angle in range(0, 360, 45):
            rad = np.radians(angle)
            circle_x = center_x + int(np.cos(rad) * (size + 10))
            circle_y = center_y + int(np.sin(rad) * (size + 10))
            circle_size = 5
            
            draw.ellipse(
                [circle_x - circle_size, circle_y - circle_size,
                 circle_x + circle_size, circle_y + circle_size],
                fill='red'
            )
    
    def _add_noise(self, image: Image.Image) -> Image.Image:
        """Add realistic noise to the image."""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Add slight noise
        noise = np.random.normal(0, 5, img_array.shape).astype(np.uint8)
        noisy_array = np.clip(img_array + noise, 0, 255)
        
        return Image.fromarray(noisy_array)
    
    def _add_aging_effects(self, image: Image.Image) -> Image.Image:
        """Add aging effects to simulate old manuscript appearance."""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Add slight yellowing/browning
        yellowing = np.array([20, 10, 0], dtype=np.uint8)
        aged_array = np.clip(img_array + yellowing, 0, 255)
        
        # Add slight blur for aged appearance
        from PIL import ImageFilter
        aged_image = Image.fromarray(aged_array)
        aged_image = aged_image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return aged_image
    
    def set_font(self, font_family: str):
        """Change the font family."""
        if font_family in self.font_mapping:
            self.font_family = font_family
            self._load_font()
        else:
            raise ValueError(f"Unknown font family: {font_family}")
    
    def set_page_size(self, page_size: Tuple[int, int]):
        """Change the page size."""
        self.page_size = page_size
        self.layout_engine.set_page_size(page_size)
    
    def set_texture(self, texture: str):
        """Change the texture."""
        if texture in ["parchment", "paper", "vellum"]:
            self.texture = texture
        else:
            raise ValueError(f"Unknown texture: {texture}")
    
    def batch_generate(
        self,
        texts: list,
        output_dir: str = "output",
        **kwargs
    ) -> list:
        """
        Generate multiple manuscript images.
        
        Args:
            texts: List of text content
            output_dir: Directory to save generated images
            **kwargs: Additional arguments for generate method
            
        Returns:
            List of generated image paths
        """
        os.makedirs(output_dir, exist_ok=True)
        generated_paths = []
        
        for i, text in enumerate(texts):
            manuscript = self.generate(text, **kwargs)
            output_path = os.path.join(output_dir, f"manuscript_{i:03d}.png")
            manuscript.save(output_path)
            generated_paths.append(output_path)
        
        return generated_paths
