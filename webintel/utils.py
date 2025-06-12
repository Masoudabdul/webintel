"""
Essential utility functions for WebIntel
"""

import re
from typing import List
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def get_domain(url: str) -> str:
    """Extract domain from URL"""
    return urlparse(url).netloc

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
    return text.strip()

# Removed extra classes - keeping only essential functions
