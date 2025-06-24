"""
Unit tests for the Fern Model Evaluation Framework.

This module contains comprehensive unit tests for all components
of the evaluation framework.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
from src.analyzers import ComprehensiveEvaluator
from src.exceptions import UnsupportedFileTypeError
from src.models import ApplicationStructure, CodeSample, EvaluationResult
from src.universal_evaluator import UniversalCodeEvaluator
from src.universal_parser import UniversalParser
from src.utils import (
    assess_complexity_level,
    calculate_complexity_score,
    extract_function_names,
    extract_imports,
    extract_jsx_elements,
)

# Create aliases for backward compatibility with tests
SemanticSimilarityAnalyzer = ComprehensiveEvaluator
QualityAnalyzer = ComprehensiveEvaluator
FernModelEvaluator = UniversalCodeEvaluator


class TestCodeSample(unittest.TestCase):
    """Test cases for CodeSample model."""

    def test_code_sample_creation(self):
        """Test creating a valid CodeSample."""
        sample = CodeSample(
            id="test-component",
            content="const Test = () => <div>Test</div>;",
            file_path="/test/Component.tsx",
            language="typescript",
            functionality="components",
            complexity="simple",
        )

        self.assertEqual(sample.id, "test-component")
        self.assertIn("Test", sample.content)
        self.assertEqual(sample.functionality, "components")
        self.assertEqual(sample.language, "typescript")

    def test_code_sample_empty_content(self):
        """Test that empty content raises ValueError."""
        with self.assertRaises(ValueError):
            CodeSample(
                id="empty",
                content="   ",  # only whitespace
                file_path="/test/Empty.tsx",
                language="typescript",
                functionality="components",
                complexity="simple",
            )


class TestEvaluationResult(unittest.TestCase):
    """Test cases for EvaluationResult model."""

    def test_evaluation_result_creation(self):
        """Test creating a valid EvaluationResult."""
        result = EvaluationResult(
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

        self.assertEqual(result.overall_similarity, 0.85)
        self.assertEqual(result.functional_equivalence, 0.90)

    def test_evaluation_result_invalid_scores(self):
        """Test that invalid scores raise ValueError."""
        with self.assertRaises(ValueError):
            EvaluationResult(
                overall_similarity=1.5,  # Invalid: > 1.0
                functional_equivalence=0.90,
                structural_similarity=0.80,
                style_consistency=0.75,
                complexity_delta=0.1,
                performance_impact=0.95,
                maintainability_score=0.88,
                accessibility_score=0.70,
                security_score=0.92,
            )

    def test_evaluation_result_to_dict(self):
        """Test converting EvaluationResult to dictionary."""
        result = EvaluationResult(
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

        result_dict = result.to_dict()
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["overall_similarity"], 0.85)
        self.assertIn("detailed_analysis", result_dict)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_extract_imports(self):
        """Test extracting import statements."""
        code = """
        import React from 'react';
        import { Button } from '@mui/material';
        import utils from '../utils/helpers';
        """

        imports = extract_imports(code)
        expected = ["react", "@mui/material", "../utils/helpers"]
        self.assertEqual(sorted(imports), sorted(expected))

    def test_extract_function_names(self):
        """Test extracting function names."""
        code = """
        function myFunction() {}
        const myComponent = () => {};
        const AnotherComponent: React.FC = () => {};
        """

        functions = extract_function_names(code)
        self.assertIn("myFunction", functions)
        self.assertIn("myComponent", functions)
        self.assertIn("AnotherComponent", functions)

    def test_extract_jsx_elements(self):
        """Test extracting JSX elements."""
        code = """
        return (
            <div>
                <Button onClick={handleClick}>
                    <span>Click me</span>
                </Button>
            </div>
        );
        """

        elements = extract_jsx_elements(code)
        expected = ["div", "Button", "span"]
        self.assertEqual(sorted(elements), sorted(expected))

    def test_calculate_complexity_score(self):
        """Test complexity score calculation."""
        simple_code = "const x = 5;"
        complex_code = """
        async function complexFunction() {
            for (let i = 0; i < 10; i++) {
                if (condition) {
                    await someFunction();
                    while (otherCondition) {
                        // complex logic
                    }
                }
            }
        }
        """

        simple_score = calculate_complexity_score(simple_code)
        complex_score = calculate_complexity_score(complex_code)

        self.assertLess(simple_score, complex_score)

    def test_assess_complexity_level(self):
        """Test complexity level assessment."""
        simple_code = "const x = 5;"
        moderate_code = """
        const Component = () => {
            const [state, setState] = useState(false);
            return <div>{state ? 'True' : 'False'}</div>;
        };
        """

        self.assertEqual(assess_complexity_level(simple_code), "simple")
        self.assertEqual(assess_complexity_level(moderate_code), "moderate")


class TestUniversalParser(unittest.TestCase):
    """Test cases for UniversalParser."""

    def setUp(self):
        """Set up test environment."""
        self.parser = UniversalParser()
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_parse_valid_file(self):
        """Test parsing a valid JavaScript file."""
        # Create a test file
        test_file = self.test_path / "TestComponent.tsx"
        test_content = """
        import React from 'react';

        const TestComponent = () => {
            return <div>Test</div>;
        };

        export default TestComponent;
        """

        test_file.write_text(test_content)

        result = self.parser.parse_file(str(test_file))

        self.assertIsNotNone(result)
        self.assertEqual(result.file_path, str(test_file))
        self.assertIn("TestComponent", result.content)

    def test_parse_unsupported_file(self):
        """Test parsing an unsupported file type."""
        test_file = self.test_path / "test.txt"
        test_file.write_text("This is a text file")

        with self.assertRaises(UnsupportedFileTypeError):
            self.parser.parse_file(str(test_file))

    def test_parse_application_structure(self):
        """Test parsing an application structure."""
        # Create test application structure
        (self.test_path / "components").mkdir()
        (self.test_path / "pages").mkdir()

        # Create test files
        component_file = self.test_path / "components" / "Button.tsx"
        component_file.write_text("const Button = () => <button>Click</button>;")

        page_file = self.test_path / "pages" / "index.tsx"
        page_file.write_text("const HomePage = () => <div>Home</div>;")

        package_file = self.test_path / "package.json"
        package_file.write_text('{"name": "test-app", "dependencies": {}}')

        structure = self.parser.parse_application(str(self.test_path))

        self.assertIsInstance(structure, ApplicationStructure)
        self.assertGreater(len(structure.all_files), 0)
        self.assertIsNotNone(structure.main_language)


class TestSemanticSimilarityAnalyzer(unittest.TestCase):
    """Test cases for SemanticSimilarityAnalyzer."""

    def setUp(self):
        """Set up test environment."""
        self.analyzer = SemanticSimilarityAnalyzer()

    @patch("sentence_transformers.SentenceTransformer")
    def test_compute_similarity(self, mock_transformer):
        """Test computing similarity between code samples."""
        # Mock the transformer model
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[1, 0, 0], [0.8, 0.6, 0]])
        mock_transformer.return_value = mock_model

        # Create a new analyzer with the mocked model
        analyzer = SemanticSimilarityAnalyzer()
        analyzer.model = mock_model

        code1 = "const x = 5;"
        code2 = "const y = 5;"

        similarity = analyzer.compute_similarity(code1, code2)

        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)


class TestQualityAnalyzer(unittest.TestCase):
    """Test cases for QualityAnalyzer."""

    def setUp(self):
        """Set up test environment."""
        self.analyzer = QualityAnalyzer()

    def test_analyze_functional_equivalence(self):
        """Test functional equivalence analysis."""
        golden = """
        function calculateSum(a, b) {
            return a + b;
        }
        """

        generated = """
        const calculateSum = (a, b) => {
            return a + b;
        }
        """

        score = self.analyzer.analyze_functional_equivalence(golden, generated)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        self.assertGreater(score, 0.5)  # Should be high similarity

    def test_analyze_structural_similarity(self):
        """Test structural similarity analysis."""
        golden = """
        import React from 'react';
        const Component = () => <div><span>Test</span></div>;
        """

        generated = """
        import React from 'react';
        const Component = () => <div><span>Test</span></div>;
        """

        score = self.analyzer.analyze_structural_similarity(golden, generated)

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_assess_accessibility(self):
        """Test accessibility assessment."""
        good_code = """
        <img src="test.jpg" alt="Description" />
        <button aria-label="Close">X</button>
        <nav>Navigation</nav>
        """

        poor_code = """
        <img src="test.jpg" />
        <div onClick={handleClick}>Click me</div>
        """

        good_score = self.analyzer.assess_accessibility(good_code)
        poor_score = self.analyzer.assess_accessibility(poor_code)

        self.assertGreater(good_score, poor_score)

    def test_assess_security(self):
        """Test security assessment."""
        secure_code = """
        const Component = ({ content }) => (
            <div>{content}</div>
        );
        """

        insecure_code = """
        const Component = ({ html }) => (
            <div dangerouslySetInnerHTML={{__html: html}} />
        );
        const password = "hardcoded-secret";
        """

        secure_score = self.analyzer.assess_security(secure_code)
        insecure_score = self.analyzer.assess_security(insecure_code)

        self.assertGreater(secure_score, insecure_score)


class TestComprehensiveEvaluator(unittest.TestCase):
    """Test cases for ComprehensiveEvaluator."""

    def setUp(self):
        """Set up test environment."""
        self.evaluator = ComprehensiveEvaluator()

    @patch("src.analyzers.SemanticSimilarityAnalyzer.compute_similarity")
    def test_evaluate_code_pair(self, mock_similarity):
        """Test comprehensive code pair evaluation."""
        mock_similarity.return_value = 0.85

        golden_code = """
        import React from 'react';
        const Button = ({ onClick, children }) => (
            <button onClick={onClick}>{children}</button>
        );
        """

        generated_code = """
        import React from 'react';
        const Button = (props) => (
            <button onClick={props.onClick}>{props.children}</button>
        );
        """

        result = self.evaluator.evaluate_code_pair(golden_code, generated_code)

        self.assertIsInstance(result, EvaluationResult)
        self.assertGreaterEqual(result.overall_similarity, 0.0)
        self.assertLessEqual(result.overall_similarity, 1.0)
        self.assertIsInstance(result.detailed_analysis, dict)


class TestFernModelEvaluator(unittest.TestCase):
    """Test cases for FernModelEvaluator."""

    def setUp(self):
        """Set up test environment."""
        self.evaluator = FernModelEvaluator(log_level="ERROR")  # Suppress logs in tests
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    @patch("src.analyzers.SemanticSimilarityAnalyzer.compute_similarity")
    def test_evaluate_single_file(self, mock_similarity):
        """Test single file evaluation."""
        mock_similarity.return_value = 0.85

        # Create test files
        golden_file = self.test_path / "Golden.tsx"
        generated_file = self.test_path / "Generated.tsx"

        golden_content = "const Component = () => <div>Golden</div>;"
        generated_content = "const Component = () => <div>Generated</div>;"

        golden_file.write_text(golden_content)
        generated_file.write_text(generated_content)

        result = self.evaluator.evaluate_single_file(
            str(golden_file), str(generated_file)
        )

        self.assertIsInstance(result, EvaluationResult)
        self.assertEqual(result.metadata.get("evaluation_type"), "file")
        self.assertIsNotNone(result.overall_similarity)

    @patch("src.analyzers.SemanticSimilarityAnalyzer.compute_similarity")
    def test_evaluate_auto_detection(self, mock_similarity):
        """Test automatic evaluation type detection."""
        mock_similarity.return_value = 0.85

        # Create test files for file evaluation
        golden_file = self.test_path / "Golden.tsx"
        generated_file = self.test_path / "Generated.tsx"

        golden_file.write_text("const Component = () => <div>Test</div>;")
        generated_file.write_text("const Component = () => <div>Test</div>;")

        result = self.evaluator.evaluate(str(golden_file), str(generated_file), "auto")

        self.assertEqual(result.metadata.get("evaluation_type"), "file")

    def test_generate_report(self):
        """Test report generation."""
        # Mock evaluation results - use flat structure as expected by generate_report
        evaluation_results = {
            "evaluation_type": "single_file",
            "golden_path": "/test/golden.tsx",
            "generated_path": "/test/generated.tsx",
            "overall_similarity": 0.85,
            "functional_equivalence": 0.90,
            "structural_similarity": 0.80,
            "style_consistency": 0.75,
            "complexity_delta": 0.1,
            "performance_impact": 0.95,
            "maintainability_score": 0.88,
            "accessibility_score": 0.70,
            "security_score": 0.92,
            "detailed_analysis": {},
        }

        report = self.evaluator.generate_report(evaluation_results)

        self.assertIsInstance(report, str)
        self.assertIn("UNIVERSAL CODE EVALUATION REPORT", report)
        self.assertIn("Overall Similarity: 0.850", report)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete framework."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.evaluator = FernModelEvaluator(log_level="ERROR")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    @patch("src.analyzers.SemanticSimilarityAnalyzer.compute_similarity")
    def test_end_to_end_single_file(self, mock_similarity):
        """Test end-to-end single file evaluation."""
        mock_similarity.return_value = 0.85

        # Create test files
        golden_file = self.test_path / "Button.tsx"
        generated_file = self.test_path / "ButtonGenerated.tsx"

        golden_content = """
        import React from 'react';

        interface ButtonProps {
            onClick: () => void;
            children: React.ReactNode;
        }

        const Button: React.FC<ButtonProps> = ({ onClick, children }) => {
            return (
                <button onClick={onClick} className="btn">
                    {children}
                </button>
            );
        };

        export default Button;
        """

        generated_content = """
        import React from 'react';

        const Button = ({ onClick, children }) => {
            return (
                <button onClick={onClick}>
                    {children}
                </button>
            );
        };

        export default Button;
        """

        golden_file.write_text(golden_content)
        generated_file.write_text(generated_content)

        # Evaluate
        result = self.evaluator.evaluate(str(golden_file), str(generated_file))

        # Generate report
        report = self.evaluator.generate_report(result)

        # Assertions
        self.assertIsInstance(result, EvaluationResult)
        self.assertEqual(result.metadata.get("evaluation_type"), "file")
        self.assertIsNotNone(result.overall_similarity)

        self.assertIsInstance(report, str)
        self.assertIn("UNIVERSAL CODE EVALUATION REPORT", report)


if __name__ == "__main__":
    # Set up test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestCodeSample,
        TestEvaluationResult,
        TestUniversalParser,
        TestSemanticSimilarityAnalyzer,
        TestQualityAnalyzer,
        TestComprehensiveEvaluator,
        TestFernModelEvaluator,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
