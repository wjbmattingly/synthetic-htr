                    
                    # Clean up
                    os.unlink(svg_path)
                    
                    # Resize to target dimensions if needed
                    if image.size != (width, height):
                        # Calculate scaling to fit within target dimensions
                        scale_x = width / image.width
                        scale_y = height / image.height
                        scale = min(scale_x, scale_y, 1.0)  # Don't upscale
                        
                        if scale < 1.0:
                            new_width = int(image.width * scale)
                            new_height = int(image.height * scale)
                            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    return image
                    
                except Exception as e:
                    if os.path.exists(svg_path):
                        os.unlink(svg_path)
                    return None
            
            return None
            
        except Exception as e:
            return None
    
    def _process_cerne_color_image(self, cerne_image, text, original_text, width, height,
                                   background_texture, parchment_color, ink_color,
                                   add_noise, noise_strength, add_aging, aging_strength):
        """
        Process the Cerne color image and integrate it into a manuscript page.
        
        Args:
            cerne_image: PIL Image with Cerne color rendering
            text: The rendered text
            original_text: Original text before augmentation
            width, height: Target dimensions
            background_texture: Background texture path
            parchment_color: Parchment color tuple
            ink_color: Ink color tuple (not used for color fonts)
            add_noise: Whether to add noise
            noise_strength: Noise strength
            add_aging: Whether to add aging effects
            aging_strength: Aging strength
            
        Returns:
            Tuple of (image, polygons, alto_xml)
        """
        # Create manuscript background
        if background_texture and os.path.exists(background_texture):
            try:
                texture = Image.open(background_texture)
                texture = texture.resize((width, height), Image.Resampling.LANCZOS)
                if texture.mode != 'RGB':
                    texture = texture.convert('RGB')
                background = texture
            except Exception:
                background = Image.new('RGB', (width, height), parchment_color)
        else:
            background = Image.new('RGB', (width, height), parchment_color)
        
        # Center the Cerne text on the background
        if cerne_image.size[0] <= width and cerne_image.size[1] <= height:
            x_offset = (width - cerne_image.width) // 2
            y_offset = (height - cerne_image.height) // 2
            
            # Paste the color text onto the background
            if cerne_image.mode == 'RGBA':
                background.paste(cerne_image, (x_offset, y_offset), cerne_image)
            else:
                background.paste(cerne_image, (x_offset, y_offset))
        else:
            # If the text is larger than the background, just paste at (0,0)
            if cerne_image.mode == 'RGBA':
                background.paste(cerne_image, (0, 0), cerne_image)
            else:
                background.paste(cerne_image, (0, 0))
        
        # Apply aging and noise effects
        if add_aging:
            background = self._add_aging_effects(background, aging_strength)
        
        if add_noise:
            background = self._add_noise(background, noise_strength)
        
        # Create simple bounding box for the text
        # This is a simplified version - in a full implementation you'd parse the SVG
        text_bbox = [50, 50, width - 50, height - 50]  # Simple margin-based bbox
        polygons = [text_bbox]
        
        # Generate simple ALTO XML
        alto_xml = self._generate_simple_alto_xml(text, original_text, width, height, polygons)
        
        return background, polygons, alto_xml
    
    def _generate_simple_alto_xml(self, text, original_text, width, height, polygons):
        """Generate a simple ALTO XML for color font rendering."""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        
        # Create ALTO structure
        alto = Element('alto')
        alto.set('xmlns', 'http://www.loc.gov/standards/alto/ns-v4#')
        
        description = SubElement(alto, 'Description')
        measurement_unit = SubElement(description, 'MeasurementUnit')
        measurement_unit.text = 'pixel'
        
        layout = SubElement(alto, 'Layout')
        page = SubElement(layout, 'Page')
        page.set('WIDTH', str(width))
        page.set('HEIGHT', str(height))
        page.set('PHYSICAL_IMG_NR', '1')
        page.set('ID', 'page_1')
        
        print_space = SubElement(page, 'PrintSpace')
        print_space.set('HPOS', '0')
        print_space.set('VPOS', '0')
        print_space.set('WIDTH', str(width))
        print_space.set('HEIGHT', str(height))
        
        # Add text block
        if polygons:
            bbox = polygons[0]
            text_block = SubElement(print_space, 'TextBlock')
            text_block.set('ID', 'block_1')
            text_block.set('HPOS', str(int(bbox[0])))
            text_block.set('VPOS', str(int(bbox[1])))
            text_block.set('WIDTH', str(int(bbox[2] - bbox[0])))
            text_block.set('HEIGHT', str(int(bbox[3] - bbox[1])))
            
            # Add text line
            text_line = SubElement(text_block, 'TextLine')
            text_line.set('ID', 'line_1')
            text_line.set('HPOS', str(int(bbox[0])))
            text_line.set('VPOS', str(int(bbox[1])))
            text_line.set('WIDTH', str(int(bbox[2] - bbox[0])))
            text_line.set('HEIGHT', str(int(bbox[3] - bbox[1])))
            
            # Add string
            string_elem = SubElement(text_line, 'String')
            string_elem.set('ID', 'string_1')
            string_elem.set('HPOS', str(int(bbox[0])))
            string_elem.set('VPOS', str(int(bbox[1])))
            string_elem.set('WIDTH', str(int(bbox[2] - bbox[0])))
            string_elem.set('HEIGHT', str(int(bbox[3] - bbox[1])))
            string_elem.set('CONTENT', original_text or text)
            string_elem.set('WC', '1.0')
        
        # Format XML
        rough_string = tostring(alto, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
