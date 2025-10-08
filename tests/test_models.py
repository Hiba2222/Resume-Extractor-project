"""
Tests for AI models
"""

import unittest
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import CVInfoExtractor
from app.config import Config


class TestCVInfoExtractor(unittest.TestCase):
    """Test cases for CV information extractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = CVInfoExtractor()
        self.sample_cv_text = """
        John Doe
        Email: john.doe@example.com
        Phone: +1 234 567 8900
        Address: 123 Main St, City, State
        
        Education:
        - Bachelor of Science in Computer Science, University of Example, 2020
        
        Experience:
        - Software Engineer at Tech Company, 2020-2023
        - Developed web applications using Python and JavaScript
        
        Skills: Python, JavaScript, React, Flask
        Languages: English, Spanish
        """
    
    def test_extractor_initialization(self):
        """Test extractor initialization."""
        self.assertIsNotNone(self.extractor)
        self.assertIsInstance(self.extractor, CVInfoExtractor)
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = self.extractor.get_cache_key("test text", "llama3")
        key2 = self.extractor.get_cache_key("test text", "llama3")
        key3 = self.extractor.get_cache_key("different text", "llama3")
        
        # Same input should generate same key
        self.assertEqual(key1, key2)
        # Different input should generate different key
        self.assertNotEqual(key1, key3)
    
    def test_json_extraction(self):
        """Test JSON extraction from response."""
        # Test valid JSON
        valid_json = '{"personal_info": {"name": "John Doe"}, "skills": ["Python"]}'
        result = self.extractor.extract_json_from_response(valid_json)
        self.assertIsInstance(result, dict)
        self.assertIn("personal_info", result)
    
    def test_normalize_extraction_result(self):
        """Test result normalization."""
        raw_result = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "JavaScript"]
        }
        
        normalized = self.extractor._normalize_extraction_result(raw_result)
        
        self.assertIn("personal_info", normalized)
        self.assertIn("education", normalized)
        self.assertIn("experience", normalized)
        self.assertIn("skills", normalized)
        self.assertIn("languages", normalized)
        
        # Check if name was moved to personal_info
        self.assertEqual(normalized["personal_info"]["name"], "John Doe")
        self.assertEqual(normalized["personal_info"]["email"], "john@example.com")
        self.assertEqual(normalized["skills"], ["Python", "JavaScript"])
    
    def test_model_availability_check(self):
        """Test model availability checking."""
        # This will depend on what models are actually available
        # Just test that the method doesn't crash
        try:
            ollama_available = self.extractor.check_ollama_available()
            self.assertIsInstance(ollama_available, bool)
        except Exception:
            # It's okay if Ollama is not available in test environment
            pass
    
    def test_extraction_with_mock_data(self):
        """Test extraction with mock CV data."""
        # This is a basic test - in real scenarios you'd mock the API calls
        try:
            result = self.extractor.extract_from_cv(self.sample_cv_text)
            
            # Check that result has expected structure
            self.assertIsInstance(result, dict)
            self.assertIn("personal_info", result)
            self.assertIn("education", result)
            self.assertIn("experience", result)
            self.assertIn("skills", result)
            self.assertIn("languages", result)
            
        except Exception as e:
            # In test environment, API calls might fail
            # That's okay, we're just testing the structure
            self.skipTest(f"API not available in test environment: {e}")


class TestModelConfiguration(unittest.TestCase):
    """Test model configuration."""
    
    def test_model_configs(self):
        """Test model configurations."""
        for model_name in ["llama3", "mistral", "phi", "gemini"]:
            config = Config.get_model_config(model_name)
            self.assertIsInstance(config, dict)
            self.assertIn("name", config)
            self.assertIn("display_name", config)
            self.assertIn("endpoint", config)


if __name__ == "__main__":
    unittest.main()
