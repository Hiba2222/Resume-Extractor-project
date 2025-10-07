"""
Configuration Module
-------------------
Centralized configuration and environment variable management.

This module provides:
- Environment variable loading and validation
- Path configuration for all project directories
- API configuration for external services
- Helper functions for directory management
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# API Keys
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Paths
POPPLER_PATH = os.environ.get("POPPLER_PATH")
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_FOLDER = DATA_DIR / "uploads"
RESULTS_FOLDER = DATA_DIR / "results"
INPUT_FOLDER = DATA_DIR / "input"
OUTPUT_FOLDER = DATA_DIR / "output"
GROUND_TRUTH_FOLDER = DATA_DIR / "ground_truth"
EVALUATION_FOLDER = DATA_DIR / "evaluation"
EVALUATION_REPORTS_DIR = PROJECT_ROOT / "evaluation_reports"

# Flask Configuration
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "cv-extractor-secret-key")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
FLASK_ENV = os.environ.get("FLASK_ENV", "development")
FLASK_DEBUG = FLASK_ENV == "development"

# Upload Configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {"pdf"}

# Model Configuration
DEFAULT_MODELS = ["llama3:latest", "phi:latest", "mistral:latest"]
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Processing Configuration
REQUEST_TIMEOUT = 30  # seconds
CONNECTION_RETRIES = 2
CONTEXT_LENGTH = 8192

def ensure_directories() -> None:
    """
    Create necessary directories if they don't exist.
    
    Creates all required directories for data storage, uploads,
    results, and evaluation reports.
    """
    directories = [
        DATA_DIR,
        UPLOAD_FOLDER,
        RESULTS_FOLDER,
        INPUT_FOLDER,
        OUTPUT_FOLDER,
        GROUND_TRUTH_FOLDER,
        EVALUATION_FOLDER,
        EVALUATION_REPORTS_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def validate_config() -> List[str]:
    """
    Validate required configuration settings.
    
    Returns:
        List[str]: List of error messages for missing or invalid configuration.
                   Empty list if all configuration is valid.
    """
    errors = []
    
    if not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY is not set in environment variables")
    
    return errors


def get_config_summary() -> Dict[str, any]:
    """
    Get a summary of current configuration.
    
    Returns:
        Dict[str, any]: Dictionary containing configuration summary with
                        paths, ports, and API key availability status.
    """
    return {
        "project_root": str(PROJECT_ROOT),
        "data_dir": str(DATA_DIR),
        "flask_port": FLASK_PORT,
        "flask_debug": FLASK_DEBUG,
        "has_google_api_key": bool(GOOGLE_API_KEY),
        "has_openrouter_api_key": bool(OPENROUTER_API_KEY),
        "has_poppler_path": bool(POPPLER_PATH),
    }
