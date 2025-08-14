"""
Image processing utilities for manuscript images.
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from typing import Tuple, Optional, List


class ImageProcessor:
    """
    Utility class for processing and enhancing manuscript images.
    """
    
    @staticmethod
    def resize_image(
        image: Image.Image,
        target_size: Tuple[int, int],
        maintain_aspect: bool = True
    ) -> Image.Image:
        """
        Resize an image to target dimensions.
        
        Args:
            image: Input image
            target_size: Target size (width, height)
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Resized image
        """
        if maintain_aspect:
            # Calculate aspect ratio
            img_ratio = image.size[0] / image.size[1]
            target_ratio = target_size[0] / target_size[1]
            
            if img_ratio > target_ratio:
                # Image is wider, fit to width
                new_width = target_size[0]
                new_height = int(target_size[0] / img_ratio)
            else:
                # Image is taller, fit to height
                new_height = target_size[1]
                new_width = int(target_size[1] * img_ratio)
            
            resized = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Create new image with target size and paste resized image
            result = Image.new('RGB', target_size, 'white')
            paste_x = (target_size[0] - new_width) // 2
            paste_y = (target_size[1] - new_height) // 2
            result.paste(resized, (paste_x, paste_y))
            
            return result
        else:
            return image.resize(target_size, Image.LANCZOS)
    
    @staticmethod
    def add_noise(
        image: Image.Image,
        noise_level: float = 0.1,
        noise_type: str = "gaussian"
    ) -> Image.Image:
        """
        Add noise to an image.
        
        Args:
            image: Input image
            noise_level: Intensity of noise (0.0-1.0)
            noise_type: Type of noise ("gaussian", "salt_pepper", "poisson")
            
        Returns:
            Image with added noise
        """
        img_array = np.array(image)
        
        if noise_type == "gaussian":
            noise = np.random.normal(0, 25 * noise_level, img_array.shape)
            noisy_array = np.clip(img_array + noise, 0, 255)
            
        elif noise_type == "salt_pepper":
            noisy_array = img_array.copy()
            # Salt noise
            salt_coords = np.random.random(img_array.shape[:2]) < noise_level * 0.5
            noisy_array[salt_coords] = 255
            # Pepper noise
            pepper_coords = np.random.random(img_array.shape[:2]) < noise_level * 0.5
            noisy_array[pepper_coords] = 0
            
        elif noise_type == "poisson":
            noise = np.random.poisson(25 * noise_level, img_array.shape)
            noisy_array = np.clip(img_array + noise, 0, 255)
            
        else:
            raise ValueError(f"Unknown noise type: {noise_type}")
        
        return Image.fromarray(noisy_array.astype(np.uint8))
    
    @staticmethod
    def add_blur(
        image: Image.Image,
        blur_radius: float = 1.0,
        blur_type: str = "gaussian"
    ) -> Image.Image:
        """
        Add blur to an image.
        
        Args:
            image: Input image
            blur_radius: Blur radius
            blur_type: Type of blur ("gaussian", "box", "unsharp")
            
        Returns:
            Blurred image
        """
        if blur_type == "gaussian":
            return image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        elif blur_type == "box":
            return image.filter(ImageFilter.BoxBlur(radius=blur_radius))
        elif blur_type == "unsharp":
            return image.filter(ImageFilter.UnsharpMask(radius=blur_radius))
        else:
            raise ValueError(f"Unknown blur type: {blur_type}")
    
    @staticmethod
    def adjust_brightness_contrast(
        image: Image.Image,
        brightness: float = 1.0,
        contrast: float = 1.0
    ) -> Image.Image:
        """
        Adjust brightness and contrast of an image.
        
        Args:
            image: Input image
            brightness: Brightness multiplier (0.0-2.0)
            contrast: Contrast multiplier (0.0-2.0)
            
        Returns:
            Adjusted image
        """
        # Adjust brightness
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        # Adjust contrast
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        return image
    
    @staticmethod
    def add_aging_effects(
        image: Image.Image,
        yellowing: float = 0.3,
        fading: float = 0.2,
        spots: float = 0.1
    ) -> Image.Image:
        """
        Add aging effects to simulate old manuscript appearance.
        
        Args:
            image: Input image
            yellowing: Amount of yellowing (0.0-1.0)
            fading: Amount of fading (0.0-1.0)
            spots: Amount of dark spots (0.0-1.0)
            
        Returns:
            Aged image
        """
        img_array = np.array(image)
        
        # Add yellowing (increase red and green, decrease blue)
        if yellowing > 0:
            yellowing_array = np.array([20, 15, -10], dtype=np.uint8) * yellowing
            img_array = np.clip(img_array + yellowing_array, 0, 255)
        
        # Add fading (reduce overall intensity)
        if fading > 0:
            fade_factor = 1.0 - (fading * 0.3)
            img_array = np.clip(img_array * fade_factor, 0, 255)
        
        # Add dark spots
        if spots > 0:
            spot_mask = np.random.random(img_array.shape[:2]) < spots * 0.05
            img_array[spot_mask] = np.clip(img_array[spot_mask] - 40, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    @staticmethod
    def add_texture_overlay(
        image: Image.Image,
        texture: Image.Image,
        opacity: float = 0.3,
        blend_mode: str = "multiply"
    ) -> Image.Image:
        """
        Add a texture overlay to the image.
        
        Args:
            image: Base image
            texture: Texture image to overlay
            opacity: Opacity of the texture (0.0-1.0)
            blend_mode: Blending mode ("multiply", "overlay", "soft_light")
            
        Returns:
            Image with texture overlay
        """
        # Ensure both images are the same size
        if texture.size != image.size:
            texture = texture.resize(image.size, Image.LANCZOS)
        
        # Convert to RGBA if needed
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        if texture.mode != 'RGBA':
            texture = texture.convert('RGBA')
        
        # Adjust texture opacity
        if opacity < 1.0:
            texture_array = np.array(texture)
            texture_array[:, :, 3] = (texture_array[:, :, 3] * opacity).astype(np.uint8)
            texture = Image.fromarray(texture_array)
        
        # Apply blend mode
        if blend_mode == "multiply":
            # Simple alpha compositing
            result = Image.alpha_composite(image, texture)
        elif blend_mode == "overlay":
            # Overlay blend mode
            result = Image.alpha_composite(image, texture)
        else:
            # Default to alpha compositing
            result = Image.alpha_composite(image, texture)
        
        return result
    
    @staticmethod
    def create_border(
        image: Image.Image,
        border_width: int = 20,
        border_color: str = "black",
        border_style: str = "solid"
    ) -> Image.Image:
        """
        Add a border around the image.
        
        Args:
            image: Input image
            border_width: Width of the border in pixels
            border_color: Color of the border
            border_style: Style of the border ("solid", "double", "decorative")
            
        Returns:
            Image with border
        """
        if border_style == "solid":
            return ImageOps.expand(image, border=border_width, fill=border_color)
        elif border_style == "double":
            # Create double border
            inner_border = ImageOps.expand(image, border=border_width//2, fill=border_color)
            outer_border = ImageOps.expand(inner_border, border=border_width//2, fill="white")
            return ImageOps.expand(outer_border, border=border_width//2, fill=border_color)
        else:
            # Default to solid border
            return ImageOps.expand(image, border=border_width, fill=border_color)
    
    @staticmethod
    def rotate_image(
        image: Image.Image,
        angle: float,
        expand: bool = True,
        fillcolor: str = "white"
    ) -> Image.Image:
        """
        Rotate an image by a given angle.
        
        Args:
            image: Input image
            angle: Rotation angle in degrees
            expand: Whether to expand the image to fit rotated content
            fillcolor: Color to fill empty areas
            
        Returns:
            Rotated image
        """
        return image.rotate(angle, expand=expand, fillcolor=fillcolor)
    
    @staticmethod
    def crop_image(
        image: Image.Image,
        crop_box: Tuple[int, int, int, int]
    ) -> Image.Image:
        """
        Crop an image to the specified box.
        
        Args:
            image: Input image
            crop_box: Crop box (left, upper, right, lower)
            
        Returns:
            Cropped image
        """
        return image.crop(crop_box)
    
    @staticmethod
    def save_image(
        image: Image.Image,
        output_path: str,
        format: str = "PNG",
        quality: int = 95
    ):
        """
        Save an image to file.
        
        Args:
            image: Image to save
            output_path: Output file path
            format: Image format
            quality: JPEG quality (1-100)
        """
        if format.upper() == "JPEG":
            image.save(output_path, format=format, quality=quality)
        else:
            image.save(output_path, format=format)
