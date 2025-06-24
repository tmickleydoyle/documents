"""
Unit tests for the config module in the Universal Code Evaluation Framework.

These tests verify configuration values and constants.
"""

from src.config import (
    ALL_SUPPORTED_EXTENSIONS,
    COMPLEXITY_THRESHOLDS,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EVALUATION_WEIGHTS,
    QUALITY_THRESHOLDS,
    SUPPORTED_CODE_EXTENSIONS,
)


class TestDefaultConfigurations:
    """Test suite for default configuration values."""

    def test_default_embedding_model(self):
        """Test default embedding model is set correctly."""
        assert DEFAULT_EMBEDDING_MODEL is not None
        assert isinstance(DEFAULT_EMBEDDING_MODEL, str)
        assert len(DEFAULT_EMBEDDING_MODEL) > 0

    def test_default_evaluation_weights(self):
        """Test default evaluation weights."""
        assert isinstance(DEFAULT_EVALUATION_WEIGHTS, dict)

        # Check required weight categories
        required_weights = ["semantic", "functional", "structural", "style"]
        for weight in required_weights:
            assert weight in DEFAULT_EVALUATION_WEIGHTS
            assert isinstance(DEFAULT_EVALUATION_WEIGHTS[weight], (int, float))
            assert 0 <= DEFAULT_EVALUATION_WEIGHTS[weight] <= 1

    def test_weights_sum_to_one(self):
        """Test that default weights sum to approximately 1.0."""
        total_weight = sum(DEFAULT_EVALUATION_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_quality_thresholds(self):
        """Test quality thresholds configuration."""
        assert isinstance(QUALITY_THRESHOLDS, dict)

        # Check for required threshold keys
        required_thresholds = ["min_similarity_score", "max_similarity_score"]
        for threshold in required_thresholds:
            if threshold in QUALITY_THRESHOLDS:
                assert isinstance(QUALITY_THRESHOLDS[threshold], (int, float))

    def test_supported_code_extensions(self):
        """Test supported code extensions configuration."""
        assert isinstance(SUPPORTED_CODE_EXTENSIONS, dict)
        assert "web_frontend" in SUPPORTED_CODE_EXTENSIONS
        assert ".js" in SUPPORTED_CODE_EXTENSIONS["web_frontend"]
        assert ".ts" in SUPPORTED_CODE_EXTENSIONS["web_frontend"]

    def test_all_supported_extensions(self):
        """Test that all supported extensions is populated."""
        assert isinstance(ALL_SUPPORTED_EXTENSIONS, set)
        assert len(ALL_SUPPORTED_EXTENSIONS) > 0
        assert ".js" in ALL_SUPPORTED_EXTENSIONS

    def test_complexity_thresholds(self):
        """Test complexity thresholds configuration."""
        assert isinstance(COMPLEXITY_THRESHOLDS, dict)
        assert "simple" in COMPLEXITY_THRESHOLDS
        assert "moderate" in COMPLEXITY_THRESHOLDS
