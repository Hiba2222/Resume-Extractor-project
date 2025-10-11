#!/usr/bin/env python3
"""
Quick test of the app infrastructure
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.pipeline import CVExtractionPipeline
from app.config import Config
from app.models import CVInfoExtractor

def test_app_infrastructure():
    """Test the app components"""
    print("🧪 Testing App Infrastructure")
    print("=" * 40)
    
    # Test config
    print("📋 Testing Config...")
    config = Config()
    print(f"✅ Config loaded - Default model: {config.DEFAULT_MODEL}")
    
    # Test CV extractor
    print("\n🤖 Testing CVInfoExtractor...")
    extractor = CVInfoExtractor()
    
    # Check Ollama availability
    ollama_available = extractor.check_ollama_available()
    if ollama_available:
        print("✅ Ollama connection successful")
    else:
        print("❌ Ollama not available")
    
    # Check OpenRouter availability  
    openrouter_available = extractor.check_openrouter_available()
    if openrouter_available:
        print("✅ OpenRouter connection successful")
    else:
        print("❌ OpenRouter not available")
    
    # Test pipeline
    print("\n🔄 Testing Pipeline...")
    pipeline = CVExtractionPipeline(config)
    print("✅ Pipeline initialized")
    
    # Test with sample CV
    cv_path = "data/input/cv1.pdf"
    if Path(cv_path).exists():
        print(f"\n📄 Testing with {cv_path}...")
        try:
            result = pipeline.process_file(cv_path, "llama3")
            if 'error' not in result:
                print("✅ CV processing successful")
                print(f"📊 Extracted fields: {list(result.keys())}")
                
                # Show sample data
                if 'personal_info' in result:
                    personal = result['personal_info']
                    print(f"👤 Name: {personal.get('name', 'N/A')}")
                    print(f"📧 Email: {personal.get('email', 'N/A')}")
                
                if 'skills' in result:
                    skills = result['skills']
                    print(f"🛠️ Skills count: {len(skills)}")
                    if skills:
                        print(f"🛠️ Sample skills: {skills[:3]}")
                
            else:
                print(f"❌ CV processing failed: {result['error']}")
        except Exception as e:
            print(f"❌ Pipeline test failed: {e}")
    else:
        print(f"⚠️ Test CV not found: {cv_path}")
    
    print("\n" + "=" * 40)
    print("🎉 App infrastructure test complete!")

if __name__ == "__main__":
    test_app_infrastructure()
