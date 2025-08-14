"""
Layout engine for positioning text on manuscript pages.
"""

import re
from typing import Dict, List, Tuple, Any
from PIL import ImageFont


class LayoutEngine:
    """
    Handles text layout and positioning on manuscript pages.
    """
    
    def __init__(
        self,
        page_size: Tuple[int, int] = (1200, 1600),
        margin_size: int = 100,
        line_spacing: float = 1.5
    ):
        """
        Initialize the layout engine.
        
        Args:
            page_size: Size of the manuscript page (width, height)
            margin_size: Size of page margins in pixels
            line_spacing: Spacing between text lines (multiplier)
        """
        self.page_size = page_size
        self.margin_size = margin_size
        self.line_spacing = line_spacing
        
        # Calculate text area
        self.text_area = {
            'x': margin_size,
            'y': margin_size,
            'width': page_size[0] - 2 * margin_size,
            'height': page_size[1] - 2 * margin_size
        }
    
    def layout_text(self, text: str, font: ImageFont.FreeTypeFont) -> Dict[str, Any]:
        """
        Layout text on the page with proper line breaks and positioning.
        
        Args:
            text: Text content to layout
            font: Font to use for measuring
            
        Returns:
            Dictionary containing layout information
        """
        # Split text into words
        words = text.split()
        
        if not words:
            return {'lines': [], 'total_height': 0}
        
        lines = []
        current_line = []
        current_width = 0
        y_position = self.text_area['y']
        
        # Get font metrics (handle both old and new PIL versions)
        try:
            font_height = font.getbbox('Ay')[3] - font.getbbox('Ay')[1]  # New PIL version
        except AttributeError:
            font_height = font.getsize('Ay')[1]  # Old PIL version
        line_height = int(font_height * self.line_spacing)
        
        for word in words:
            # Measure word width (handle both old and new PIL versions)
            try:
                word_width = font.getbbox(word + ' ')[2]  # New PIL version
            except AttributeError:
                word_width = font.getsize(word + ' ')[0]  # Old PIL version
            
            # Check if word fits on current line
            if current_width + word_width <= self.text_area['width']:
                current_line.append(word)
                current_width += word_width
            else:
                # Start new line
                if current_line:
                    lines.append({
                        'text': ' '.join(current_line),
                        'position': (self.text_area['x'], y_position),
                        'width': current_width
                    })
                    y_position += line_height
                
                # Start new line with current word
                current_line = [word]
                current_width = word_width
        
        # Add the last line
        if current_line:
            lines.append({
                'text': ' '.join(current_line),
                'position': (self.text_area['x'], y_position),
                'width': current_width
            })
            y_position += line_height
        
        return {
            'lines': lines,
            'total_height': y_position - self.text_area['y'],
            'line_height': line_height,
            'text_area': self.text_area
        }
    
    def set_page_size(self, page_size: Tuple[int, int]):
        """Update the page size and recalculate text area."""
        self.page_size = page_size
        self.text_area = {
            'x': self.margin_size,
            'y': self.margin_size,
            'width': page_size[0] - 2 * self.margin_size,
            'height': page_size[1] - 2 * self.margin_size
        }
    
    def set_margin_size(self, margin_size: int):
        """Update the margin size and recalculate text area."""
        self.margin_size = margin_size
        self.text_area = {
            'x': margin_size,
            'y': margin_size,
            'width': self.page_size[0] - 2 * margin_size,
            'height': self.page_size[1] - 2 * margin_size
        }
    
    def set_line_spacing(self, line_spacing: float):
        """Update the line spacing."""
        self.line_spacing = line_spacing
    
    def get_text_area(self) -> Dict[str, int]:
        """Get the current text area dimensions."""
        return self.text_area.copy()
    
    def estimate_lines_needed(self, text: str, font: ImageFont.FreeTypeFont) -> int:
        """
        Estimate how many lines will be needed for the text.
        
        Args:
            text: Text content
            font: Font to use for measuring
            
        Returns:
            Estimated number of lines
        """
        words = text.split()
        if not words:
            return 0
        
        current_width = 0
        lines_count = 1
        
        for word in words:
            # Measure word width (handle both old and new PIL versions)
            try:
                word_width = font.getbbox(word + ' ')[2]  # New PIL version
            except AttributeError:
                word_width = font.getsize(word + ' ')[0]  # Old PIL version
            
            if current_width + word_width <= self.text_area['width']:
                current_width += word_width
            else:
                lines_count += 1
                current_width = word_width
        
        return lines_count
    
    def can_fit_text(self, text: str, font: ImageFont.FreeTypeFont) -> bool:
        """
        Check if the text can fit on the page.
        
        Args:
            text: Text content
            font: Font to use for measuring
            
        Returns:
            True if text can fit, False otherwise
        """
        lines_needed = self.estimate_lines_needed(text, font)
        # Get font height (handle both old and new PIL versions)
        try:
            font_height = font.getbbox('Ay')[3] - font.getbbox('Ay')[1]  # New PIL version
        except AttributeError:
            font_height = font.getsize('Ay')[1]  # Old PIL version
        line_height = int(font_height * self.line_spacing)
        
        total_height_needed = lines_needed * line_height
        
        return total_height_needed <= self.text_area['height']
    
    def optimize_font_size(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        min_size: int = 12,
        max_size: int = 48
    ) -> int:
        """
        Find the optimal font size that fits the text on the page.
        
        Args:
            text: Text content
            font: Base font to resize
            min_size: Minimum font size
            max_size: Maximum font size
            
        Returns:
            Optimal font size
        """
        # Binary search for optimal font size
        left, right = min_size, max_size
        optimal_size = min_size
        
        while left <= right:
            mid = (left + right) // 2
            
            # Create font with current size
            try:
                test_font = ImageFont.truetype(font.path, mid)
            except:
                # Fallback for default fonts
                test_font = ImageFont.load_default()
            
            if self.can_fit_text(text, test_font):
                optimal_size = mid
                left = mid + 1
            else:
                right = mid - 1
        
        return optimal_size
