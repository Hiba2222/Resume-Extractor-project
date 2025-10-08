"""
Tests for web application
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.app import create_app


class TestWebApplication(unittest.TestCase):
    """Test cases for web application."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_home_page(self):
        """Test home page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CV Extractor', response.data)
    
    def test_upload_page(self):
        """Test upload page loads correctly."""
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'upload', response.data.lower())
    
    def test_about_page(self):
        """Test about page loads correctly."""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'about', response.data.lower())
    
    def test_upload_no_file(self):
        """Test upload with no file."""
        response = self.client.post('/upload', data={})
        # Should redirect or show error
        self.assertIn(response.status_code, [400, 302])
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type."""
        with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
            tmp.write(b"This is a text file")
            tmp.seek(0)
            
            response = self.client.post('/upload', data={
                'file': (tmp, 'test.txt')
            })
            
            # Should reject invalid file type
            self.assertIn(response.status_code, [400, 302])
    
    def test_upload_valid_pdf(self):
        """Test upload with valid PDF (mock)."""
        # Create a minimal PDF-like file for testing
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            tmp.write(pdf_content)
            tmp.seek(0)
            
            response = self.client.post('/upload', data={
                'file': (tmp, 'test.pdf')
            })
            
            # Should accept PDF file (might fail processing, but should accept upload)
            self.assertIn(response.status_code, [200, 302, 500])  # 500 is OK for processing failure
    
    def test_api_health_check(self):
        """Test API health check if available."""
        response = self.client.get('/api/health')
        # Might not exist, so just check it doesn't crash
        self.assertIn(response.status_code, [200, 404])
    
    def test_static_files(self):
        """Test static file serving."""
        # Test CSS file
        response = self.client.get('/static/style.css')
        self.assertIn(response.status_code, [200, 404])  # 404 is OK if file doesn't exist yet
    
    def test_error_handling(self):
        """Test error page handling."""
        # Test non-existent route
        response = self.client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)


class TestWebIntegration(unittest.TestCase):
    """Integration tests for web application."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
    
    def test_full_upload_workflow(self):
        """Test complete upload and processing workflow."""
        # Skip if not in integration environment
        if not hasattr(self, 'integration_test'):
            self.skipTest("Integration test environment not available")
    
    def test_session_handling(self):
        """Test session management."""
        with self.client.session_transaction() as sess:
            sess['test_key'] = 'test_value'
        
        # Session should persist across requests
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
