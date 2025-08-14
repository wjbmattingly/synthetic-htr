"""
Main visualization class for displaying manuscript images and analysis results.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
from typing import List, Tuple, Dict, Any, Optional
import xml.etree.ElementTree as ET


class ManuscriptVisualizer:
    """
    Visualizes manuscript images with text polygons, analysis results, and debugging information.
    """
    
    def __init__(self, figure_size: Tuple[int, int] = (15, 10)):
        """
        Initialize the visualizer.
        
        Args:
            figure_size: Default figure size for plots
        """
        self.figure_size = figure_size
        self.colors = [
            'red', 'blue', 'green', 'orange', 'purple', 
            'brown', 'pink', 'gray', 'olive', 'cyan'
        ]
    
    def visualize_manuscript_with_polygons(
        self,
        image: Image.Image,
        polygons: List[Tuple[str, List[Tuple[int, int]]]],
        title: str = "Manuscript with Text Polygons",
        show_text: bool = True,
        polygon_color: str = 'red',
        polygon_alpha: float = 0.7,
        save_dir: Optional[str] = None,
        save_prefix: str = "manuscript",
        show_plot: bool = True
    ):
        """
        Visualize manuscript image with text polygons overlaid.
        
        Args:
            image: PIL Image of the manuscript
            polygons: List of (text, polygon_points) tuples
            title: Title for the plot
            show_text: Whether to display text labels
            polygon_color: Color for polygon outlines
            polygon_alpha: Transparency of polygons
            save_dir: Directory to save images (if None, only display)
            save_prefix: Prefix for saved image filenames
            show_plot: Whether to display the plot (if False, only save files)
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figure_size)
        
        # Original image
        ax1.imshow(image)
        ax1.set_title("Original Manuscript")
        ax1.axis('off')
        
        # Image with polygons
        ax2.imshow(image)
        
        for i, (text, polygon_points) in enumerate(polygons):
            if len(polygon_points) < 3:  # Need at least 3 points for a polygon
                continue
                
            # Create polygon patch
            polygon = patches.Polygon(
                polygon_points, 
                closed=True, 
                fill=False, 
                edgecolor=polygon_color,
                alpha=polygon_alpha,
                linewidth=1
            )
            ax2.add_patch(polygon)
            
            # Add text label if requested
            if show_text and polygon_points:
                center_x = sum(p[0] for p in polygon_points) / len(polygon_points)
                center_y = sum(p[1] for p in polygon_points) / len(polygon_points)
                
                # Only show first few words to avoid clutter
                display_text = text[:20] + "..." if len(text) > 20 else text
                ax2.text(
                    center_x, center_y, display_text, 
                    fontsize=8, ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7)
                )
        
        ax2.set_title(title)
        ax2.axis('off')
        
        plt.tight_layout()
        
        # Save images if directory specified
        if save_dir:
            import os
            os.makedirs(save_dir, exist_ok=True)
            
            # Save original image
            original_path = os.path.join(save_dir, f"{save_prefix}_original.png")
            image.save(original_path)
            
            # Save image with bounding boxes drawn
            bbox_image = self._create_bbox_image(image, polygons, polygon_color, show_text)
            bbox_path = os.path.join(save_dir, f"{save_prefix}_with_bboxes.png")
            bbox_image.save(bbox_path)
            
            # Save the matplotlib figure
            fig_path = os.path.join(save_dir, f"{save_prefix}_comparison.png")
            plt.savefig(fig_path, dpi=300, bbox_inches='tight')
            
            print(f"Saved visualization files to {save_dir}:")
            print(f"  - {original_path}")
            print(f"  - {bbox_path}")
            print(f"  - {fig_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def _create_bbox_image(
        self,
        image: Image.Image,
        polygons: List[Tuple[str, List[Tuple[int, int]]]],
        polygon_color: str = 'red',
        show_text: bool = True
    ) -> Image.Image:
        """
        Create an image with bounding boxes drawn directly on it.
        
        Args:
            image: Original image
            polygons: List of (text, polygon_points) tuples
            polygon_color: Color for bounding boxes
            show_text: Whether to show text labels
            
        Returns:
            Image with bounding boxes drawn
        """
        from PIL import ImageDraw, ImageFont
        
        # Create a copy of the image
        bbox_image = image.copy()
        draw = ImageDraw.Draw(bbox_image)
        
        # Try to load a font for text labels
        try:
            label_font = ImageFont.truetype("arial.ttf", 12)
        except:
            try:
                label_font = ImageFont.load_default()
            except:
                label_font = None
        
        # Draw bounding boxes
        for i, (text, polygon_points) in enumerate(polygons):
            if len(polygon_points) < 3:
                continue
            
            # Draw polygon outline
            if len(polygon_points) >= 2:
                # Close the polygon by adding the first point at the end
                closed_polygon = polygon_points + [polygon_points[0]]
                draw.line(closed_polygon, fill=polygon_color, width=2)
            
            # Add text label if requested
            if show_text and polygon_points and label_font:
                # Calculate center point
                center_x = sum(p[0] for p in polygon_points) / len(polygon_points)
                center_y = sum(p[1] for p in polygon_points) / len(polygon_points)
                
                # Create label (first few words or region number)
                if len(text) > 15:
                    label = f"{i+1}: {text[:12]}..."
                else:
                    label = f"{i+1}: {text}"
                
                # Draw background rectangle for text
                try:
                    bbox = draw.textbbox((center_x, center_y), label, font=label_font)
                    draw.rectangle(bbox, fill='white', outline='black')
                    draw.text((center_x, center_y), label, fill='black', font=label_font)
                except:
                    # Fallback without textbbox
                    draw.text((center_x, center_y), label, fill='black', font=label_font)
        
        return bbox_image
    
    def visualize_text_lines(
        self,
        image: Image.Image,
        text_lines: List[Dict[str, Any]],
        title: str = "Text Line Detection"
    ):
        """
        Visualize detected text lines with different colors.
        
        Args:
            image: PIL Image of the manuscript
            text_lines: List of text line dictionaries with 'polygon' and 'text' keys
            title: Title for the plot
        """
        fig, ax = plt.subplots(1, 1, figsize=self.figure_size)
        ax.imshow(image)
        
        for i, line_info in enumerate(text_lines):
            color = self.colors[i % len(self.colors)]
            polygon_points = line_info.get('polygon', [])
            text = line_info.get('text', '')
            
            if len(polygon_points) >= 3:
                polygon = patches.Polygon(
                    polygon_points,
                    closed=True,
                    fill=False,
                    edgecolor=color,
                    linewidth=2,
                    alpha=0.8
                )
                ax.add_patch(polygon)
                
                # Add line number
                if polygon_points:
                    center_x = sum(p[0] for p in polygon_points) / len(polygon_points)
                    center_y = sum(p[1] for p in polygon_points) / len(polygon_points)
                    
                    ax.text(
                        center_x, center_y, str(i+1),
                        fontsize=12, fontweight='bold',
                        ha='center', va='center',
                        color=color,
                        bbox=dict(boxstyle="circle", facecolor="white", alpha=0.8)
                    )
        
        ax.set_title(title)
        ax.axis('off')
        plt.tight_layout()
        plt.show()
    
    def compare_manuscripts(
        self,
        images: List[Image.Image],
        titles: List[str],
        subtitle: str = "Manuscript Comparison"
    ):
        """
        Compare multiple manuscript images side by side.
        
        Args:
            images: List of PIL Images
            titles: List of titles for each image
            subtitle: Overall subtitle for the comparison
        """
        num_images = len(images)
        if num_images == 0:
            return
        
        fig, axes = plt.subplots(1, num_images, figsize=(5 * num_images, 8))
        if num_images == 1:
            axes = [axes]
        
        for i, (image, title) in enumerate(zip(images, titles)):
            axes[i].imshow(image)
            axes[i].set_title(title)
            axes[i].axis('off')
        
        fig.suptitle(subtitle, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def visualize_augmentation_process(
        self,
        original_text: str,
        augmented_text: str,
        changes: List[Dict[str, Any]],
        title: str = "Text Augmentation Process"
    ):
        """
        Visualize the text augmentation process showing changes made.
        
        Args:
            original_text: Original input text
            augmented_text: Text after augmentation
            changes: List of changes made during augmentation
            title: Title for the visualization
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.axis('off')
        
        # Display original and augmented text
        text_display = f"Original: {original_text}\n\n"
        text_display += f"Augmented: {augmented_text}\n\n"
        text_display += "Changes Made:\n"
        
        for i, change in enumerate(changes):
            change_type = change.get('type', 'unknown')
            original = change.get('original', '')
            replacement = change.get('replacement', '')
            text_display += f"{i+1}. {change_type}: '{original}' → '{replacement}'\n"
        
        ax.text(0.05, 0.95, text_display, transform=ax.transAxes, 
                fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def visualize_font_comparison(
        self,
        text: str,
        font_samples: Dict[str, Image.Image],
        title: str = "Font Comparison"
    ):
        """
        Compare different fonts rendering the same text.
        
        Args:
            text: Text to display
            font_samples: Dictionary of font_name -> rendered_image
            title: Title for the comparison
        """
        num_fonts = len(font_samples)
        if num_fonts == 0:
            return
        
        fig, axes = plt.subplots(num_fonts, 1, figsize=(12, 3 * num_fonts))
        if num_fonts == 1:
            axes = [axes]
        
        for i, (font_name, image) in enumerate(font_samples.items()):
            axes[i].imshow(image)
            axes[i].set_title(f"{font_name}: {text[:50]}...")
            axes[i].axis('off')
        
        fig.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def visualize_texture_effects(
        self,
        base_image: Image.Image,
        textured_images: Dict[str, Image.Image],
        title: str = "Texture Effects Comparison"
    ):
        """
        Compare base image with different texture effects applied.
        
        Args:
            base_image: Original image without texture
            textured_images: Dictionary of texture_name -> textured_image
            title: Title for the comparison
        """
        num_textures = len(textured_images)
        
        fig, axes = plt.subplots(1, num_textures + 1, figsize=(4 * (num_textures + 1), 6))
        
        # Show base image
        axes[0].imshow(base_image)
        axes[0].set_title("Original")
        axes[0].axis('off')
        
        # Show textured images
        for i, (texture_name, image) in enumerate(textured_images.items()):
            axes[i + 1].imshow(image)
            axes[i + 1].set_title(texture_name.title())
            axes[i + 1].axis('off')
        
        fig.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    def plot_character_frequency(
        self,
        text: str,
        title: str = "Character Frequency Analysis"
    ):
        """
        Plot character frequency distribution in the text.
        
        Args:
            text: Text to analyze
            title: Title for the plot
        """
        # Count character frequencies
        char_counts = {}
        for char in text.lower():
            if char.isalpha():
                char_counts[char] = char_counts.get(char, 0) + 1
        
        # Sort by frequency
        sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_chars:
            print("No alphabetic characters found in text")
            return
        
        chars, counts = zip(*sorted_chars)
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        bars = ax.bar(chars, counts, color='steelblue', alpha=0.7)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   str(count), ha='center', va='bottom')
        
        ax.set_xlabel('Characters')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def save_complete_analysis(
        self,
        image: Image.Image,
        polygons: List[Tuple[str, List[Tuple[int, int]]]],
        alto_xml: Optional[Any] = None,
        output_dir: str = "manuscript_analysis",
        base_name: str = "manuscript",
        include_stats: bool = True,
        show_plots: bool = False
    ) -> Dict[str, str]:
        """
        Save a complete manuscript analysis with all visualization outputs.
        
        Args:
            image: Original manuscript image
            polygons: List of text polygons
            alto_xml: ALTO XML element (optional)
            output_dir: Output directory for all files
            base_name: Base name for output files
            include_stats: Whether to generate and save statistics
            show_plots: Whether to display plots (default False for batch processing)
            
        Returns:
            Dictionary mapping output type to file path
        """
        import os
        import json
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        saved_files = {}
        
        # Save original image
        original_path = os.path.join(output_dir, f"{base_name}_original.png")
        image.save(original_path)
        saved_files['original'] = original_path
        
        # Save image with bounding boxes
        bbox_image = self._create_bbox_image(image, polygons, 'red', True)
        bbox_path = os.path.join(output_dir, f"{base_name}_with_bboxes.png")
        bbox_image.save(bbox_path)
        saved_files['bboxes'] = bbox_path
        
        # Save different colored versions
        colors = ['blue', 'green', 'purple']
        for i, color in enumerate(colors):
            colored_bbox_image = self._create_bbox_image(image, polygons, color, False)
            colored_path = os.path.join(output_dir, f"{base_name}_bboxes_{color}.png")
            colored_bbox_image.save(colored_path)
            saved_files[f'bboxes_{color}'] = colored_path
        
        # Save comparison figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12))
        
        ax1.imshow(image)
        ax1.set_title("Original Manuscript", fontsize=16)
        ax1.axis('off')
        
        ax2.imshow(bbox_image)
        ax2.set_title("With Text Detection Boxes", fontsize=16)
        ax2.axis('off')
        
        plt.tight_layout()
        comparison_path = os.path.join(output_dir, f"{base_name}_comparison.png")
        plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
        if not show_plots:
            plt.close()
        saved_files['comparison'] = comparison_path
        
        # Save ALTO XML if provided
        if alto_xml is not None:
            from xml.etree.ElementTree import tostring
            import xml.dom.minidom as minidom
            
            xml_path = os.path.join(output_dir, f"{base_name}.xml")
            rough_string = tostring(alto_xml, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            with open(xml_path, "w", encoding="utf-8") as f:
                f.write(reparsed.toprettyxml(indent="  "))
            saved_files['alto_xml'] = xml_path
        
        # Save polygon data as JSON
        polygons_data = {
            'image_size': image.size,
            'total_regions': len(polygons),
            'regions': [
                {
                    'id': i,
                    'text': text,
                    'polygon': polygon_points,
                    'bbox': {
                        'left': min(p[0] for p in polygon_points),
                        'top': min(p[1] for p in polygon_points),
                        'right': max(p[0] for p in polygon_points),
                        'bottom': max(p[1] for p in polygon_points)
                    } if polygon_points else None
                }
                for i, (text, polygon_points) in enumerate(polygons)
            ]
        }
        
        json_path = os.path.join(output_dir, f"{base_name}_polygons.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(polygons_data, f, indent=2, ensure_ascii=False)
        saved_files['polygons_json'] = json_path
        
        # Generate and save statistics if requested
        if include_stats and polygons:
            from ..visualization.ocr_analyzer import OCRAnalyzer
            analyzer = OCRAnalyzer()
            analysis = analyzer.analyze_text_distribution(polygons, image.width, image.height)
            
            # Create statistics plot
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # Text coverage
            coverage_data = [
                analysis.get('text_coverage', {}).get('horizontal', {}).get('coverage_ratio', 0),
                analysis.get('text_coverage', {}).get('vertical', {}).get('coverage_ratio', 0)
            ]
            ax1.bar(['Horizontal', 'Vertical'], coverage_data, color=['skyblue', 'lightcoral'])
            ax1.set_title('Text Coverage Ratios')
            ax1.set_ylabel('Coverage Ratio')
            ax1.set_ylim(0, 1)
            
            # Line heights
            line_stats = analysis.get('line_statistics', {})
            heights = ['Min', 'Average', 'Max']
            height_values = [
                line_stats.get('min_height', 0),
                line_stats.get('average_height', 0),
                line_stats.get('max_height', 0)
            ]
            ax2.bar(heights, height_values, color='lightgreen')
            ax2.set_title('Line Height Statistics')
            ax2.set_ylabel('Height (pixels)')
            
            # Region count
            ax3.bar(['Total Regions'], [len(polygons)], color='orange')
            ax3.set_title('Number of Text Regions')
            ax3.set_ylabel('Count')
            
            # Text area
            total_area = analysis.get('area_statistics', {}).get('total_text_area', 0)
            ax4.bar(['Total Area'], [total_area], color='purple')
            ax4.set_title('Total Text Area')
            ax4.set_ylabel('Area (pixels²)')
            
            plt.suptitle('Manuscript Analysis Statistics', fontsize=16)
            plt.tight_layout()
            
            stats_path = os.path.join(output_dir, f"{base_name}_statistics.png")
            plt.savefig(stats_path, dpi=300, bbox_inches='tight')
            if not show_plots:
                plt.close()
            saved_files['statistics'] = stats_path
            
            # Save statistics as JSON
            stats_json_path = os.path.join(output_dir, f"{base_name}_analysis.json")
            with open(stats_json_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2)
            saved_files['analysis_json'] = stats_json_path
        
        # Create summary report
        summary_path = os.path.join(output_dir, f"{base_name}_summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"Manuscript Analysis Summary\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Base name: {base_name}\n")
            f.write(f"Image size: {image.size[0]} x {image.size[1]} pixels\n")
            f.write(f"Total text regions: {len(polygons)}\n")
            f.write(f"Generated files:\n\n")
            
            for file_type, file_path in saved_files.items():
                f.write(f"  {file_type}: {os.path.basename(file_path)}\n")
            
            if polygons:
                f.write(f"\nText Regions:\n")
                for i, (text, _) in enumerate(polygons[:10]):  # Show first 10
                    preview = text[:50] + "..." if len(text) > 50 else text
                    f.write(f"  {i+1}: {preview}\n")
                if len(polygons) > 10:
                    f.write(f"  ... and {len(polygons) - 10} more regions\n")
        
        saved_files['summary'] = summary_path
        
        print(f"\n=== Complete Analysis Saved ===")
        print(f"Output directory: {output_dir}")
        print(f"Files generated: {len(saved_files)}")
        for file_type, file_path in saved_files.items():
            print(f"  {file_type}: {os.path.basename(file_path)}")
        
        return saved_files
    
    def save_visualization(
        self,
        figure: plt.Figure,
        filename: str,
        dpi: int = 300,
        format: str = 'png'
    ):
        """
        Save a matplotlib figure to file.
        
        Args:
            figure: Matplotlib figure to save
            filename: Output filename
            dpi: DPI for the saved image
            format: Image format (png, jpg, pdf, etc.)
        """
        figure.savefig(filename, dpi=dpi, format=format, bbox_inches='tight')
        print(f"Visualization saved to: {filename}")
