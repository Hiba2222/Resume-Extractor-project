#!/usr/bin/env python3
"""
CV Extractor - Main Entry Point
Professional AI-powered CV/Resume data extraction tool
"""

import sys
import argparse
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from web.app import create_app
from app.pipeline import CVExtractionPipeline
from app.config import Config


def run_web_app():
    """Run the web application."""
    app = create_app()
    print(f"🚀 Starting CV Extractor Web Application")
    print(f"📍 Server: http://{Config.HOST}:{Config.PORT}")
    print(f"🔧 Debug mode: {Config.DEBUG}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )


def run_cli(args):
    """Run CLI processing."""
    pipeline = CVExtractionPipeline()
    
    if args.input:
        print(f"🔄 Processing file: {args.input}")
        result = pipeline.process_file(args.input, model=args.model)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                import json
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Results saved to: {args.output}")
        else:
            import json
            print("\n📄 Extraction Results:")
            print(json.dumps(result, indent=2, ensure_ascii=False))


def run_evaluation():
    """Run evaluation."""
    try:
        from scripts.run_evaluation import main as eval_main
        eval_main()
    except ImportError:
        print("❌ Evaluation module not found. Please check scripts/run_evaluation.py")


def run_tests():
    """Run tests."""
    try:
        from scripts.run_tests import main as test_main
        test_main()
    except ImportError:
        print("❌ Test module not found. Please check scripts/run_tests.py")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CV Extractor - AI-powered resume processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py web                           # Start web application
  python main.py cli -i resume.pdf            # Process single file
  python main.py cli -i resume.pdf -o out.json # Process and save to file
  python main.py eval                          # Run evaluation
  python main.py test                          # Run tests
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Web app command
    web_parser = subparsers.add_parser('web', help='Run web application')
    
    # CLI command
    cli_parser = subparsers.add_parser('cli', help='Run CLI processing')
    cli_parser.add_argument('--input', '-i', required=True, help='Input PDF file path')
    cli_parser.add_argument('--output', '-o', help='Output JSON file path')
    cli_parser.add_argument('--model', '-m', default='llama3', 
                          choices=['llama3', 'mistral', 'phi', 'gemini'],
                          help='AI model to use')
    
    # Evaluation command
    eval_parser = subparsers.add_parser('eval', help='Run evaluation')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    
    args = parser.parse_args()
    
    if args.command == 'web':
        run_web_app()
    elif args.command == 'cli':
        run_cli(args)
    elif args.command == 'eval':
        run_evaluation()
    elif args.command == 'test':
        run_tests()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
