# Synthetic HTR - Medieval Manuscript Generator

A Python package for generating synthetic medieval manuscripts with Handwritten Text Recognition (HTR) capabilities. This package includes an advanced text augmentor that can convert modern text into medieval Latin style manuscripts with authentic ligatures, abbreviations, and historical writing conventions.

## Features

- **Synthetic Manuscript Generation**: Create realistic medieval manuscript images
- **Text Augmentation**: Convert modern text to medieval Latin style with ligatures
- **Multiple Font Support**: Various medieval and historical fonts included
- **Texture Integration**: Parchment and paper textures for authentic appearance
- **HTR Training Data**: Generate training data for handwritten text recognition models
- **Customizable Output**: Control over layout, style, and content

## Installation

```bash
pip install synthetic-htr
```

For development installation:
```bash
git clone https://github.com/wjbmattingly/synthetic-htr.git
cd synthetic-htr
pip install -e .
```

## Quick Start

### Basic Usage

```python
from synthetic_htr import ManuscriptGenerator, TextAugmentor

# Initialize the text augmentor
augmentor = TextAugmentor()

# Convert modern text to medieval style
medieval_text = augmentor.augment_text("Lorem ipsum dolor sit amet")

# Generate manuscript image
generator = ManuscriptGenerator()
manuscript_image = generator.generate(medieval_text)
manuscript_image.save("medieval_manuscript.png")
```

### Advanced Text Augmentation

```python
from synthetic_htr.augmentor import TextAugmentor

augmentor = TextAugmentor(
    ligature_probability=0.8,
    abbreviation_probability=0.6,
    medieval_style="carolingian"
)

# Convert text with specific medieval conventions
medieval_text = augmentor.augment_text(
    "In nomine Domini nostri Iesu Christi",
    add_ligatures=True,
    add_abbreviations=True,
    add_decorations=True
)
```

### Custom Manuscript Generation

```python
from synthetic_htr.generator import ManuscriptGenerator

generator = ManuscriptGenerator(
    page_size=(1200, 1600),
    font_family="medieval",
    texture="parchment",
    margin_size=100,
    line_spacing=1.5
)

# Generate with custom parameters
manuscript = generator.generate(
    text=medieval_text,
    add_illuminations=True,
    add_marginalia=True,
    add_decorative_borders=True
)
```

## Package Structure

```
synthetic_htr/
├── __init__.py
├── augmentor/
│   ├── __init__.py
│   ├── text_augmentor.py
│   ├── ligature_rules.py
│   └── abbreviation_rules.py
├── generator/
│   ├── __init__.py
│   ├── manuscript_generator.py
│   ├── layout_engine.py
│   └── texture_manager.py
├── fonts/
│   ├── medieval.otf
│   ├── vitor.ttf
│   └── junicode.ttf
├── textures/
│   └── parchment_texture.jpg
└── utils/
    ├── __init__.py
    ├── image_processing.py
    └── validation.py
```

## Text Augmentation Features

### Ligatures
- **Common Ligatures**: æ, œ, ct, st, ff, fi, fl
- **Medieval Ligatures**: Special character combinations used in historical manuscripts
- **Custom Ligature Rules**: Extensible system for adding new ligature patterns

### Abbreviations
- **Suspension**: omitting letters at the end of words
- **Contraction**: omitting letters in the middle of words
- **Superscript**: raised letters for common abbreviations
- **Tironian Notes**: historical shorthand symbols

### Medieval Conventions
- **Carolingian Minuscule**: Standard medieval script style
- **Gothic Script**: Alternative medieval writing style
- **Decorative Elements**: Initials, borders, and marginal decorations

## Configuration

The package can be configured through environment variables or configuration files:

```bash
export SYNTHETIC_HTR_FONT_PATH="./fonts"
export SYNTHETIC_HTR_TEXTURE_PATH="./textures"
export SYNTHETIC_HTR_DEFAULT_STYLE="carolingian"
```

## Examples

Check out the `examples/` directory for complete working examples:

- Basic manuscript generation
- Advanced text augmentation
- Custom font integration
- Batch processing for HTR training data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Acknowledgments

- Historical font designers and typographers
- Medieval manuscript scholars and researchers
- Open source community contributors
