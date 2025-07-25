"""
Analyzer classes for semantic similarity and code evaluation.

This module contains the core analysis engines responsible for computing
semantic similarity and multi-dimensional code quality metrics.
"""

import logging
import re
from typing import Dict, List, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .cache import get_embedding_cache

from .config import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EVALUATION_WEIGHTS,
    QUALITY_THRESHOLDS,
)
from .exceptions import EvaluationError
from .models import EvaluationResult, FileComparisonResult
from .utils import (
    calculate_complexity_score,
    clamp,
    extract_function_names,
    extract_hooks,
    extract_imports,
    extract_jsx_elements,
    preprocess_code_for_analysis,
    safe_divide,
)

logger = logging.getLogger(__name__)


class SemanticSimilarityAnalyzer:
    """
    Core semantic similarity analysis engine using transformer models.

    This class handles the computation of semantic embeddings and similarity
    scores for code samples.
    """

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        """
        Initialize the semantic similarity analyzer.

        Args:
            model_name: Name of the transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.model_type = "unknown"
        self._load_model()

    def _load_model(self) -> None:
        """Load the transformer model for embeddings."""
        try:
            if "unixcoder" in self.model_name.lower():
                # Use UniXcoder for code-specific embeddings
                from transformers import AutoTokenizer, AutoModel
                import torch
                
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModel.from_pretrained(self.model_name)
                self.model_type = "unixcoder"
                logger.info(f"Successfully loaded UniXcoder model: {self.model_name}")
            else:
                # Use sentence-transformers for general embeddings
                from sentence_transformers import SentenceTransformer
                
                self.model = SentenceTransformer(self.model_name)
                self.model_type = "sentence_transformer"
                logger.info(f"Successfully loaded SentenceTransformer model: {self.model_name}")
                
        except ImportError as e:
            logger.warning(f"Required library not available: {e}. Using fallback.")
            self._load_fallback_model()
        except Exception as e:
            logger.warning(f"Failed to load {self.model_name}: {e}. Using fallback.")
            self._load_fallback_model()
    
    def _load_fallback_model(self) -> None:
        """Load fallback model when primary model fails."""
        try:
            from sentence_transformers import SentenceTransformer
            from .config import FALLBACK_EMBEDDING_MODEL
            
            self.model = SentenceTransformer(FALLBACK_EMBEDDING_MODEL)
            self.model_type = "sentence_transformer"
            logger.info(f"Loaded fallback model: {FALLBACK_EMBEDDING_MODEL}")
        except Exception as e:
            logger.warning(f"Fallback model also failed: {e}. Using random embeddings.")
            self.model = None
            self.model_type = "random"

    def compute_embeddings(self, code_samples: List[str]) -> np.ndarray:
        """
        Compute embeddings for code samples.

        Args:
            code_samples: List of code strings

        Returns:
            NumPy array of embeddings
        """
        if self.model is None:
            # Fallback to random embeddings for testing
            logger.warning("Using random embeddings (model not available)")
            return np.random.rand(len(code_samples), 768)

        try:
            if self.model_type == "unixcoder":
                return self._compute_unixcoder_embeddings(code_samples)
            elif self.model_type == "sentence_transformer":
                return self._compute_sentence_transformer_embeddings(code_samples)
            else:
                logger.warning("Unknown model type, using random embeddings")
                return np.random.rand(len(code_samples), 768)
                
        except Exception as e:
            logger.error(f"Failed to compute embeddings: {e}")
            # Return random embeddings as fallback
            return np.random.rand(len(code_samples), 768)
    
    def _compute_unixcoder_embeddings(self, code_samples: List[str]) -> np.ndarray:
        """Compute embeddings using UniXcoder model."""
        import torch
        
        embeddings = []
        for code in code_samples:
            # Preprocess code for better embeddings
            processed_code = preprocess_code_for_analysis(code)
            
            # Tokenize for UniXcoder (encoder-only mode)
            inputs = self.tokenizer(
                processed_code,
                max_length=512,
                truncation=True,
                padding=True,
                return_tensors="pt"
            )
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of last hidden states
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def _compute_sentence_transformer_embeddings(self, code_samples: List[str]) -> np.ndarray:
        """Compute embeddings using SentenceTransformer model."""
        # Preprocess code for better embeddings
        processed_samples = [
            preprocess_code_for_analysis(code) for code in code_samples
        ]
        embeddings = self.model.encode(processed_samples)
        logger.debug(f"Computed embeddings for {len(code_samples)} samples")
        return embeddings

    def compute_similarity(self, code1: str, code2: str) -> float:
        """
        Compute semantic similarity between two code samples.

        Args:
            code1: First code sample
            code2: Second code sample

        Returns:
            Similarity score between 0 and 1
        """
        try:
            embeddings = self.compute_embeddings([code1, code2])
            if embeddings.shape[0] >= 2:
                similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                return clamp(float(similarity))
            else:
                return 0.5  # Fallback similarity
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            return 0.5

    def compute_similarity_score(self, code1: str, code2: str) -> float:
        """
        Alias for compute_similarity for backward compatibility.

        Args:
            code1: First code sample
            code2: Second code sample

        Returns:
            Similarity score between 0 and 1
        """
        return self.compute_similarity(code1, code2)

    def analyze_similarity(self, code1: str, code2: str) -> float:
        """
        Alias for compute_similarity for backward compatibility.

        Args:
            code1: First code sample
            code2: Second code sample

        Returns:
            Similarity score between 0 and 1
        """
        return self.compute_similarity(code1, code2)


class QualityAnalyzer:
    """
    Analyzer for code quality metrics.

    This class implements various code quality assessment methods including
    functional equivalence, structural similarity, and maintainability.
    """

    def analyze_functional_equivalence(self, golden: str, generated: str) -> float:
        """
        Analyze functional equivalence between code samples.

        Args:
            golden: Golden standard code
            generated: Generated code

        Returns:
            Functional equivalence score (0-1)
        """
        try:
            golden_functions = set(extract_function_names(golden))
            generated_functions = set(extract_function_names(generated))

            if not golden_functions:
                return 1.0  # No functions to compare

            common_functions = golden_functions & generated_functions
            return len(common_functions) / len(golden_functions)
        except Exception as e:
            logger.error(f"Error analyzing functional equivalence: {e}")
            return 0.0

    def analyze_structural_similarity(self, golden: str, generated: str) -> float:
        """
        Analyze structural similarity between code samples.

        Args:
            golden: Golden standard code
            generated: Generated code

        Returns:
            Structural similarity score (0-1)
        """
        try:
            # If files are identical, return perfect similarity
            if golden.strip() == generated.strip():
                return 1.0
            
            # Compare import statements
            golden_imports = set(extract_imports(golden))
            generated_imports = set(extract_imports(generated))

            import_similarity = 1.0  # Default to 1.0 if no imports
            if golden_imports:
                common_imports = golden_imports & generated_imports
                import_similarity = len(common_imports) / len(golden_imports)

            # Compare JSX structure
            golden_jsx = set(extract_jsx_elements(golden))
            generated_jsx = set(extract_jsx_elements(generated))

            jsx_similarity = 1.0  # Default to 1.0 if no JSX
            if golden_jsx:
                common_jsx = golden_jsx & generated_jsx
                jsx_similarity = len(common_jsx) / len(golden_jsx)

            # Compare hooks usage
            golden_hooks = set(extract_hooks(golden))
            generated_hooks = set(extract_hooks(generated))

            hooks_similarity = 1.0  # Default to 1.0 if no hooks
            if golden_hooks:
                common_hooks = golden_hooks & generated_hooks
                hooks_similarity = len(common_hooks) / len(golden_hooks)

            # Weighted average of structural components
            weights = [0.4, 0.4, 0.2]  # imports, jsx, hooks
            similarities = [import_similarity, jsx_similarity, hooks_similarity]

            return sum(w * s for w, s in zip(weights, similarities))
        except Exception as e:
            logger.error(f"Error analyzing structural similarity: {e}")
            return 0.0

    def analyze_style_consistency(self, golden: str, generated: str) -> float:
        """
        Analyze code style consistency.

        Args:
            golden: Golden standard code
            generated: Generated code

        Returns:
            Style consistency score (0-1)
        """
        try:
            style_factors = []

            # Indentation consistency
            golden_lines = golden.split("\n")
            generated_lines = generated.split("\n")

            golden_indented = sum(1 for line in golden_lines if line.startswith("  "))
            generated_indented = sum(
                1 for line in generated_lines if line.startswith("  ")
            )

            if golden_lines:
                indent_ratio = safe_divide(
                    generated_indented, golden_indented, default=0.5
                )
                style_factors.append(min(1.0, indent_ratio))

            # Naming convention consistency (camelCase)
            golden_camel_case = len(re.findall(r"\\b[a-z][a-zA-Z0-9]*\\b", golden))
            generated_camel_case = len(
                re.findall(r"\\b[a-z][a-zA-Z0-9]*\\b", generated)
            )

            if golden_camel_case > 0:
                naming_similarity = safe_divide(
                    generated_camel_case, golden_camel_case, default=0.5
                )
                style_factors.append(min(1.0, naming_similarity))

            # Arrow function vs function declaration consistency
            golden_arrow = len(re.findall(r"=>", golden))
            generated_arrow = len(re.findall(r"=>", generated))
            golden_func = len(re.findall(r"function\\s+\\w+", golden))
            generated_func = len(re.findall(r"function\\s+\\w+", generated))

            if golden_arrow + golden_func > 0:
                arrow_ratio_golden = safe_divide(
                    golden_arrow, golden_arrow + golden_func
                )
                arrow_ratio_generated = safe_divide(
                    generated_arrow, generated_arrow + generated_func
                )
                arrow_consistency = 1.0 - abs(
                    arrow_ratio_golden - arrow_ratio_generated
                )
                style_factors.append(arrow_consistency)

            return np.mean(style_factors) if style_factors else 0.5
        except Exception as e:
            logger.error(f"Error analyzing style consistency: {e}")
            return 0.0

    def analyze_complexity_delta(self, golden: str, generated: str) -> float:
        """
        Analyze complexity difference between code samples.

        Args:
            golden: Golden standard code
            generated: Generated code

        Returns:
            Complexity delta (can be negative if generated is simpler)
        """
        try:
            golden_complexity = calculate_complexity_score(golden)
            generated_complexity = calculate_complexity_score(generated)

            if golden_complexity == 0:
                return 0.0

            return (generated_complexity - golden_complexity) / golden_complexity
        except Exception as e:
            logger.error(f"Error analyzing complexity delta: {e}")
            return 0.0

    def estimate_performance_impact(self, golden: str, generated: str) -> float:
        """
        Estimate performance impact of generated code.

        Args:
            golden: Golden standard code
            generated: Generated code

        Returns:
            Performance impact score (0-1, higher is better)
        """
        try:
            # If files are identical, performance impact is perfect
            if golden.strip() == generated.strip():
                return 1.0
            
            antipatterns = 0

            # Check for missing keys in map operations
            if ".map(" in generated and "key=" not in generated:
                antipatterns += 1

            # Check for inefficient state updates
            if "useState" in generated and "useCallback" not in generated:
                callback_needed = len(re.findall(r"on\w+={", generated))
                if callback_needed > 2:  # Multiple event handlers without useCallback
                    antipatterns += 1

            # Check for missing dependency arrays
            useeffect_count = len(re.findall(r"useEffect\(", generated))
            dependency_arrays = len(re.findall(r"useEffect\([^)]+,\s*\[", generated))
            if useeffect_count > dependency_arrays:
                antipatterns += 1

            penalty = (
                antipatterns * QUALITY_THRESHOLDS["performance_penalty_per_antipattern"]
            )
            return clamp(1.0 - penalty)
        except Exception as e:
            logger.error(f"Error estimating performance impact: {e}")
            return 0.5

    def assess_maintainability(self, code: str) -> float:
        """
        Assess code maintainability.

        Args:
            code: Code to assess

        Returns:
            Maintainability score (0-1)
        """
        try:
            factors = []
            lines = code.split("\\n")

            # Function length (shorter is generally better)
            function_count = len(extract_function_names(code))
            if function_count > 0:
                avg_function_length = len(lines) / function_count
                # Ideal function length is around 10-20 lines
                length_score = clamp(1.0 - max(0, avg_function_length - 20) / 30)
                factors.append(length_score)

            # Comment density
            comment_lines = len(re.findall(r"//|/\\*", code))
            comment_ratio = safe_divide(comment_lines, len(lines))
            # Ideal comment ratio is around 10-20%
            comment_score = min(1.0, comment_ratio * 10)
            factors.append(comment_score)

            # Meaningful variable names (length > 2, not all caps)
            meaningful_names = len(re.findall(r"\\b[a-z][a-zA-Z]{2,}\\b", code))
            total_identifiers = len(re.findall(r"\\b[a-zA-Z_]\\w*\\b", code))
            if total_identifiers > 0:
                name_quality = safe_divide(meaningful_names, total_identifiers)
                factors.append(name_quality)

            return np.mean(factors) if factors else 0.5
        except Exception as e:
            logger.error(f"Error assessing maintainability: {e}")
            return 0.0

    def assess_maintainability_similarity(self, golden: str, generated: str) -> float:
        """
        Assess maintainability similarity between golden and generated code.

        Args:
            golden: Golden standard code
            generated: Generated code

        Returns:
            Maintainability similarity score (0-1)
        """
        try:
            # If files are identical, maintainability similarity is perfect
            if golden.strip() == generated.strip():
                return 1.0
            
            golden_score = self.assess_maintainability(golden)
            generated_score = self.assess_maintainability(generated)
            
            # Calculate similarity based on the difference in scores
            if golden_score == generated_score:
                return 1.0
            
            if golden_score == 0 and generated_score == 0:
                return 1.0
            
            max_score = max(golden_score, generated_score)
            min_score = min(golden_score, generated_score)
            
            if max_score == 0:
                return 1.0
            
            return min_score / max_score
        except Exception as e:
            logger.error(f"Error assessing maintainability similarity: {e}")
            return 0.0

    def assess_accessibility(self, code: str) -> float:
        """
        Assess accessibility considerations in code.

        Args:
            code: Code to assess

        Returns:
            Accessibility score (0-1)
        """
        try:
            accessibility_features = 0
            total_possible = 1

            # Check for alt attributes
            if "alt=" in code:
                accessibility_features += 1
            total_possible += 1

            # Check for aria attributes
            if "aria-" in code:
                accessibility_features += 1
            total_possible += 1

            # Check for semantic HTML
            semantic_tags = [
                "<header",
                "<nav",
                "<main",
                "<article",
                "<section",
                "<aside",
            ]
            if any(tag in code for tag in semantic_tags):
                accessibility_features += 1
            total_possible += 1

            # Check for form labels
            if "<label" in code or "htmlFor=" in code:
                accessibility_features += 1
            total_possible += 1

            # Check for keyboard navigation support
            if "onKeyDown" in code or "tabIndex" in code:
                accessibility_features += 1
            total_possible += 1

            return accessibility_features / total_possible
        except Exception as e:
            logger.error(f"Error assessing accessibility: {e}")
            return 0.0

    def assess_accessibility_similarity(self, golden: str, generated: str) -> float:
        """
        Assess accessibility similarity between golden and generated code.

        Args:
            golden: Golden standard code
            generated: Generated code

        Returns:
            Accessibility similarity score (0-1)
        """
        try:
            # If files are identical, accessibility similarity is perfect
            if golden.strip() == generated.strip():
                return 1.0
            
            golden_score = self.assess_accessibility(golden)
            generated_score = self.assess_accessibility(generated)
            
            # If both have the same accessibility score, they're similar
            if golden_score == generated_score:
                return 1.0
            
            # Calculate similarity based on the difference in scores
            if golden_score == 0 and generated_score == 0:
                return 1.0  # Both have no accessibility features
            
            max_score = max(golden_score, generated_score)
            min_score = min(golden_score, generated_score)
            
            if max_score == 0:
                return 1.0
            
            return min_score / max_score
        except Exception as e:
            logger.error(f"Error assessing accessibility similarity: {e}")
            return 0.0

    def assess_security(self, code: str) -> float:
        """
        Assess security considerations in code.

        Args:
            code: Code to assess

        Returns:
            Security score (0-1)
        """
        try:
            security_issues = 0

            # Check for dangerous HTML injection
            if "dangerouslySetInnerHTML" in code:
                security_issues += 1

            # Check for potential secret exposure
            secret_pattern = r'(password|secret|key|token)\\s*=\\s*["\'][^"\']+["\']'
            if re.search(secret_pattern, code, re.IGNORECASE):
                security_issues += 1

            # Check for eval usage
            if "eval(" in code:
                security_issues += 1

            # Check for direct DOM manipulation that could be unsafe
            if "innerHTML" in code and "dangerouslySetInnerHTML" not in code:
                security_issues += 1

            penalty = security_issues * QUALITY_THRESHOLDS["security_penalty_per_issue"]
            return clamp(1.0 - penalty)
        except Exception as e:
            logger.error(f"Error assessing security: {e}")
            return 0.5

    def assess_security_similarity(self, golden: str, generated: str) -> float:
        """
        Assess security similarity between golden and generated code.

        Args:
            golden: Golden standard code
            generated: Generated code

        Returns:
            Security similarity score (0-1)
        """
        try:
            # If files are identical, security similarity is perfect
            if golden.strip() == generated.strip():
                return 1.0
            
            golden_score = self.assess_security(golden)
            generated_score = self.assess_security(generated)
            
            # Calculate similarity based on the difference in scores
            if golden_score == generated_score:
                return 1.0
            
            if golden_score == 0 and generated_score == 0:
                return 1.0
            
            max_score = max(golden_score, generated_score)
            min_score = min(golden_score, generated_score)
            
            if max_score == 0:
                return 1.0
            
            return min_score / max_score
        except Exception as e:
            logger.error(f"Error assessing security similarity: {e}")
            return 0.0

    def analyze_structure(self, code1: str, code2: str) -> float:
        """
        Alias for analyze_structural_similarity for backward compatibility.

        Args:
            code1: First code sample
            code2: Second code sample

        Returns:
            Structural similarity score between 0 and 1
        """
        return self.analyze_structural_similarity(code1, code2)


class ComprehensiveEvaluator:
    """
    Main evaluation engine implementing the complete framework.

    This class orchestrates all the different analysis components to provide
    comprehensive evaluation of code samples and applications.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the comprehensive evaluator.

        Args:
            weights: Custom weights for different evaluation dimensions
        """
        self.semantic_analyzer = SemanticSimilarityAnalyzer()
        self.quality_analyzer = QualityAnalyzer()
        self.weights = weights or DEFAULT_EVALUATION_WEIGHTS.copy()
        self._validate_weights()

    def _validate_weights(self) -> None:
        """Validate that weights sum to approximately 1.0."""
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total_weight}, not 1.0. Normalizing...")
            for key in self.weights:
                self.weights[key] /= total_weight

    def evaluate_code_pair(
        self, golden_code: str, generated_code: str
    ) -> EvaluationResult:
        """
        Evaluate a pair of code samples comprehensively.

        Args:
            golden_code: Golden standard code
            generated_code: Generated code to evaluate

        Returns:
            Comprehensive evaluation result

        Raises:
            EvaluationError: If evaluation fails
        """
        try:
            # Compute semantic similarity
            semantic_similarity = self.semantic_analyzer.compute_similarity(
                golden_code, generated_code
            )

            # Compute quality metrics
            functional_equivalence = (
                self.quality_analyzer.analyze_functional_equivalence(
                    golden_code, generated_code
                )
            )
            structural_similarity = self.quality_analyzer.analyze_structural_similarity(
                golden_code, generated_code
            )
            style_consistency = self.quality_analyzer.analyze_style_consistency(
                golden_code, generated_code
            )
            complexity_delta = self.quality_analyzer.analyze_complexity_delta(
                golden_code, generated_code
            )
            performance_impact = self.quality_analyzer.estimate_performance_impact(
                golden_code, generated_code
            )
            maintainability_score = self.quality_analyzer.assess_maintainability_similarity(
                golden_code, generated_code
            )
            accessibility_score = self.quality_analyzer.assess_accessibility_similarity(
                golden_code, generated_code
            )
            security_score = self.quality_analyzer.assess_security_similarity(
                golden_code, generated_code
            )

            # Calculate weighted overall similarity
            overall_similarity = (
                self.weights.get("semantic", 0) * semantic_similarity
                + self.weights.get("functional", 0) * functional_equivalence
                + self.weights.get("structural", 0) * structural_similarity
                + self.weights.get("style", 0) * style_consistency
                + self.weights.get("maintainability", 0) * maintainability_score
                + self.weights.get("accessibility", 0) * accessibility_score
            )

            # Detailed analysis
            detailed_analysis = {
                "semantic_similarity": float(semantic_similarity),
                "code_length_ratio": safe_divide(
                    len(generated_code), len(golden_code), 1.0
                ),
                "line_count_ratio": safe_divide(
                    len(generated_code.split("\\n")), len(golden_code.split("\\n")), 1.0
                ),
                "weights_used": self.weights.copy(),
                "complexity_scores": {
                    "golden": calculate_complexity_score(golden_code),
                    "generated": calculate_complexity_score(generated_code),
                },
            }

            return EvaluationResult(
                overall_similarity=clamp(overall_similarity),
                functional_equivalence=clamp(functional_equivalence),
                structural_similarity=clamp(structural_similarity),
                style_consistency=clamp(style_consistency),
                complexity_delta=complexity_delta,
                performance_impact=clamp(performance_impact),
                maintainability_score=clamp(maintainability_score),
                accessibility_score=clamp(accessibility_score),
                security_score=clamp(security_score),
                detailed_analysis=detailed_analysis,
            )

        except Exception as e:
            raise EvaluationError(f"Failed to evaluate code pair: {e}")

    def compare_file_collections(
        self, golden_files: Dict[str, str], generated_files: Dict[str, str]
    ) -> FileComparisonResult:
        """
        Compare collections of files (components, pages, etc.).

        Args:
            golden_files: Dictionary of golden standard files
            generated_files: Dictionary of generated files

        Returns:
            File comparison result
        """
        result = FileComparisonResult()

        # Find missing and extra files
        golden_files_set = set(golden_files.keys())
        generated_files_set = set(generated_files.keys())

        result.missing_files = list(golden_files_set - generated_files_set)
        result.extra_files = list(generated_files_set - golden_files_set)

        # Compare common files
        common_files = golden_files_set & generated_files_set
        scores = []

        for file_name in common_files:
            try:
                evaluation = self.evaluate_code_pair(
                    golden_files[file_name], generated_files[file_name]
                )
                result.scores[file_name] = evaluation
                scores.append(evaluation.overall_similarity)
                logger.debug(
                    f"Evaluated {file_name}: {evaluation.overall_similarity:.3f}"
                )
            except Exception as e:
                logger.error(f"Failed to evaluate {file_name}: {e}")

        if scores:
            result.category_average = np.mean(scores)

        return result

    def evaluate_similarity(
        self, golden_code: str, generated_code: str
    ) -> EvaluationResult:
        """
        Alias for evaluate_code_pair for backward compatibility.

        Args:
            golden_code: The golden standard code
            generated_code: The generated code to evaluate

        Returns:
            EvaluationResult containing all metrics
        """
        return self.evaluate_code_pair(golden_code, generated_code)

    # Additional method aliases for backward compatibility
    def compute_similarity(self, code1: str, code2: str) -> float:
        """Alias for evaluate_similarity that returns just the overall similarity
        score."""
        result = self.evaluate_similarity(code1, code2)
        return result.overall_similarity

    def analyze_functional_equivalence(self, golden: str, generated: str) -> float:
        """Analyze functional equivalence between two code samples."""
        result = self.evaluate_code_pair(golden, generated)
        return result.functional_equivalence

    def analyze_structural_similarity(self, golden: str, generated: str) -> float:
        """Analyze structural similarity between two code samples."""
        result = self.evaluate_code_pair(golden, generated)
        return result.structural_similarity

    def assess_accessibility(self, code: str) -> float:
        """Assess accessibility score of a code sample."""
        # For single code analysis, compare with empty code to get absolute score
        result = self.evaluate_code_pair("", code)
        return result.accessibility_score

    def assess_security(self, code: str) -> float:
        """Assess security score of a code sample."""
        # For single code analysis, compare with empty code to get absolute score
        result = self.evaluate_code_pair("", code)
        return result.security_score
