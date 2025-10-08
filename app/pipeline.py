#!/usr/bin/env python3
"""
CV Extractor Pipeline
--------------------
Core processing pipeline for CV extraction and analysis.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from app.config import Config
from app.extractor import ExtractFromPDF
from app.models import CVInfoExtractor
from app.utils import ensure_directories, validate_file


class CVExtractionPipeline:
    """Main pipeline for CV extraction and processing."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the pipeline."""
        self.config = config or Config()
        ensure_directories()
        
        # Initialize components
        self.pdf_extractor = ExtractFromPDF()
        self.cv_processor = CVInfoExtractor()
    
    def is_supported_file(self, filename: str) -> bool:
        """Check if file type is supported."""
        return filename.lower().endswith('.pdf')
    
    def process_file(self, file_path: str, model: str = None) -> Dict[str, Any]:
        """Process a single CV file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.is_supported_file(file_path.name):
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Use default model if not specified
        if model is None:
            model = self.config.DEFAULT_MODEL
        
        print(f"Processing: {file_path.name}")
        print(f"Using model: {model}")
        
        try:
            # Step 1: Extract text from PDF
            print("  [1/2] Extracting text from PDF...")
            extracted_text = self.pdf_extractor.extract_text(str(file_path))
            
            # Step 2: Process with LLM
            print("  [2/2] Processing with AI model...")
            result = self.cv_processor.extract_from_cv(extracted_text, model=model)
            
            # Add metadata
            result['metadata'] = {
                'filename': file_path.name,
                'model_used': model,
                'processing_status': 'success'
            }
            
            print("  ✅ Processing complete")
            return result
            
        except Exception as e:
            error_result = {
                'error': str(e),
                'metadata': {
                    'filename': file_path.name,
                    'model_used': model,
                    'processing_status': 'failed'
                }
            }
            print(f"  ❌ Error: {e}")
            return error_result
    
    def process_directory(self, input_dir: str, models: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """Process all PDF files in a directory."""
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")
        
        # Get all PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if not pdf_files:
            raise ValueError(f"No PDF files found in {input_dir}")
        
        if models is None:
            models = [self.config.DEFAULT_MODEL]
        
        print(f"\n--- CV Extraction Pipeline ---")
        print(f"Found {len(pdf_files)} PDF files in {input_dir}")
        print(f"Using models: {', '.join(models)}")
        
        all_results = {}
        
        for model in models:
            print(f"\n🔄 Processing with model: {model}")
            model_results = {}
            
            for pdf_file in pdf_files:
                result = self.process_file(str(pdf_file), model)
                model_results[pdf_file.name] = result
            
            all_results[model] = model_results
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], output_dir: str, filename: str = "results.json"):
        """Save results to file."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {output_file}")
        return str(output_file)
    
    def process_and_save(self, input_path: str, output_dir: str = None, models: List[str] = None) -> str:
        """Process files and save results."""
        if output_dir is None:
            output_dir = self.config.OUTPUT_FOLDER
        
        input_path = Path(input_path)
        
        if input_path.is_file():
            # Process single file
            result = self.process_file(str(input_path), models[0] if models else None)
            filename = f"{input_path.stem}_result.json"
        else:
            # Process directory
            result = self.process_directory(str(input_path), models)
            filename = "batch_results.json"
        
        return self.save_results(result, output_dir, filename)


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CV Extractor Pipeline")
    parser.add_argument("input", help="Input PDF file or directory")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--models", "-m", nargs="+", default=["llama3"],
                       help="Models to use for processing")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = CVExtractionPipeline()
    
    try:
        # Process and save
        output_file = pipeline.process_and_save(
            args.input, 
            args.output, 
            args.models
        )
        
        print(f"\n✅ Pipeline completed successfully!")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
