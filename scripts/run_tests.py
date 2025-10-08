#!/usr/bin/env python3
"""
Run tests script for CV Extractor
"""

import sys
import unittest
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_all_tests():
    """Run all tests."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent.parent / "tests"
    suite = loader.discover(str(start_dir), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_tests(test_modules):
    """Run specific test modules."""
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            module = __import__(f"tests.{module_name}", fromlist=[module_name])
            tests = unittest.TestLoader().loadTestsFromModule(module)
            suite.addTests(tests)
        except ImportError as e:
            print(f"Warning: Could not import test module '{module_name}': {e}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_tests():
    """Run integration tests."""
    # Set integration test flag
    import tests.test_pipeline
    import tests.test_web
    
    tests.test_pipeline.TestPipelineIntegration.integration_test = True
    tests.test_web.TestWebIntegration.integration_test = True
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add integration test classes
    suite.addTests(loader.loadTestsFromTestCase(tests.test_pipeline.TestPipelineIntegration))
    suite.addTests(loader.loadTestsFromTestCase(tests.test_web.TestWebIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run CV Extractor tests")
    
    parser.add_argument(
        "--module", "-m",
        nargs="+",
        help="Specific test modules to run (e.g., test_pipeline test_web)"
    )
    
    parser.add_argument(
        "--integration", "-i",
        action="store_true",
        help="Run integration tests"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run tests with coverage report"
    )
    
    args = parser.parse_args()
    
    if args.coverage:
        try:
            import coverage
            cov = coverage.Coverage()
            cov.start()
        except ImportError:
            print("Warning: coverage package not installed. Install with: pip install coverage")
            args.coverage = False
    
    success = True
    
    try:
        if args.integration:
            print("Running integration tests...")
            success = run_integration_tests()
        elif args.module:
            print(f"Running specific test modules: {', '.join(args.module)}")
            success = run_specific_tests(args.module)
        else:
            print("Running all tests...")
            success = run_all_tests()
    
    finally:
        if args.coverage:
            cov.stop()
            cov.save()
            
            print("\nCoverage Report:")
            cov.report()
            
            # Generate HTML report
            html_dir = Path(__file__).parent.parent / "htmlcov"
            cov.html_report(directory=str(html_dir))
            print(f"HTML coverage report generated in: {html_dir}")
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
