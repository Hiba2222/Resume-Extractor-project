"""
Evaluation module for CV Extractor models
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipeline import CVExtractionPipeline
from evaluation.metrics import EvaluationMetrics


@dataclass
class EvaluationResult:
    """Evaluation result for a single CV."""
    filename: str
    model: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    extraction_time: float
    errors: List[str]


class CVEvaluator:
    """Evaluates CV extraction models against ground truth data."""
    
    def __init__(self, ground_truth_dir: str = "data/ground_truth"):
        self.ground_truth_dir = Path(ground_truth_dir)
        self.pipeline = CVExtractionPipeline()
        self.metrics = EvaluationMetrics()
        
    def load_ground_truth(self, filename: str) -> Dict[str, Any]:
        """Load ground truth data for a CV."""
        gt_file = self.ground_truth_dir / f"{filename}.json"
        if not gt_file.exists():
            raise FileNotFoundError(f"Ground truth file not found: {gt_file}")
            
        with open(gt_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def evaluate_single_cv(self, cv_path: str, model: str = "llama3") -> EvaluationResult:
        """Evaluate extraction for a single CV."""
        import time
        
        filename = Path(cv_path).stem
        
        try:
            # Load ground truth
            ground_truth = self.load_ground_truth(filename)
            
            # Extract data using model
            start_time = time.time()
            extracted_data = self.pipeline.process_file(cv_path, model=model)
            extraction_time = time.time() - start_time
            
            # Calculate metrics
            accuracy = self.metrics.calculate_accuracy(extracted_data, ground_truth)
            precision = self.metrics.calculate_precision(extracted_data, ground_truth)
            recall = self.metrics.calculate_recall(extracted_data, ground_truth)
            f1_score = self.metrics.calculate_f1_score(precision, recall)
            
            return EvaluationResult(
                filename=filename,
                model=model,
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1_score,
                extraction_time=extraction_time,
                errors=[]
            )
            
        except Exception as e:
            return EvaluationResult(
                filename=filename,
                model=model,
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                extraction_time=0.0,
                errors=[str(e)]
            )
    
    def evaluate_dataset(self, cv_dir: str, models: List[str] = None) -> Dict[str, List[EvaluationResult]]:
        """Evaluate multiple CVs with multiple models."""
        if models is None:
            models = ["llama3", "mistral", "phi"]
            
        cv_dir = Path(cv_dir)
        results = {model: [] for model in models}
        
        # Get all PDF files
        pdf_files = list(cv_dir.glob("*.pdf"))
        
        print(f"Evaluating {len(pdf_files)} CVs with {len(models)} models...")
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            
            for model in models:
                print(f"  - Using model: {model}")
                result = self.evaluate_single_cv(str(pdf_file), model)
                results[model].append(result)
        
        return results
    
    def generate_report(self, results: Dict[str, List[EvaluationResult]]) -> Dict[str, Any]:
        """Generate evaluation report."""
        report = {
            "summary": {},
            "detailed_results": results,
            "model_comparison": {}
        }
        
        # Calculate summary statistics for each model
        for model, model_results in results.items():
            if not model_results:
                continue
                
            accuracies = [r.accuracy for r in model_results if not r.errors]
            precisions = [r.precision for r in model_results if not r.errors]
            recalls = [r.recall for r in model_results if not r.errors]
            f1_scores = [r.f1_score for r in model_results if not r.errors]
            times = [r.extraction_time for r in model_results if not r.errors]
            
            report["summary"][model] = {
                "total_cvs": len(model_results),
                "successful_extractions": len([r for r in model_results if not r.errors]),
                "failed_extractions": len([r for r in model_results if r.errors]),
                "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
                "avg_precision": sum(precisions) / len(precisions) if precisions else 0,
                "avg_recall": sum(recalls) / len(recalls) if recalls else 0,
                "avg_f1_score": sum(f1_scores) / len(f1_scores) if f1_scores else 0,
                "avg_extraction_time": sum(times) / len(times) if times else 0
            }
        
        # Model comparison
        if len(results) > 1:
            best_accuracy = max(report["summary"].items(), 
                              key=lambda x: x[1]["avg_accuracy"])
            best_speed = min(report["summary"].items(), 
                           key=lambda x: x[1]["avg_extraction_time"])
            
            report["model_comparison"] = {
                "best_accuracy": {"model": best_accuracy[0], "score": best_accuracy[1]["avg_accuracy"]},
                "fastest": {"model": best_speed[0], "time": best_speed[1]["avg_extraction_time"]}
            }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_file: str = "data/evaluation_report.json"):
        """Save evaluation report to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert dataclasses to dict for JSON serialization
        serializable_report = self._make_serializable(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_report, f, indent=2, ensure_ascii=False)
        
        print(f"Evaluation report saved to: {output_path}")
    
    def _make_serializable(self, obj):
        """Convert dataclasses and other objects to JSON serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, EvaluationResult):
            return {
                "filename": obj.filename,
                "model": obj.model,
                "accuracy": obj.accuracy,
                "precision": obj.precision,
                "recall": obj.recall,
                "f1_score": obj.f1_score,
                "extraction_time": obj.extraction_time,
                "errors": obj.errors
            }
        else:
            return obj
