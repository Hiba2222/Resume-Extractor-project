#!/usr/bin/env python3
"""
Setup script for real model integration
Install required packages for CV evaluation with real models
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    """Install packages for real model integration"""
    print("🚀 Setting up real model integration for CV evaluation")
    print("=" * 60)
    
    # Required packages for different model integrations
    packages = {
        "PDF Processing": [
            "PyPDF2",
            "pdfplumber"
        ],
        "Ollama Integration": [
            "ollama"
        ],
        "OpenAI Integration": [
            "openai"
        ],
        "Hugging Face Integration": [
            "transformers",
            "torch",
            "accelerate"
        ],
        "Additional Utils": [
            "requests",
            "numpy"
        ]
    }
    
    print("📦 Installing packages...")
    
    for category, package_list in packages.items():
        print(f"\n🔧 {category}:")
        for package in package_list:
            install_package(package)
    
    print("\n" + "=" * 60)
    print("🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. For Ollama: Install Ollama and pull models:")
    print("   - Download from: https://ollama.ai")
    print("   - Run: ollama pull llama3")
    print("   - Run: ollama pull mistral")
    print("   - Run: ollama pull phi")
    
    print("\n2. For OpenAI: Set your API key:")
    print("   - Set environment variable: OPENAI_API_KEY=your_key_here")
    
    print("\n3. For Hugging Face: Models will download automatically")
    
    print("\n🚀 Run evaluation:")
    print("   python scripts/run_evaluate.py --single-cv data/input/cv1.pdf")

if __name__ == "__main__":
    main()
