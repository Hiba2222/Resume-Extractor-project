#!/usr/bin/env python3
"""
CV Extractor Pipeline Launcher
------------------------------
Run the complete CV extraction pipeline:
1. Extract text from PDFs in the input folder
2. Process extracted text with various LLMs
3. Evaluate results against ground truth (if available)

Usage:
    python bin/pipeline.py [--input INPUT_DIR] [--models MODEL1,MODEL2]
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cv_extractor.config import (
    GOOGLE_API_KEY,
    POPPLER_PATH,
    INPUT_FOLDER,
    OUTPUT_FOLDER,
    RESULTS_FOLDER,
    validate_config,
    ensure_directories
)
from cv_extractor.pdf import ExtractFromPDF
from cv_extractor.llm import CVInfoExtractor

# Ensure directories exist
ensure_directories()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="CV Extractor Pipeline")
    parser.add_argument("--input", type=str, default=str(INPUT_FOLDER),
                        help="Directory containing PDF files to process")
    parser.add_argument("--output", type=str, default=str(OUTPUT_FOLDER),
                        help="Directory to save extracted text")
    parser.add_argument("--results", type=str, default=str(RESULTS_FOLDER),
                        help="Directory to save structured JSON results")
    parser.add_argument("--models", type=str, default="phi,mistral,llama3",
                        help="Comma-separated list of models to use")
    parser.add_argument("--eval", action="store_true",
                        help="Evaluate results against ground truth")
    
    return parser.parse_args()


def main():
    """Main pipeline function"""
    # Validate configuration
    errors = validate_config()
    if errors:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease check your .env file and ensure all required variables are set.\n")
        return 1
    
    # Parse arguments
    args = parse_arguments()
    
    # Create necessary directories
    input_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)
    results_dir = os.path.abspath(args.results)
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    # Check if there are any PDF files in the input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"\n❌ No PDF files found in {input_dir}")
        print(f"Please add PDF files to the input directory and try again.\n")
        return 1
    
    print("\n--- CV Extractor Pipeline ---\n")
    print(f"Found {len(pdf_files)} PDF files in {input_dir}")
    
    # Step 1: Extract text from PDFs
    print("\n[1/2] Extracting text from PDFs...")
    
    extractor = ExtractFromPDF(
        raw_folder=input_dir,
        output_folder=output_dir,
        poppler_path=POPPLER_PATH,
        api_key=GOOGLE_API_KEY
    )
    
    extraction_results = extractor.process_all_pdfs()
    print(f"✅ Extracted text from {len(extraction_results)} PDF files")
    
    # Step 2: Process the extracted text with LLMs
    print("\n[2/2] Processing extracted text with LLMs...")
    models = args.models.split(",")
    print(f"Using models: {', '.join(models)}")
    
    all_results = {}
    
    for model in models:
        print(f"\n🔄 Processing with model: {model}...")
        processor = CVInfoExtractor()
        
        model_results = {}
        
        for filename, text in extraction_results.items():
            print(f"  Processing {filename}...")
            base_name = os.path.splitext(filename)[0]
            try:
                result = processor.extract_from_cv(text)
                model_results[filename] = result
                
                # Save individual result
                result_file = os.path.join(results_dir, f"{base_name}_{model}_result.json")
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"  ❌ Error processing {filename} with {model}: {e}")
        
        all_results[model] = model_results
    
    # Save combined results
    combined_file = os.path.join(results_dir, "combined_results.json")
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\n--- Pipeline Complete ---")
    print(f"✅ Extracted text files saved to: {output_dir}")
    print(f"✅ Structured results saved to: {results_dir}")
    print(f"✅ Combined results saved to: {combined_file}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
