#!/usr/bin/env python3
"""
CV Extractor Evaluation Runner
------------------------------
Prepare data and run model performance evaluation.

Usage:
    python bin/run_evaluation.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cv_extractor.config import ensure_directories
from cv_extractor.evaluation.runner import (
    prepare_ground_truth,
    organize_model_results,
    main as run_evaluation_main
)

# Ensure directories exist
ensure_directories()


def main():
    """Main evaluation function"""
    print("=" * 60)
    print("CV Extractor - Model Evaluation System")
    print("=" * 60)
    
    print("\n[1/3] Preparing ground truth data...")
    try:
        ground_truth_path, combined_ground_truth = prepare_ground_truth()
        print(f"✅ Ground truth prepared: {ground_truth_path}")
    except Exception as e:
        print(f"❌ Error preparing ground truth: {e}")
        return 1
    
    print("\n[2/3] Organizing model results...")
    try:
        results_dir = organize_model_results(combined_ground_truth)
        print(f"✅ Model results organized: {results_dir}")
    except Exception as e:
        print(f"❌ Error organizing results: {e}")
        return 1
    
    print("\n[3/3] Running evaluation...")
    print(f"Ground Truth: {ground_truth_path}")
    print(f"Results Directory: {results_dir}")
    
    try:
        # Run evaluation
        results = run_evaluation_main(ground_truth_path, results_dir)
        
        print("\n" + "=" * 60)
        print("✅ Evaluation completed successfully!")
        print("=" * 60)
        print("\n📊 Check the 'evaluation_reports' directory for:")
        print("  - Detailed results and visualizations")
        print("  - Model comparison charts")
        print("  - Performance metrics\n")
        
        return 0
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
