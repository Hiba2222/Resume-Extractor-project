#!/usr/bin/env python3
"""
CV Extractor Pipeline (Legacy Entry Point)
------------------------------------------
This script redirects to the new bin/pipeline.py entry point.

Usage:
    python pipeline.py [--input INPUT_DIR] [--models MODEL1,MODEL2]
    
Note: This file is kept for backward compatibility.
      Please use: python bin/pipeline.py
"""

import os
import sys
import subprocess

# Get the path to the new entry point
bin_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'pipeline.py')

if __name__ == "__main__":
    print("⚠️  Note: Redirecting to new entry point at bin/pipeline.py")
    print("   Please update your scripts to use: python bin/pipeline.py\n")
    
    # Execute the new script
    sys.exit(subprocess.call([sys.executable, bin_script] + sys.argv[1:])) 