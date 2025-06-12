"""
Configuration management for WebIntel
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Disable all logging
logging.disable(logging.CRITICAL)

# Load environment variables
load_dotenv()

class ScrapingConfig(BaseModel):
    """Web scraping configuration"""
    max_concurrent_requests: int = Field(default=10, ge=1, le=50)
    request_timeout: int = Field(default=30, ge=5, le=120)
    retry_attempts: int = Field(default=3, ge=1, le=10)
    delay_between_requests: float = Field(default=0.5, ge=0.1, le=5.0)
    max_pages_per_site: int = Field(default=5, ge=1, le=20)
    user_agent_rotation: bool = Field(default=True)

class GeminiConfig(BaseModel):
    """Gemini AI configuration"""
    api_key: str = Field(default="")
    model_name: str = Field(default="gemini-2.0-flash")
    max_tokens: int = Field(default=8192, ge=1000, le=32000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.1, le=1.0)
    top_k: int = Field(default=40, ge=1, le=100)

class OutputConfig(BaseModel):
    """Output formatting configuration"""
    format: str = Field(default="rich", pattern="^(rich|json|markdown|plain)$")
    save_to_file: bool = Field(default=False)
    output_directory: str = Field(default="./webintel_results")
    include_sources: bool = Field(default=True)
    max_summary_length: int = Field(default=2000, ge=500, le=5000)

class Config(BaseModel):
    """Main configuration class"""
    scraping: ScrapingConfig = Field(default_factory=ScrapingConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    
    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = Path.home() / ".webintel" / "config.yaml"
        
        config_path = Path(config_path)
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            return cls(**config_data)
        else:
            # Create default config
            config = cls()
            config.save_to_file(config_path)
            return config
    
    def save_to_file(self, config_path: Optional[str] = None) -> None:
        """Save configuration to YAML file"""
        if config_path is None:
            config_path = Path.home() / ".webintel" / "config.yaml"
        
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, indent=2)
    
    def update_from_env(self) -> None:
        """Update configuration from environment variables"""
        if os.getenv("GEMINI_API_KEY"):
            self.gemini.api_key = os.getenv("GEMINI_API_KEY")
        
        if os.getenv("WEBINTEL_MAX_CONCURRENT"):
            self.scraping.max_concurrent_requests = int(os.getenv("WEBINTEL_MAX_CONCURRENT"))
        
        if os.getenv("WEBINTEL_OUTPUT_FORMAT"):
            self.output.format = os.getenv("WEBINTEL_OUTPUT_FORMAT")

def get_default_config() -> Config:
    """Get default configuration with environment variable overrides"""
    config = Config.load_from_file()
    config.update_from_env()
    return config
