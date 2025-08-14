"""
Configuration module for the Synthetic HTR package.
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for the Synthetic HTR package."""
    
    # Default configuration
    DEFAULT_CONFIG = {
        'fonts': {
            'medieval': 'medieval.otf',
            'gothic': 'vitor.ttf',
            'uncial': 'JunicodeTwoBeta-Regular.ttf',
            'serif': 'cmr10.ttf',
            'decorative': 'HeavyRain-X3y9P.ttf'
        },
        'textures': {
            'parchment': 'parchment_texture.jpg',
            'paper': 'paper_texture.jpg',
            'vellum': 'vellum_texture.jpg'
        },
        'styles': {
            'carolingian': {
                'ligature_probability': 0.7,
                'abbreviation_probability': 0.5,
                'decorations': True
            },
            'gothic': {
                'ligature_probability': 0.8,
                'abbreviation_probability': 0.7,
                'decorations': True
            },
            'uncial': {
                'ligature_probability': 0.6,
                'abbreviation_probability': 0.4,
                'decorations': False
            }
        },
        'page_sizes': {
            'folio': (1200, 1600),
            'quarto': (900, 1200),
            'octavo': (600, 800),
            'custom': (1200, 1600)
        },
        'output': {
            'format': 'PNG',
            'quality': 95,
            'dpi': 300
        }
    }
    
    def __init__(self, config_file: str = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        
        # Load environment variables
        self._load_env_vars()
    
    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # Font path
        font_path = os.getenv('SYNTHETIC_HTR_FONT_PATH')
        if font_path:
            self.config['font_path'] = font_path
        
        # Texture path
        texture_path = os.getenv('SYNTHETIC_HTR_TEXTURE_PATH')
        if texture_path:
            self.config['texture_path'] = texture_path
        
        # Default style
        default_style = os.getenv('SYNTHETIC_HTR_DEFAULT_STYLE')
        if default_style:
            self.config['default_style'] = default_style
        
        # Output directory
        output_dir = os.getenv('SYNTHETIC_HTR_OUTPUT_DIR')
        if output_dir:
            self.config['output_dir'] = output_dir
    
    def load_config(self, config_file: str):
        """Load configuration from file."""
        try:
            import json
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self._merge_config(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing config."""
        for key, value in new_config.items():
            if isinstance(value, dict) and key in self.config:
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_font_path(self, font_family: str) -> str:
        """Get the path for a font family."""
        font_name = self.config['fonts'].get(font_family)
        if not font_name:
            return self.config['fonts']['medieval']
        
        font_path = self.get('font_path', 'fonts')
        return os.path.join(font_path, font_name)
    
    def get_texture_path(self, texture_name: str) -> str:
        """Get the path for a texture."""
        texture_file = self.config['textures'].get(texture_name)
        if not texture_file:
            return self.config['textures']['parchment']
        
        texture_path = self.get('texture_path', 'textures')
        return os.path.join(texture_path, texture_file)
    
    def get_style_config(self, style: str) -> Dict[str, Any]:
        """Get configuration for a specific style."""
        return self.config['styles'].get(style, self.config['styles']['carolingian'])
    
    def get_page_size(self, size_name: str) -> tuple:
        """Get page size configuration."""
        return self.config['page_sizes'].get(size_name, self.config['page_sizes']['folio'])
    
    def save_config(self, config_file: str):
        """Save current configuration to file."""
        try:
            import json
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file {config_file}: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_env_vars()
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        return self.config.copy()


# Global configuration instance
config = Config()
