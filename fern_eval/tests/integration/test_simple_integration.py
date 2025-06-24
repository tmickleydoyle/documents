"""
Simple integration tests for the Universal Code Evaluation Framework.

This module contains basic integration tests to verify the framework works end-to-end.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.models import EvaluationResult
from src.universal_evaluator import UniversalCodeEvaluator
from src.universal_parser import UniversalParser


class TestSimpleIntegration(unittest.TestCase):
    """Simple integration tests for the framework."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.parser = UniversalParser()
        self.evaluator = UniversalCodeEvaluator()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_parse_and_evaluate_python_file(self):
        """Test parsing and evaluating a Python file."""
        # Create test file
        test_file = self.test_path / "test_function.py"
        test_content = """
def calculate_sum(a, b):
    \"\"\"Calculate the sum of two numbers.\"\"\"
    return a + b

def multiply(x, y):
    \"\"\"Multiply two numbers.\"\"\"
    return x * y
"""
        test_file.write_text(test_content)

        # Parse the file
        file_info = self.parser.parse_file(str(test_file))

        # Verify parsing worked
        self.assertIsNotNone(file_info)
        self.assertEqual(file_info.language, "python")
        self.assertIn("calculate_sum", file_info.content)
        self.assertIn("multiply", file_info.content)

    def test_parse_and_evaluate_javascript_file(self):
        """Test parsing and evaluating a JavaScript file."""
        # Create test file
        test_file = self.test_path / "component.jsx"
        test_content = """
import React from 'react';

const Button = ({ onClick, children }) => {
    return (
        <button onClick={onClick} className="btn">
            {children}
        </button>
    );
};

export default Button;
"""
        test_file.write_text(test_content)

        # Parse the file
        file_info = self.parser.parse_file(str(test_file))

        # Verify parsing worked
        self.assertIsNotNone(file_info)
        self.assertEqual(file_info.language, "javascript")
        self.assertIn("Button", file_info.content)
        self.assertIn("React", file_info.content)

    @patch("src.analyzers.ComprehensiveEvaluator.evaluate_code_pair")
    def test_end_to_end_evaluation(self, mock_evaluate):
        """Test end-to-end file evaluation."""
        # Mock the evaluation
        mock_result = EvaluationResult(
            overall_similarity=0.85,
            functional_equivalence=0.90,
            structural_similarity=0.80,
            style_consistency=0.75,
            complexity_delta=0.1,
            performance_impact=0.95,
            maintainability_score=0.88,
            accessibility_score=0.70,
            security_score=0.92,
        )
        mock_evaluate.return_value = mock_result

        # Create test files
        golden_file = self.test_path / "golden.py"
        generated_file = self.test_path / "generated.py"

        golden_content = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

        generated_content = """
def factorial(num):
    if num <= 1:
        return 1
    else:
        return num * factorial(num - 1)
"""

        golden_file.write_text(golden_content)
        generated_file.write_text(generated_content)

        # Evaluate
        result = self.evaluator.evaluate_files(str(golden_file), str(generated_file))

        # Verify evaluation worked
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EvaluationResult)
        self.assertEqual(result.overall_similarity, 0.85)

    def test_parse_application_structure(self):
        """Test parsing a simple application structure."""
        # Create test application structure
        (self.test_path / "src").mkdir()
        (self.test_path / "src" / "components").mkdir()
        (self.test_path / "src" / "utils").mkdir()

        # Create test files
        component_file = self.test_path / "src" / "components" / "Button.tsx"
        component_file.write_text("const Button = () => <button>Click</button>;")

        util_file = self.test_path / "src" / "utils" / "helpers.js"
        util_file.write_text("export const add = (a, b) => a + b;")

        main_file = self.test_path / "src" / "index.js"
        main_file.write_text("console.log('Hello World');")

        package_file = self.test_path / "package.json"
        package_file.write_text('{"name": "test-app", "version": "1.0.0"}')

        # Parse the application
        structure = self.parser.parse_application(str(self.test_path))

        # Verify parsing worked
        self.assertIsNotNone(structure)
        self.assertGreater(len(structure.all_files), 0)
        self.assertIsNotNone(structure.main_language)


if __name__ == "__main__":
    unittest.main(verbosity=2)
