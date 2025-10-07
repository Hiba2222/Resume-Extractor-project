#!/usr/bin/env python3
"""
CV Extractor Web Interface Launcher
-----------------------------------
Thin wrapper to launch the Flask web application.

Usage:
    python bin/run_web.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cv_extractor.config import (
    GOOGLE_API_KEY,
    FLASK_PORT,
    FLASK_DEBUG,
    validate_config,
    ensure_directories
)
from cv_extractor.web import app

# Ensure directories exist
ensure_directories()

# Validate configuration
errors = validate_config()
if errors:
    print("\n❌ Configuration errors:")
    for error in errors:
        print(f"  - {error}")
    print("\nPlease check your .env file and ensure all required variables are set.\n")
    sys.exit(1)

if __name__ == "__main__":
    print(f"\n--- CV Extractor Web Interface ---")
    print(f"Upload and process individual PDF files")
    print(f"Access the web interface at: http://localhost:{FLASK_PORT}")
    print(f"Debug mode: {FLASK_DEBUG}\n")
    
    app.run(debug=FLASK_DEBUG, host="0.0.0.0", port=FLASK_PORT)
