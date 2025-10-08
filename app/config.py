"""
Configuration Module
-------------------
Centralized configuration and environment variable management.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Config:
    """Application configuration."""
    
    # Base paths
    BASE_DIR = PROJECT_ROOT
    DATA_DIR = BASE_DIR / "data"
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Paths
    POPPLER_PATH = os.getenv("POPPLER_PATH")
    UPLOAD_FOLDER = DATA_DIR / "uploads"
    OUTPUT_FOLDER = DATA_DIR / "outputs"
    RESULTS_FOLDER = DATA_DIR / "results"
    INPUT_FOLDER = DATA_DIR / "input"
    GROUND_TRUTH_FOLDER = DATA_DIR / "ground_truth"
    EVALUATION_FOLDER = DATA_DIR / "evaluation"
    
    # Web application settings
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # AI Model settings
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Processing Configuration
    REQUEST_TIMEOUT = 120  # seconds (increased for complex processing)
    CONNECTION_RETRIES = 3
    CONTEXT_LENGTH = 8192
    
    # Model configurations
    MODELS = {
        "llama3": {
            "name": "llama3",
            "display_name": "Llama 3",
            "endpoint": "llama3:latest",
            "temperature": 0.1,
            "max_tokens": 4000
        },
        "mistral": {
            "name": "mistral",
            "display_name": "Mistral",
            "endpoint": "mistral:latest",
            "temperature": 0.1,
            "max_tokens": 4000
        },
        "phi": {
            "name": "phi",
            "display_name": "Microsoft Phi",
            "endpoint": "phi:latest",
            "temperature": 0.1,
            "max_tokens": 4000
        },
        "gemini": {
            "name": "gemini",
            "display_name": "Gemini",
            "endpoint": "gemini-pro",
            "temperature": 0.1,
            "max_tokens": 4000,
            "api_key": GEMINI_API_KEY
        }
    }
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        return cls.MODELS.get(model_name, cls.MODELS[cls.DEFAULT_MODEL])
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        directories = [
            cls.DATA_DIR,
            cls.UPLOAD_FOLDER,
            cls.OUTPUT_FOLDER,
            cls.RESULTS_FOLDER,
            cls.INPUT_FOLDER,
            cls.GROUND_TRUTH_FOLDER,
            cls.EVALUATION_FOLDER,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate required configuration settings."""
        errors = []
        
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is not set in environment variables")
        
        return errors
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            "project_root": str(cls.BASE_DIR),
            "data_dir": str(cls.DATA_DIR),
            "flask_port": cls.PORT,
            "flask_debug": cls.DEBUG,
            "has_google_api_key": bool(cls.GOOGLE_API_KEY),
            "has_openrouter_api_key": bool(cls.OPENROUTER_API_KEY),
            "has_poppler_path": bool(cls.POPPLER_PATH),
        }


# Convenience functions for backward compatibility
def ensure_directories():
    """Create necessary directories if they don't exist."""
    Config.ensure_directories()

def validate_config():
    """Validate required configuration settings."""
    return Config.validate_config()

def get_config_summary():
    """Get a summary of current configuration."""
    return Config.get_config_summary()
