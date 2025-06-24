"""
Exception classes for the Fern Model Evaluation Framework.
"""


class FernEvaluationError(Exception):
    """Base exception class for all Fern evaluation errors."""

    pass


class FileParsingError(FernEvaluationError):
    """Raised when a file cannot be parsed."""

    def __init__(self, file_path: str, original_error: Exception):
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(f"Failed to parse file {file_path}: {original_error}")


class ModelLoadingError(FernEvaluationError):
    """Raised when the embedding model cannot be loaded."""

    def __init__(self, model_name: str, original_error: Exception):
        self.model_name = model_name
        self.original_error = original_error
        super().__init__(f"Failed to load model {model_name}: {original_error}")


class EvaluationError(FernEvaluationError):
    """Raised when evaluation fails."""

    def __init__(self, message: str, details: dict = None):
        self.details = details or {}
        super().__init__(message)


class InvalidConfigurationError(FernEvaluationError):
    """Raised when configuration is invalid."""

    pass


class UnsupportedFileTypeError(FernEvaluationError):
    """Raised when an unsupported file type is encountered."""

    def __init__(self, file_path: str, file_extension: str):
        self.file_path = file_path
        self.file_extension = file_extension
        super().__init__(
            f"Unsupported file type '{file_extension}' for file: {file_path}"
        )


class StructureAnalysisError(FernEvaluationError):
    """Raised when application structure analysis fails."""

    def __init__(self, message: str, app_path: str = None):
        self.app_path = app_path
        if app_path:
            super().__init__(f"Structure analysis failed for {app_path}: {message}")
        else:
            super().__init__(f"Structure analysis failed: {message}")
