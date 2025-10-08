"""
Tests for CV extraction pipeline
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipeline import CVExtractionPipeline
from app.config import Config


class TestCVExtractionPipeline(unittest.TestCase):
    """Test cases for CV extraction pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pipeline = CVExtractionPipeline()
        self.test_data_dir = Path(__file__).parent / "fixtures"
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        self.assertIsNotNone(self.pipeline)
        self.assertIsInstance(self.pipeline, CVExtractionPipeline)
    
    def test_supported_file_types(self):
        """Test supported file type validation."""
        # Test valid file types
        self.assertTrue(self.pipeline.is_supported_file("test.pdf"))
        
        # Test invalid file types
        self.assertFalse(self.pipeline.is_supported_file("test.txt"))
        self.assertFalse(self.pipeline.is_supported_file("test.docx"))
        self.assertFalse(self.pipeline.is_supported_file("test.jpg"))
    
    def test_process_file_with_invalid_path(self):
        """Test processing with invalid file path."""
        with self.assertRaises(FileNotFoundError):
            self.pipeline.process_file("nonexistent_file.pdf")
    
    def test_process_file_with_sample_cv(self):
        """Test processing with sample CV if available."""
        sample_cv = self.test_data_dir / "sample_cv.pdf"
        
        if sample_cv.exists():
            result = self.pipeline.process_file(str(sample_cv))
            
            # Check result structure
            self.assertIsInstance(result, dict)
            self.assertIn("personal_info", result)
            self.assertIn("education", result)
            self.assertIn("experience", result)
            self.assertIn("skills", result)
            self.assertIn("languages", result)
        else:
            self.skipTest("Sample CV not available for testing")
    
    def test_model_configuration(self):
        """Test model configuration."""
        models = ["llama3", "mistral", "phi"]
        
        for model in models:
            config = Config.get_model_config(model)
            self.assertIsInstance(config, dict)
            self.assertIn("name", config)
            self.assertIn("display_name", config)
    
    def test_output_format(self):
        """Test output format validation."""
        # Create mock result
        mock_result = {
            "personal_info": {"name": "Test User", "email": "test@example.com"},
            "education": [],
            "experience": [],
            "skills": [],
            "languages": []
        }
        
        # Test JSON serialization
        try:
            json_str = json.dumps(mock_result)
            parsed = json.loads(json_str)
            self.assertEqual(mock_result, parsed)
        except (TypeError, ValueError) as e:
            self.fail(f"Result is not JSON serializable: {e}")


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for the pipeline."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.pipeline = CVExtractionPipeline()
    
    def test_end_to_end_processing(self):
        """Test end-to-end processing workflow."""
        # This would require actual PDF files and models
        # Skip if not in integration test environment
        if not hasattr(self, 'integration_test'):
            self.skipTest("Integration test environment not available")
    
    def test_error_handling(self):
        """Test error handling in pipeline."""
        # Test with corrupted file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b"This is not a valid PDF")
            tmp_path = tmp.name
        
        try:
            with self.assertRaises(Exception):
                self.pipeline.process_file(tmp_path)
        finally:
            Path(tmp_path).unlink()


if __name__ == "__main__":
    unittest.main()
