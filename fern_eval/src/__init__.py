"""
Universal Code Evaluation Framework
===================================

A comprehensive framework for evaluating any type of application in any
programming language using semantic similarity analysis and
intelligent functionality-based matching.
"""

__version__ = "2.0.0"
__author__ = "Universal Evaluation Team"

from .analyzers import ComprehensiveEvaluator
from .config import ALL_SUPPORTED_EXTENSIONS, FUNCTIONALITY_PATTERNS, LANGUAGE_PATTERNS
from .exceptions import (
    EvaluationError,
    FernEvaluationError,
    FileParsingError,
    UnsupportedFileTypeError,
)
from .matching import IntelligentFileMatcher
from .models import (
    ApplicationStructure,
    BatchEvaluationResult,
    CodeSample,
    EvaluationResult,
    FileInfo,
    FunctionalSignature,
)
from .universal_evaluator import UniversalCodeEvaluator
from .universal_parser import UniversalParser

__all__ = [
    "UniversalCodeEvaluator",
    "UniversalParser",
    "EvaluationResult",
    "CodeSample",
    "ApplicationStructure",
    "FileInfo",
    "FunctionalSignature",
    "BatchEvaluationResult",
    "ComprehensiveEvaluator",
    "IntelligentFileMatcher",
    "FernEvaluationError",
    "FileParsingError",
    "UnsupportedFileTypeError",
    "EvaluationError",
    "ALL_SUPPORTED_EXTENSIONS",
    "LANGUAGE_PATTERNS",
    "FUNCTIONALITY_PATTERNS",
]
