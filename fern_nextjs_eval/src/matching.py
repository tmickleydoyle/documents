"""
Intelligent file matching and structure analysis for flexible evaluation.

This module provides sophisticated algorithms to match files between golden
and generated codebases even when they have different directory structures.
"""

import ast
import logging
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Set

from .models import ApplicationStructure, FileMatchResult

logger = logging.getLogger(__name__)


@dataclass
class FileAnalysis:
    """Analysis of a single file's characteristics."""

    file_path: Path
    file_type: str
    component_name: Optional[str]
    exports: List[str]
    imports: List[str]
    dependencies: Set[str]
    complexity_score: float
    functionality_signature: str
    content_hash: str


class IntelligentFileMatcher:
    """
    Matches files between golden and generated codebases using multiple strategies.

    Handles cases where:
    - Files are in different directories
    - Files have different names but same functionality
    - Directory structures are completely different
    - Files are split or combined differently
    """

    def __init__(self):
        self.component_patterns = {
            "react_component": (
                r"(export\s+default\s+|export\s+const\s+|export\s+function\s+)(\w+)"
            ),
            "page_component": r"(pages?/|src/pages?/)",
            "layout_component": r"(layout|Layout)",
            "api_route": r"(api/|pages?/api/)",
            "utility": r"(utils?/|helpers?/|lib/)",
            "style": r"\.(css|scss|sass|less)$",
            "config": r"\.(json|js|ts)$",
            "hook": r"use[A-Z]\w+",
        }

    def match_files(
        self,
        golden_structure: ApplicationStructure,
        generated_structure: ApplicationStructure,
    ) -> Dict[str, FileMatchResult]:
        """
        Match files between golden and generated structures using multiple strategies.

        Returns a mapping of golden file paths to their best matches in generated
        structure.
        """
        logger.info("Starting intelligent file matching process")

        golden_analyses = self._analyze_files(golden_structure)
        generated_analyses = self._analyze_files(generated_structure)

        matches = {}
        used_generated_files = set()

        # Strategy 1: Exact name match
        matches.update(
            self._match_by_exact_name(
                golden_analyses, generated_analyses, used_generated_files
            )
        )

        # Strategy 2: Component signature match
        matches.update(
            self._match_by_component_signature(
                golden_analyses, generated_analyses, used_generated_files
            )
        )

        # Strategy 3: Functionality similarity
        matches.update(
            self._match_by_functionality(
                golden_analyses, generated_analyses, used_generated_files
            )
        )

        # Strategy 4: Content similarity
        matches.update(
            self._match_by_content_similarity(
                golden_analyses, generated_analyses, used_generated_files
            )
        )

        # Strategy 5: Fallback - best available match
        matches.update(
            self._match_fallback(
                golden_analyses, generated_analyses, used_generated_files
            )
        )

        logger.info(f"Matched {len(matches)} files out of {len(golden_analyses)}")
        return matches

    def _analyze_files(
        self, structure: ApplicationStructure
    ) -> Dict[str, FileAnalysis]:
        """Analyze all files in the structure to extract characteristics."""
        analyses = {}

        for file_path in structure.all_files:
            try:
                analysis = self._analyze_single_file(file_path)
                analyses[str(file_path)] = analysis
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")

        return analyses

    def _analyze_single_file(self, file_path: Path) -> FileAnalysis:
        """Perform deep analysis of a single file."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        return FileAnalysis(
            file_path=file_path,
            file_type=self._determine_file_type(file_path, content),
            component_name=self._extract_component_name(content),
            exports=self._extract_exports(content),
            imports=self._extract_imports(content),
            dependencies=self._extract_dependencies(content),
            complexity_score=self._calculate_complexity(content),
            functionality_signature=self._generate_functionality_signature(content),
            content_hash=self._calculate_content_hash(content),
        )

    def _match_by_exact_name(
        self,
        golden: Dict[str, FileAnalysis],
        generated: Dict[str, FileAnalysis],
        used: Set[str],
    ) -> Dict[str, FileMatchResult]:
        """Match files with identical names."""
        matches = {}

        for golden_path, golden_analysis in golden.items():
            golden_name = golden_analysis.file_path.name

            for gen_path, gen_analysis in generated.items():
                if gen_path in used:
                    continue

                if gen_analysis.file_path.name == golden_name:
                    matches[golden_path] = FileMatchResult(
                        golden_file=golden_path,
                        generated_file=gen_path,
                        confidence=1.0,
                        match_strategy="exact_name",
                        similarity_reasons=["identical_filename"],
                    )
                    used.add(gen_path)
                    break

        return matches

    def _match_by_component_signature(
        self,
        golden: Dict[str, FileAnalysis],
        generated: Dict[str, FileAnalysis],
        used: Set[str],
    ) -> Dict[str, FileMatchResult]:
        """Match files by component signatures (exports, component names)."""
        matches = {}

        for golden_path, golden_analysis in golden.items():
            if golden_path in matches:
                continue

            best_match = None
            best_confidence = 0.0

            for gen_path, gen_analysis in generated.items():
                if gen_path in used:
                    continue

                confidence = self._calculate_signature_similarity(
                    golden_analysis, gen_analysis
                )

                # Clamp confidence to [0, 1]
                confidence = min(1.0, max(0.0, confidence))

                if confidence > 0.7 and confidence > best_confidence:
                    best_confidence = confidence
                    best_match = gen_path

            if best_match:
                # Ensure confidence is clamped to [0, 1]
                best_confidence = min(1.0, max(0.0, best_confidence))
                matches[golden_path] = FileMatchResult(
                    golden_file=golden_path,
                    generated_file=best_match,
                    confidence=best_confidence,
                    match_strategy="component_signature",
                    similarity_reasons=self._get_signature_reasons(
                        golden_analysis, generated[best_match]
                    ),
                )
                used.add(best_match)

        return matches

    def _match_by_functionality(
        self,
        golden: Dict[str, FileAnalysis],
        generated: Dict[str, FileAnalysis],
        used: Set[str],
    ) -> Dict[str, FileMatchResult]:
        """Match files by functionality signatures."""
        matches = {}

        for golden_path, golden_analysis in golden.items():
            if golden_path in matches:
                continue

            best_match = None
            best_confidence = 0.0

            for gen_path, gen_analysis in generated.items():
                if gen_path in used:
                    continue

                # Compare functionality signatures
                similarity = SequenceMatcher(
                    None,
                    golden_analysis.functionality_signature,
                    gen_analysis.functionality_signature,
                ).ratio()

                # Boost confidence if file types match
                if golden_analysis.file_type == gen_analysis.file_type:
                    similarity *= 1.2

                # Clamp similarity to [0, 1] to ensure valid confidence
                similarity = min(1.0, max(0.0, similarity))

                if similarity > 0.6 and similarity > best_confidence:
                    best_confidence = similarity
                    best_match = gen_path

            if best_match:
                # Ensure confidence is clamped to [0, 1]
                best_confidence = min(1.0, max(0.0, best_confidence))
                matches[golden_path] = FileMatchResult(
                    golden_file=golden_path,
                    generated_file=best_match,
                    confidence=best_confidence,
                    match_strategy="functionality",
                    similarity_reasons=[
                        f"functionality_similarity: {best_confidence:.2f}"
                    ],
                )
                used.add(best_match)

        return matches

    def _match_by_content_similarity(
        self,
        golden: Dict[str, FileAnalysis],
        generated: Dict[str, FileAnalysis],
        used: Set[str],
    ) -> Dict[str, FileMatchResult]:
        """Match files by content similarity using semantic analysis."""
        matches = {}

        for golden_path, golden_analysis in golden.items():
            if golden_path in matches:
                continue

            best_match = None
            best_confidence = 0.0

            for gen_path, gen_analysis in generated.items():
                if gen_path in used:
                    continue

                # Compare content characteristics
                confidence = self._calculate_content_similarity(
                    golden_analysis, gen_analysis
                )

                # Clamp confidence to [0, 1]
                confidence = min(1.0, max(0.0, confidence))

                if confidence > 0.5 and confidence > best_confidence:
                    best_confidence = confidence
                    best_match = gen_path

            if best_match:
                # Ensure confidence is clamped to [0, 1]
                best_confidence = min(1.0, max(0.0, best_confidence))
                matches[golden_path] = FileMatchResult(
                    golden_file=golden_path,
                    generated_file=best_match,
                    confidence=best_confidence,
                    match_strategy="content_similarity",
                    similarity_reasons=[f"content_similarity: {best_confidence:.2f}"],
                )
                used.add(best_match)

        return matches

    def _match_fallback(
        self,
        golden: Dict[str, FileAnalysis],
        generated: Dict[str, FileAnalysis],
        used: Set[str],
    ) -> Dict[str, FileMatchResult]:
        """Fallback matching for remaining unmatched files."""
        matches = {}
        available_generated = {k: v for k, v in generated.items() if k not in used}

        for golden_path, golden_analysis in golden.items():
            if golden_path in matches or not available_generated:
                continue

            # Find the best remaining match by file type preference
            type_matches = [
                (path, analysis)
                for path, analysis in available_generated.items()
                if analysis.file_type == golden_analysis.file_type
            ]

            if type_matches:
                # Pick the first type match
                best_path, best_analysis = type_matches[0]
                confidence = 0.3  # Low confidence fallback
            else:
                # Pick any remaining file
                best_path, best_analysis = next(iter(available_generated.items()))
                confidence = 0.1  # Very low confidence

            matches[golden_path] = FileMatchResult(
                golden_file=golden_path,
                generated_file=best_path,
                confidence=confidence,
                match_strategy="fallback",
                similarity_reasons=["fallback_match"],
            )

            del available_generated[best_path]

        return matches

    def _determine_file_type(self, file_path: Path, content: str) -> str:
        """Determine the type/category of a file."""
        extension = file_path.suffix.lower()
        path_str = str(file_path).lower()

        # Check patterns
        for file_type, pattern in self.component_patterns.items():
            if re.search(pattern, path_str) or re.search(pattern, content):
                return file_type

        # Extension-based fallback
        extension_map = {
            ".tsx": "react_component",
            ".jsx": "react_component",
            ".ts": "typescript",
            ".js": "javascript",
            ".css": "style",
            ".scss": "style",
            ".json": "config",
            ".md": "documentation",
        }

        return extension_map.get(extension, "unknown")

    def _extract_component_name(self, content: str) -> Optional[str]:
        """Extract the main component name from file content."""
        # React component patterns
        patterns = [
            r"export\s+default\s+(\w+)",
            r"export\s+const\s+(\w+)\s*=",
            r"export\s+function\s+(\w+)",
            r"const\s+(\w+)\s*=\s*\(",
            r"function\s+(\w+)\s*\(",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        return None

    def _extract_exports(self, content: str) -> List[str]:
        """Extract all exports from the file."""
        exports = []

        # Export patterns
        patterns = [
            r"export\s+(?:default\s+)?(?:const|let|var|function|class)\s+(\w+)",
            r"export\s+\{\s*([^}]+)\s*\}",
            r'export\s+\*\s+from\s+[\'"][^\'"]+[\'"]',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if "," in match.group(1):
                    # Handle export { a, b, c }
                    names = [name.strip() for name in match.group(1).split(",")]
                    exports.extend(names)
                else:
                    exports.append(match.group(1))

        return exports

    def _extract_imports(self, content: str) -> List[str]:
        """Extract all imports from the file."""
        imports = []

        # Import patterns
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.finditer(import_pattern, content)

        for match in matches:
            imports.append(match.group(1))

        return imports

    def _extract_dependencies(self, content: str) -> Set[str]:
        """Extract dependency names from imports."""
        dependencies = set()

        for import_path in self._extract_imports(content):
            # Extract package name (first part of path)
            if not import_path.startswith("."):
                package = import_path.split("/")[0]
                dependencies.add(package)

        return dependencies

    def _calculate_complexity(self, content: str) -> float:
        """Calculate a complexity score for the file."""
        try:
            tree = ast.parse(content)

            complexity = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                    complexity += 1
                elif isinstance(node, ast.FunctionDef):
                    complexity += 2
                elif isinstance(node, ast.ClassDef):
                    complexity += 3

            return min(complexity / 10.0, 1.0)  # Normalize to 0-1

        except SyntaxError:
            # For non-Python files, use simple heuristics
            lines = content.split("\n")
            complexity_indicators = [
                "if",
                "else",
                "for",
                "while",
                "switch",
                "case",
                "function",
                "const",
                "let",
                "var",
                "class",
                "useState",
                "useEffect",
                "useCallback",
            ]

            score = 0
            for line in lines:
                for indicator in complexity_indicators:
                    if indicator in line:
                        score += 1

            return min(score / 50.0, 1.0)  # Normalize

    def _generate_functionality_signature(self, content: str) -> str:
        """Generate a signature representing the file's functionality."""
        # Extract key functional elements
        functions = re.findall(r"function\s+(\w+)", content)
        hooks = re.findall(r"use\w+", content)
        jsx_elements = re.findall(r"<(\w+)", content)
        state_vars = re.findall(r"useState\s*\(", content)

        signature_parts = []
        signature_parts.extend(f"func:{name}" for name in functions[:5])
        signature_parts.extend(f"hook:{hook}" for hook in set(hooks))
        signature_parts.extend(f"jsx:{elem}" for elem in set(jsx_elements[:10]))
        signature_parts.append(f"state_count:{len(state_vars)}")

        return "|".join(signature_parts)

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate a hash representing the content structure."""
        import hashlib

        # Normalize content by removing whitespace and comments
        normalized = re.sub(r"\s+", " ", content)
        normalized = re.sub(r"//.*?\n", "", normalized)
        normalized = re.sub(r"/\*.*?\*/", "", normalized, flags=re.DOTALL)

        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def _calculate_signature_similarity(
        self, golden: FileAnalysis, generated: FileAnalysis
    ) -> float:
        """Calculate similarity based on component signatures."""
        score = 0.0

        # Component name similarity
        if golden.component_name and generated.component_name:
            name_sim = SequenceMatcher(
                None, golden.component_name, generated.component_name
            ).ratio()
            score += name_sim * 0.3

        # Export similarity
        if golden.exports and generated.exports:
            common_exports = set(golden.exports) & set(generated.exports)
            export_sim = len(common_exports) / max(
                len(golden.exports), len(generated.exports)
            )
            score += export_sim * 0.3

        # Dependency similarity
        if golden.dependencies and generated.dependencies:
            common_deps = golden.dependencies & generated.dependencies
            dep_sim = len(common_deps) / len(
                golden.dependencies | generated.dependencies
            )
            score += dep_sim * 0.2

        # File type match
        if golden.file_type == generated.file_type:
            score += 0.2

        return min(score, 1.0)

    def _calculate_content_similarity(
        self, golden: FileAnalysis, generated: FileAnalysis
    ) -> float:
        """Calculate similarity based on content characteristics."""
        score = 0.0

        # Functionality signature similarity
        func_sim = SequenceMatcher(
            None, golden.functionality_signature, generated.functionality_signature
        ).ratio()
        score += func_sim * 0.4

        # Complexity similarity
        complexity_diff = abs(golden.complexity_score - generated.complexity_score)
        complexity_sim = 1.0 - complexity_diff
        score += complexity_sim * 0.2

        # Import similarity
        if golden.imports and generated.imports:
            common_imports = set(golden.imports) & set(generated.imports)
            import_sim = len(common_imports) / len(
                set(golden.imports) | set(generated.imports)
            )
            score += import_sim * 0.2

        # File type bonus
        if golden.file_type == generated.file_type:
            score += 0.2

        return min(score, 1.0)

    def _get_signature_reasons(
        self, golden: FileAnalysis, generated: FileAnalysis
    ) -> List[str]:
        """Get reasons for signature-based matching."""
        reasons = []

        if golden.component_name == generated.component_name:
            reasons.append("identical_component_name")

        common_exports = set(golden.exports) & set(generated.exports)
        if common_exports:
            reasons.append(f"common_exports: {', '.join(common_exports)}")

        if golden.file_type == generated.file_type:
            reasons.append(f"same_file_type: {golden.file_type}")

        return reasons


class AdaptiveEvaluationStrategy:
    """
    Determines the best evaluation strategy based on file matching results.
    """

    def __init__(self, file_matcher: IntelligentFileMatcher):
        self.file_matcher = file_matcher

    def create_evaluation_plan(
        self, matches: Dict[str, FileMatchResult]
    ) -> Dict[str, str]:
        """
        Create an evaluation plan based on file matching confidence.

        Returns strategy per file: 'direct', 'semantic', 'structural', 'skip'
        """
        plan = {}

        for golden_file, match_result in matches.items():
            if match_result.confidence >= 0.8:
                plan[golden_file] = "direct"
            elif match_result.confidence >= 0.5:
                plan[golden_file] = "semantic"
            elif match_result.confidence >= 0.3:
                plan[golden_file] = "structural"
            else:
                plan[golden_file] = "skip"

        return plan

    def should_evaluate_as_application(
        self, matches: Dict[str, FileMatchResult]
    ) -> bool:
        """
        Determine if the evaluation should proceed as application-level
        or fall back to individual file comparisons.
        """
        if not matches:
            return False

        high_confidence_matches = sum(
            1 for match in matches.values() if match.confidence >= 0.5
        )

        match_ratio = high_confidence_matches / len(matches)
        return match_ratio >= 0.6  # At least 60% good matches
