#!/usr/bin/env python3
"""
CV Extractor Web Interface (Legacy Entry Point)
-----------------------------------------------
This script redirects to the new bin/run_web.py entry point.

Usage:
    python run_web.py
    
Note: This file is kept for backward compatibility.
      Please use: python bin/run_web.py
"""

import os
import sys
import subprocess

# Get the path to the new entry point
bin_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'run_web.py')

if __name__ == "__main__":
    print("⚠️  Note: Redirecting to new entry point at bin/run_web.py")
    print("   Please update your scripts to use: python bin/run_web.py\n")
    
    # Execute the new script
    sys.exit(subprocess.call([sys.executable, bin_script] + sys.argv[1:]))