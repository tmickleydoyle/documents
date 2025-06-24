"""
Universal parser classes for any programming language and application structure.

This module contains the UniversalParser class responsible for parsing
applications in any programming language and extracting their structure.
"""

import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from .config import (
    ALL_SUPPORTED_EXTENSIONS,
    COMMON_DIRECTORY_PATTERNS,
    FUNCTIONALITY_PATTERNS,
    LANGUAGE_PATTERNS,
)
from .exceptions import FileParsingError, UnsupportedFileTypeError
from .models import ApplicationStructure, CodeSample, FileInfo, FunctionalSignature

logger = logging.getLogger(__name__)


class UniversalParser:
    """
    Universal parser for applications in any programming language.

    This class handles the parsing of individual files and entire applications,
    extracting their structure and content for evaluation regardless of language
    or framework.
    """

    def __init__(self):
        """Initialize the parser with universal file support."""
        self.supported_extensions = ALL_SUPPORTED_EXTENSIONS
        self.language_patterns = LANGUAGE_PATTERNS
        self.functionality_patterns = FUNCTIONALITY_PATTERNS
        self.directory_patterns = COMMON_DIRECTORY_PATTERNS

    def parse_file(self, file_path: str) -> Optional[CodeSample]:
        """
        Parse a single file into a CodeSample, regardless of language.

        Args:
            file_path: Path to the file to parse

        Returns:
            CodeSample object or None if parsing fails

        Raises:
            FileParsingError: If the file cannot be parsed
            UnsupportedFileTypeError: If the file type is not supported
        """
        try:
            path = Path(file_path)

            # Check if file extension is supported first (for better error messages)
            if (
                path.suffix not in self.supported_extensions
                and path.suffix != ""
                and path.name not in {"Dockerfile", "Makefile"}
            ):
                raise UnsupportedFileTypeError(file_path, path.suffix)

            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content.strip():
                logger.warning(f"File {file_path} is empty")
                return None

            # Detect language and functionality
            language = self._detect_language(path, content)
            functionality = self._detect_functionality(path, content)
            complexity = self._assess_complexity(content)
            metadata = self._calculate_file_metrics(path, content)

            return CodeSample(
                id=path.name,
                content=content,
                file_path=str(path),
                language=language,
                functionality=functionality,
                complexity=complexity,
                metadata=metadata,
            )

        except FileNotFoundError:
            # Re-raise FileNotFoundError as-is for tests
            raise
        except UnsupportedFileTypeError:
            # Re-raise UnsupportedFileTypeError as-is for tests
            raise
        except (OSError, IOError) as e:
            raise FileParsingError(file_path, e)
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}")
            raise FileParsingError(file_path, e)

    def parse_application(self, app_path: str) -> ApplicationStructure:
        """
        Parse an entire application regardless of language or structure.

        Args:
            app_path: Path to the application root directory

        Returns:
            ApplicationStructure object containing the parsed application

        Raises:
            FileParsingError: If the application cannot be parsed
        """
        try:
            app_path = Path(app_path)

            if not app_path.exists():
                raise FileNotFoundError(f"Application path not found: {app_path}")

            if not app_path.is_dir():
                raise ValueError(f"Application path must be a directory: {app_path}")

            # Initialize structure
            structure = ApplicationStructure(root_path=app_path)

            # Parse all files in the application
            all_files = []
            language_count = defaultdict(int)
            functionality_groups = defaultdict(list)

            # Walk through all files
            for file_path in app_path.rglob("*"):
                if self._should_include_file(file_path):
                    # Read content to analyze
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()

                        # Detect language and functionality
                        language = self._detect_language(file_path, content)
                        functionality = self._detect_functionality(file_path, content)

                        # Calculate file metrics for metadata
                        metadata = self._calculate_file_metrics(file_path, content)
                        metadata.update(
                            {
                                "language": language,
                                "functionality": functionality,
                                "complexity": self._assess_complexity(content),
                            }
                        )

                        # Create FileInfo object with metadata
                        file_info = FileInfo(file_path=file_path, metadata=metadata)
                        all_files.append(file_info)

                        # Update counters
                        language_count[language] += 1
                        functionality_groups[functionality].append(file_info)

                        # Categorize special file types
                        self._categorize_special_files(
                            file_path, content, structure, file_info
                        )

                    except Exception as e:
                        logger.warning(f"Failed to analyze {file_path}: {e}")
                        # Still add the file with minimal metadata including language
                        language = self._detect_language(file_path)
                        file_info = FileInfo(
                            file_path=file_path,
                            metadata={
                                "error": str(e),
                                "language": language,
                                "functionality": "unknown",
                            },
                        )
                        all_files.append(file_info)

            # Populate structure
            structure.all_files = all_files
            structure.language_distribution = dict(language_count)
            structure.functionality_groups = dict(functionality_groups)
            structure.detected_frameworks = self._detect_frameworks(app_path, all_files)
            structure.directory_structure = self._analyze_directory_structure(app_path)

            logger.info(
                f"Parsed {structure.get_primary_language()} application with "
                f"{structure.total_files()} files"
            )
            return structure

        except Exception as e:
            raise FileParsingError(str(app_path), e)

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included in parsing."""
        # Only include actual files, not directories
        if not file_path.is_file():
            return False

        # Skip hidden files and directories (except important ones)
        if any(part.startswith(".") for part in file_path.parts):
            important_hidden = {".env", ".gitignore", ".dockerignore", ".editorconfig"}
            if file_path.name not in important_hidden:
                return False

        # Skip common build/cache directories
        skip_dirs = {
            "node_modules",
            "__pycache__",
            ".git",
            "target",
            "build",
            "dist",
            ".next",
            "venv",
        }
        if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
            return False

        # Check if file extension is supported (include files without extension
        # for config files)
        return (
            file_path.suffix in self.supported_extensions
            or file_path.suffix == ""
            or file_path.name in {"Dockerfile", "Makefile"}
        )

    def _detect_language(self, file_path: Path, content: str) -> str:
        """Detect the programming language of a file."""
        # First, try extension-based detection
        for language, info in self.language_patterns.items():
            if file_path.suffix in info["extensions"]:
                return language

        # Then, try content-based detection
        content_lower = content.lower()

        # Score each language based on keyword matches
        language_scores = {}
        for language, info in self.language_patterns.items():
            score = 0
            for keyword in info["keywords"]:
                if keyword.lower() in content_lower:
                    score += 1
            if score > 0:
                language_scores[language] = score

        # Return the language with the highest score (minimum 1 keyword for
        # content-based)
        if language_scores:
            best_language = max(language_scores.items(), key=lambda x: x[1])
            if best_language[1] >= 1:
                return best_language[0]

        # Default based on file extension
        ext_mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".php": "php",
            ".rb": "ruby",
            ".cpp": "cpp",
            ".c": "c",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
        }

        return ext_mapping.get(file_path.suffix, "unknown")

    def _detect_functionality(self, file_path: Path, content: str) -> str:
        """Detect the functionality category of a file."""
        file_name_lower = file_path.name.lower()
        content_lower = content.lower()
        file_path_str = str(file_path).lower()

        # Check for test files first (high priority)
        test_indicators = ["test", "spec", "mock", "__tests__", ".test.", ".spec."]
        if any(indicator in file_path_str for indicator in test_indicators):
            return "tests"

        # Check patterns in filename and path
        for functionality, info in self.functionality_patterns.items():
            # Check filename patterns
            for pattern in info["patterns"]:
                if re.search(pattern, file_path_str, re.IGNORECASE):
                    return functionality

            # Check keywords in filename
            if any(keyword in file_name_lower for keyword in info["keywords"]):
                return functionality

            # Check keywords in content (for more specific detection)
            keyword_count = sum(
                1 for keyword in info["keywords"] if keyword in content_lower
            )
            if keyword_count >= 2:
                return functionality

        # Default categorization based on file location
        path_parts = [part.lower() for part in file_path.parts]

        if any(part in ["test", "tests", "spec", "specs"] for part in path_parts):
            return "tests"
        elif any(part in ["config", "settings", "env"] for part in path_parts):
            return "configuration"
        elif any(part in ["style", "css", "scss", "sass"] for part in path_parts):
            return "styling"
        elif any(part in ["api", "routes", "controllers"] for part in path_parts):
            return "api_routes"
        elif any(part in ["component", "components", "widgets"] for part in path_parts):
            return "ui_components"
        elif any(part in ["util", "utils", "helpers", "lib"] for part in path_parts):
            return "utilities"
        elif any(
            part in ["model", "models", "schema", "database"] for part in path_parts
        ):
            return "database"

        return "general"

    def _assess_complexity(self, content: str) -> str:
        """Assess the complexity level of code content."""
        lines = content.split("\n")
        line_count = len([line for line in lines if line.strip()])

        # Count various complexity indicators
        nesting_indicators = (
            content.count("{")
            + content.count("if ")
            + content.count("for ")
            + content.count("while ")
        )
        function_indicators = (
            content.count("def ") + content.count("function ") + content.count("class ")
        )

        complexity_score = (
            line_count * 0.1 + nesting_indicators * 2 + function_indicators * 1.5
        )

        if complexity_score < 2:
            return "simple"
        elif complexity_score < 12:
            return "moderate"
        else:
            return "complex"

    def _calculate_file_metrics(self, file_path: Path, content: str) -> Dict[str, any]:
        """Calculate various metrics for a file."""
        lines = content.split("\n")

        return {
            "file_size": len(content),
            "line_count": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": len(
                [
                    line
                    for line in lines
                    if line.strip().startswith(("#", "//", "/*", "*"))
                ]
            ),
            "extension": file_path.suffix,
            "directory": str(file_path.parent),
        }

    def _categorize_special_files(
        self,
        file_path: Path,
        content: str,
        structure: ApplicationStructure,
        file_info: FileInfo,
    ) -> None:
        """Categorize files into special categories."""
        file_name = file_path.name.lower()

        # Entry points
        if file_name in [
            "main.py",
            "app.py",
            "index.js",
            "main.js",
            "main.go",
            "main.java",
            "program.cs",
        ]:
            structure.entry_points.append(file_info)

        # Configuration files
        config_patterns = [
            "config",
            ".env",
            "setting",
            "properties",
            ".yml",
            ".yaml",
            ".json",
            ".toml",
        ]
        if any(pattern in file_name for pattern in config_patterns):
            structure.configuration_files.append(file_info)
            structure.config_files.append(file_path)  # Backward compatibility

        # Build files
        build_patterns = [
            "dockerfile",
            "makefile",
            "build.",
            "pom.xml",
            "package.json",
            "requirements.txt",
            "cargo.toml",
        ]
        if any(pattern in file_name for pattern in build_patterns):
            structure.build_files.append(file_info)

            # Special handling for package.json
            if file_name == "package.json":
                structure.package_json = str(file_path)

        # Test files
        test_patterns = ["test", "spec", "mock"]
        if any(pattern in file_name for pattern in test_patterns):
            structure.test_files.append(file_info)

        # Backward compatibility categorization based on directory structure
        path_str = str(file_path).lower()
        if "/component" in path_str or "/components" in path_str:
            structure.components.append(file_path)
        elif "/page" in path_str or "/pages" in path_str:
            structure.pages.append(file_path)
        elif "/api" in path_str or "/routes" in path_str:
            structure.api_routes.append(file_path)
        elif "/style" in path_str or "/css" in path_str or "/scss" in path_str:
            structure.styles.append(file_path)
        elif "/util" in path_str or "/utils" in path_str or "/helper" in path_str:
            structure.utils.append(file_path)
        elif "/hook" in path_str or "/hooks" in path_str:
            structure.hooks.append(file_path)
        elif "/lib" in path_str:
            structure.lib.append(file_path)

    def _detect_frameworks(
        self, app_path: Path, all_files: List[FileInfo]
    ) -> List[str]:
        """Detect frameworks and libraries used in the application."""
        frameworks = []

        # Check for framework-specific files and patterns
        framework_indicators = {
            "react": ["package.json", "jsx", "tsx", "react"],
            "nextjs": ["next.config.js", "pages/", "_app.js"],
            "vue": ["vue.config.js", ".vue", "vuejs"],
            "angular": ["angular.json", ".component.ts", "@angular"],
            "django": ["manage.py", "settings.py", "django"],
            "flask": ["app.py", "flask"],
            "express": ["express", "package.json"],
            "spring": ["pom.xml", "@SpringBootApplication", "spring"],
            "rails": ["Gemfile", "config/routes.rb", "rails"],
            "laravel": ["artisan", "composer.json", "laravel"],
        }

        for framework, indicators in framework_indicators.items():
            for indicator in indicators:
                # Check for specific files
                if (app_path / indicator).exists():
                    frameworks.append(framework)
                    break

                # Check for patterns in file paths or content
                for file_info in all_files:
                    if indicator in str(file_info.file_path).lower():
                        frameworks.append(framework)
                        break

        return list(set(frameworks))  # Remove duplicates

    def _analyze_directory_structure(self, app_path: Path) -> Dict[str, any]:
        """Analyze the directory structure of the application."""
        structure = {}

        for root, dirs, files in app_path.walk():
            relative_path = root.relative_to(app_path)

            # Skip hidden and build directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in {"node_modules", "__pycache__", "target", "build"}
            ]

            structure[str(relative_path)] = {
                "directories": dirs,
                "files": files,
                "file_count": len(files),
            }

        return structure

    def create_functional_signature(self, file_path: str) -> FunctionalSignature:
        """Create a functional signature for intelligent file matching."""
        try:
            code_sample = self.parse_file(file_path)
            if not code_sample:
                return FunctionalSignature(
                    language="unknown", functionality_category="unknown"
                )

            content = code_sample.content
            language = code_sample.language
            functionality = code_sample.functionality

            # Extract various code elements
            exports = self._extract_exports(content, language)
            imports = self._extract_imports(content, language)
            functions = self._extract_functions(content, language)
            classes = self._extract_classes(content, language)
            keywords = self._extract_keywords(content)
            api_endpoints = self._extract_api_endpoints(content)
            ui_elements = self._extract_ui_elements(content)

            return FunctionalSignature(
                language=language,
                functionality_category=functionality,
                exports=exports,
                imports=imports,
                functions=functions,
                classes=classes,
                keywords=keywords,
                api_endpoints=api_endpoints,
                ui_elements=ui_elements,
            )

        except Exception as e:
            logger.warning(
                f"Failed to create functional signature for {file_path}: {e}"
            )
            return FunctionalSignature(
                language="unknown", functionality_category="unknown"
            )

    def _extract_exports(self, content: str, language: str) -> List[str]:
        """Extract exported symbols from code."""
        exports = []

        patterns = {
            "javascript": [
                r"export\s+(?:default\s+)?(?:function\s+)?(\w+)",
                r"module\.exports\s*=\s*(\w+)",
            ],
            "typescript": [
                r"export\s+(?:default\s+)?(?:function\s+|class\s+|interface\s+)?(\w+)"
            ],
            "python": [r"def\s+(\w+)", r"class\s+(\w+)"],
            "java": [r"public\s+(?:static\s+)?(?:class\s+|interface\s+)(\w+)"],
            "csharp": [r"public\s+(?:static\s+)?(?:class\s+|interface\s+)(\w+)"],
        }

        for pattern in patterns.get(language, []):
            exports.extend(re.findall(pattern, content, re.IGNORECASE))

        return list(set(exports))

    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract imported modules/packages from code."""
        imports = []

        patterns = {
            "javascript": [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'require\([\'"]([^\'"]+)[\'"]\)',
            ],
            "typescript": [r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'],
            "python": [r"import\s+(\w+)", r"from\s+(\w+)\s+import"],
            "java": [r"import\s+([\w.]+)"],
            "csharp": [r"using\s+([\w.]+)"],
            "go": [r'import\s+[\'"]([^\'"]+)[\'"]'],
        }

        for pattern in patterns.get(language, []):
            imports.extend(re.findall(pattern, content, re.IGNORECASE))

        return list(set(imports))

    def _extract_functions(self, content: str, language: str) -> List[str]:
        """Extract function names from code."""
        functions = []

        patterns = {
            "javascript": [
                r"function\s+(\w+)",
                r"(\w+)\s*:\s*function",
                r"const\s+(\w+)\s*=\s*\(",
            ],
            "typescript": [r"function\s+(\w+)", r"(\w+)\s*\(.*?\)\s*:\s*\w+"],
            "python": [r"def\s+(\w+)"],
            "java": [
                r"(?:public|private|protected)?\s*(?:static\s+)?[\w<>]+\s+(\w+)\s*\("
            ],
            "csharp": [
                r"(?:public|private|protected)?\s*(?:static\s+)?[\w<>]+\s+(\w+)\s*\("
            ],
            "go": [r"func\s+(\w+)"],
            "rust": [r"fn\s+(\w+)"],
        }

        for pattern in patterns.get(language, []):
            functions.extend(re.findall(pattern, content, re.IGNORECASE))

        return list(set(functions))

    def _extract_classes(self, content: str, language: str) -> List[str]:
        """Extract class names from code."""
        classes = []

        patterns = {
            "javascript": [r"class\s+(\w+)"],
            "typescript": [r"class\s+(\w+)", r"interface\s+(\w+)"],
            "python": [r"class\s+(\w+)"],
            "java": [
                r"(?:public\s+)?class\s+(\w+)",
                r"(?:public\s+)?interface\s+(\w+)",
            ],
            "csharp": [
                r"(?:public\s+)?class\s+(\w+)",
                r"(?:public\s+)?interface\s+(\w+)",
            ],
            "cpp": [r"class\s+(\w+)", r"struct\s+(\w+)"],
            "rust": [r"struct\s+(\w+)", r"impl\s+(\w+)"],
        }

        for pattern in patterns.get(language, []):
            classes.extend(re.findall(pattern, content, re.IGNORECASE))

        return list(set(classes))

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords and identifiers from code."""
        # Common programming keywords and domain-specific terms
        important_terms = []

        # Look for API-related terms
        api_terms = re.findall(
            r"\b(api|endpoint|route|controller|service|handler)\b",
            content,
            re.IGNORECASE,
        )
        important_terms.extend(api_terms)

        # Look for UI-related terms
        ui_terms = re.findall(
            r"\b(component|widget|view|page|screen|button|form|input)\b",
            content,
            re.IGNORECASE,
        )
        important_terms.extend(ui_terms)

        # Look for data-related terms
        data_terms = re.findall(
            r"\b(model|schema|database|table|query|data)\b", content, re.IGNORECASE
        )
        important_terms.extend(data_terms)

        return list(set(important_terms))

    def _extract_api_endpoints(self, content: str) -> List[str]:
        """Extract API endpoints from code."""
        endpoints = []

        # Common API endpoint patterns
        patterns = [
            r'[\'"][/][\w/]+[\'"]',  # "/api/users", "/auth/login"
            r'@app\.route\([\'"]([^\'"]+)[\'"]',  # Flask routes
            r'@RequestMapping\([\'"]([^\'"]+)[\'"]',  # Spring routes
            r'app\.[get|post|put|delete]+\([\'"]([^\'"]+)[\'"]',  # Express routes
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            endpoints.extend(matches)

        return list(set(endpoints))

    def _extract_ui_elements(self, content: str) -> List[str]:
        """Extract UI elements from code."""
        elements = []

        # HTML/JSX elements
        html_elements = re.findall(r"<(\w+)", content)
        elements.extend(html_elements)

        # React/Vue component names
        component_elements = re.findall(r"<([A-Z]\w+)", content)
        elements.extend(component_elements)

        return list(set(elements))
