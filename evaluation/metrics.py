"""
Evaluation metrics for CV extraction
"""

from typing import Dict, Any, Set, List
import re


class EvaluationMetrics:
    """Calculates evaluation metrics for CV extraction."""
    
    def __init__(self):
        self.field_weights = {
            'personal_info': 0.3,
            'education': 0.25,
            'experience': 0.25,
            'skills': 0.15,
            'languages': 0.05
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', str(text).lower().strip())
    
    def extract_text_fields(self, data: Dict[str, Any]) -> Set[str]:
        """Extract all text fields from data for comparison."""
        fields = set()
        
        def extract_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_prefix = f"{prefix}.{key}" if prefix else key
                    extract_recursive(value, new_prefix)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_recursive(item, f"{prefix}[{i}]")
            elif obj is not None:
                normalized = self.normalize_text(str(obj))
                if normalized:
                    fields.add(f"{prefix}:{normalized}")
        
        extract_recursive(data)
        return fields
    
    def calculate_field_accuracy(self, extracted: Dict[str, Any], ground_truth: Dict[str, Any], field: str) -> float:
        """Calculate accuracy for a specific field."""
        if field not in ground_truth:
            return 1.0 if field not in extracted else 0.0
        
        if field not in extracted:
            return 0.0
        
        extracted_fields = self.extract_text_fields({field: extracted[field]})
        gt_fields = self.extract_text_fields({field: ground_truth[field]})
        
        if not gt_fields:
            return 1.0 if not extracted_fields else 0.0
        
        intersection = extracted_fields.intersection(gt_fields)
        return len(intersection) / len(gt_fields)
    
    def calculate_accuracy(self, extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Calculate overall accuracy."""
        total_accuracy = 0.0
        
        for field, weight in self.field_weights.items():
            field_accuracy = self.calculate_field_accuracy(extracted, ground_truth, field)
            total_accuracy += field_accuracy * weight
        
        return total_accuracy
    
    def calculate_precision(self, extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Calculate precision (correct extractions / total extractions)."""
        extracted_fields = self.extract_text_fields(extracted)
        gt_fields = self.extract_text_fields(ground_truth)
        
        if not extracted_fields:
            return 1.0 if not gt_fields else 0.0
        
        correct = extracted_fields.intersection(gt_fields)
        return len(correct) / len(extracted_fields)
    
    def calculate_recall(self, extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Calculate recall (correct extractions / total ground truth)."""
        extracted_fields = self.extract_text_fields(extracted)
        gt_fields = self.extract_text_fields(ground_truth)
        
        if not gt_fields:
            return 1.0
        
        correct = extracted_fields.intersection(gt_fields)
        return len(correct) / len(gt_fields)
    
    def calculate_f1_score(self, precision: float, recall: float) -> float:
        """Calculate F1 score."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def calculate_field_completeness(self, extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, float]:
        """Calculate completeness for each field."""
        completeness = {}
        
        for field in self.field_weights.keys():
            if field in ground_truth:
                gt_data = ground_truth[field]
                extracted_data = extracted.get(field, {})
                
                if isinstance(gt_data, dict):
                    gt_keys = set(gt_data.keys())
                    extracted_keys = set(extracted_data.keys()) if isinstance(extracted_data, dict) else set()
                    completeness[field] = len(extracted_keys.intersection(gt_keys)) / len(gt_keys) if gt_keys else 1.0
                elif isinstance(gt_data, list):
                    gt_count = len(gt_data)
                    extracted_count = len(extracted_data) if isinstance(extracted_data, list) else 0
                    completeness[field] = min(extracted_count / gt_count, 1.0) if gt_count > 0 else 1.0
                else:
                    completeness[field] = 1.0 if extracted_data else 0.0
            else:
                completeness[field] = 1.0
        
        return completeness
    
    def calculate_detailed_metrics(self, extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed metrics for comprehensive evaluation."""
        return {
            "overall": {
                "accuracy": self.calculate_accuracy(extracted, ground_truth),
                "precision": self.calculate_precision(extracted, ground_truth),
                "recall": self.calculate_recall(extracted, ground_truth),
                "f1_score": self.calculate_f1_score(
                    self.calculate_precision(extracted, ground_truth),
                    self.calculate_recall(extracted, ground_truth)
                )
            },
            "field_accuracy": {
                field: self.calculate_field_accuracy(extracted, ground_truth, field)
                for field in self.field_weights.keys()
            },
            "field_completeness": self.calculate_field_completeness(extracted, ground_truth)
        }
