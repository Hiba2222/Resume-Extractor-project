#!/usr/bin/env python3
"""
Run Web Application Script
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.app import create_app
from app.config import Config


def main():
    """Run the web application."""
    print("🚀 Starting CV Extractor Web Application")
    print(f"📍 Server: http://{Config.HOST}:{Config.PORT}")
    print(f"🔧 Debug mode: {Config.DEBUG}")
    print("Press Ctrl+C to stop the server")
    
    app = create_app()
    
    try:
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")


if __name__ == "__main__":
    main()
