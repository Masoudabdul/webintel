"""
WebIntel - High-Performance Web Information Retrieval CLI Tool
Powered by Google Gemini 2.0 Flash AI

A comprehensive web information retrieval tool that performs intelligent
web scraping and data collection with multi-threaded processing for
real-time results.
"""

__version__ = "1.0.0"
__author__ = "WebIntel Development Team"
__description__ = "High-Performance Web Information Retrieval CLI Tool"

from .cli import main
from .config import Config
from .ai_engine import AIEngine
from .processor import DataProcessor

__all__ = [
    "main",
    "Config",
    "AIEngine",
    "DataProcessor"
]
