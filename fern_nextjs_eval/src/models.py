"""
Data models for the Universal Code Evaluation Framework.

This module contains all the dataclasses and type definitions used throughout
the evaluation framework, designed to work with any programming language and
project structure.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class CodeSample:
    """
    Represents a code sample for evaluation.

    Attributes:
        id: Unique identifier for the code sample
        content: The actual code content
        file_path: Path to the source file
        language: Programming language detected
        functionality: Detected functionality category
        complexity: Complexity level ('simple', 'moderate', 'complex')
        metadata: Additional metadata about the code sample
    """

    id: str
    content: str
    file_path: str
    language: str
    functionality: str
    complexity: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the code sample after initialization."""
        if not self.content.strip():
            raise ValueError("Code content cannot be empty")


@dataclass
class EvaluationResult:
    """
    Results from semantic similarity evaluation.

    This dataclass contains all the metrics computed during the evaluation
    of two code samples.
    """

    overall_similarity: float
    functional_equivalence: float
    structural_similarity: float
    style_consistency: float
    complexity_delta: float
    performance_impact: float
    maintainability_score: float
    accessibility_score: float
    security_score: float
    detailed_analysis: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        overall_similarity: float,
        functional_equivalence: float,
        structural_similarity: float,
        style_consistency: float = 0.0,
        complexity_delta: float = 0.0,
        performance_impact: float = 0.0,
        maintainability_score: float = 0.0,
        accessibility_score: float = 0.0,
        security_score: float = 0.0,
        detailed_analysis: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize EvaluationResult with backward compatibility."""
        self.overall_similarity = overall_similarity
        self.functional_equivalence = functional_equivalence
        self.structural_similarity = structural_similarity
        self.style_consistency = style_consistency
        self.complexity_delta = complexity_delta
        self.performance_impact = performance_impact
        self.maintainability_score = maintainability_score
        self.accessibility_score = accessibility_score
        self.security_score = security_score

        # Handle backward compatibility for 'details' parameter
        if details is not None and detailed_analysis is None:
            self.detailed_analysis = details
        else:
            self.detailed_analysis = detailed_analysis or {}

        self.metadata = metadata or {}

        # Validate after initialization
        self.__post_init__()

    # Backward compatibility aliases
    @property
    def details(self) -> Dict[str, Any]:
        """Alias for detailed_analysis for backward compatibility."""
        return self.detailed_analysis

    @details.setter
    def details(self, value: Dict[str, Any]) -> None:
        """Setter for details alias."""
        self.detailed_analysis = value

    def __post_init__(self) -> None:
        """Validate evaluation results after initialization."""
        score_fields = [
            "overall_similarity",
            "functional_equivalence",
            "structural_similarity",
            "style_consistency",
            "maintainability_score",
            "accessibility_score",
            "security_score",
        ]

        for field_name in score_fields:
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
                raise ValueError(f"{field_name} must be a number between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the evaluation result to a dictionary."""
        return {
            "overall_similarity": self.overall_similarity,
            "functional_equivalence": self.functional_equivalence,
            "structural_similarity": self.structural_similarity,
            "style_consistency": self.style_consistency,
            "complexity_delta": self.complexity_delta,
            "performance_impact": self.performance_impact,
            "maintainability_score": self.maintainability_score,
            "accessibility_score": self.accessibility_score,
            "security_score": self.security_score,
            "detailed_analysis": self.detailed_analysis,
            "metadata": self.metadata,
        }


@dataclass
class FileMatchResult:
    """
    Result of matching a golden file to a generated file.

    Attributes:
        golden_file: Path to the golden standard file
        generated_file: Path to the matched generated file
        confidence: Confidence score (0-1) of the match
        match_strategy: Strategy used for matching
        similarity_reasons: List of reasons why files were matched
    """

    golden_file: str
    generated_file: str
    confidence: float
    match_strategy: str
    similarity_reasons: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate match result."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")


@dataclass
class FileInfo:
    """
    Information about a file including its path and metadata.
    """

    file_path: Path
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure file_path is a Path object."""
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)

    def read_text(self, encoding: str = "utf-8", errors: str = "ignore") -> str:
        """Read the text content of the file."""
        return self.file_path.read_text(encoding=encoding, errors=errors)

    def exists(self) -> bool:
        """Check if the file exists."""
        return self.file_path.exists()

    @property
    def suffix(self) -> str:
        """Get the file extension."""
        return self.file_path.suffix

    @property
    def name(self) -> str:
        """Get the file name."""
        return self.file_path.name

    @property
    def stem(self) -> str:
        """Get the file name without extension."""
        return self.file_path.stem

    @property
    def parent(self) -> Path:
        """Get the parent directory."""
        return self.file_path.parent

    def __str__(self) -> str:
        """String representation of the file path."""
        return str(self.file_path)

    def __fspath__(self) -> str:
        """Support for os.fspath()."""
        return str(self.file_path)


@dataclass
class FunctionalSignature:
    """
    Signature of a code file for functionality-based matching.

    Attributes:
        language: Programming language
        functionality_category: Primary functionality category
        exports: List of exported symbols/functions/classes
        imports: List of imported modules/packages
        functions: List of function names
        classes: List of class names
        keywords: Important keywords found in the code
        api_endpoints: API endpoints if applicable
        ui_elements: UI elements if applicable
    """

    language: str
    functionality_category: str
    exports: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    ui_elements: List[str] = field(default_factory=list)


@dataclass
class ApplicationStructure:
    """
    Represents the structure of any application, language-agnostic.

    Attributes:
        root_path: Root directory of the application
        language_distribution: Dict of language -> file count
        functionality_groups: Dict of functionality -> list of file info
        all_files: List of all relevant files with metadata
        directory_structure: Dict representing directory hierarchy
        detected_frameworks: List of detected frameworks/libraries
        entry_points: List of main entry point files
        configuration_files: List of configuration files
        build_files: List of build-related files
        test_files: List of test files
    """

    root_path: Path
    language_distribution: Dict[str, int] = field(default_factory=dict)
    functionality_groups: Dict[str, List[FileInfo]] = field(default_factory=dict)
    all_files: List[FileInfo] = field(default_factory=list)
    directory_structure: Dict[str, Any] = field(default_factory=dict)
    detected_frameworks: List[str] = field(default_factory=list)
    entry_points: List[FileInfo] = field(default_factory=list)
    configuration_files: List[FileInfo] = field(default_factory=list)
    build_files: List[FileInfo] = field(default_factory=list)
    test_files: List[FileInfo] = field(default_factory=list)

    # Backward compatibility fields for existing parsers
    components: List[Path] = field(default_factory=list)
    pages: List[Path] = field(default_factory=list)
    api_routes: List[Path] = field(default_factory=list)
    styles: List[Path] = field(default_factory=list)
    utils: List[Path] = field(default_factory=list)
    hooks: List[Path] = field(default_factory=list)
    lib: List[Path] = field(default_factory=list)
    config_files: List[Path] = field(default_factory=list)
    package_json: Optional[str] = None

    def total_files(self) -> int:
        """Return the total number of files in the application."""
        return len(self.all_files)

    @property
    def detected_languages(self) -> set:
        """Return set of detected languages."""
        return set(self.language_distribution.keys())

    @property
    def main_language(self) -> str:
        """Return the primary language of the application based on file count."""
        if not self.language_distribution:
            return "unknown"
        return max(self.language_distribution.items(), key=lambda x: x[1])[0]

    def get_primary_language(self) -> str:
        """Get the most common programming language in the application."""
        if not self.language_distribution:
            return "unknown"
        return max(self.language_distribution.items(), key=lambda x: x[1])[0]

    def get_functionality_coverage(self) -> Dict[str, float]:
        """Get percentage of files in each functionality category."""
        total = len(self.all_files)
        if total == 0:
            return {}
        return {
            functionality: len(files) / total * 100
            for functionality, files in self.functionality_groups.items()
        }


@dataclass
class FileComparisonResult:
    """
    Results from comparing collections of files.

    Used for component-wise, page-wise, or style-wise comparisons.
    """

    scores: Dict[str, EvaluationResult] = field(default_factory=dict)
    missing_files: List[str] = field(default_factory=list)
    extra_files: List[str] = field(default_factory=list)
    category_average: float = 0.0

    def get_best_score(self) -> Optional[float]:
        """Get the highest similarity score from all comparisons."""
        if not self.scores:
            return None
        return max(result.overall_similarity for result in self.scores.values())

    def get_worst_score(self) -> Optional[float]:
        """Get the lowest similarity score from all comparisons."""
        if not self.scores:
            return None
        return min(result.overall_similarity for result in self.scores.values())


@dataclass
class ApplicationEvaluationResult:
    """
    Complete results from evaluating two Next.js applications.

    This dataclass aggregates all the individual file comparisons and
    provides application-level metrics.
    """

    overall_score: float
    component_scores: FileComparisonResult = field(default_factory=FileComparisonResult)
    page_scores: FileComparisonResult = field(default_factory=FileComparisonResult)
    style_scores: FileComparisonResult = field(default_factory=FileComparisonResult)
    util_scores: FileComparisonResult = field(default_factory=FileComparisonResult)
    structure_analysis: Dict[str, Any] = field(default_factory=dict)
    detailed_breakdown: Dict[str, Any] = field(default_factory=dict)

    def get_total_files_compared(self) -> int:
        """Get the total number of files that were compared."""
        return (
            len(self.component_scores.scores)
            + len(self.page_scores.scores)
            + len(self.style_scores.scores)
            + len(self.util_scores.scores)
        )

    def get_all_scores(self) -> List[float]:
        """Get all individual similarity scores as a flat list."""
        scores = []
        for comparison_result in [
            self.component_scores,
            self.page_scores,
            self.style_scores,
            self.util_scores,
        ]:
            scores.extend(
                [
                    result.overall_similarity
                    for result in comparison_result.scores.values()
                ]
            )
        return scores


class BatchEvaluationResult:
    """
    Results from evaluating multiple models against the same golden standard.

    Used for comparing the performance of different AI models.
    """

    def __init__(
        self,
        model_results: Optional[
            Dict[str, Union[EvaluationResult, ApplicationEvaluationResult]]
        ] = None,
        rankings: Optional[List] = None,
        summary_statistics: Optional[Dict[str, Any]] = None,
        model_scores: Optional[Dict[str, float]] = None,
        best_model: Optional[str] = None,
        worst_model: Optional[str] = None,
        detailed_results: Optional[List] = None,
    ):
        """Initialize BatchEvaluationResult with backward compatibility."""

        # Handle backward compatibility for model_scores parameter
        if model_scores is not None and model_results is None:
            # Convert simple scores to EvaluationResult objects
            self.model_results = {}
            for model_name, score in model_scores.items():
                self.model_results[model_name] = EvaluationResult(
                    overall_similarity=score,
                    functional_equivalence=score,
                    structural_similarity=score,
                )
        else:
            self.model_results = model_results or {}

        self.rankings = rankings or []
        self.detailed_results = detailed_results or []

        # Handle direct assignment of best/worst models for testing
        self._best_model = best_model
        self._worst_model = worst_model

        # Only calculate if not provided explicitly (for testing flexibility)
        if summary_statistics is not None:
            self.summary_statistics = summary_statistics
        else:
            self.summary_statistics = {}

        # Calculate rankings and summary statistics if we have model_results and
        # they weren't provided
        if self.model_results:
            if not rankings:
                self._calculate_rankings()
            if summary_statistics is None:
                self._calculate_summary_statistics()

    # Backward compatibility properties
    @property
    def model_scores(self) -> Dict[str, float]:
        """Get model scores for backward compatibility."""
        scores = {}
        for model_name, result in self.model_results.items():
            if isinstance(result, EvaluationResult):
                scores[model_name] = result.overall_similarity
            elif isinstance(result, ApplicationEvaluationResult):
                scores[model_name] = result.overall_score
            else:
                scores[model_name] = 0.0
        return scores

    @property
    def best_model(self) -> Optional[str]:
        """Get the best model name."""
        if self._best_model is not None:
            return self._best_model
        return self.get_best_model()

    @property
    def worst_model(self) -> Optional[str]:
        """Get the worst model name."""
        if self._worst_model is not None:
            return self._worst_model
        return self.get_worst_model()

    def _calculate_rankings(self) -> None:
        """Calculate model rankings based on overall scores."""
        scores = []
        for model_name, result in self.model_results.items():
            if isinstance(result, EvaluationResult):
                score = result.overall_similarity
            elif isinstance(result, ApplicationEvaluationResult):
                score = result.overall_score
            else:
                score = 0.0
            scores.append((model_name, score))

        self.rankings = sorted(scores, key=lambda x: x[1], reverse=True)

    def _calculate_summary_statistics(self) -> None:
        """Calculate summary statistics for the batch evaluation."""
        scores = [score for _, score in self.rankings]
        if scores:
            import statistics

            self.summary_statistics = {
                "mean_score": statistics.mean(scores),
                "median_score": statistics.median(scores),
                "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
                "min_score": min(scores),
                "max_score": max(scores),
                "score_range": max(scores) - min(scores),
            }

    def get_best_model(self) -> Optional[str]:
        """Get the name of the best-performing model."""
        return self.rankings[0][0] if self.rankings else None

    def get_worst_model(self) -> Optional[str]:
        """Get the name of the worst-performing model."""
        return self.rankings[-1][0] if self.rankings else None
