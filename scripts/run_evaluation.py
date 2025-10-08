#!/usr/bin/env python3
"""
Run evaluation script for CV Extractor
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.evaluator import CVEvaluator


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Run CV Extractor evaluation")
    
    parser.add_argument(
        "--cv-dir", 
        default="data/samples",
        help="Directory containing CV files to evaluate"
    )
    
    parser.add_argument(
        "--ground-truth-dir",
        default="data/ground_truth", 
        help="Directory containing ground truth JSON files"
    )
    
    parser.add_argument(
        "--models",
        nargs="+",
        default=["llama3", "mistral", "phi"],
        help="Models to evaluate"
    )
    
    parser.add_argument(
        "--output",
        default="data/evaluation_report.json",
        help="Output file for evaluation report"
    )
    
    parser.add_argument(
        "--single-cv",
        help="Evaluate a single CV file"
    )
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = CVEvaluator(ground_truth_dir=args.ground_truth_dir)
    
    if args.single_cv:
        # Evaluate single CV
        print(f"Evaluating single CV: {args.single_cv}")
        
        for model in args.models:
            print(f"\nUsing model: {model}")
            result = evaluator.evaluate_single_cv(args.single_cv, model)
            
            print(f"Results for {result.filename}:")
            print(f"  Accuracy: {result.accuracy:.3f}")
            print(f"  Precision: {result.precision:.3f}")
            print(f"  Recall: {result.recall:.3f}")
            print(f"  F1 Score: {result.f1_score:.3f}")
            print(f"  Extraction Time: {result.extraction_time:.2f}s")
            
            if result.errors:
                print(f"  Errors: {', '.join(result.errors)}")
    
    else:
        # Evaluate dataset
        print(f"Evaluating dataset in: {args.cv_dir}")
        print(f"Using models: {', '.join(args.models)}")
        
        # Check if directories exist
        cv_dir = Path(args.cv_dir)
        if not cv_dir.exists():
            print(f"Error: CV directory not found: {cv_dir}")
            return 1
        
        gt_dir = Path(args.ground_truth_dir)
        if not gt_dir.exists():
            print(f"Error: Ground truth directory not found: {gt_dir}")
            return 1
        
        # Run evaluation
        results = evaluator.evaluate_dataset(str(cv_dir), args.models)
        
        # Generate and save report
        report = evaluator.generate_report(results)
        evaluator.save_report(report, args.output)
        
        # Print summary
        print("\n" + "="*50)
        print("EVALUATION SUMMARY")
        print("="*50)
        
        for model, summary in report["summary"].items():
            print(f"\nModel: {model}")
            print(f"  Total CVs: {summary['total_cvs']}")
            print(f"  Successful: {summary['successful_extractions']}")
            print(f"  Failed: {summary['failed_extractions']}")
            print(f"  Avg Accuracy: {summary['avg_accuracy']:.3f}")
            print(f"  Avg Precision: {summary['avg_precision']:.3f}")
            print(f"  Avg Recall: {summary['avg_recall']:.3f}")
            print(f"  Avg F1 Score: {summary['avg_f1_score']:.3f}")
            print(f"  Avg Time: {summary['avg_extraction_time']:.2f}s")
        
        # Model comparison
        if "model_comparison" in report and report["model_comparison"]:
            print(f"\nBest Accuracy: {report['model_comparison']['best_accuracy']['model']} "
                  f"({report['model_comparison']['best_accuracy']['score']:.3f})")
            print(f"Fastest: {report['model_comparison']['fastest']['model']} "
                  f"({report['model_comparison']['fastest']['time']:.2f}s)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
