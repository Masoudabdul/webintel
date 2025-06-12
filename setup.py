"""
Setup script for WebIntel
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
try:
    long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
except UnicodeDecodeError:
    try:
        long_description = readme_path.read_text(encoding="utf-16") if readme_path.exists() else ""
    except:
        long_description = "WebIntel - Advanced Web Intelligence System"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="webintel",
    version="2.0.3",
    author="JustM3Sunny",
    author_email="justm3sunny@gmail.com",
    description="🤖 AI-Powered Web Intelligence System - Real-time research, comprehensive analysis, and intelligent insights using Google Gemini 2.0 Flash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JustM3Sunny/webintel",
    download_url="https://github.com/JustM3Sunny/webintel/archive/v2.0.0.tar.gz",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=0.18.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "responses>=0.22.0",
        ]
    },
    # Entry points are now defined in pyproject.toml
    keywords=[
        "ai", "artificial intelligence", "web intelligence", "research", "automation",
        "gemini", "google ai", "web scraping", "data analysis", "nlp", "search engine",
        "real-time", "comprehensive analysis", "intelligent insights", "web research",
        "market research", "competitive analysis", "news monitoring", "trend analysis",
        "content creation", "academic research", "financial analysis", "cryptocurrency",
        "technology trends", "cli tool", "python api", "async", "fast", "reliable"
    ],
    project_urls={
        "Homepage": "https://github.com/JustM3Sunny/webintel",
        "Documentation": "https://github.com/JustM3Sunny/webintel#readme",
        "Repository": "https://github.com/JustM3Sunny/webintel",
        "Bug Reports": "https://github.com/JustM3Sunny/webintel/issues",
        "Feature Requests": "https://github.com/JustM3Sunny/webintel/discussions",
        "Changelog": "https://github.com/JustM3Sunny/webintel/releases",
        "PyPI": "https://pypi.org/project/webintel/2.0.0/",
    },
    include_package_data=True,
    package_data={
        "webintel": ["*.json", "*.yaml", "*.yml"],
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    license_files=["LICENSE"],
)
