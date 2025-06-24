# filepath: tests/unit/test_exceptions.py
"""
Unit tests for the exceptions module.

This module tests custom exception classes and error handling.
"""

import pytest
from src.exceptions import (
    EvaluationError,
    FileParsingError,
    InvalidConfigurationError,
    ModelLoadingError,
    UnsupportedFileTypeError,
)


class TestEvaluationError:
    """Test the EvaluationError exception."""

    def test_evaluation_error_creation(self):
        """Test creating an EvaluationError."""
        message = "Test evaluation error"
        error = EvaluationError(message)

        assert isinstance(error, Exception)
        assert str(error) == message

    def test_evaluation_error_inheritance(self):
        """Test that EvaluationError inherits from Exception."""
        error = EvaluationError("Test")
        assert isinstance(error, Exception)


class TestModelLoadingError:
    """Test the ModelLoadingError exception."""

    def test_model_loading_error_creation(self):
        """Test creating a ModelLoadingError."""
        model_name = "test-model"
        original_error = ValueError("Test error")
        error = ModelLoadingError(model_name, original_error)

        assert isinstance(error, Exception)
        assert model_name in str(error)

    def test_model_loading_error_inheritance(self):
        """Test that ModelLoadingError inherits from Exception."""
        error = ModelLoadingError("test", ValueError("test"))
        assert isinstance(error, Exception)


class TestFileParsingError:
    """Test the FileParsingError exception."""

    def test_file_parsing_error_creation(self):
        """Test creating a FileParsingError."""
        file_path = "/path/to/file.py"
        cause = SyntaxError("Invalid syntax")
        error = FileParsingError(file_path, cause)

        assert isinstance(error, Exception)
        assert file_path in str(error)

    def test_file_parsing_error_inheritance(self):
        """Test that FileParsingError inherits from Exception."""
        error = FileParsingError("test.py", ValueError("error"))
        assert isinstance(error, Exception)


class TestUnsupportedFileTypeError:
    """Test the UnsupportedFileTypeError exception."""

    def test_unsupported_file_type_error_creation(self):
        """Test creating an UnsupportedFileTypeError."""
        file_path = "/path/to/file.xyz"
        extension = ".xyz"
        error = UnsupportedFileTypeError(file_path, extension)

        assert isinstance(error, Exception)
        assert file_path in str(error)
        assert extension in str(error)

    def test_unsupported_file_type_error_inheritance(self):
        """Test that UnsupportedFileTypeError inherits from Exception."""
        error = UnsupportedFileTypeError("test.xyz", ".xyz")
        assert isinstance(error, Exception)


class TestInvalidConfigurationError:
    """Test the InvalidConfigurationError exception."""

    def test_configuration_error_creation(self):
        """Test creating an InvalidConfigurationError."""
        message = "Invalid configuration setting"
        error = InvalidConfigurationError(message)

        assert isinstance(error, Exception)
        assert str(error) == message

    def test_configuration_error_inheritance(self):
        """Test that InvalidConfigurationError inherits from Exception."""
        error = InvalidConfigurationError("Test")
        assert isinstance(error, Exception)


class TestExceptionHierarchy:
    """Test the exception hierarchy and relationships."""

    def test_all_exceptions_are_exceptions(self):
        """Test that all custom exceptions inherit from Exception."""
        exceptions = [
            EvaluationError("test"),
            ModelLoadingError("test", ValueError("error")),
            FileParsingError("test.py", ValueError("error")),
            UnsupportedFileTypeError("test.xyz", ".xyz"),
            InvalidConfigurationError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, Exception)

    def test_exceptions_can_be_raised_and_caught(self):
        """Test that exceptions can be raised and caught properly."""
        # Test EvaluationError
        with pytest.raises(EvaluationError):
            raise EvaluationError("Test")

        # Test ModelLoadingError
        with pytest.raises(ModelLoadingError):
            raise ModelLoadingError("test", ValueError("error"))

        # Test FileParsingError
        with pytest.raises(FileParsingError):
            raise FileParsingError("test.py", ValueError("error"))

        # Test UnsupportedFileTypeError
        with pytest.raises(UnsupportedFileTypeError):
            raise UnsupportedFileTypeError("test.xyz", ".xyz")

        # Test InvalidConfigurationError
        with pytest.raises(InvalidConfigurationError):
            raise InvalidConfigurationError("Test")
