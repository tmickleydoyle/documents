"""
Unit tests for the UniversalCodeEvaluator class.

These tests verify the main evaluation functionality with mocked dependencies
to ensure isolated, fast, and reliable testing.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from src.exceptions import EvaluationError
from src.models import ApplicationStructure, EvaluationResult, FileInfo
from src.universal_evaluator import UniversalCodeEvaluator


class TestUniversalCodeEvaluator:
    """Test suite for UniversalCodeEvaluator class."""

    def test_init_default(self):
        """Test evaluator initialization with default parameters."""
        evaluator = UniversalCodeEvaluator()

        assert evaluator.weights is not None
        assert evaluator.parser is not None
        assert evaluator.evaluator is not None
        assert evaluator.file_matcher is not None

    def test_init_custom_weights(self):
        """Test evaluator initialization with custom weights."""
        custom_weights = {
            "semantic_similarity": 0.5,
            "structural_similarity": 0.3,
            "functionality_match": 0.2,
        }

        evaluator = UniversalCodeEvaluator(weights=custom_weights)
        assert evaluator.weights == custom_weights

    @patch("src.universal_evaluator.Path")
    def test_determine_evaluation_type_file(self, mock_path):
        """Test evaluation type determination for files."""
        mock_path.return_value.is_dir.return_value = False

        evaluator = UniversalCodeEvaluator()
        eval_type = evaluator._determine_evaluation_type("test.py", "test2.py", "auto")

        assert eval_type == "file"

    @patch("src.universal_evaluator.Path")
    def test_determine_evaluation_type_app(self, mock_path):
        """Test evaluation type determination for applications."""
        mock_path.return_value.is_dir.return_value = True

        evaluator = UniversalCodeEvaluator()
        eval_type = evaluator._determine_evaluation_type("app1/", "app2/", "auto")

        assert eval_type == "app"

    @patch("src.universal_evaluator.Path")
    def test_determine_evaluation_type_mixed(self, mock_path):
        """Test evaluation type determination for mixed inputs."""
        # First path is file, second is directory - should default to file evaluation
        mock_path.return_value.is_dir.side_effect = [
            False,
            True,
        ]  # golden is not dir, generated is dir

        evaluator = UniversalCodeEvaluator()
        eval_type = evaluator._determine_evaluation_type("test.py", "app/", "auto")
        assert eval_type == "file"

    @patch.object(UniversalCodeEvaluator, "_evaluate_single_file")
    def test_evaluate_file_type(self, mock_evaluate_file):
        """Test evaluate method with file type."""
        mock_evaluate_file.return_value = {"type": "file", "score": 0.85}

        evaluator = UniversalCodeEvaluator()
        result = evaluator.evaluate("test1.py", "test2.py", evaluation_type="file")

        assert result["type"] == "file"
        assert result["score"] == 0.85
        mock_evaluate_file.assert_called_once_with("test1.py", "test2.py")

    @patch.object(UniversalCodeEvaluator, "_evaluate_applications")
    def test_evaluate_app_type(self, mock_evaluate_apps):
        """Test evaluate method with application type."""
        mock_evaluate_apps.return_value = {"type": "application", "score": 0.75}

        evaluator = UniversalCodeEvaluator()
        result = evaluator.evaluate("app1/", "app2/", evaluation_type="app")

        assert result["type"] == "application"
        assert result["score"] == 0.75
        mock_evaluate_apps.assert_called_once_with("app1/", "app2/")

    @patch.object(UniversalCodeEvaluator, "_determine_evaluation_type")
    @patch.object(UniversalCodeEvaluator, "_evaluate_single_file")
    def test_evaluate_auto_type(self, mock_evaluate_file, mock_determine_type):
        """Test evaluate method with auto type detection."""
        mock_determine_type.return_value = "file"
        mock_evaluate_file.return_value = {"type": "file", "score": 0.90}

        evaluator = UniversalCodeEvaluator()
        _ = evaluator.evaluate("test1.py", "test2.py", evaluation_type="auto")

        mock_determine_type.assert_called_once_with("test1.py", "test2.py", "auto")
        mock_evaluate_file.assert_called_once_with("test1.py", "test2.py")

    def test_evaluate_invalid_type(self):
        """Test evaluate method with invalid evaluation type."""
        evaluator = UniversalCodeEvaluator()

        with pytest.raises(EvaluationError):
            evaluator.evaluate("test1.py", "test2.py", evaluation_type="invalid")


class TestSingleFileEvaluation:
    """Test suite for single file evaluation."""

    @patch("src.universal_evaluator.UniversalParser")
    @patch("src.universal_evaluator.ComprehensiveEvaluator")
    def test_evaluate_single_file_success(self, mock_analyzer_class, mock_parser_class):
        """Test successful single file evaluation."""
        # Setup mocks
        mock_parser = Mock()
        mock_analyzer = Mock()
        mock_parser_class.return_value = mock_parser
        mock_analyzer_class.return_value = mock_analyzer

        # Mock parser responses
        golden_sample = Mock()
        golden_sample.language = "python"
        golden_sample.content = "def hello(): return 'world'"
        golden_sample.metadata = {"language": "python"}
        generated_sample = Mock()
        generated_sample.language = "python"
        generated_sample.content = "def hello(): return 'world'"
        generated_sample.metadata = {"language": "python"}

        mock_parser.parse_file.side_effect = [golden_sample, generated_sample]

        # Mock analyzer response
        mock_analyzer.evaluate_code_pair.return_value = EvaluationResult(
            overall_similarity=0.85,
            functional_equivalence=0.90,
            structural_similarity=0.80,
            detailed_analysis={"test": "data"},
            metadata={"evaluation_type": "file"},
        )

        evaluator = UniversalCodeEvaluator()
        result = evaluator._evaluate_single_file("golden.py", "generated.py")

        assert result.metadata["evaluation_type"] == "file"
        assert result.metadata["golden_file"] == "golden.py"
        assert result.metadata["generated_file"] == "generated.py"
        assert result.overall_similarity == 0.85
        assert result.functional_equivalence == 0.90
        assert result.structural_similarity == 0.80

    @patch("src.universal_evaluator.UniversalParser")
    def test_evaluate_single_file_parse_failure(self, mock_parser_class):
        """Test single file evaluation when parsing fails."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Mock parser to return None (parsing failure)
        mock_parser.parse_file.return_value = None

        evaluator = UniversalCodeEvaluator()

        # Should raise EvaluationError when parsing fails
        with pytest.raises(EvaluationError) as exc_info:
            evaluator._evaluate_single_file("golden.py", "generated.py")

        assert "Could not parse" in str(exc_info.value)

    @patch("src.universal_evaluator.UniversalParser")
    def test_evaluate_single_file_language_mismatch(self, mock_parser_class):
        """Test single file evaluation with language mismatch."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Mock parser to return different languages
        golden_sample = Mock()
        golden_sample.language = "python"
        golden_sample.content = "def hello(): return 'world'"
        golden_sample.metadata = {"language": "python"}
        generated_sample = Mock()
        generated_sample.language = "javascript"
        generated_sample.content = "function hello() { return 'world'; }"
        generated_sample.metadata = {"language": "javascript"}

        mock_parser.parse_file.side_effect = [golden_sample, generated_sample]

        evaluator = UniversalCodeEvaluator()
        result = evaluator._evaluate_single_file("golden.py", "generated.js")

        assert result.metadata["evaluation_type"] == "file"
        assert result.metadata["golden_language"] == "python"
        assert result.metadata["generated_language"] == "javascript"
        # Should still succeed even with language mismatch
        assert isinstance(result, EvaluationResult)


class TestApplicationEvaluation:
    """Test suite for application evaluation."""

    @patch("src.universal_evaluator.UniversalParser")
    @patch("src.universal_evaluator.IntelligentFileMatching")
    def test_evaluate_applications_success(self, mock_matcher_class, mock_parser_class):
        """Test successful application evaluation."""
        # Setup mocks
        mock_parser = Mock()
        mock_matcher = Mock()
        mock_parser_class.return_value = mock_parser
        mock_matcher_class.return_value = mock_matcher

        # Create mock application structures
        golden_structure = ApplicationStructure(root_path=Path("golden/"))
        golden_structure.language_distribution = {"python": 5}
        golden_structure.all_files = [
            FileInfo(file_path=Path("golden/main.py"), metadata={"language": "python"})
        ]

        generated_structure = ApplicationStructure(root_path=Path("generated/"))
        generated_structure.language_distribution = {"python": 5}
        generated_structure.all_files = [
            FileInfo(
                file_path=Path("generated/main.py"), metadata={"language": "python"}
            )
        ]

        mock_parser.parse_application.side_effect = [
            golden_structure,
            generated_structure,
        ]

        # Mock file matching
        mock_matcher.find_matches.return_value = {
            str(golden_structure.all_files[0]): {
                "generated_file": str(generated_structure.all_files[0]),
                "confidence": 1.0,
                "match_strategy": "exact_name",
            }
        }

        evaluator = UniversalCodeEvaluator()
        result = evaluator._evaluate_applications("golden/", "generated/")

        assert result.metadata["evaluation_type"] == "application"
        assert result.metadata["golden_app_path"] == "golden/"
        assert result.metadata["generated_app_path"] == "generated/"
        assert "golden_languages" in result.detailed_analysis
        assert "generated_languages" in result.detailed_analysis
        assert "file_matches" in result.detailed_analysis

    @patch("src.universal_evaluator.UniversalParser")
    def test_evaluate_applications_parse_failure(self, mock_parser_class):
        """Test application evaluation when parsing fails."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Mock parser to raise exception
        mock_parser.parse_application.side_effect = Exception("Parse error")

        evaluator = UniversalCodeEvaluator()

        # Should raise the original Exception when parsing fails
        with pytest.raises(Exception) as exc_info:
            evaluator._evaluate_applications("golden/", "generated/")

        assert "Parse error" in str(exc_info.value)


class TestUtilityMethods:
    """Test suite for utility methods."""

    def test_extract_overall_score_with_score(self):
        """Test overall score extraction when score exists."""
        evaluator = UniversalCodeEvaluator()
        result = {"overall_score": 0.85, "other_data": "test"}

        score = evaluator._extract_overall_score(result)
        assert score == 0.85

    def test_extract_overall_score_without_score(self):
        """Test overall score extraction when score doesn't exist."""
        evaluator = UniversalCodeEvaluator()
        result = {"other_data": "test"}

        score = evaluator._extract_overall_score(result)
        assert score == 0.0

    def test_calculate_summary_statistics(self):
        """Test summary statistics calculation."""
        evaluator = UniversalCodeEvaluator()
        scores = [0.8, 0.9, 0.7, 0.85, 0.75]

        stats = evaluator._calculate_summary_statistics(scores)

        assert "mean" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats
        assert abs(stats["mean"] - 0.8) < 0.01
        assert stats["min"] == 0.7
        assert stats["max"] == 0.9

    def test_calculate_summary_statistics_empty(self):
        """Test summary statistics with empty list."""
        evaluator = UniversalCodeEvaluator()
        scores = []

        stats = evaluator._calculate_summary_statistics(scores)

        assert stats["mean"] == 0.0
        assert stats["std"] == 0.0
        assert stats["min"] == 0.0
        assert stats["max"] == 0.0

    def test_calculate_summary_statistics_single(self):
        """Test summary statistics with single score."""
        evaluator = UniversalCodeEvaluator()
        scores = [0.85]

        stats = evaluator._calculate_summary_statistics(scores)

        assert stats["mean"] == 0.85
        assert stats["std"] == 0.0
        assert stats["min"] == 0.85
        assert stats["max"] == 0.85


class TestBatchEvaluation:
    """Test suite for batch evaluation functionality."""

    @patch.object(UniversalCodeEvaluator, "evaluate")
    def test_evaluate_batch_success(self, mock_evaluate):
        """Test successful batch evaluation."""
        # Setup mock responses
        mock_evaluate.side_effect = [
            {"overall_score": 0.85},
            {"overall_score": 0.75},
            {"overall_score": 0.90},
        ]

        evaluator = UniversalCodeEvaluator()

        # Create mock batch structure
        batch_paths = ["model1/", "model2/", "model3/"]

        result = evaluator.evaluate_batch("golden/", batch_paths)

        assert result.best_model == "model3/"  # model3/ has highest score 0.90
        assert result.worst_model == "model2/"  # model2/ has lowest score 0.75
        assert len(result.model_scores) == 3
        assert result.model_scores["model1/"] == 0.85
        assert result.model_scores["model2/"] == 0.75
        assert result.model_scores["model3/"] == 0.90

    @patch.object(UniversalCodeEvaluator, "evaluate")
    def test_evaluate_batch_with_failures(self, mock_evaluate):
        """Test batch evaluation with some failures."""
        # Setup mock responses with one failure
        mock_evaluate.side_effect = [
            {"overall_score": 0.85},
            Exception("Evaluation failed"),
            {"overall_score": 0.90},
        ]

        evaluator = UniversalCodeEvaluator()

        # Create mock batch structure
        batch_paths = ["model1/", "model2/", "model3/"]

        result = evaluator.evaluate_batch("golden/", batch_paths)

        # Should only include successful evaluations
        assert len(result.model_scores) == 2
        assert "model1/" in result.model_scores
        assert "model2/" not in result.model_scores  # Failed evaluation
        assert "model3/" in result.model_scores

    @patch.object(UniversalCodeEvaluator, "evaluate")
    def test_evaluate_batch_empty_list(self, mock_evaluate):
        """Test batch evaluation with empty batch list."""
        evaluator = UniversalCodeEvaluator()

        result = evaluator.evaluate_batch("golden/", [])

        assert len(result.model_scores) == 0
        assert result.best_model is None
        assert result.worst_model is None
        assert result.summary_statistics["mean"] == 0.0


class TestLanguageCompatibility:
    """Test suite for language compatibility analysis."""

    def test_analyze_language_compatibility_identical(self):
        """Test language compatibility with identical languages."""
        evaluator = UniversalCodeEvaluator()

        golden_langs = {"python", "javascript"}
        generated_langs = {"python", "javascript"}

        compatibility = evaluator._analyze_language_compatibility(
            golden_langs, generated_langs
        )

        assert compatibility["status"] == "compatible"
        assert compatibility["overlap_percentage"] == 100.0
        assert compatibility["common_languages"] == golden_langs
        assert compatibility["missing_languages"] == set()
        assert compatibility["extra_languages"] == set()

    def test_analyze_language_compatibility_partial(self):
        """Test language compatibility with partial overlap."""
        evaluator = UniversalCodeEvaluator()

        golden_langs = {"python", "javascript", "css"}
        generated_langs = {"python", "typescript", "css"}

        compatibility = evaluator._analyze_language_compatibility(
            golden_langs, generated_langs
        )

        assert compatibility["status"] == "partially_compatible"
        assert abs(compatibility["overlap_percentage"] - 66.67) < 0.01  # 2/3 = 66.67%
        assert compatibility["common_languages"] == {"python", "css"}
        assert compatibility["missing_languages"] == {"javascript"}
        assert compatibility["extra_languages"] == {"typescript"}

    def test_analyze_language_compatibility_incompatible(self):
        """Test language compatibility with no overlap."""
        evaluator = UniversalCodeEvaluator()

        golden_langs = {"python", "go"}
        generated_langs = {"javascript", "typescript"}

        compatibility = evaluator._analyze_language_compatibility(
            golden_langs, generated_langs
        )

        assert compatibility["status"] == "incompatible"
        assert compatibility["overlap_percentage"] == 0.0
        assert compatibility["common_languages"] == set()
        assert compatibility["missing_languages"] == golden_langs
        assert compatibility["extra_languages"] == generated_langs

    def test_analyze_language_compatibility_empty_sets(self):
        """Test language compatibility with empty language sets."""
        evaluator = UniversalCodeEvaluator()

        compatibility = evaluator._analyze_language_compatibility(set(), set())

        assert compatibility["status"] == "compatible"  # Both empty = compatible
        assert compatibility["overlap_percentage"] == 100.0
        assert compatibility["common_languages"] == set()
        assert compatibility["missing_languages"] == set()
        assert compatibility["extra_languages"] == set()
