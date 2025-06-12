"""
WebIntel - Advanced Web Intelligence System
Powered by Google Gemini 2.0 Flash AI

A superfast AI-powered web intelligence system that provides real-time web research,
comprehensive analysis, and intelligent insights using Google Gemini 2.0 Flash.
"""

import os
import sys
from pathlib import Path

__version__ = "2.0.3"
__author__ = "JustM3Sunny"
__email__ = "justm3sunny@gmail.com"
__description__ = "AI-Powered Web Intelligence System - Real-time research and intelligent insights"

def setup_webintel():
    """Auto-setup WebIntel configuration and directories"""
    try:
        # Create config directory
        config_dir = Path.home() / ".webintel"
        config_dir.mkdir(exist_ok=True)

        # Create default config if it doesn't exist
        config_file = config_dir / "config.yaml"
        if not config_file.exists():
            default_config = """# WebIntel Configuration
gemini:
  api_key: ""  # Set your Google Gemini API key here or use GEMINI_API_KEY env var
  model_name: "gemini-2.0-flash"
  max_tokens: 8192
  temperature: 0.7

scraping:
  max_concurrent_requests: 10
  request_timeout: 30
  retry_attempts: 3

output:
  format: "rich"
  save_to_file: false
  include_sources: true
"""
            config_file.write_text(default_config)

        # Create cache and output directories
        (config_dir / "cache").mkdir(exist_ok=True)
        (config_dir / "output").mkdir(exist_ok=True)

        return True
    except Exception:
        return False

# Auto-setup on import
setup_webintel()

# Import main classes for easy access
try:
    from .cli import main
    from .config import Config
    from .ai_engine import AIEngine
    from .processor import DataProcessor

    __all__ = [
        "main",
        "Config",
        "AIEngine",
        "DataProcessor",
        "setup_webintel",
        "__version__",
        "__author__",
        "__email__",
        "__description__"
    ]
except ImportError as e:
    # Handle import errors gracefully during installation
    __all__ = [
        "setup_webintel",
        "__version__",
        "__author__",
        "__email__",
        "__description__"
    ]
