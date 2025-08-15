"""
OCR analysis and visualization utilities for manuscript analysis.
Enhanced with advanced typography features for better manuscript rendering.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import List, Tuple, Dict, Any, Optional
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Import advanced typography features
try:
    from ..typography import AdvancedFontManager, ColorFontRenderer, LetterformVariationEngine
    ADVANCED_TYPOGRAPHY_AVAILABLE = True
except ImportError:
    ADVANCED_TYPOGRAPHY_AVAILABLE = False
    print("Advanced typography features not available for OCR analyzer.")


class OCRAnalyzer:
    """
    Analyzes and visualizes OCR-related data for synthetic manuscripts.
    """
    
    def __init__(self, use_advanced_typography: bool = True):
        """
        Initialize the OCR analyzer.
        
        Args:
            use_advanced_typography: Whether to use advanced typography features
        """
        self.alto_namespace = "http://www.loc.gov/standards/alto/ns-v4#"
        self.use_advanced_typography = use_advanced_typography and ADVANCED_TYPOGRAPHY_AVAILABLE
        
        # Initialize advanced typography components if available
        if self.use_advanced_typography:
            self.font_manager = AdvancedFontManager()
            self.color_renderer = ColorFontRenderer()
            self.variation_engine = LetterformVariationEngine()
        else:
            self.font_manager = None
            self.color_renderer = None
            self.variation_engine = None
    
    def generate_synthetic_ocr_data(
        self,
        text: str,
        width: int = 1200,
        height: int = 1600,
        font_size: int = 20,
        font_path: str = None,
        num_columns: int = 1,
        marginalia: bool = False,
        marginalia_probability: float = 0.2,
        curve_amount: float = 0.0,
        heading_lines: int = 0,
        margin_size: int = 100,
        word_spacing_factor: float = 1.0,
        texture_name: str = None,
        ink_opacity_range: Tuple[float, float] = (0.7, 0.9),
        ink_color_variation: bool = True,
        add_noise: bool = True,
        original_text: str = None,
        # New advanced typography parameters
        medieval_font: str = "cerne",
        color_scheme: str = "cerne",
        use_color_layers: bool = False,
        use_letterform_variations: bool = True,
        writing_speed: str = "normal",
        formality: str = "formal",
        fatigue_level: str = "fresh",
        illumination_level: str = "simple"
    ) -> Tuple[Image.Image, List[Tuple[str, List[Tuple[int, int]]]], ET.Element]:
        """
        Generate synthetic OCR data with text polygons and ALTO XML.
        Enhanced with advanced typography features for authentic medieval appearance.
        
        Args:
            text: Input text to render
            width: Image width
            height: Image height
            font_size: Font size for rendering
            font_path: Path to font file (fallback if advanced typography unavailable)
            num_columns: Number of text columns
            marginalia: Whether to add marginal notes
            marginalia_probability: Probability of adding marginalia
            curve_amount: Amount of text curvature (0.0-1.0)
            heading_lines: Number of heading lines
            margin_size: Size of page margins in pixels
            word_spacing_factor: Multiplier for word spacing (0.5 = closer, 1.5 = farther)
            texture_name: Name of texture to apply (None for no texture)
            ink_opacity_range: Range of opacity values for ink (min, max)
            ink_color_variation: Whether to use brownish-black ink colors
            add_noise: Whether to add minimal noise to the image
            original_text: Original text before abbreviations (for XML output)
            medieval_font: Medieval font to use ("cerne", "junicode", "medieval", "vitor")
            color_scheme: Color scheme for rendering ("cerne", "kells", "lindisfarne", "winchester")
            use_color_layers: Whether to use color font rendering with multiple layers
            use_letterform_variations: Whether to apply natural letterform variations
            writing_speed: Speed of writing ("careful", "normal", "hasty")
            formality: Level of formality ("formal", "informal")
            fatigue_level: Scribe fatigue level ("fresh", "tired", "exhausted")
            illumination_level: Level of illumination for capitals ("simple", "ornate", "historiated")
            
        Returns:
            Tuple of (image, polygons, alto_xml)
        """
        # Create a blank white image
        image = Image.new('RGB', (width, height), color='white')
        
        # Apply texture if specified
        if texture_name:
            try:
                from ..generator.texture_manager import TextureManager
                texture_manager = TextureManager()
                image = texture_manager.apply_texture(image, texture_name, opacity=0.3)
            except ImportError:
                print(f"Warning: Could not import TextureManager, skipping texture application")
            except Exception as e:
                print(f"Warning: Could not apply texture '{texture_name}': {e}")
        
        # Generate ink color and opacity for this page
        if ink_color_variation:
            # Generate more brownish ink color
            base_darkness = random.randint(20, 50)  # Dark base
            brown_boost = random.randint(15, 30)    # More brown tint
            ink_color = (
                base_darkness + brown_boost,            # Red component (more brownish)
                base_darkness + random.randint(5, 15), # Green component (warmer)
                base_darkness - random.randint(5, 15)  # Blue component (much less blue)
            )
        else:
            ink_color = (0, 0, 0)  # Pure black
        
        # Random opacity for this page
        ink_opacity = random.uniform(ink_opacity_range[0], ink_opacity_range[1])
        
        draw = ImageDraw.Draw(image)
        
        # Try to use Cerne color font rendering first
        cerne_color_image = self._render_with_cerne_colors(
            text, font_size, width, height
        )
        
        if cerne_color_image:
            print("✅ Using Cerne color font rendering")
            # Process the color image and return results
            return self._process_cerne_color_image(
                cerne_color_image, text, original_text, width, height,
                background_texture, parchment_color, ink_color, 
                add_noise, noise_strength, add_aging, aging_strength
            )
        
        # Fallback to regular font rendering
        print("⚠️ Falling back to regular font rendering")
        
        # Load fonts - prioritize Cerne font if available
        cerne_font_paths = [
            "/Users/wjm55/yale/Cerne-font/fonts/Cerne.otf",
            "/Users/wjm55/yale/Cerne-font/fonts/Cerne.woff2",
            "/Users/wjm55/yale/synthetic-htr/synthetic_htr/fonts/Cerne.otf",
            font_path  # User-provided fallback
        ]
        
        font = None
        heading_font = None
        
        # Try to load Cerne font first
        for cerne_path in cerne_font_paths:
            if cerne_path and os.path.exists(cerne_path):
                try:
                    font = ImageFont.truetype(cerne_path, font_size)
                    heading_font = ImageFont.truetype(cerne_path, int(font_size * 1.5))
                    print(f"✅ Using Cerne font from: {cerne_path}")
                    break
                except Exception as e:
                    print(f"Failed to load Cerne font from {cerne_path}: {e}")
                    continue
        
        # Fallback to other fonts if Cerne not available
        if font is None:
            font, heading_font = self._load_fallback_fonts(font_path, font_size)
            print("Using fallback fonts")
        
        # Calculate layout parameters
        # Calculate layout dimensions with custom margins
        main_width = width - (2 * margin_size)  # Account for left and right margins
        margin_width = width - main_width  # Marginalia takes the remaining space
        column_width = main_width // num_columns
        
        # Split text into words
        words = text.split()
        
        # Create word mapping between original and abbreviated text if original_text is provided
        word_mapping = {}
        if original_text:
            original_words = original_text.split()
            # Simple mapping assuming words correspond by position (this is approximate)
            for i, (orig_word, abbrev_word) in enumerate(zip(original_words, words)):
                word_mapping[abbrev_word] = orig_word
        
        # Initialize variables with custom margins
        x, y = margin_size, margin_size
        line_height = font_size + 5
        current_column = 0
        text_polygons = []
        current_line = []
        line_start_y = y
        
        # Initialize ALTO XML structure
        alto = ET.Element("alto", xmlns=self.alto_namespace)
        layout = ET.SubElement(alto, "Layout")
        page = ET.SubElement(layout, "Page", 
                           ID="PAGE_0001", 
                           PHYSICAL_IMG_NR="1", 
                           HEIGHT=str(height), 
                           WIDTH=str(width))
        print_space = ET.SubElement(page, "PrintSpace", ID="PS_0001")
        current_text_block = ET.SubElement(print_space, "TextBlock", ID="TB_0001")
        
        def add_curved_line_polygon(line_text, start_x, start_y, block_id):
            """Add a curved text line with polygon coordinates."""
            # Get text dimensions (handle both old and new PIL versions)
            try:
                bbox = draw.textbbox((start_x, start_y), line_text, font=font)
                line_width = bbox[2] - bbox[0]
                line_height_actual = bbox[3] - bbox[1]
            except AttributeError:
                # Fallback for older PIL versions
                try:
                    line_width, line_height_actual = draw.textsize(line_text, font=font)
                except AttributeError:
                    # Ultimate fallback
                    line_width = len(line_text) * 10
                    line_height_actual = 20
            
            if line_width == 0:
                return
            
            # Calculate curve
            curve_points = np.linspace(0, np.pi, max(line_width, 1))
            curve = np.sin(curve_points) * curve_amount * font_size
            
            # Draw curved text
            char_positions = []
            char_width = line_width / len(line_text) if line_text else 1
            
            for i, char in enumerate(line_text):
                char_x = start_x + i * char_width
                char_y = start_y + curve[min(i * len(curve) // len(line_text), len(curve) - 1)]
                
                # Use Cerne-inspired colors for better medieval appearance
                if "Cerne" in str(getattr(font, 'path', '')) or medieval_font == "cerne":
                    # Use Cerne-inspired brown ink color
                    cerne_brown = (101, 67, 33)  # Dark reddish brown from Cerne palette
                    char_color = cerne_brown
                else:
                    # Apply slight random variation to ink opacity per character
                    char_opacity_variation = random.uniform(0.95, 1.05)
                    char_opacity = min(1.0, ink_opacity * char_opacity_variation)
                    
                    # Create color with opacity
                    char_color = tuple(int(c * char_opacity) for c in ink_color)
                
                draw.text((char_x, char_y), char, fill=char_color, font=font)
                char_positions.append((char_x, char_y))
            
            # Create polygon points
            polygon_points = []
            
            # Top edge of text
            for i in range(0, line_width, max(1, line_width // 20)):
                idx = min(i * len(curve) // line_width, len(curve) - 1)
                polygon_points.append((start_x + i, start_y + curve[idx]))
            
            # Bottom edge of text (reversed)
            for i in range(line_width-1, -1, -max(1, line_width // 20)):
                idx = min(i * len(curve) // line_width, len(curve) - 1)
                polygon_points.append((start_x + i, start_y + curve[idx] + line_height_actual))
            
            text_polygons.append((line_text, polygon_points))
            
            # Add line to ALTO XML
            text_line = ET.SubElement(current_text_block, "TextLine", ID=f"TL_{str(block_id).zfill(4)}")
            coords = " ".join([f"{int(x)},{int(y)}" for x, y in polygon_points])
            ET.SubElement(text_line, "Coords", POINTS=coords)
            
            # Create original content for this line if mapping exists
            original_line_text = line_text
            if word_mapping:
                line_words = line_text.split()
                original_words = [word_mapping.get(word, word) for word in line_words]
                original_line_text = " ".join(original_words)
            
            string_elem = ET.SubElement(text_line, "String", 
                                      CONTENT=line_text,  # Abbreviated form (what's displayed)
                                      HEIGHT=str(int(line_height_actual)),
                                      WIDTH=str(int(line_width)),
                                      HPOS=str(int(start_x)),
                                      VPOS=str(int(start_y)))
            
            # Add original transcription as a custom attribute if different from abbreviated
            if original_line_text != line_text:
                string_elem.set("ORIGINAL_CONTENT", original_line_text)
        
        # Add headings if requested
        block_counter = 1
        if heading_lines > 0:
            heading_text = " ".join(words[:heading_lines * 5])  # Approximate words per heading
            y += int(font_size * 0.5)  # Extra space before heading
            add_curved_line_polygon(heading_text, margin_size, y, block_counter)
            block_counter += 1
            y += line_height * 2  # Extra space after heading
            words = words[heading_lines * 5:]  # Remove heading words
        
        # Process main text
        for word in words:
            bbox = draw.textbbox((x, y), word, font=font)
            word_width = bbox[2] - bbox[0]
            
            # Check if word fits on current line
            if x + word_width > (current_column + 1) * column_width + margin_size - margin_size:
                # Draw the current line
                if current_line:
                    line_text = " ".join(current_line)
                    add_curved_line_polygon(line_text, (column_width * current_column) + margin_size, 
                                          line_start_y, block_counter)
                    block_counter += 1
                    current_line.clear()
                
                # Move to the next line
                x = (column_width * current_column) + margin_size
                y += line_height
                line_start_y = y
                
                # Check if we need to move to next column
                if y + line_height > height - margin_size:
                    current_column += 1
                    if current_column >= num_columns:
                        break
                    x = (column_width * current_column) + margin_size
                    y = margin_size
                    line_start_y = y
                    current_text_block = ET.SubElement(print_space, "TextBlock", 
                                                     ID=f"TB_{current_column+1:04d}")
            
            current_line.append(word)
            x += word_width + int((font_size // 2) * word_spacing_factor)
        
        # Draw any remaining words in the last line
        if current_line:
            line_text = " ".join(current_line)
            add_curved_line_polygon(line_text, (column_width * current_column) + margin_size, 
                                  line_start_y, block_counter)
        
        # Add marginalia if requested
        if marginalia and words:
            margin_x = main_width + margin_size
            margin_y = margin_size
            margin_lines = []
            marginalia_block = ET.SubElement(print_space, "TextBlock", ID="TB_MARG")
            
            # Select random words for marginalia
            num_margin_notes = int(len(words) * marginalia_probability)
            for _ in range(num_margin_notes):
                if words:
                    margin_text = np.random.choice(words)
                    margin_lines.append(margin_text)
                
                if len(margin_lines) * line_height > height - margin_size:
                    break
            
            # Draw marginalia
            for i, margin_text in enumerate(margin_lines):
                add_curved_line_polygon(margin_text, margin_x, margin_y, f"MARG_{str(i+1).zfill(4)}")
                margin_y += line_height
        
        # Apply minimal noise if requested
        if add_noise:
            image = self._add_minimal_noise(image)
        
        return image, text_polygons, alto
    
    def _load_fallback_fonts(self, font_path: str, font_size: int) -> Tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
        """Load fallback fonts when advanced typography is not available."""
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
                heading_font = ImageFont.truetype(font_path, int(font_size * 1.5))
            else:
                font = ImageFont.load_default()
                heading_font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
            heading_font = ImageFont.load_default()
        
        return font, heading_font
    
    def _render_text_with_advanced_typography(
        self,
        draw: ImageDraw.Draw,
        text: str,
        position: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        medieval_font: str,
        color_scheme: str,
        use_color_layers: bool,
        illumination_level: str
    ) -> List[Tuple[int, int, int, int]]:
        """Render text using advanced typography features."""
        if not self.use_advanced_typography or not self.color_renderer:
            # Fallback to basic rendering
            draw.text(position, text, font=font, fill=(0, 0, 0))
            try:
                bbox = draw.textbbox(position, text, font=font)
            except AttributeError:
                w, h = draw.textsize(text, font=font)
                bbox = (position[0], position[1], position[0] + w, position[1] + h)
            return [bbox]
        
        # Use advanced color font rendering
        return self.color_renderer.render_color_text(
            draw=draw,
            text=text,
            position=position,
            font=font,
            color_scheme=color_scheme,
            illumination_level=illumination_level,
            context="religious",
            add_backgrounds=use_color_layers
        )
    
    def _add_minimal_noise(self, image: Image.Image) -> Image.Image:
        """
        Add minimal random noise to simulate paper imperfections and aging.
        
        Args:
            image: Input image
            
        Returns:
            Image with added noise
        """
        # Convert to numpy array for noise manipulation
        img_array = np.array(image)
        
        # Generate very subtle noise (much smaller range than typical)
        noise_intensity = random.uniform(0.5, 2.0)  # Very low intensity
        noise = np.random.normal(0, noise_intensity, img_array.shape).astype(np.int16)
        
        # Apply noise only to a small percentage of pixels
        noise_mask = np.random.random(img_array.shape[:2]) < 0.1  # Only 10% of pixels get noise
        
        # Apply noise with clipping to valid range
        noisy_array = img_array.astype(np.int16) + noise
        noisy_array = np.clip(noisy_array, 0, 255).astype(np.uint8)
        
        # Apply the mask so only some pixels are affected
        for channel in range(img_array.shape[2]):
            img_array[:, :, channel] = np.where(
                noise_mask, 
                noisy_array[:, :, channel], 
                img_array[:, :, channel]
            )
        
        # Add some very subtle dust specks
        if random.random() < 0.3:  # 30% chance of dust
            num_specks = random.randint(1, 5)
            for _ in range(num_specks):
                x = random.randint(0, img_array.shape[1] - 1)
                y = random.randint(0, img_array.shape[0] - 1)
                speck_size = random.randint(1, 2)
                speck_color = random.randint(200, 240)  # Light gray specks
                
                # Create small speck
                for dx in range(-speck_size, speck_size + 1):
                    for dy in range(-speck_size, speck_size + 1):
                        if (0 <= x + dx < img_array.shape[1] and 
                            0 <= y + dy < img_array.shape[0]):
                            if img_array.shape[2] == 4:  # RGBA
                                img_array[y + dy, x + dx] = [speck_color, speck_color, speck_color, 255]
                            else:  # RGB
                                img_array[y + dy, x + dx] = [speck_color, speck_color, speck_color]
        
        return Image.fromarray(img_array)
    
    def visualize_ocr_results(
        self,
        image: Image.Image,
        polygons: List[Tuple[str, List[Tuple[int, int]]]],
        title: str = "OCR Analysis Results"
    ):
        """
        Visualize OCR results with text polygons.
        
        Args:
            image: Original manuscript image
            polygons: List of (text, polygon_points) tuples
            title: Title for the visualization
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12))
        
        # Display original image
        ax1.imshow(image)
        ax1.set_title("Original Image")
        ax1.axis('off')
        
        # Display image with polygons
        ax2.imshow(image)
        for i, (text, poly) in enumerate(polygons):
            if len(poly) >= 3:
                x_coords, y_coords = zip(*poly)
                ax2.plot(list(x_coords) + [x_coords[0]], 
                        list(y_coords) + [y_coords[0]], 
                        'r-', linewidth=1, alpha=0.8)
                
                # Add text labels for first few polygons to avoid clutter
                if i < 10:
                    center_x = sum(x_coords) / len(x_coords)
                    center_y = sum(y_coords) / len(y_coords)
                    ax2.text(center_x, center_y, str(i+1), 
                           fontsize=8, ha='center', va='center',
                           bbox=dict(boxstyle="circle", facecolor="yellow", alpha=0.7))
        
        ax2.set_title("Image with Text Polygons")
        ax2.axis('off')
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def save_alto_xml(
        self,
        alto: ET.Element,
        filename: str
    ):
        """
        Save ALTO XML to file with proper formatting.
        
        Args:
            alto: ALTO XML element tree
            filename: Output filename
        """
        # Convert to string and reparse for pretty printing
        rough_string = ET.tostring(alto, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(reparsed.toprettyxml(indent="  "))
        
        print(f"ALTO XML saved to: {filename}")
    
    def analyze_text_distribution(
        self,
        polygons: List[Tuple[str, List[Tuple[int, int]]]],
        image_width: int,
        image_height: int
    ) -> Dict[str, Any]:
        """
        Analyze the distribution of text across the manuscript page.
        
        Args:
            polygons: List of text polygons
            image_width: Width of the manuscript image
            image_height: Height of the manuscript image
            
        Returns:
            Dictionary with analysis results
        """
        if not polygons:
            return {}
        
        # Calculate text region statistics
        all_x_coords = []
        all_y_coords = []
        line_heights = []
        text_areas = []
        
        for text, polygon_points in polygons:
            if len(polygon_points) >= 3:
                x_coords = [p[0] for p in polygon_points]
                y_coords = [p[1] for p in polygon_points]
                
                all_x_coords.extend(x_coords)
                all_y_coords.extend(y_coords)
                
                # Calculate approximate line height and area
                min_y, max_y = min(y_coords), max(y_coords)
                min_x, max_x = min(x_coords), max(x_coords)
                
                line_heights.append(max_y - min_y)
                text_areas.append((max_x - min_x) * (max_y - min_y))
        
        # Calculate statistics
        analysis = {
            'total_text_regions': len(polygons),
            'text_coverage': {
                'horizontal': {
                    'min': min(all_x_coords) if all_x_coords else 0,
                    'max': max(all_x_coords) if all_x_coords else 0,
                    'span': max(all_x_coords) - min(all_x_coords) if all_x_coords else 0,
                    'coverage_ratio': (max(all_x_coords) - min(all_x_coords)) / image_width if all_x_coords else 0
                },
                'vertical': {
                    'min': min(all_y_coords) if all_y_coords else 0,
                    'max': max(all_y_coords) if all_y_coords else 0,
                    'span': max(all_y_coords) - min(all_y_coords) if all_y_coords else 0,
                    'coverage_ratio': (max(all_y_coords) - min(all_y_coords)) / image_height if all_y_coords else 0
                }
            },
            'line_statistics': {
                'average_height': np.mean(line_heights) if line_heights else 0,
                'height_std': np.std(line_heights) if line_heights else 0,
                'min_height': min(line_heights) if line_heights else 0,
                'max_height': max(line_heights) if line_heights else 0
            },
            'area_statistics': {
                'total_text_area': sum(text_areas),
                'average_area': np.mean(text_areas) if text_areas else 0,
                'area_std': np.std(text_areas) if text_areas else 0
            }
        }
        
        return analysis
    
    def plot_text_distribution(
        self,
        analysis: Dict[str, Any],
        title: str = "Text Distribution Analysis"
    ):
        """
        Plot text distribution statistics.
        
        Args:
            analysis: Analysis results from analyze_text_distribution
            title: Title for the plot
        """
        if not analysis:
            print("No analysis data to plot")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Coverage ratios
        coverage_data = [
            analysis['text_coverage']['horizontal']['coverage_ratio'],
            analysis['text_coverage']['vertical']['coverage_ratio']
        ]
        coverage_labels = ['Horizontal', 'Vertical']
        
        ax1.bar(coverage_labels, coverage_data, color=['skyblue', 'lightcoral'])
        ax1.set_title('Text Coverage Ratios')
        ax1.set_ylabel('Coverage Ratio')
        ax1.set_ylim(0, 1)
        
        # Line height distribution (if available)
        if 'line_statistics' in analysis:
            line_stats = analysis['line_statistics']
            heights = ['Min', 'Average', 'Max']
            height_values = [
                line_stats['min_height'],
                line_stats['average_height'],
                line_stats['max_height']
            ]
            
            ax2.bar(heights, height_values, color='lightgreen')
            ax2.set_title('Line Height Statistics')
            ax2.set_ylabel('Height (pixels)')
        
        # Text regions count
        ax3.bar(['Total Regions'], [analysis['total_text_regions']], color='orange')
        ax3.set_title('Number of Text Regions')
        ax3.set_ylabel('Count')
        
        # Total text area
        if 'area_statistics' in analysis:
            ax4.bar(['Total Area'], [analysis['area_statistics']['total_text_area']], color='purple')
            ax4.set_title('Total Text Area')
            ax4.set_ylabel('Area (pixels²)')
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def _render_with_cerne_colors(self, text: str, font_size: int, width: int, height: int):
        """
        Render text using Cerne color font via BlackRenderer SVG.
        
        Args:
            text: Text to render
            font_size: Font size in pixels
            width: Target image width
            height: Target image height
            
        Returns:
            PIL Image with color rendering, or None if failed
        """
        try:
            import subprocess
            import tempfile
            
            # Find Cerne font
            cerne_paths = [
                "/Users/wjm55/yale/Cerne-font/fonts/Cerne.otf",
                "/Users/wjm55/yale/synthetic-htr/synthetic_htr/fonts/Cerne.otf",
                "synthetic_htr/fonts/Cerne.otf"
            ]
            
            cerne_font_path = None
            for path in cerne_paths:
                if os.path.exists(path):
                    cerne_font_path = path
                    break
            
            if not cerne_font_path:
                return None
            
            # Create temporary SVG file
            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_svg:
                svg_path = tmp_svg.name
            
            # Use BlackRenderer to create SVG
            cmd = [
                'blackrenderer',
                cerne_font_path,
                text,
                svg_path,
                '--font-size', str(font_size),
                '--backend', 'svg'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return None
            
            # Convert SVG to PIL Image
            if os.path.exists(svg_path):
                try:
                     # Try rsvg-convert first (preserves colors better)
                     try:
                         import subprocess
                         import tempfile
                         
                         # Create temporary PNG file
                         with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
                             png_path = tmp_png.name
                         
                         # Use rsvg-convert to convert SVG to PNG
                         convert_cmd = ['rsvg-convert', '-o', png_path, svg_path]
                         convert_result = subprocess.run(convert_cmd, capture_output=True)
                         
                         if convert_result.returncode == 0:
                             image = Image.open(png_path)
                             os.unlink(png_path)  # Clean up temp PNG
                         else:
                             # Fallback: try cairosvg if rsvg-convert fails
                             try:
                                 import cairosvg
                                 import io
                                 png_data = cairosvg.svg2png(url=svg_path)
                                 image = Image.open(io.BytesIO(png_data))
                             except ImportError:
                                 # Final fallback: return None to use regular rendering
                                 os.unlink(svg_path)
                                 return None
