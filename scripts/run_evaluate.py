#!/usr/bin/env python3
"""
Real CV Evaluation Script with Optimized Model Extraction
Evaluates actual model performance using the existing app infrastructure
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from existing app infrastructure
from app.pipeline import CVExtractionPipeline
from app.config import Config
from app.models import CVInfoExtractor


class OptimizedCVEvaluator:
    """Optimized CV evaluator using existing app infrastructure"""
    
    def __init__(self, ground_truth_dir: str):
        self.ground_truth_dir = Path(ground_truth_dir)
        self.config = Config()
        self.models = ["llama3", "mistral", "phi"]
        
        # Initialize the pipeline and extractor from your app
        self.pipeline = CVExtractionPipeline(self.config)
        self.cv_extractor = CVInfoExtractor()
        
        # Optimize the extraction prompt in your existing CVInfoExtractor
        self._optimize_extraction_prompts()
    
    def _optimize_extraction_prompts(self):
        """Optimize the extraction prompts for better accuracy"""
        # Enhanced prompt for maximum accuracy
        optimized_prompt = """You are a professional CV data extraction specialist. Extract information from this resume with 100% accuracy.

CRITICAL INSTRUCTIONS:
1. Extract EXACTLY what is written - do not infer or guess
2. Maintain original formatting and spelling  
3. Include ALL skills mentioned anywhere in the document
4. Capture complete education and work history
5. Return ONLY valid JSON - no explanations or markdown

REQUIRED JSON STRUCTURE:
{{
  "personal_info": {{
    "name": "Full name as written on CV",
    "email": "Exact email address", 
    "phone": "Complete phone number with formatting",
    "address": "Full address if mentioned"
  }},
  "skills": ["Every skill mentioned", "Include technical and soft skills", "Preserve exact wording"],
  "education": [
    {{
      "degree": "Complete degree/qualification name",
      "institution": "Full institution name",
      "year": "Exact year or date range",
      "description": "Additional details"
    }}
  ],
  "experience": [
    {{
      "job_title": "Complete job title as written",
      "company": "Full company name",
      "duration": "Exact employment period",
      "description": "Key responsibilities and achievements"
    }}
  ],
  "languages": ["Language 1", "Language 2"]
}}

EXTRACT EVERYTHING. BE PRECISE. RETURN ONLY JSON.

CV Text:
{{cv_text}}"""
        
        # Replace the prompt in the existing extractor
        self.cv_extractor.extraction_prompt = optimized_prompt
    
    def load_ground_truth(self, cv_name: str) -> Dict[str, Any]:
        """Load ground truth data for a CV"""
        # Convert cv1 -> gt1, cv2 -> gt2, etc.
        if cv_name.startswith('cv'):
            gt_name = cv_name.replace('cv', 'gt')
        else:
            gt_name = f"gt{cv_name}"
        
        gt_file = self.ground_truth_dir / f"{gt_name}.json"
        if not gt_file.exists():
            raise FileNotFoundError(f"Ground truth not found: {gt_file}")
        
        with open(gt_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_with_model(self, cv_path: str, model: str) -> Dict[str, Any]:
        """Extract CV data using your existing app pipeline"""
        try:
            print(f"🔗 Using real model: {model}")
            
            # Use your existing pipeline to process the CV
            start_time = time.time()
            result = self.pipeline.process_file(cv_path, model)
            extraction_time = time.time() - start_time
            
            # Check if extraction was successful
            if 'error' in result:
                print(f"❌ Extraction error: {result['error']}")
                return self._create_error_result(model, result['error'], extraction_time)
            
            # Convert your app's format to evaluation format
            standardized_result = self._convert_app_format_to_eval_format(result)
            standardized_result['_extraction_time'] = extraction_time
            standardized_result['_model'] = model
            
            print(f"✅ Real extraction completed")
            return standardized_result
            
        except Exception as e:
            print(f"❌ Pipeline failed for {model}: {e}")
            return self._create_error_result(model, str(e), 0)
    
    def _convert_app_format_to_eval_format(self, app_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert your app's result format to evaluation format"""
        # Your app returns: personal_info, education, experience, skills, languages
        # Evaluation expects: Name, Email, Phone, Skills, Education, Experience
        
        personal_info = app_result.get('personal_info', {})
        
        return {
            "Name": personal_info.get('name', ''),
            "Email": personal_info.get('email', ''),
            "Phone": personal_info.get('phone', ''),
            "Skills": app_result.get('skills', []),
            "Education": app_result.get('education', []),
            "Experience": app_result.get('experience', [])
        }
    
    def _create_error_result(self, model: str, error: str, extraction_time: float) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            "Name": "Extraction Error",
            "Email": "",
            "Phone": "",
            "Skills": [],
            "Education": [],
            "Experience": [],
            "_extraction_time": extraction_time,
            "_model": model,
            "_error": error
        }
    
    def calculate_field_accuracy(self, extracted: Any, ground_truth: Any, field_name: str) -> float:
        """Calculate accuracy for a specific field"""
        if field_name in ['Name', 'Email', 'Phone']:
            # String fields - exact match
            return 1.0 if str(extracted).strip().lower() == str(ground_truth).strip().lower() else 0.0
        
        elif field_name == 'Skills':
            # List fields - Jaccard similarity
            if not ground_truth or not extracted:
                return 1.0 if not ground_truth and not extracted else 0.0
            
            gt_skills = set(skill.lower().strip() for skill in ground_truth)
            ex_skills = set(skill.lower().strip() for skill in extracted)
            
            if not gt_skills and not ex_skills:
                return 1.0
            
            intersection = len(gt_skills.intersection(ex_skills))
            union = len(gt_skills.union(ex_skills))
            return intersection / union if union > 0 else 0.0
        
        elif field_name in ['Education', 'Experience']:
            # Complex list fields
            if not ground_truth or not extracted:
                return 1.0 if not ground_truth and not extracted else 0.0
            
            if len(ground_truth) != len(extracted):
                return 0.5  # Partial credit for different lengths
            
            total_score = 0.0
            for gt_item, ex_item in zip(ground_truth, extracted):
                item_score = 0.0
                item_fields = 0
                
                for key in gt_item.keys():
                    if key in ex_item:
                        if str(gt_item[key]).strip().lower() == str(ex_item[key]).strip().lower():
                            item_score += 1.0
                    item_fields += 1
                
                total_score += item_score / item_fields if item_fields > 0 else 0.0
            
            return total_score / len(ground_truth)
        
        return 0.0
    
    def calculate_overall_accuracy(self, extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Calculate overall accuracy across all fields"""
        field_weights = {
            'Name': 0.15,
            'Email': 0.10,
            'Phone': 0.10,
            'Skills': 0.25,
            'Education': 0.20,
            'Experience': 0.20
        }
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for field, weight in field_weights.items():
            if field in ground_truth:
                accuracy = self.calculate_field_accuracy(
                    extracted.get(field), 
                    ground_truth.get(field), 
                    field
                )
                total_weighted_score += accuracy * weight
                total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def evaluate_single_cv(self, cv_path: str, models: List[str] = None) -> Dict[str, Any]:
        """Evaluate a single CV with specified models"""
        cv_path = Path(cv_path)
        cv_name = cv_path.stem
        
        if models is None:
            models = self.models
        
        print(f"📄 Evaluating: {cv_name}")
        
        # Load ground truth
        try:
            ground_truth = self.load_ground_truth(cv_name)
        except FileNotFoundError as e:
            print(f"❌ {e}")
            return {"error": str(e)}
        
        results = {}
        
        for model in models:
            print(f"  🤖 {model}... ", end="")
            
            # Extract with model
            extracted = self.extract_with_model(str(cv_path), model)
            
            # Calculate accuracy
            if '_error' not in extracted:
                accuracy = self.calculate_overall_accuracy(extracted, ground_truth)
                print(f"✅ {accuracy:.3f}")
            else:
                accuracy = 0.0
                print(f"❌ Error")
            
            results[model] = {
                'accuracy': accuracy,
                'extraction_time': extracted.get('_extraction_time', 0),
                'extracted_data': extracted,
                'error': extracted.get('_error')
            }
        
        return {
            'cv_name': cv_name,
            'ground_truth': ground_truth,
            'results': results
        }
    
    def evaluate_dataset(self, cv_dir: str, models: List[str] = None) -> Dict[str, Any]:
        """Evaluate entire dataset"""
        cv_dir = Path(cv_dir)
        
        if models is None:
            models = self.models
        
        print(f"🚀 Real CV Model Evaluation")
        print("=" * 50)
        print(f"📁 Dataset: {cv_dir}")
        
        # Find all CV files
        cv_files = list(cv_dir.glob("*.pdf"))
        cv_files.sort()
        
        print(f"📄 Found {len(cv_files)} CV files")
        print(f"🤖 Models: {', '.join(models)}")
        print()
        
        all_results = {}
        model_stats = {model: {'total': 0, 'successful': 0, 'failed': 0, 'total_accuracy': 0.0, 'total_time': 0.0} for model in models}
        
        for i, cv_file in enumerate(cv_files, 1):
            print(f"[{i}/{len(cv_files)}]")
            
            result = self.evaluate_single_cv(cv_file, models)
            
            if 'error' not in result:
                all_results[result['cv_name']] = result
                
                # Update statistics
                for model in models:
                    model_result = result['results'][model]
                    stats = model_stats[model]
                    stats['total'] += 1
                    
                    if model_result['error'] is None:
                        stats['successful'] += 1
                        stats['total_accuracy'] += model_result['accuracy']
                        stats['total_time'] += model_result['extraction_time']
                    else:
                        stats['failed'] += 1
            
            print()
        
        # Calculate final statistics
        summary = {}
        best_accuracy = 0.0
        best_model = ""
        fastest_model = ""
        fastest_time = float('inf')
        
        for model in models:
            stats = model_stats[model]
            avg_accuracy = stats['total_accuracy'] / stats['successful'] if stats['successful'] > 0 else 0.0
            avg_time = stats['total_time'] / stats['successful'] if stats['successful'] > 0 else 0.0
            success_rate = (stats['successful'] / stats['total']) * 100 if stats['total'] > 0 else 0.0
            
            summary[model] = {
                'total_cvs': stats['total'],
                'successful': stats['successful'],
                'failed': stats['failed'],
                'success_rate': success_rate,
                'avg_accuracy': avg_accuracy,
                'avg_time': avg_time
            }
            
            if avg_accuracy > best_accuracy:
                best_accuracy = avg_accuracy
                best_model = model
            
            if avg_time < fastest_time and stats['successful'] > 0:
                fastest_time = avg_time
                fastest_model = model
        
        # Print summary
        print("=" * 50)
        print("📊 EVALUATION SUMMARY")
        print("=" * 50)
        print()
        
        for model in models:
            stats = summary[model]
            print(f"🤖 {model.upper()}")
            print(f"   📄 Total CVs: {stats['total_cvs']}")
            print(f"   ✅ Successful: {stats['successful']}")
            print(f"   ❌ Failed: {stats['failed']}")
            print(f"   📊 Success Rate: {stats['success_rate']:.1f}%")
            print(f"   🎯 Avg Accuracy: {stats['avg_accuracy']:.3f}")
            print(f"   ⏱️  Avg Time: {stats['avg_time']:.2f}s")
            print()
        
        if best_model:
            print(f"🏆 Best Accuracy: {best_model} ({best_accuracy:.3f})")
        if fastest_model:
            print(f"⚡ Fastest: {fastest_model} ({fastest_time:.2f}s)")
        
        return {
            'summary': summary,
            'detailed_results': all_results,
            'best_model': best_model,
            'fastest_model': fastest_model
        }
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save evaluation results to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="🚀 Real CV Model Evaluation")
    parser.add_argument("--cv-dir", default="data/input", help="CV files directory")
    parser.add_argument("--ground-truth-dir", default="data/ground_truth", help="Ground truth directory")
    parser.add_argument("--models", nargs="+", default=["llama3", "mistral", "phi"], help="Models to evaluate")
    parser.add_argument("--output", default="data/real_evaluation_results.json", help="Output file")
    parser.add_argument("--single-cv", help="Evaluate single CV file")
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = OptimizedCVEvaluator(args.ground_truth_dir)
    
    try:
        if args.single_cv:
            # Evaluate single CV
            results = evaluator.evaluate_single_cv(args.single_cv, args.models)
            print(f"\n📊 Results for {Path(args.single_cv).stem}:")
            
            if 'error' not in results:
                for model, result in results['results'].items():
                    accuracy = result['accuracy']
                    time_taken = result['extraction_time']
                    print(f"  🤖 {model}: {accuracy:.3f} accuracy, {time_taken:.2f}s")
            
        else:
            # Evaluate entire dataset
            results = evaluator.evaluate_dataset(args.cv_dir, args.models)
        
        # Save results
        evaluator.save_results(results, args.output)
        
    except KeyboardInterrupt:
        print("\n👋 Evaluation interrupted by user")
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
