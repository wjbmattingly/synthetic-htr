"""
Texture manager for applying parchment and paper textures to manuscript images.
"""

import os
import random
from typing import Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np


class TextureManager:
    """
    Manages and applies textures to manuscript images.
    """
    
    def __init__(self):
        """Initialize the texture manager."""
        self.textures = {}
        self._load_textures()
    
    def _load_textures(self):
        """Load available textures from the fonts directory."""
        texture_dir = os.path.join(
            os.path.dirname(__file__),
            "..",
            "textures"
        )
        
        if os.path.exists(texture_dir):
            for filename in os.listdir(texture_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    texture_path = os.path.join(texture_dir, filename)
                    try:
                        texture = Image.open(texture_path)
                        texture_name = os.path.splitext(filename)[0].lower()
                        self.textures[texture_name] = texture
                    except Exception as e:
                        print(f"Warning: Could not load texture {texture_path}: {e}")
    
    def apply_texture(
        self,
        image: Image.Image,
        texture_name: str,
        opacity: float = 0.3,
        scale: float = 1.0
    ) -> Image.Image:
        """
        Apply a texture to the image.
        
        Args:
            image: Base image to apply texture to
            texture_name: Name of the texture to apply
            opacity: Opacity of the texture (0.0-1.0)
            scale: Scale factor for the texture
            
        Returns:
            Image with applied texture
        """
        if texture_name not in self.textures:
            print(f"Warning: Texture '{texture_name}' not found, using default")
            return self._apply_default_texture(image)
        
        texture = self.textures[texture_name]
        
        # Resize texture to match image size
        texture_size = (
            int(image.size[0] * scale),
            int(image.size[1] * scale)
        )
        texture = texture.resize(texture_size, Image.LANCZOS)
        
        # If texture is smaller than image, tile it
        if texture.size != image.size:
            texture = self._tile_texture(texture, image.size)
        
        # Convert images to RGBA if needed
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        if texture.mode != 'RGBA':
            texture = texture.convert('RGBA')
        
        # Apply texture with specified opacity
        result = self._blend_textures(image, texture, opacity)
        
        return result
    
    def _tile_texture(self, texture: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Tile a texture to fill the target size."""
        # Create a new image of the target size
        tiled = Image.new('RGBA', target_size, (0, 0, 0, 0))
        
        # Tile the texture
        for y in range(0, target_size[1], texture.size[1]):
            for x in range(0, target_size[0], texture.size[0]):
                tiled.paste(texture, (x, y))
        
        return tiled
    
    def _blend_textures(
        self,
        base_image: Image.Image,
        texture: Image.Image,
        opacity: float
    ) -> Image.Image:
        """Blend the texture with the base image."""
        # Create a copy of the base image
        result = base_image.copy()
        
        # Adjust texture opacity
        if opacity < 1.0:
            # Create a new image with adjusted alpha
            adjusted_texture = Image.new('RGBA', texture.size, (0, 0, 0, 0))
            for x in range(texture.size[0]):
                for y in range(texture.size[1]):
                    r, g, b, a = texture.getpixel((x, y))
                    adjusted_texture.putpixel((x, y), (r, g, b, int(a * opacity)))
            texture = adjusted_texture
        
        # Composite the texture over the base image
        result = Image.alpha_composite(result, texture)
        
        return result
    
    def _apply_default_texture(self, image: Image.Image) -> Image.Image:
        """Apply a default parchment-like texture."""
        # Create a subtle noise pattern
        width, height = image.size
        
        # Generate noise pattern
        noise = np.random.normal(128, 20, (height, width, 3)).astype(np.uint8)
        
        # Add some color variation for parchment effect
        noise[:, :, 0] = np.clip(noise[:, :, 0] + 20, 0, 255)  # Slight red tint
        noise[:, :, 1] = np.clip(noise[:, :, 1] + 10, 0, 255)  # Slight green tint
        noise[:, :, 2] = np.clip(noise[:, :, 2] - 5, 0, 255)   # Slight blue reduction
        
        # Convert to PIL image
        texture_image = Image.fromarray(noise, 'RGB')
        
        # Apply slight blur for natural appearance
        texture_image = texture_image.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Blend with original image
        return self._blend_textures(image, texture_image, 0.2)
    
    def create_parchment_texture(
        self,
        size: Tuple[int, int],
        color_variation: float = 0.1,
        noise_level: float = 0.2
    ) -> Image.Image:
        """
        Create a custom parchment texture.
        
        Args:
            size: Size of the texture (width, height)
            color_variation: Amount of color variation (0.0-1.0)
            noise_level: Level of noise to add (0.0-1.0)
            
        Returns:
            Generated parchment texture
        """
        width, height = size
        
        # Base parchment color
        base_color = np.array([245, 235, 220])  # Light cream color
        
        # Create base image
        texture = np.full((height, width, 3), base_color, dtype=np.uint8)
        
        # Add color variation
        if color_variation > 0:
            variation = np.random.normal(0, 25 * color_variation, (height, width, 3))
            texture = np.clip(texture + variation, 0, 255)
        
        # Add noise
        if noise_level > 0:
            noise = np.random.normal(0, 15 * noise_level, (height, width, 3))
            texture = np.clip(texture + noise, 0, 255)
        
        # Add some darker spots for authenticity
        spots = np.random.random((height, width)) < 0.05
        texture[spots] = np.clip(texture[spots] - 30, 0, 255)
        
        # Convert to PIL image
        texture_image = Image.fromarray(texture.astype(np.uint8), 'RGB')
        
        # Apply slight blur for natural appearance
        texture_image = texture_image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return texture_image
    
    def create_paper_texture(
        self,
        size: Tuple[int, int],
        roughness: float = 0.3
    ) -> Image.Image:
        """
        Create a custom paper texture.
        
        Args:
            size: Size of the texture (width, height)
            roughness: Roughness of the paper (0.0-1.0)
            
        Returns:
            Generated paper texture
        """
        width, height = size
        
        # Base paper color
        base_color = np.array([250, 250, 250])  # Off-white
        
        # Create base image
        texture = np.full((height, width, 3), base_color, dtype=np.uint8)
        
        # Add subtle grain pattern
        grain = np.random.normal(0, 8 * roughness, (height, width))
        for i in range(3):
            texture[:, :, i] = np.clip(texture[:, :, i] + grain, 0, 255)
        
        # Add some fiber-like patterns
        if roughness > 0.5:
            for _ in range(int(roughness * 20)):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                length = np.random.randint(5, 20)
                angle = np.random.uniform(0, 2 * np.pi)
                
                for l in range(length):
                    dx = int(l * np.cos(angle))
                    dy = int(l * np.sin(angle))
                    nx, ny = x + dx, y + dy
                    
                    if 0 <= nx < width and 0 <= ny < height:
                        texture[ny, nx] = np.clip(texture[ny, nx] - 10, 0, 255)
        
        # Convert to PIL image
        texture_image = Image.fromarray(texture.astype(np.uint8), 'RGB')
        
        return texture_image
    
    def get_available_textures(self) -> list:
        """Get list of available texture names."""
        return list(self.textures.keys())
    
    def add_texture(self, name: str, texture: Image.Image):
        """Add a custom texture."""
        self.textures[name.lower()] = texture
    
    def remove_texture(self, name: str):
        """Remove a texture."""
        if name.lower() in self.textures:
            del self.textures[name.lower()]
    
    def enhance_texture(
        self,
        texture_name: str,
        brightness: float = 1.0,
        contrast: float = 1.0,
        saturation: float = 1.0
    ):
        """
        Enhance a texture with various adjustments.
        
        Args:
            texture_name: Name of the texture to enhance
            brightness: Brightness adjustment (0.0-2.0)
            contrast: Contrast adjustment (0.0-2.0)
            saturation: Saturation adjustment (0.0-2.0)
        """
        if texture_name not in self.textures:
            print(f"Warning: Texture '{texture_name}' not found")
            return
        
        texture = self.textures[texture_name]
        
        # Apply enhancements
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(texture)
            texture = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(texture)
            texture = enhancer.enhance(contrast)
        
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(texture)
            texture = enhancer.enhance(saturation)
        
        self.textures[texture_name] = texture
