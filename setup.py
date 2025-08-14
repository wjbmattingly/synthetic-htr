from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="synthetic-htr",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for generating synthetic medieval manuscripts with HTR capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/synthetic-htr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=9.0.0",
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
        "matplotlib>=3.5.0",
        "scikit-image>=0.19.0",
        "lxml>=4.6.0",
        "requests>=2.25.0",
        "tqdm>=4.62.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "ipywidgets>=7.6.0",
        ],
    },
    include_package_data=True,
    package_data={
        "synthetic_htr": [
            "fonts/*.ttf",
            "fonts/*.otf",
            "textures/*.jpg",
            "textures/*.png",
        ],
    },
    entry_points={
        "console_scripts": [
            "synthetic-htr=synthetic_htr.cli:main",
        ],
    },
)
