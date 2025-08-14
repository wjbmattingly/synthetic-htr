#!/usr/bin/env python3
"""
Medieval Letters Demo - Generate synthetic manuscripts from the medieval-data/medieval-letters dataset.

This demo uses the Hugging Face dataset at:
https://huggingface.co/datasets/medieval-data/medieval-letters

Structure:
- pl_head as header
- salutation as one block of text  
- text field as main text
- 1 column, no marginalia
- Specify number of lines per page
- Generate each page with XML and store in organized directories
"""

import os
import sys
import argparse
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Optional
import json
import time
from PIL import Image
import multiprocessing
from functools import lru_cache

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.abspath('.'))

try:
    from datasets import load_dataset
except ImportError:
    print("Error: datasets library not found. Install with: pip install datasets")
    sys.exit(1)

try:
    from synthetic_htr import TextAugmentor, ManuscriptVisualizer, OCRAnalyzer
    from synthetic_htr.augmentor import ComplexAbbreviationRules
except ImportError:
    print("Error: synthetic_htr package not found. Make sure it's installed or in your Python path.")
    sys.exit(1)


class MedievalLetterProcessor:
    """Process medieval letters from the dataset into synthetic manuscripts."""
    
    def __init__(self, style: str = "carolingian", lines_per_page: int = 30, words_per_line: int = 8, skip_existing: bool = True):
        """
        Initialize the processor.
        
        Args:
            style: Medieval script style (carolingian, gothic, uncial)
            lines_per_page: Number of lines per manuscript page
            words_per_line: Number of words per line for text splitting
        """
        self.style = style
        self.lines_per_page = lines_per_page
        self.words_per_line = words_per_line
        self.skip_existing = skip_existing
        
        # Initialize components
        self.augmentor = TextAugmentor(medieval_style=style)
        self.analyzer = OCRAnalyzer()
        self.visualizer = ManuscriptVisualizer()
        
        # Cache for dataset to avoid repeated loading
        self._dataset_cache = None
        
        print(f"Initialized MedievalLetterProcessor with {style} style, {lines_per_page} lines per page, {words_per_line} words per line")
        
        # Get available textures
        self.available_textures = self._get_available_textures()
        print(f"Available textures: {self.available_textures}")
    
    def _get_available_textures(self) -> List[str]:
        """Get list of available texture files."""
        texture_dir = os.path.join(os.path.dirname(__file__), "synthetic_htr", "textures")
        textures = []
        
        if os.path.exists(texture_dir):
            for filename in os.listdir(texture_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    texture_name = os.path.splitext(filename)[0].lower()
                    textures.append(texture_name)
        
        return textures if textures else ["parchment"]  # fallback
    
    def _select_random_texture(self) -> str:
        """Select a random texture from available textures."""
        if self.available_textures:
            return random.choice(self.available_textures)
        return "parchment"  # fallback
    
    @lru_cache(maxsize=128)
    def _get_resize_dimensions(self, width: int, height: int, max_resolution: int = 500) -> Tuple[int, int]:
        """Calculate resize dimensions with caching."""
        if max(width, height) <= max_resolution:
            return width, height
        
        if width > height:
            scale_factor = max_resolution / width
        else:
            scale_factor = max_resolution / height
        
        return int(width * scale_factor), int(height * scale_factor)
    
    def _resize_image(self, image, max_resolution: int = 500):
        """
        Resize image to maximum resolution while maintaining aspect ratio.
        
        Args:
            image: PIL Image to resize
            max_resolution: Maximum width or height in pixels
            
        Returns:
            Resized PIL Image
        """
        # Get cached dimensions
        width, height = image.size
        new_width, new_height = self._get_resize_dimensions(width, height, max_resolution)
        
        # If dimensions unchanged, return original
        if new_width == width and new_height == height:
            return image
        
        # Resize with high quality resampling
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def load_dataset(self):
        """Load the complete medieval-letters dataset with caching."""
        if self._dataset_cache is not None:
            return self._dataset_cache
            
        print("Loading medieval-letters dataset from Hugging Face...")
        try:
            self._dataset_cache = load_dataset("medieval-data/medieval-letters", split="train")
            print(f"Loaded dataset: {len(self._dataset_cache)} letters total")
            return self._dataset_cache
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return None
    
    def prepare_text_blocks(self, row: dict) -> List[Tuple[str, str]]:
        """
        Prepare text blocks from the dataset row.
        
        Args:
            row: Dataset row containing pl_head, salutation, text fields
            
        Returns:
            List of (block_type, text_content) tuples
        """
        blocks = []
        
        # Header from pl_head
        if row.get('pl_head'):
            blocks.append(("header", row['pl_head'].strip()))
        
        # Salutation as one block
        if row.get('salutation'):
            blocks.append(("salutation", row['salutation'].strip()))
        
        # Main text
        if row.get('text'):
            blocks.append(("main_text", row['text'].strip()))
        
        return blocks
    
    def augment_text_blocks(self, blocks: List[Tuple[str, str]], context: str = "religious") -> List[Tuple[str, str]]:
        """
        Apply medieval text augmentation to each text block.
        
        Args:
            blocks: List of (block_type, text_content) tuples
            context: Context for abbreviations (religious, legal, academic)
            
        Returns:
            List of (block_type, augmented_text) tuples
        """
        augmented_blocks = []
        
        for block_type, text in blocks:
            print(f"Augmenting {block_type} text...")
            
            # Apply augmentation based on block type
            if block_type == "header":
                # Less aggressive augmentation for headers
                augmented = self.augmentor.augment_text(
                    text,
                    add_ligatures=False,
                    add_abbreviations=False,
                    add_complex_abbreviations=False,  # Keep headers more readable
                    preserve_case=True,  # Keep headers uppercase
                    context=context
                )
            else:
                # Full augmentation for salutation and main text
                augmented = self.augmentor.augment_text(
                    text,
                    add_ligatures=False,
                    add_abbreviations=False,
                    add_complex_abbreviations=True,
                    preserve_case=True,  # Keep original case
                    context=context
                )
            
            augmented_blocks.append((block_type, augmented))
        
        return augmented_blocks
    
    def split_into_pages(self, blocks: List[Tuple[str, str]]) -> List[str]:
        """
        Split text blocks into pages based on lines_per_page and words_per_line.
        
        Args:
            blocks: List of (block_type, text_content) tuples
            
        Returns:
            List of page texts
        """
        pages = []
        current_page_lines = []
        current_line_count = 0
        
        for block_type, text in blocks:
            if block_type == "header":
                header_line = f"{text}"
                
                if current_line_count >= self.lines_per_page:
                    # Start new page
                    pages.append('\n'.join(current_page_lines))
                    current_page_lines = [header_line]
                    current_line_count = 1
                else:
                    current_page_lines.append(header_line)
                    current_line_count += 1
                    
            elif block_type == "salutation":
                # Add blank line before salutation if there's room
                if current_line_count < self.lines_per_page - 1:
                    current_page_lines.append("")
                    current_line_count += 1
                elif current_line_count >= self.lines_per_page:
                    # Start new page
                    pages.append('\n'.join(current_page_lines))
                    current_page_lines = [""]
                    current_line_count = 1
                
                # Split salutation into lines using word-split
                salutation_lines = self._split_text_into_lines(text)
                for line in salutation_lines:
                    if current_line_count >= self.lines_per_page:
                        # Start new page
                        pages.append('\n'.join(current_page_lines))
                        current_page_lines = [line]
                        current_line_count = 1
                    else:
                        current_page_lines.append(line)
                        current_line_count += 1
                        
            else:  # main_text
                # Add blank line before main text if there's room
                if current_line_count < self.lines_per_page - 1:
                    current_page_lines.append("")
                    current_line_count += 1
                elif current_line_count >= self.lines_per_page:
                    # Start new page
                    pages.append('\n'.join(current_page_lines))
                    current_page_lines = [""]
                    current_line_count = 1
                
                # Split main text into lines using word-split
                main_text_lines = self._split_text_into_lines(text)
                for line in main_text_lines:
                    if current_line_count >= self.lines_per_page:
                        # Start new page
                        pages.append('\n'.join(current_page_lines))
                        current_page_lines = [line]
                        current_line_count = 1
                    else:
                        current_page_lines.append(line)
                        current_line_count += 1
        
        # Add the last page
        if current_page_lines:
            pages.append('\n'.join(current_page_lines))
        
        return pages
    
    def _split_text_into_lines(self, text: str) -> List[str]:
        """
        Split text into lines based on words_per_line.
        
        Args:
            text: Text to split
            
        Returns:
            List of lines with specified number of words per line
        """
        words = text.split()
        lines = []
        
        for i in range(0, len(words), self.words_per_line):
            line_words = words[i:i + self.words_per_line]
            lines.append(' '.join(line_words))
        
        return lines
    
    def generate_manuscript_page(self, page_text: str, page_num: int, original_page_text: str = None) -> Tuple:
        """
        Generate a manuscript page with OCR data.
        
        Args:
            page_text: Text content for the page (augmented)
            page_num: Page number
            original_page_text: Original text content before augmentation
            
        Returns:
            Tuple of (image, polygons, alto_xml)
        """
        print(f"Generating manuscript page {page_num}...")
        
        # Check for medieval font
        medieval_font_path = None
        font_name = "Cerne.otf"
        possible_paths = [
            font_name,
            f"synthetic_htr/fonts/{font_name}", 
            f"./synthetic_htr/fonts/{font_name}",
            os.path.join(os.path.dirname(__file__), "synthetic_htr", "fonts", font_name)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                medieval_font_path = path
                print(f"Using medieval font: {path}")
                break
        
        if not medieval_font_path:
            print("Warning: JunicodeTwoBeta-Regular.ttf not found, using default font")
        
        # Select a random texture for this page
        selected_texture = self._select_random_texture()
        print(f"Using texture: {selected_texture}")
        
        # Generate OCR data with enhanced parameters for natural look
        image, polygons, alto_xml = self.analyzer.generate_synthetic_ocr_data(
            text=page_text,
            width=1200,
            height=1600,
            font_size=36,  # Doubled font size (was 18)
            num_columns=1,  # Single column as requested
            marginalia=False,  # No marginalia as requested
            curve_amount=0.25,  # Increased curvature for more realism
            heading_lines=1 if page_num == 1 else 0,  # First page has heading
            font_path=medieval_font_path,
            margin_size=120,  # More natural margins (was using default)
            word_spacing_factor=0.7,  # Closer word spacing
            texture_name=selected_texture,  # Random texture application
            ink_opacity_range=(1, 2),  # Random faint ink opacity
            ink_color_variation=True,  # Use brownish-black ink colors
            add_noise=True,  # Add minimal realistic noise
            original_text=original_page_text  # Original text for XML
        )
        
        return image, polygons, alto_xml
    
    def is_letter_processed(self, row_index: int, output_base_dir: str) -> bool:
        """Check if a letter has already been processed."""
        if not self.skip_existing:
            return False
            
        letter_dir = os.path.join(output_base_dir, f"{row_index:04d}")
        
        # Check if directory exists and has metadata
        if not os.path.exists(letter_dir):
            return False
            
        metadata_path = os.path.join(letter_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            return False
            
        # Check if at least one page exists
        page_files = [f for f in os.listdir(letter_dir) if f.startswith("page_") and f.endswith("_original.png")]
        return len(page_files) > 0
    
    def process_letter(self, row: dict, row_index: int = 0, output_base_dir: str = "medieval_letters_output") -> str:
        """
        Process a single letter from the dataset.
        
        Args:
            row: Dataset row to process
            row_index: Index of the row being processed
            output_base_dir: Base directory for output
            
        Returns:
            Path to the created output directory
        """
        if not row:
            return None
        
        # Check if already processed
        if self.is_letter_processed(row_index, output_base_dir):
            letter_dir = os.path.join(output_base_dir, f"{row_index:04d}")
            print(f"⏭️  Skipping already processed letter {row_index}: {letter_dir}")
            return letter_dir
        
        # Create output directory with formatted name
        letter_dir = os.path.join(output_base_dir, f"{row_index:04d}")
        os.makedirs(letter_dir, exist_ok=True)
        
        print(f"Processing letter to directory: {letter_dir}")
        
        # Prepare and augment text
        blocks = self.prepare_text_blocks(row)
        augmented_blocks = self.augment_text_blocks(blocks, context="religious")
        
        # Split into pages for both original and augmented text
        pages = self.split_into_pages(augmented_blocks)
        original_pages = self.split_into_pages(blocks)  # Original text without augmentation
        print(f"Split letter into {len(pages)} pages")
        
        # Generate manuscript pages
        saved_files = []
        for page_num, (page_text, original_page_text) in enumerate(zip(pages, original_pages), 1):
            # Generate manuscript page with both original and augmented text
            image, polygons, alto_xml = self.generate_manuscript_page(page_text, page_num, original_page_text)
            
            # Save both original and annotated images
            page_prefix = f"page_{page_num:02d}"
            
            # 1. Save original image (resized to max 500px)
            resized_image = self._resize_image(image, max_resolution=1000)
            original_path = os.path.join(letter_dir, f"{page_prefix}_original.png")
            resized_image.save(original_path)
            saved_files.append(original_path)
            
            # 2. Save image with blue bounding boxes (resized to max 500px)
            bbox_image = self.visualizer._create_bbox_image(image, polygons, 'blue', True)
            resized_bbox_image = self._resize_image(bbox_image, max_resolution=500)
            bbox_path = os.path.join(letter_dir, f"{page_prefix}_with_blue_bboxes.png")
            resized_bbox_image.save(bbox_path)
            saved_files.append(bbox_path)
            
            # 3. Save ALTO XML
            xml_path = os.path.join(letter_dir, f"{page_prefix}.xml")
            self.analyzer.save_alto_xml(alto_xml, xml_path)
            saved_files.append(xml_path)
            
            # 4. Create and save page summary
            summary_path = os.path.join(letter_dir, f"{page_prefix}_summary.txt")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"Page {page_num} Summary\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"Page number: {page_num}\n")
                f.write(f"Original image size: {image.size[0]} x {image.size[1]} pixels\n")
                f.write(f"Saved image size: {resized_image.size[0]} x {resized_image.size[1]} pixels\n")
                f.write(f"Total text regions: {len(polygons)}\n")
                f.write(f"Lines of text: {len([line for line in page_text.split('\n') if line.strip()])}\n")
                f.write(f"Font: medieval.otf (if available)\n")
                f.write(f"Style: {self.style}\n")
                f.write(f"\nText content preview:\n")
                preview_lines = page_text.split('\n')[:5]
                for i, line in enumerate(preview_lines, 1):
                    if line.strip():
                        f.write(f"  {i}: {line[:60]}{'...' if len(line) > 60 else ''}\n")
                
                f.write(f"\nText regions detected:\n")
                for i, (text, _) in enumerate(polygons[:10], 1):
                    preview = text[:50] + "..." if len(text) > 50 else text
                    f.write(f"  {i}: {preview}\n")
                if len(polygons) > 10:
                    f.write(f"  ... and {len(polygons) - 10} more regions\n")
            
            saved_files.append(summary_path)
            
            print(f"Saved page {page_num}: original image, blue bboxes image, XML, and summary")
        
        # Save metadata about the letter
        metadata = {
            "dataset_row": row_index,
            "author": row.get("author", "Unknown"),
            "pl_number": row.get("pl_number"),
            "style": self.style,
            "lines_per_page": self.lines_per_page,
            "total_pages": len(pages),
            "blocks_processed": len(blocks),
            "viaf_link": row.get("author_viaf_link"),
            "original_text_length": sum(len(block[1]) for block in blocks),
            "augmented_text_length": sum(len(block[1]) for block in augmented_blocks)
        }
        
        metadata_path = os.path.join(letter_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully processed letter:")
        print(f"   Author: {row.get('author', 'Unknown')}")
        print(f"   Pages generated: {len(pages)}")
        print(f"   Output directory: {letter_dir}")
        print(f"   Files saved: {len(saved_files) + 1}")  # +1 for metadata
        
        return letter_dir
    
    def process_all_letters(self, output_base_dir: str = "medieval_letters_output", start_index: int = 0, end_index: int = None) -> List[str]:
        """
        Process all letters from the dataset.
        
        Args:
            output_base_dir: Base directory for output
            start_index: Starting index (for resuming)
            end_index: Ending index (None for all)
            
        Returns:
            List of created output directories
        """
        # Load the complete dataset
        dataset = self.load_dataset()
        if not dataset:
            return []
        
        total_letters = len(dataset)
        if end_index is None:
            end_index = total_letters
        
        print(f"Processing letters {start_index} to {end_index-1} out of {total_letters} total")
        
        created_dirs = []
        failed_count = 0
        
        for i in range(start_index, min(end_index, total_letters)):
            try:
                print(f"\n{'='*60}")
                print(f"Processing letter {i+1}/{total_letters} (Index: {i})")
                print(f"Author: {dataset[i].get('author', 'Unknown')}")
                
                # Process this letter
                letter_dir = self.process_letter(dataset[i], row_index=i, output_base_dir=output_base_dir)
                
                if letter_dir:
                    created_dirs.append(letter_dir)
                    print(f"✅ Successfully processed letter {i}")
                else:
                    print(f"❌ Failed to process letter {i}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"❌ Error processing letter {i}: {e}")
                failed_count += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"📊 Processing Summary:")
        print(f"  Total processed: {len(created_dirs)}")
        print(f"  Failed: {failed_count}")
        print(f"  Success rate: {len(created_dirs)/(len(created_dirs) + failed_count)*100:.1f}%")
        
        return created_dirs
    
    def process_single_letter_thread_safe(self, dataset_row, row_index: int, output_base_dir: str) -> Tuple[bool, str, str, bool]:
        """
        Thread-safe version of process_letter for concurrent execution.
        
        Args:
            dataset_row: Row from the dataset
            row_index: Index of the row being processed
            output_base_dir: Base directory for output
            
        Returns:
            Tuple of (success, letter_dir_or_error, author, was_skipped)
        """
        try:
            author = dataset_row.get('author', 'Unknown')
            
            # Check if already processed before doing any work
            if self.is_letter_processed(row_index, output_base_dir):
                letter_dir = os.path.join(output_base_dir, f"{row_index:04d}")
                return (True, letter_dir, author, True)  # was_skipped = True
            
            letter_dir = self.process_letter(dataset_row, row_index=row_index, output_base_dir=output_base_dir)
            return (True, letter_dir, author, False)  # was_skipped = False
        except Exception as e:
            return (False, str(e), dataset_row.get('author', 'Unknown'), False)
    
    def process_all_letters_multithreaded(
        self, 
        output_base_dir: str = "medieval_letters_output", 
        start_index: int = 0, 
        end_index: int = None,
        num_threads: int = None
    ) -> List[str]:
        """
        Process all letters from the dataset using multiple threads.
        
        Args:
            output_base_dir: Base directory for output
            start_index: Starting index (for resuming)
            end_index: Ending index (None for all)
            num_threads: Number of worker threads
            
        Returns:
            List of created output directories
        """
        # Load the complete dataset
        dataset = self.load_dataset()
        if not dataset:
            return []
        
        total_letters = len(dataset)
        if end_index is None:
            end_index = total_letters
        
        # Auto-determine optimal thread count if not specified
        if num_threads is None:
            # For I/O bound tasks, use more threads than CPU cores
            # But cap at reasonable limit to avoid overhead
            cpu_count = multiprocessing.cpu_count()
            num_threads = min(cpu_count * 2, 16)  # Cap at 16 threads
        
        # Ensure output directory exists
        Path(output_base_dir).mkdir(parents=True, exist_ok=True)
        
        # Create progress tracking file
        progress_file = os.path.join(output_base_dir, f"progress_{start_index}_{end_index}.json")
        
        # Pre-check how many letters are already processed
        already_processed = 0
        if self.skip_existing:
            print("Checking for already processed letters...")
            for i in range(start_index, min(end_index, total_letters)):
                if self.is_letter_processed(i, output_base_dir):
                    already_processed += 1
        
        remaining_to_process = (end_index - start_index) - already_processed
        
        print(f"Processing letters {start_index} to {end_index-1} out of {total_letters} total")
        print(f"Already processed: {already_processed}, Remaining: {remaining_to_process}")
        print(f"Using {num_threads} threads for parallel processing")
        
        # Save initial progress
        progress_data = {
            "start_index": start_index,
            "end_index": end_index,
            "total_letters": total_letters,
            "already_processed": already_processed,
            "remaining_to_process": remaining_to_process,
            "start_time": time.time(),
            "completed": [],
            "failed": [],
            "skipped": []
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        created_dirs = []
        failed_count = 0
        processed_count = 0
        skipped_count = 0
        
        # Thread-safe progress tracking
        progress_lock = threading.Lock()
        start_time = time.time()
        
        def update_progress(success: bool, letter_dir_or_error: str, author: str, index: int, was_skipped: bool = False):
            nonlocal processed_count, failed_count, skipped_count
            with progress_lock:
                processed_count += 1
                if success:
                    created_dirs.append(letter_dir_or_error)
                    if was_skipped:
                        skipped_count += 1
                        status = "⏭️ "
                        progress_data["skipped"].append({"index": index, "author": author, "timestamp": time.time()})
                    else:
                        status = "✅"
                        progress_data["completed"].append({"index": index, "author": author, "timestamp": time.time()})
                else:
                    failed_count += 1
                    status = "❌"
                    progress_data["failed"].append({"index": index, "author": author, "error": letter_dir_or_error, "timestamp": time.time()})
                
                # Update progress file every 10 items or on failure
                if processed_count % 10 == 0 or not success:
                    try:
                        with open(progress_file, 'w') as f:
                            json.dump(progress_data, f, indent=2)
                    except Exception:
                        pass  # Don't let progress file errors stop processing
                
                # Progress reporting
                elapsed_time = time.time() - start_time
                progress_pct = (processed_count / (end_index - start_index)) * 100
                rate = processed_count / elapsed_time if elapsed_time > 0 else 0
                eta = (end_index - start_index - processed_count) / rate if rate > 0 else 0
                
                print(f"{status} [{processed_count:4d}/{end_index - start_index}] "
                      f"({progress_pct:5.1f}%) Letter {index:5d}: {author:20.20s} "
                      f"| Rate: {rate:4.1f}/sec | ETA: {eta/60:4.1f}m")
                
                if not success:
                    print(f"     Error: {letter_dir_or_error}")
        
        # Create thread pool and submit jobs
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit all jobs
            future_to_index = {
                executor.submit(
                    self.process_single_letter_thread_safe, 
                    dataset[i], 
                    i, 
                    output_base_dir
                ): i for i in range(start_index, min(end_index, total_letters))
            }
            
            # Process completed jobs
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    success, letter_dir_or_error, author, was_skipped = future.result()
                    update_progress(success, letter_dir_or_error, author, index, was_skipped)
                except Exception as e:
                    update_progress(False, f"Thread exception: {e}", "Unknown", index, False)
        
        # Final summary
        elapsed_time = time.time() - start_time
        print(f"\n{'='*80}")
        print(f"📊 Multi-threaded Processing Summary:")
        print(f"  Total processed: {len(created_dirs)}")
        print(f"  Skipped (already done): {skipped_count}")
        print(f"  Newly processed: {len(created_dirs) - skipped_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Success rate: {len(created_dirs)/(len(created_dirs) + failed_count)*100:.1f}%")
        print(f"  Total time: {elapsed_time/60:.1f} minutes")
        print(f"  Average rate: {processed_count/elapsed_time:.1f} letters/second")
        print(f"  Threads used: {num_threads}")
        if skipped_count > 0:
            print(f"  Time saved by skipping: ~{(skipped_count * elapsed_time / max(1, len(created_dirs) - skipped_count))/60:.1f} minutes")
        
        # Final progress file update
        progress_data["end_time"] = time.time()
        progress_data["total_time_minutes"] = elapsed_time / 60
        progress_data["success_rate"] = len(created_dirs)/(len(created_dirs) + failed_count)*100 if (len(created_dirs) + failed_count) > 0 else 0
        progress_data["final_summary"] = {
            "total_processed": len(created_dirs),
            "skipped": skipped_count,
            "newly_processed": len(created_dirs) - skipped_count,
            "failed": failed_count,
            "threads_used": num_threads
        }
        
        try:
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
            print(f"📄 Progress saved to: {progress_file}")
        except Exception as e:
            print(f"⚠️  Could not save final progress: {e}")
        
        return created_dirs


def main():
    """Main function to run the medieval letters demo."""
    parser = argparse.ArgumentParser(description="Generate synthetic manuscripts from medieval letters dataset")
    parser.add_argument("--style", choices=["carolingian", "gothic", "uncial"], 
                       default="carolingian", help="Medieval script style")
    parser.add_argument("--lines-per-page", type=int, default=30, 
                       help="Number of lines per manuscript page")
    parser.add_argument("--words-per-line", type=int, default=8,
                       help="Number of words per line for text splitting")
    parser.add_argument("--row-index", type=int, default=None,
                       help="Dataset row index to process (single letter mode)")
    parser.add_argument("--all", action="store_true",
                       help="Process all letters in the dataset")
    parser.add_argument("--start-index", type=int, default=0,
                       help="Starting index for batch processing")
    parser.add_argument("--end-index", type=int, default=None,
                       help="Ending index for batch processing (None for all)")
    parser.add_argument("--threads", type=int, default=None,
                       help="Number of threads for parallel processing (auto-detect if not specified)")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                       help="Skip already processed letters (default: True)")
    parser.add_argument("--force-reprocess", action="store_true", default=False,
                       help="Force reprocessing of all letters, even if already done")
    parser.add_argument("--output-dir", default="/Users/wjm55/data/medieval-letters-synthetic",
                       help="Output directory for generated manuscripts")
    
    args = parser.parse_args()
    
    print("🏰 Medieval Letters Manuscript Generator")
    print("=" * 50)
    print(f"Dataset: https://huggingface.co/datasets/medieval-data/medieval-letters")
    print(f"Style: {args.style}")
    print(f"Lines per page: {args.lines_per_page}")
    print(f"Words per line: {args.words_per_line}")
    
    if args.all:
        print(f"Mode: Process ALL letters (indices {args.start_index} to {args.end_index or 'end'})")
        print(f"Threads: {args.threads or 'auto-detect'} parallel workers")
        print(f"Skip existing: {not args.force_reprocess}")
    elif args.row_index is not None:
        print(f"Mode: Process single letter (index {args.row_index})")
    else:
        print("Error: Must specify either --row-index for single letter or --all for batch processing")
        return 1
    
    print()
    
    try:
        # Initialize processor
        processor = MedievalLetterProcessor(
            style=args.style,
            lines_per_page=args.lines_per_page,
            words_per_line=args.words_per_line,
            skip_existing=not args.force_reprocess
        )
        
        if args.all:
            # Process all letters with multi-threading
            output_dirs = processor.process_all_letters_multithreaded(
                output_base_dir=args.output_dir,
                start_index=args.start_index,
                end_index=args.end_index,
                num_threads=args.threads
            )
            
            if output_dirs:
                print("\n🎉 Batch processing completed successfully!")
                print(f"📁 Processed {len(output_dirs)} letters")
                print(f"📁 Check your results in: {args.output_dir}")
            else:
                print("❌ Batch processing failed. Check the error messages above.")
                return 1
        else:
            # Process single letter
            dataset = processor.load_dataset()
            if not dataset or args.row_index >= len(dataset):
                print(f"❌ Invalid row index {args.row_index}. Dataset has {len(dataset) if dataset else 0} letters.")
                return 1
            
            output_dir = processor.process_letter(
                row=dataset[args.row_index],
                row_index=args.row_index,
                output_base_dir=args.output_dir
            )
            
            if output_dir:
                print("\n🎉 Processing completed successfully!")
                print(f"📁 Check your results in: {output_dir}")
            else:
                print("❌ Processing failed. Check the error messages above.")
                return 1
        
        print("\nGenerated files include:")
        print("  - Original manuscript images")
        print("  - Images with bounding boxes")
        print("  - ALTO XML format files with original and abbreviated content")
        print("  - Page summaries")
        print("  - Metadata files")
    
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user.")
        return 1
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
