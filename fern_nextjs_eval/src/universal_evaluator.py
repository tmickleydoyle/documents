"""
Universal evaluator class following senior software engineering best practices.

This module contains the UniversalCodeEvaluator class that can evaluate any type
of application in any programming language with intelligent functionality-based
matching.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

from .analyzers import ComprehensiveEvaluator
from .exceptions import EvaluationError
from .matching import AdaptiveEvaluationStrategy, IntelligentFileMatcher
from .models import (
    ApplicationStructure,
    BatchEvaluationResult,
    EvaluationResult,
    FileMatchResult,
)
from .universal_parser import UniversalParser
from .utils import safe_divide, setup_logging

# Backward compatibility alias for tests
IntelligentFileMatching = IntelligentFileMatcher

logger = logging.getLogger(__name__)


class UniversalCodeEvaluator:
    """
    Universal entry point for code evaluation across any language or framework.

    Supports any programming language and application structure with intelligent
    functionality-based file matching. Designed to be maintained by junior engineers.
    """

    def __init__(
        self, weights: Optional[Dict[str, float]] = None, log_level: str = "INFO"
    ):
        """Initialize the universal evaluator with optional custom weights."""
        setup_logging(log_level)
        # Import here to avoid circular import
        from .config import DEFAULT_EVALUATION_WEIGHTS

        self.weights = (
            weights or DEFAULT_EVALUATION_WEIGHTS.copy()
        )  # Store weights for testing/introspection
        self.parser = UniversalParser()
        self.evaluator = ComprehensiveEvaluator(weights)
        self.file_matcher = IntelligentFileMatcher()
        self.adaptive_strategy = AdaptiveEvaluationStrategy(self.file_matcher)
        logger.info("Universal Code Evaluator initialized")

    def evaluate(
        self, golden_path: str, generated_path: str, evaluation_type: str = "auto"
    ) -> EvaluationResult:
        """
        Main evaluation method - auto-detects if comparing files or applications.

        Args:
            golden_path: Path to golden standard (file or directory)
            generated_path: Path to generated code (file or directory)
            evaluation_type: 'file', 'app', or 'auto' (default: auto-detect)

        Returns:
            Dictionary with evaluation results

        Raises:
            EvaluationError: If evaluation fails or inputs are invalid
        """
        try:
            evaluation_type = self._determine_evaluation_type(
                golden_path, generated_path, evaluation_type
            )

            if evaluation_type == "file":
                return self._evaluate_single_file(golden_path, generated_path)
            elif evaluation_type == "app":
                return self._evaluate_applications(golden_path, generated_path)
            else:
                raise EvaluationError(f"Unsupported evaluation type: {evaluation_type}")

        except FileNotFoundError as e:
            # Return error result for file not found instead of raising exception
            logger.warning(f"File not found: {e}")
            return EvaluationResult(
                overall_similarity=0.0,
                functional_equivalence=0.0,
                structural_similarity=0.0,
                metadata={"evaluation_type": evaluation_type, "error": str(e)},
            )
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise EvaluationError(f"Evaluation failed: {e}")

    def evaluate_batch(
        self,
        golden_path: str,
        model_outputs: Union[Dict[str, str], List[str]],
        evaluation_type: str = "auto",
    ) -> BatchEvaluationResult:
        """
        Evaluate multiple models against the same golden standard.

        Args:
            golden_path: Path to the golden standard
            model_outputs: Dict mapping model names to their output paths, or list
                of paths
            evaluation_type: Type of evaluation ('file', 'app', or 'auto')

        Returns:
            Batch evaluation result with rankings and statistics
        """
        if not model_outputs:
            # Return empty result instead of raising error for test compatibility
            return self._create_batch_result({})

        logger.info(f"Starting batch evaluation of {len(model_outputs)} models")

        model_scores = self._evaluate_all_models(
            golden_path, model_outputs, evaluation_type
        )
        return self._create_batch_result(model_scores)

    def generate_report(
        self, evaluation_results: Dict[str, Any], output_file: Optional[str] = None
    ) -> str:
        """
        Generate a human-readable evaluation report.

        Args:
            evaluation_results: Results from evaluate() method
            output_file: Optional file path to save the report

        Returns:
            Formatted report string
        """
        try:
            # Convert EvaluationResult to dictionary format if needed
            if hasattr(evaluation_results, "overall_similarity"):
                # This is an EvaluationResult object, convert to dict format
                results_dict = self._evaluation_result_to_dict(evaluation_results)
            else:
                # This is already a dictionary
                results_dict = evaluation_results

            report_lines = self._build_report_lines(results_dict)
            report = "\n".join(report_lines)

            if output_file:
                self._save_report_to_file(report, output_file)

            return report

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"Error generating report: {e}"

    # Private helper methods - small, focused, easy to understand

    def _determine_evaluation_type(
        self, golden_path: str, generated_path: str, evaluation_type: str
    ) -> str:
        """Determine if we're comparing files or applications."""
        if evaluation_type != "auto":
            return evaluation_type

        golden_is_dir = Path(golden_path).is_dir()
        generated_is_dir = Path(generated_path).is_dir()

        if golden_is_dir and generated_is_dir:
            return "app"
        elif not golden_is_dir and not generated_is_dir:
            return "file"
        else:
            # When mixed, default to file evaluation
            logger.warning(
                "Mixed input types detected (file vs directory). "
                "Defaulting to file evaluation."
            )
            return "file"

    def _evaluate_single_file(
        self, golden_path: str, generated_path: str
    ) -> EvaluationResult:
        """Evaluate two individual files."""
        logger.info(f"Evaluating files: {golden_path} vs {generated_path}")

        # Handle case where one path is a directory - find main file
        actual_golden_path = self._resolve_file_path(golden_path)
        actual_generated_path = self._resolve_file_path(generated_path)

        golden_sample = self.parser.parse_file(actual_golden_path)
        generated_sample = self.parser.parse_file(actual_generated_path)

        if not golden_sample or not generated_sample:
            raise EvaluationError("Could not parse one or both files")

        result = self.evaluator.evaluate_code_pair(
            golden_sample.content, generated_sample.content
        )

        # Add metadata to the result
        result.metadata.update(
            {
                "evaluation_type": "file",
                "golden_file": golden_path,
                "generated_file": generated_path,
                "golden_path": golden_path,  # Keep for backward compatibility
                "generated_path": generated_path,  # Keep for backward compatibility
                "golden_metadata": golden_sample.metadata,
                "generated_metadata": generated_sample.metadata,
                "golden_language": golden_sample.language,
                "generated_language": generated_sample.language,
            }
        )

        return result

    def _evaluate_applications(
        self, golden_app_path: str, generated_app_path: str
    ) -> EvaluationResult:
        """Evaluate two complete applications with intelligent functionality-based
        matching."""
        logger.info(
            f"Evaluating applications: {golden_app_path} vs {generated_app_path}"
        )

        # Parse application structures using universal parser
        golden_structure = self.parser.parse_application(golden_app_path)
        generated_structure = self.parser.parse_application(generated_app_path)

        # Log detected languages and frameworks
        logger.info(f"Golden app languages: {golden_structure.detected_languages}")
        logger.info(
            f"Generated app languages: {generated_structure.detected_languages}"
        )

        # Find file matches using intelligent functionality-based algorithms
        file_matches = self.file_matcher.match_files(
            golden_structure, generated_structure
        )

        # Create evaluation strategy based on match confidence
        evaluation_plan = self.adaptive_strategy.create_evaluation_plan(file_matches)

        # Evaluate each matched file pair
        file_results = self._evaluate_matched_files(file_matches, evaluation_plan)

        # Analyze structural differences
        structure_analysis = self._analyze_structure_differences(
            golden_structure, generated_structure, file_matches
        )

        # Calculate overall score
        overall_score = self._calculate_weighted_score(file_results, file_matches)

        # Calculate aggregate metrics for the application
        avg_functional_equiv = self._calculate_average_metric(
            file_results, "functional_equivalence"
        )
        avg_structural_sim = self._calculate_average_metric(
            file_results, "structural_similarity"
        )
        avg_style_consistency = self._calculate_average_metric(
            file_results, "style_consistency"
        )
        avg_complexity_delta = self._calculate_average_metric(
            file_results, "complexity_delta"
        )
        avg_performance_impact = self._calculate_average_metric(
            file_results, "performance_impact"
        )
        avg_maintainability = self._calculate_average_metric(
            file_results, "maintainability_score"
        )
        avg_accessibility = self._calculate_average_metric(
            file_results, "accessibility_score"
        )
        avg_security = self._calculate_average_metric(file_results, "security_score")

        # Create detailed analysis for the application
        detailed_analysis = {
            "evaluation_type": "application",
            "golden_app_path": golden_app_path,
            "generated_app_path": generated_app_path,
            "golden_languages": list(golden_structure.detected_languages),
            "generated_languages": list(generated_structure.detected_languages),
            "file_matches": {k: v.__dict__ for k, v in file_matches.items()},
            "evaluation_plan": evaluation_plan,
            "file_results": {
                k: v.__dict__ if hasattr(v, "__dict__") else v.to_dict()
                for k, v in file_results.items()
            },
            "structure_analysis": structure_analysis,
            "match_statistics": self._calculate_match_statistics(file_matches),
            "recommendations": self._generate_recommendations(
                file_results, structure_analysis, file_matches
            ),
        }

        # Create and return EvaluationResult object
        result = EvaluationResult(
            overall_similarity=overall_score,
            functional_equivalence=avg_functional_equiv,
            structural_similarity=avg_structural_sim,
            style_consistency=avg_style_consistency,
            complexity_delta=avg_complexity_delta,
            performance_impact=avg_performance_impact,
            maintainability_score=avg_maintainability,
            accessibility_score=avg_accessibility,
            security_score=avg_security,
            detailed_analysis=detailed_analysis,
        )

        # Add metadata
        result.metadata.update(
            {
                "evaluation_type": "application",
                "golden_app_path": golden_app_path,
                "generated_app_path": generated_app_path,
                "total_files_matched": len(file_matches),
                "overall_score": overall_score,
            }
        )

        return result

    def _evaluate_matched_files(
        self, file_matches: Dict[str, FileMatchResult], evaluation_plan: Dict[str, str]
    ) -> Dict[str, EvaluationResult]:
        """Evaluate each pair of matched files."""
        file_results = {}

        for golden_file, match_result in file_matches.items():
            strategy = evaluation_plan.get(golden_file, "skip")

            if strategy == "skip":
                logger.debug(f"Skipping {golden_file} due to low match confidence")
                continue

            try:
                result = self._evaluate_file_pair_with_strategy(
                    golden_file,
                    match_result.generated_file,
                    strategy,
                    match_result.confidence,
                )
                file_results[golden_file] = result

            except Exception as e:
                logger.warning(f"Failed to evaluate {golden_file}: {e}")

        return file_results

    def _evaluate_file_pair_with_strategy(
        self,
        golden_file: str,
        generated_file: str,
        strategy: str,
        match_confidence: float,
    ) -> EvaluationResult:
        """Evaluate a file pair using the specified strategy."""
        # Parse both files
        golden_sample = self.parser.parse_file(golden_file)
        generated_sample = self.parser.parse_file(generated_file)

        if not golden_sample or not generated_sample:
            raise EvaluationError(
                f"Could not parse files: {golden_file}, {generated_file}"
            )

        # Get base evaluation
        result = self.evaluator.evaluate_code_pair(
            golden_sample.content, generated_sample.content
        )

        # Apply strategy-specific adjustments
        self._apply_strategy_adjustments(result, strategy, match_confidence)

        return result

    def _apply_strategy_adjustments(
        self, result: EvaluationResult, strategy: str, match_confidence: float
    ) -> None:
        """Apply strategy-specific score adjustments."""
        if strategy == "semantic":
            result.overall_similarity *= match_confidence
        elif strategy == "structural":
            result.structural_similarity *= match_confidence
        elif strategy == "functional":
            # For functional strategy, weight all scores by confidence
            result.overall_similarity *= match_confidence
            result.functional_equivalence *= match_confidence
        # 'direct' strategy uses original scores

        # Add metadata
        result.metadata["match_confidence"] = match_confidence
        result.metadata["evaluation_strategy"] = strategy

    def _evaluate_all_models(
        self,
        golden_path: str,
        model_outputs: Union[Dict[str, str], List[str]],
        evaluation_type: str,
    ) -> Dict[str, float]:
        """Evaluate all models and return their scores."""
        results = {}

        # Handle both list and dict inputs for backward compatibility
        if isinstance(model_outputs, list):
            # Use the actual path as the key for easier access in tests
            model_dict = {path: path for path in model_outputs}
        else:
            model_dict = model_outputs

        for model_name, output_path in model_dict.items():
            logger.info(f"Evaluating model: {model_name}")

            try:
                result = self.evaluate(golden_path, output_path, evaluation_type)
                score = self._extract_overall_score(result)
                results[model_name] = score

            except Exception as e:
                logger.warning(f"Failed to evaluate model {model_name}: {e}")
                # Skip failed evaluations rather than setting to 0.0
                continue

        return results

    def _extract_overall_score(
        self, result: Union[Dict[str, Any], EvaluationResult]
    ) -> float:
        """Extract the main score from evaluation result."""
        if isinstance(result, EvaluationResult):
            return result.overall_similarity

        # Handle legacy dictionary results for backward compatibility
        if "overall_score" in result:
            return result["overall_score"]

        # Check for evaluation_type-based extraction
        evaluation_type = result.get("evaluation_type", "file")  # Default to 'file'
        if evaluation_type == "application":
            return result.get("overall_score", 0.0)
        else:
            return result.get("result", {}).get("overall_similarity", 0.0)

    def _create_batch_result(
        self, model_scores: Dict[str, float]
    ) -> BatchEvaluationResult:
        """Create batch result with rankings and statistics."""
        scores = list(model_scores.values())
        rankings = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)

        summary_stats = self._calculate_summary_statistics(
            scores
        )  # Always call to get proper empty structure

        # Get best and worst models from rankings
        best_model = rankings[0][0] if rankings else None
        worst_model = rankings[-1][0] if rankings else None

        return BatchEvaluationResult(
            model_scores=model_scores,  # Pass model_scores for backward compatibility
            rankings=rankings,
            summary_statistics=summary_stats,
            best_model=best_model,
            worst_model=worst_model,
        )

    def _calculate_summary_statistics(self, scores: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for a list of scores."""
        if not scores:
            return {
                "mean": 0.0,
                "median": 0.0,
                "std": 0.0,  # Add 'std' key for tests
                "std_dev": 0.0,
                "min": 0.0,  # Add 'min' key for tests
                "max": 0.0,  # Add 'max' key for tests
                "min_score": 0.0,
                "max_score": 0.0,
                # Also include the _score versions for backward compatibility
                "mean_score": 0.0,
                "median_score": 0.0,
            }

        mean_val = float(np.mean(scores))
        median_val = float(np.median(scores))
        std_val = float(np.std(scores))
        min_val = float(min(scores))
        max_val = float(max(scores))

        return {
            # Test-expected keys
            "mean": mean_val,
            "median": median_val,
            "std": std_val,  # Add the 'std' key that tests expect
            "std_dev": std_val,
            "min": min_val,  # Add 'min' key for tests
            "max": max_val,  # Add 'max' key for tests
            "min_score": min_val,
            "max_score": max_val,
            # Backward compatibility keys
            "mean_score": mean_val,
            "median_score": median_val,
        }

    def _analyze_structure_differences(
        self,
        golden_structure: ApplicationStructure,
        generated_structure: ApplicationStructure,
        file_matches: Dict[str, FileMatchResult],
    ) -> Dict[str, Any]:
        """Analyze differences in application structure."""
        return {
            "language_compatibility": self._analyze_language_compatibility(
                golden_structure, generated_structure
            ),
            "functionality_coverage": self._analyze_functionality_coverage(
                golden_structure, generated_structure
            ),
            "directory_similarity": self._calculate_directory_similarity(
                golden_structure, generated_structure
            ),
            "missing_files": self._find_missing_files(golden_structure, file_matches),
            "extra_files": self._find_extra_files(generated_structure, file_matches),
            "architecture_patterns": self._analyze_architecture_patterns(
                golden_structure, generated_structure
            ),
        }

    def _analyze_language_compatibility(
        self,
        golden: Union[ApplicationStructure, set],
        generated: Union[ApplicationStructure, set],
    ) -> Dict[str, Any]:
        """Analyze compatibility between detected languages."""
        # Handle both ApplicationStructure objects and raw sets for testing
        if isinstance(golden, set):
            golden_languages = golden
        else:
            golden_languages = golden.detected_languages

        if isinstance(generated, set):
            generated_languages = generated
        else:
            generated_languages = generated.detected_languages

        common_languages = golden_languages & generated_languages
        golden_only = golden_languages - generated_languages
        generated_only = generated_languages - golden_languages

        total_languages = golden_languages | generated_languages
        language_similarity = (
            len(common_languages) / len(total_languages) if total_languages else 1.0
        )

        # Calculate overlap percentage as expected by tests (common / max of the two sets)
        max_lang_count = (
            max(len(golden_languages), len(generated_languages))
            if (golden_languages or generated_languages)
            else 0
        )
        if max_lang_count == 0:
            # Both sets are empty - this should be 100% compatible
            overlap_percentage = 100.0
        else:
            overlap_percentage = (len(common_languages) / max_lang_count) * 100.0

        # Determine compatibility status
        if language_similarity == 1.0:
            status = "compatible"
        elif language_similarity >= 0.5:
            status = "partially_compatible"
        else:
            status = "incompatible"

        return {
            "status": status,  # Add status key for tests
            "overlap_percentage": overlap_percentage,  # Add overlap_percentage for tests
            "common_languages": common_languages,  # Keep as set for test compatibility
            "missing_languages": golden_only,  # golden_only_languages renamed to missing_languages
            "extra_languages": generated_only,  # generated_only_languages renamed to extra_languages
            "golden_only_languages": list(
                golden_only
            ),  # Keep for backward compatibility
            "generated_only_languages": list(
                generated_only
            ),  # Keep for backward compatibility
            "language_similarity": language_similarity,
        }

    def _analyze_functionality_coverage(
        self, golden: ApplicationStructure, generated: ApplicationStructure
    ) -> Dict[str, Any]:
        """Analyze how well the generated app covers the golden app's functionality."""
        golden_functionalities = set(
            file.metadata.get("functionality", "unknown") for file in golden.all_files
        )
        generated_functionalities = set(
            file.metadata.get("functionality", "unknown")
            for file in generated.all_files
        )

        covered_functionalities = golden_functionalities & generated_functionalities
        missing_functionalities = golden_functionalities - generated_functionalities
        extra_functionalities = generated_functionalities - golden_functionalities

        return {
            "covered_functionalities": list(covered_functionalities),
            "missing_functionalities": list(missing_functionalities),
            "extra_functionalities": list(extra_functionalities),
            "functionality_coverage": len(covered_functionalities)
            / len(golden_functionalities)
            if golden_functionalities
            else 1.0,
        }

    def _calculate_directory_similarity(
        self, golden: ApplicationStructure, generated: ApplicationStructure
    ) -> float:
        """Calculate how similar the directory structures are."""
        golden_dirs = set(str(file.file_path.parent) for file in golden.all_files)
        generated_dirs = set(str(file.file_path.parent) for file in generated.all_files)

        if not golden_dirs:
            return 1.0 if not generated_dirs else 0.0

        common_dirs = golden_dirs & generated_dirs
        total_dirs = golden_dirs | generated_dirs

        return len(common_dirs) / len(total_dirs)

    def _find_missing_files(
        self,
        golden_structure: ApplicationStructure,
        file_matches: Dict[str, FileMatchResult],
    ) -> List[str]:
        """Find files present in golden but missing in generated."""
        matched_golden_files = set(file_matches.keys())
        all_golden_files = set(
            str(file.file_path) for file in golden_structure.all_files
        )
        return list(all_golden_files - matched_golden_files)

    def _find_extra_files(
        self,
        generated_structure: ApplicationStructure,
        file_matches: Dict[str, FileMatchResult],
    ) -> List[str]:
        """Find files present in generated but not in golden."""
        matched_generated_files = set(
            match.generated_file for match in file_matches.values()
        )
        all_generated_files = set(
            str(file.file_path) for file in generated_structure.all_files
        )
        return list(all_generated_files - matched_generated_files)

    def _analyze_architecture_patterns(
        self, golden: ApplicationStructure, generated: ApplicationStructure
    ) -> Dict[str, Any]:
        """Analyze architectural patterns and conventions."""
        golden_by_function = {}
        generated_by_function = {}

        for file in golden.all_files:
            func = file.metadata.get("functionality", "unknown")
            golden_by_function[func] = golden_by_function.get(func, 0) + 1

        for file in generated.all_files:
            func = file.metadata.get("functionality", "unknown")
            generated_by_function[func] = generated_by_function.get(func, 0) + 1

        return {
            "file_counts_by_functionality": {
                "golden": golden_by_function,
                "generated": generated_by_function,
            },
            "total_files": {
                "golden": len(golden.all_files),
                "generated": len(generated.all_files),
            },
            "languages": {
                "golden": list(golden.detected_languages),
                "generated": list(generated.detected_languages),
            },
        }

    def _calculate_weighted_score(
        self,
        file_results: Dict[str, EvaluationResult],
        file_matches: Dict[str, FileMatchResult],
    ) -> float:
        """Calculate overall score weighted by match confidence."""
        if not file_results:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for golden_file, result in file_results.items():
            match_confidence = file_matches[golden_file].confidence
            weighted_sum += result.overall_similarity * match_confidence
            total_weight += match_confidence

        return safe_divide(weighted_sum, total_weight, 0.0)

    def _calculate_match_statistics(
        self, file_matches: Dict[str, FileMatchResult]
    ) -> Dict[str, Any]:
        """Calculate statistics about file matching quality."""
        if not file_matches:
            return {
                "total_files": 0,
                "avg_confidence": 0.0,
                "min_confidence": 0.0,
                "max_confidence": 0.0,
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0,
                "strategy_distribution": {},
            }

        confidences = [match.confidence for match in file_matches.values()]
        strategies = [match.match_strategy for match in file_matches.values()]

        return {
            "total_files": len(file_matches),
            "avg_confidence": float(np.mean(confidences)),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "high_confidence_count": sum(1 for c in confidences if c >= 0.8),
            "medium_confidence_count": sum(1 for c in confidences if 0.5 <= c < 0.8),
            "low_confidence_count": sum(1 for c in confidences if c < 0.5),
            "strategy_distribution": {
                strategy: strategies.count(strategy) for strategy in set(strategies)
            },
        }

    def _generate_recommendations(
        self,
        file_results: Dict[str, EvaluationResult],
        structure_analysis: Dict[str, Any],
        file_matches: Dict[str, FileMatchResult],
    ) -> List[str]:
        """Generate actionable recommendations for improvement."""
        recommendations = []

        # Language compatibility recommendations
        lang_analysis = structure_analysis.get("language_compatibility", {})
        if lang_analysis.get("language_similarity", 1.0) < 0.8:
            recommendations.append(
                f"Consider using more similar technologies - language compatibility is {lang_analysis.get('language_similarity', 0):.1%}"
            )

        # Functionality coverage recommendations
        func_analysis = structure_analysis.get("functionality_coverage", {})
        missing_functions = func_analysis.get("missing_functionalities", [])
        if missing_functions:
            recommendations.append(
                f"Missing functionality areas: {', '.join(missing_functions[:3])}{'...' if len(missing_functions) > 3 else ''}"
            )

        # Check for low match confidence
        low_confidence_count = sum(
            1 for match in file_matches.values() if match.confidence < 0.5
        )
        if low_confidence_count > 0:
            recommendations.append(
                f"Consider improving file organization - {low_confidence_count} files had low match confidence"
            )

        # Check for missing files
        missing_files = structure_analysis.get("missing_files", [])
        if missing_files:
            recommendations.append(
                f"Missing {len(missing_files)} files from golden standard"
            )

        # Check for low quality files
        low_quality_count = sum(
            1 for result in file_results.values() if result.overall_similarity < 0.6
        )
        if low_quality_count > 0:
            recommendations.append(
                f"Improve code quality in {low_quality_count} files with low similarity scores"
            )

        return recommendations

    def _build_report_lines(self, results: Dict[str, Any]) -> List[str]:
        """Build formatted report lines."""
        lines = [
            "=" * 70,
            "UNIVERSAL CODE EVALUATION REPORT",
            "=" * 70,
            f"Evaluation Type: {results.get('evaluation_type', 'unknown')}",
            "",
        ]

        if results["evaluation_type"] == "application":
            lines.extend(self._build_application_report_lines(results))
        else:
            lines.extend(self._build_file_report_lines(results))

        return lines

    def _build_application_report_lines(self, results: Dict[str, Any]) -> List[str]:
        """Build report lines for application evaluation."""
        lines = [
            f"Golden Application: {results['golden_app_path']}",
            f"Generated Application: {results['generated_app_path']}",
            "",
        ]

        # Language information
        if "golden_languages" in results:
            lines.extend(
                [
                    "DETECTED LANGUAGES:",
                    f"  Golden: {', '.join(results['golden_languages'])}",
                    f"  Generated: {', '.join(results['generated_languages'])}",
                    "",
                ]
            )

        # Match statistics
        if "match_statistics" in results:
            stats = results["match_statistics"]
            lines.extend(
                [
                    "FILE MATCHING STATISTICS:",
                    f"  Total files matched: {stats['total_files']}",
                    f"  Average match confidence: {stats['avg_confidence']:.3f}",
                    f"  High confidence matches: {stats['high_confidence_count']}",
                    f"  Medium confidence matches: {stats['medium_confidence_count']}",
                    f"  Low confidence matches: {stats['low_confidence_count']}",
                    "",
                ]
            )

        # Functionality coverage
        if "structure_analysis" in results:
            func_analysis = results["structure_analysis"].get(
                "functionality_coverage", {}
            )
            if func_analysis:
                coverage = func_analysis.get("functionality_coverage", 0)
                lines.extend(
                    [
                        "FUNCTIONALITY COVERAGE:",
                        f"  Coverage: {coverage:.1%}",
                        f"  Covered: {', '.join(func_analysis.get('covered_functionalities', []))}",
                        "",
                    ]
                )

        # Overall score
        lines.append(f"OVERALL SCORE: {results.get('overall_score', 0.0):.3f}")
        lines.append("")

        # Recommendations
        if "recommendations" in results and results["recommendations"]:
            lines.append("RECOMMENDATIONS:")
            for rec in results["recommendations"]:
                lines.append(f"  • {rec}")

        return lines

    def _build_file_report_lines(self, results: Dict[str, Any]) -> List[str]:
        """Build report lines for file evaluation."""

        # The results dict has the values at the top level now
        overall_sim = results.get("overall_similarity", 0.0)
        functional_eq = results.get("functional_equivalence", 0.0)
        structural_sim = results.get("structural_similarity", 0.0)
        style_cons = results.get("style_consistency", 0.0)

        return [
            f"Golden File: {results['golden_path']}",
            f"Generated File: {results['generated_path']}",
            "",
            "EVALUATION SCORES:",
            f"  Overall Similarity: {overall_sim:.3f}",
            f"  Functional Equivalence: {functional_eq:.3f}",
            f"  Structural Similarity: {structural_sim:.3f}",
            f"  Style Consistency: {style_cons:.3f}",
            "",
        ]

    def _save_report_to_file(self, report: str, output_file: str) -> None:
        """Save report to file with proper error handling."""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Report saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save report to {output_file}: {e}")
            raise EvaluationError(f"Could not save report: {e}")

    def _calculate_average_metric(
        self, file_results: Dict[str, EvaluationResult], metric_name: str
    ) -> float:
        """Calculate the average of a specific metric across all file results."""
        if not file_results:
            return 0.0

        values = []
        for result in file_results.values():
            if hasattr(result, metric_name):
                values.append(getattr(result, metric_name))

        return float(np.mean(values)) if values else 0.0

    def _resolve_file_path(self, path: str) -> str:
        """Resolve a path to a specific file, handling directories by finding main files."""
        path_obj = Path(path)

        if path_obj.is_file():
            return path

        if path_obj.is_dir():
            # Look for common main files
            main_candidates = [
                "main.py",
                "index.js",
                "index.ts",
                "index.tsx",
                "app.py",
                "app.js",
                "app.ts",
            ]

            for candidate in main_candidates:
                main_file = path_obj / candidate
                if main_file.exists():
                    return str(main_file)

            # If no main file found, use the first supported file
            for file_path in path_obj.rglob("*"):
                if file_path.is_file() and self.parser._should_include_file(file_path):
                    return str(file_path)

            raise FileNotFoundError(f"No suitable files found in directory: {path}")

        # If path doesn't exist, let the file parser handle the error
        return path

    # Method aliases for backward compatibility
    def evaluate_single_file(
        self, golden_path: str, generated_path: str
    ) -> EvaluationResult:
        """Alias for evaluate() with file evaluation type."""
        return self.evaluate(golden_path, generated_path, evaluation_type="file")

    def evaluate_files(self, golden_path: str, generated_path: str) -> EvaluationResult:
        """Alias for evaluate() with file evaluation type."""
        return self.evaluate(golden_path, generated_path, evaluation_type="file")

    def _evaluation_result_to_dict(self, result) -> Dict[str, Any]:
        """Convert EvaluationResult object to dictionary format for report generation."""
        results_dict = {
            "evaluation_type": result.metadata.get("evaluation_type", "unknown"),
            "overall_similarity": result.overall_similarity,
            "functional_equivalence": result.functional_equivalence,
            "structural_similarity": result.structural_similarity,
            "style_consistency": result.style_consistency,
            "complexity_delta": result.complexity_delta,
            "performance_impact": result.performance_impact,
            "maintainability_score": result.maintainability_score,
            "accessibility_score": result.accessibility_score,
            "security_score": result.security_score,
            "detailed_analysis": result.detailed_analysis,
            "metadata": result.metadata,
        }

        # Add any additional fields from metadata
        for key, value in result.metadata.items():
            if key not in results_dict:
                results_dict[key] = value

        return results_dict
