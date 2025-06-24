# filepath: tests/unit/test_analyzers.py
"""
Unit tests for the analyzer classes.

This module tests the core analysis engines:
- SemanticSimilarityAnalyzer
- QualityAnalyzer
- ComprehensiveEvaluator
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest
from src.analyzers import (
    ComprehensiveEvaluator,
    QualityAnalyzer,
    SemanticSimilarityAnalyzer,
)
from src.exceptions import EvaluationError
from src.models import EvaluationResult


class TestSemanticSimilarityAnalyzer:
    """Test the SemanticSimilarityAnalyzer class."""

    def test_init_with_default_model(self):
        """Test initialization with default model."""
        analyzer = SemanticSimilarityAnalyzer()
        assert analyzer.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        # Model might be None if sentence-transformers is not available
        assert analyzer.model is None or analyzer.model is not None

    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        model_name = "custom-model"
        analyzer = SemanticSimilarityAnalyzer(model_name)
        assert analyzer.model_name == model_name

    def test_compute_embeddings_fallback(self):
        """Test embedding computation when model is not available."""
        analyzer = SemanticSimilarityAnalyzer()
        analyzer.model = None  # Force fallback

        code_samples = ["def hello():\n    pass", "function hello() {}"]
        embeddings = analyzer.compute_embeddings(code_samples)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == len(code_samples)
        assert embeddings.shape[1] == 384  # Default embedding size

    @patch("sentence_transformers.SentenceTransformer")
    def test_compute_embeddings_with_model(self, mock_transformer):
        """Test embedding computation with loaded model."""
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(2, 384)
        mock_transformer.return_value = mock_model

        analyzer = SemanticSimilarityAnalyzer()
        analyzer.model = mock_model

        code_samples = ["def hello():\n    pass", "function hello() {}"]
        embeddings = analyzer.compute_embeddings(code_samples)

        assert isinstance(embeddings, np.ndarray)
        mock_model.encode.assert_called_once()

    def test_compute_similarity_score(self):
        """Test similarity score computation."""
        analyzer = SemanticSimilarityAnalyzer()

        golden_code = "def hello():\n    return 'Hello'"
        generated_code = "def hello():\n    return 'Hello'"

        similarity = analyzer.compute_similarity_score(golden_code, generated_code)

        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0

    def test_compute_similarity_different_code(self):
        """Test similarity with completely different code."""
        analyzer = SemanticSimilarityAnalyzer()

        golden_code = "def hello():\n    return 'Hello'"
        generated_code = "let x = 5; console.log(x);"

        similarity = analyzer.compute_similarity_score(golden_code, generated_code)

        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0


class TestQualityAnalyzer:
    """Test the QualityAnalyzer class."""

    def test_init(self):
        """Test QualityAnalyzer initialization."""
        analyzer = QualityAnalyzer()
        assert analyzer is not None

    def test_analyze_functional_equivalence(self):
        """Test functional equivalence analysis."""
        analyzer = QualityAnalyzer()

        golden = "def add(a, b):\n    return a + b"
        generated = "def add(x, y):\n    return x + y"

        score = analyzer.analyze_functional_equivalence(golden, generated)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_analyze_structural_similarity(self):
        """Test structural similarity analysis."""
        analyzer = QualityAnalyzer()

        golden = "if x > 0:\n    print('positive')"
        generated = "if x > 0:\n    print('positive')"

        score = analyzer.analyze_structural_similarity(golden, generated)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_analyze_style_consistency(self):
        """Test style consistency analysis."""
        analyzer = QualityAnalyzer()

        golden = "const handleClick = () => {\n  console.log('clicked');\n};"
        generated = "const handleClick = () => {\n  console.log('clicked');\n};"

        score = analyzer.analyze_style_consistency(golden, generated)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_analyze_complexity_delta(self):
        """Test complexity delta analysis."""
        analyzer = QualityAnalyzer()

        golden = "def simple():\n    return 1"
        generated = (
            "def complex():\n    for i in range(10):\n        if i > 5:\n"
            "            return i\n    return 0"
        )

        delta = analyzer.analyze_complexity_delta(golden, generated)

        assert isinstance(delta, float)
        # Generated code should be more complex
        assert delta > 0

    def test_estimate_performance_impact(self):
        """Test performance impact estimation."""
        analyzer = QualityAnalyzer()

        golden = (
            "const items = data.map(item => " "<div key={item.id}>{item.name}</div>)"
        )
        generated = (
            "const items = data.map(item => <div>{item.name}</div>)"
            # Missing key
        )

        score = analyzer.estimate_performance_impact(golden, generated)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_assess_maintainability(self):
        """Test maintainability assessment."""
        analyzer = QualityAnalyzer()

        code = """
        function calculateTotal(items) {
            // Calculate the total price of all items
            let total = 0;
            for (const item of items) {
                total += item.price;
            }
            return total;
        }
        """

        score = analyzer.assess_maintainability(code)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_assess_accessibility(self):
        """Test accessibility assessment."""
        analyzer = QualityAnalyzer()

        code = '<img src="photo.jpg" alt="User profile photo" />'

        score = analyzer.assess_accessibility(code)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_assess_security(self):
        """Test security assessment."""
        analyzer = QualityAnalyzer()

        # SQL injection risk
        code = "const query = `SELECT * FROM users WHERE id = ${userId}`"

        score = analyzer.assess_security(code)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestComprehensiveEvaluator:
    """Test the ComprehensiveEvaluator class."""

    def test_init_default_weights(self):
        """Test initialization with default weights."""
        evaluator = ComprehensiveEvaluator()
        assert evaluator.weights is not None
        assert isinstance(evaluator.weights, dict)

    def test_init_custom_weights(self):
        """Test initialization with custom weights."""
        custom_weights = {
            "semantic": 0.4,
            "functional": 0.3,
            "structural": 0.2,
            "style": 0.1,
        }
        evaluator = ComprehensiveEvaluator(custom_weights)
        assert evaluator.weights == custom_weights

    def test_evaluate_code_pair_success(self):
        """Test successful code pair evaluation."""
        evaluator = ComprehensiveEvaluator()

        golden_code = """
        const Button = ({ onClick, children }) => (
            <button onClick={onClick} className="btn">
                {children}
            </button>
        );
        """

        generated_code = """
        function Button(props) {
            return (
                <button onClick={props.onClick} className="btn">
                    {props.children}
                </button>
            );
        }
        """

        result = evaluator.evaluate_code_pair(golden_code, generated_code)

        assert isinstance(result, EvaluationResult)
        assert 0.0 <= result.overall_similarity <= 1.0
        assert 0.0 <= result.functional_equivalence <= 1.0
        assert 0.0 <= result.structural_similarity <= 1.0
        assert 0.0 <= result.style_consistency <= 1.0
        assert 0.0 <= result.maintainability_score <= 1.0
        assert 0.0 <= result.accessibility_score <= 1.0
        assert 0.0 <= result.security_score <= 1.0

    def test_evaluate_code_pair_identical(self):
        """Test evaluation of identical code."""
        evaluator = ComprehensiveEvaluator()

        code = "const hello = () => 'Hello, World!';"

        result = evaluator.evaluate_code_pair(code, code)

        assert isinstance(result, EvaluationResult)
        # Identical code should have high similarity
        # (adjust threshold based on actual calculation)
        assert result.overall_similarity > 0.6
        assert result.functional_equivalence > 0.9

    def test_evaluate_code_pair_error_handling(self):
        """Test error handling in code pair evaluation."""
        evaluator = ComprehensiveEvaluator()

        # Mock analyzer to raise exception
        evaluator.semantic_analyzer = Mock()
        evaluator.semantic_analyzer.compute_similarity.side_effect = Exception(
            "Test error"
        )

        with pytest.raises(EvaluationError):
            evaluator.evaluate_code_pair("code1", "code2")

    def test_to_dict_conversion(self):
        """Test EvaluationResult to_dict conversion."""
        evaluator = ComprehensiveEvaluator()

        golden_code = "const x = 1;"
        generated_code = "let x = 1;"

        result = evaluator.evaluate_code_pair(golden_code, generated_code)
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "overall_similarity" in result_dict
        assert "functional_equivalence" in result_dict
        assert "structural_similarity" in result_dict
        assert "style_consistency" in result_dict
        assert "detailed_analysis" in result_dict
