"""
Utility functions for plotting and visualization.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
from typing import List, Tuple, Dict, Any, Optional
import seaborn as sns


class PlotUtils:
    """
    Utility functions for creating various plots and visualizations.
    """
    
    @staticmethod
    def setup_matplotlib_style(style: str = 'default'):
        """
        Setup matplotlib style for consistent plotting.
        
        Args:
            style: Style name ('default', 'seaborn', 'classic', etc.)
        """
        if style == 'seaborn':
            try:
                sns.set_style("whitegrid")
                plt.rcParams['figure.figsize'] = (12, 8)
                plt.rcParams['font.size'] = 12
            except ImportError:
                print("Seaborn not available, using default style")
                plt.style.use('default')
        else:
            plt.style.use(style)
    
    @staticmethod
    def create_color_palette(n_colors: int, palette: str = 'tab10') -> List[str]:
        """
        Create a color palette with specified number of colors.
        
        Args:
            n_colors: Number of colors needed
            palette: Palette name ('tab10', 'Set1', 'viridis', etc.)
            
        Returns:
            List of color codes
        """
        if palette == 'tab10':
            base_colors = plt.cm.tab10(np.linspace(0, 1, 10))
        elif palette == 'Set1':
            base_colors = plt.cm.Set1(np.linspace(0, 1, 9))
        elif palette == 'viridis':
            base_colors = plt.cm.viridis(np.linspace(0, 1, n_colors))
        else:
            base_colors = plt.cm.get_cmap(palette)(np.linspace(0, 1, n_colors))
        
        # Extend colors if needed
        colors = []
        for i in range(n_colors):
            color_idx = i % len(base_colors)
            colors.append(base_colors[color_idx])
        
        return colors
    
    @staticmethod
    def plot_text_metrics(
        metrics: Dict[str, float],
        title: str = "Text Metrics",
        figsize: Tuple[int, int] = (10, 6)
    ):
        """
        Plot various text metrics as a bar chart.
        
        Args:
            metrics: Dictionary of metric_name -> value
            title: Plot title
            figsize: Figure size
        """
        if not metrics:
            print("No metrics to plot")
            return
        
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        
        metric_names = list(metrics.keys())
        values = list(metrics.values())
        
        bars = ax.bar(metric_names, values, color='steelblue', alpha=0.7)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{value:.2f}', ha='center', va='bottom')
        
        ax.set_title(title)
        ax.set_ylabel('Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_character_distribution(
        text: str,
        title: str = "Character Distribution",
        top_n: int = 20,
        figsize: Tuple[int, int] = (12, 6),
        show_plot: bool = True
    ):
        """
        Plot character frequency distribution.
        
        Args:
            text: Text to analyze
            title: Plot title
            top_n: Number of top characters to show
            figsize: Figure size
            show_plot: Whether to display the plot
        """
        # Count character frequencies
        char_counts = {}
        for char in text.lower():
            if char.isalnum() or char in '.,;:!?':
                char_counts[char] = char_counts.get(char, 0) + 1
        
        # Sort by frequency and take top N
        sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        if not sorted_chars:
            print("No characters found to plot")
            return
        
        chars, counts = zip(*sorted_chars)
        
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        bars = ax.bar(chars, counts, color='darkgreen', alpha=0.7)
        
        # Add value labels
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   str(count), ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Characters')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    @staticmethod
    def plot_word_length_distribution(
        text: str,
        title: str = "Word Length Distribution",
        figsize: Tuple[int, int] = (10, 6),
        show_plot: bool = True
    ):
        """
        Plot distribution of word lengths.
        
        Args:
            text: Text to analyze
            title: Plot title
            figsize: Figure size
            show_plot: Whether to display the plot
        """
        words = text.split()
        word_lengths = [len(word.strip('.,;:!?()[]{}')) for word in words]
        
        if not word_lengths:
            print("No words found to plot")
            return
        
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        
        # Create histogram
        n, bins, patches = ax.hist(word_lengths, bins=range(1, max(word_lengths) + 2), 
                                  alpha=0.7, color='purple', edgecolor='black')
        
        # Add statistics
        mean_length = np.mean(word_lengths)
        median_length = np.median(word_lengths)
        
        ax.axvline(mean_length, color='red', linestyle='--', 
                  label=f'Mean: {mean_length:.1f}')
        ax.axvline(median_length, color='orange', linestyle='--', 
                  label=f'Median: {median_length:.1f}')
        
        ax.set_xlabel('Word Length (characters)')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    @staticmethod
    def plot_line_spacing_analysis(
        polygons: List[Tuple[str, List[Tuple[int, int]]]],
        title: str = "Line Spacing Analysis",
        figsize: Tuple[int, int] = (10, 6)
    ):
        """
        Analyze and plot line spacing in text polygons.
        
        Args:
            polygons: List of text polygons
            title: Plot title
            figsize: Figure size
        """
        if len(polygons) < 2:
            print("Need at least 2 text lines for spacing analysis")
            return
        
        # Calculate vertical centers of each line
        line_centers = []
        for text, polygon_points in polygons:
            if polygon_points:
                y_coords = [p[1] for p in polygon_points]
                center_y = sum(y_coords) / len(y_coords)
                line_centers.append(center_y)
        
        line_centers.sort()
        
        # Calculate spacing between consecutive lines
        spacings = []
        for i in range(1, len(line_centers)):
            spacing = line_centers[i] - line_centers[i-1]
            spacings.append(spacing)
        
        if not spacings:
            print("No line spacings calculated")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Histogram of spacings
        ax1.hist(spacings, bins=20, alpha=0.7, color='teal', edgecolor='black')
        ax1.set_xlabel('Line Spacing (pixels)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Distribution of Line Spacings')
        ax1.grid(axis='y', alpha=0.3)
        
        # Line plot showing spacing over lines
        ax2.plot(range(len(spacings)), spacings, 'o-', color='darkred', alpha=0.7)
        ax2.set_xlabel('Line Number')
        ax2.set_ylabel('Spacing to Next Line (pixels)')
        ax2.set_title('Line Spacing Variation')
        ax2.grid(alpha=0.3)
        
        # Add statistics
        mean_spacing = np.mean(spacings)
        std_spacing = np.std(spacings)
        ax2.axhline(mean_spacing, color='blue', linestyle='--', 
                   label=f'Mean: {mean_spacing:.1f}±{std_spacing:.1f}')
        ax2.legend()
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def create_comparison_grid(
        images: List[Image.Image],
        titles: List[str],
        rows: int,
        cols: int,
        figsize: Tuple[int, int] = (15, 10),
        main_title: str = "Image Comparison"
    ):
        """
        Create a grid comparison of multiple images.
        
        Args:
            images: List of PIL Images
            titles: List of titles for each image
            rows: Number of rows in grid
            cols: Number of columns in grid
            figsize: Figure size
            main_title: Main title for the entire grid
        """
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        
        # Handle single row or column
        if rows == 1 and cols == 1:
            axes = [axes]
        elif rows == 1 or cols == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        # Plot images
        for i in range(rows * cols):
            if i < len(images):
                axes[i].imshow(images[i])
                axes[i].set_title(titles[i] if i < len(titles) else f"Image {i+1}")
            else:
                axes[i].set_visible(False)
            
            axes[i].axis('off')
        
        plt.suptitle(main_title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_augmentation_statistics(
        augmentation_stats: Dict[str, Any],
        title: str = "Text Augmentation Statistics",
        figsize: Tuple[int, int] = (12, 8)
    ):
        """
        Plot statistics about text augmentation process.
        
        Args:
            augmentation_stats: Dictionary with augmentation statistics
            title: Plot title
            figsize: Figure size
        """
        if not augmentation_stats:
            print("No augmentation statistics to plot")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # Plot ligature applications
        if 'ligatures' in augmentation_stats:
            ligatures = augmentation_stats['ligatures']
            if ligatures:
                lig_names, lig_counts = zip(*ligatures.items())
                ax1.bar(lig_names, lig_counts, color='lightblue')
                ax1.set_title('Ligature Applications')
                ax1.set_ylabel('Count')
                plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # Plot abbreviation applications
        if 'abbreviations' in augmentation_stats:
            abbreviations = augmentation_stats['abbreviations']
            if abbreviations:
                abbr_names, abbr_counts = zip(*abbreviations.items())
                ax2.bar(abbr_names, abbr_counts, color='lightcoral')
                ax2.set_title('Abbreviation Applications')
                ax2.set_ylabel('Count')
                plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        # Plot character count changes
        if 'character_changes' in augmentation_stats:
            changes = augmentation_stats['character_changes']
            categories = ['Original', 'Augmented', 'Net Change']
            values = [changes.get('original', 0), 
                     changes.get('augmented', 0),
                     changes.get('net_change', 0)]
            
            colors = ['gray', 'green', 'blue' if values[2] >= 0 else 'red']
            ax3.bar(categories, values, color=colors, alpha=0.7)
            ax3.set_title('Character Count Changes')
            ax3.set_ylabel('Character Count')
        
        # Plot processing time if available
        if 'processing_time' in augmentation_stats:
            times = augmentation_stats['processing_time']
            if times:
                time_labels, time_values = zip(*times.items())
                ax4.pie(time_values, labels=time_labels, autopct='%1.1f%%')
                ax4.set_title('Processing Time Distribution')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def save_plot(
        filename: str,
        dpi: int = 300,
        format: str = 'png',
        bbox_inches: str = 'tight'
    ):
        """
        Save the current matplotlib figure.
        
        Args:
            filename: Output filename
            dpi: DPI for the saved image
            format: Image format
            bbox_inches: Bounding box setting
        """
        plt.savefig(filename, dpi=dpi, format=format, bbox_inches=bbox_inches)
        print(f"Plot saved to: {filename}")
    
    @staticmethod
    def close_all_plots():
        """Close all open matplotlib figures."""
        plt.close('all')
