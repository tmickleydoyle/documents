"""
Utility functions for the Fern Model Evaluation Framework.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List

from .config import COMPLEXITY_THRESHOLDS

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration for the framework.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def extract_imports(code: str) -> List[str]:
    """
    Extract import statements from JavaScript/TypeScript code.

    Args:
        code: Source code string

    Returns:
        List of imported module names
    """
    import_pattern = r'import.*?from\s+["\']([^"\']+)["\']'
    return re.findall(import_pattern, code)


def extract_function_names(code: str) -> List[str]:
    """
    Extract function and component names from JavaScript/TypeScript code.

    Args:
        code: Source code string

    Returns:
        List of function/component names
    """
    patterns = [
        r"function\s+(\w+)",  # function declarations
        r"const\s+(\w+)\s*=\s*(?:\([^)]*\)\s*=>|\([^)]*\)\s*:\s*\w+\s*=>)",
        # arrow functions
        r"const\s+(\w+):\s*React\.FC",  # React functional components
    ]

    names = []
    for pattern in patterns:
        names.extend(re.findall(pattern, code))

    return list(set(names))  # Remove duplicates


def extract_jsx_elements(code: str) -> List[str]:
    """
    Extract JSX element names from React code.

    Args:
        code: Source code string

    Returns:
        List of JSX element names
    """
    jsx_pattern = r"<(\w+)"
    return list(set(re.findall(jsx_pattern, code)))


def extract_hooks(code: str) -> List[str]:
    """
    Extract React hooks usage from code.

    Args:
        code: Source code string

    Returns:
        List of hook names
    """
    hook_pattern = r"(use[A-Z]\w*)"
    return list(set(re.findall(hook_pattern, code)))


def calculate_complexity_score(code: str) -> float:
    """
    Calculate a complexity score for a piece of code.

    Args:
        code: Source code string

    Returns:
        Complexity score as a float
    """
    factors = {
        "lines": len(code.split("\n")) * 0.1,
        "functions": len(extract_function_names(code)) * 2,
        "conditionals": len(re.findall(r"if|switch|\?", code)) * 1.5,
        "loops": len(re.findall(r"for|while|map|forEach", code)) * 2,
        "async": len(re.findall(r"async|await|Promise", code)) * 1.5,
        "hooks": len(extract_hooks(code)) * 1.2,
    }

    return sum(factors.values())


def assess_complexity_level(code: str) -> str:
    """
    Assess the complexity level of code as simple, moderate, or complex.

    Args:
        code: Source code string

    Returns:
        Complexity level ('simple', 'moderate', 'complex')
    """
    lines = len(code.split("\n"))
    complexity_score = calculate_complexity_score(code)

    simple_thresholds = COMPLEXITY_THRESHOLDS["simple"]
    moderate_thresholds = COMPLEXITY_THRESHOLDS["moderate"]

    if (
        lines < simple_thresholds["lines"]
        and complexity_score < simple_thresholds["complexity_score"]
    ):
        return "simple"
    elif (
        lines < moderate_thresholds["lines"]
        and complexity_score < moderate_thresholds["complexity_score"]
    ):
        return "moderate"
    else:
        return "complex"


def determine_file_category(file_path: str, content: str) -> str:
    """
    Determine the category of a code file based on its path and content.

    Args:
        file_path: Path to the file
        content: File content

    Returns:
        Category string
    """
    file_name = Path(file_path).name.lower()

    # Page components
    if "pages/" in file_path or "_app." in file_name or "_document." in file_name:
        return "pages"

    # Category keywords mapping
    category_keywords = {
        "forms": ["form", "input", "validation", "submit"],
        "navigation": ["nav", "menu", "router", "link"],
        "data-display": ["table", "list", "card", "grid"],
        "interactive": ["modal", "dropdown", "accordion", "tooltip"],
        "state-management": ["usestate", "useeffect", "usereducer", "context"],
        "styling": ["styled", "css", "theme", "style"],
        "api": ["api", "fetch", "axios", "request"],
        "auth": ["auth", "login", "signin", "signup", "logout"],
    }

    content_lower = content.lower()

    for category, keywords in category_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            return category

    return "general"


def preprocess_code_for_analysis(code: str) -> str:
    """
    Preprocess code for better semantic analysis.

    Args:
        code: Raw source code

    Returns:
        Preprocessed code string
    """
    # Remove comments
    code = re.sub(r"//.*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)

    # Normalize whitespace
    code = re.sub(r"\s+", " ", code)

    # Extract and combine key components
    components = []

    # Extract imports
    imports = extract_imports(code)
    components.extend([f"import {imp}" for imp in imports])

    # Extract function/component names
    functions = extract_function_names(code)
    components.extend([f"function {func}" for func in functions])

    # Extract hooks usage
    hooks = extract_hooks(code)
    components.extend([f"hook {hook}" for hook in hooks])

    # Extract JSX elements
    jsx_elements = extract_jsx_elements(code)
    components.extend([f"element {elem}" for elem in jsx_elements])

    # Combine processed components with truncated original code
    processed = " ".join(components)
    truncated_original = code[:500] if len(code) > 500 else code

    return f"{processed} {truncated_original}"


def detect_language_from_content(content: str, file_extension: str = None) -> str:
    """
    Detect programming language from code content and file extension.

    Args:
        content: Source code string
        file_extension: File extension (e.g., '.py', '.js')

    Returns:
        Detected language name
    """
    from .config import LANGUAGE_PATTERNS

    content_lower = content.lower()

    # First, try extension-based detection
    if file_extension:
        for language, info in LANGUAGE_PATTERNS.items():
            if file_extension in info["extensions"]:
                return language

    # Then, try content-based detection
    best_match = "unknown"
    max_matches = 0

    for language, info in LANGUAGE_PATTERNS.items():
        keyword_count = sum(
            1 for keyword in info["keywords"] if keyword.lower() in content_lower
        )
        if keyword_count > max_matches:
            max_matches = keyword_count
            best_match = language

    return best_match if max_matches >= 2 else "unknown"


def categorize_by_functionality(file_path: str, content: str) -> str:
    """
    Categorize a file by its functionality based on path and content.

    Args:
        file_path: Path to the file
        content: File content

    Returns:
        Functionality category
    """
    import re

    from .config import FUNCTIONALITY_PATTERNS

    file_path_lower = file_path.lower()
    content_lower = content.lower()

    # Check patterns in filename and path
    for functionality, info in FUNCTIONALITY_PATTERNS.items():
        # Check filename patterns
        for pattern in info["patterns"]:
            if re.search(pattern, file_path_lower, re.IGNORECASE):
                return functionality

        # Check keywords in filename
        if any(keyword in file_path_lower for keyword in info["keywords"]):
            return functionality

        # Check keywords in content
        keyword_count = sum(
            1 for keyword in info["keywords"] if keyword in content_lower
        )
        if keyword_count >= 2:
            return functionality

    # Default categorization based on file location
    path_parts = [part.lower() for part in Path(file_path).parts]

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
    elif any(part in ["model", "models", "schema", "database"] for part in path_parts):
        return "database"

    return "general"


def calculate_file_metrics(file_path: str, content: str) -> Dict[str, Any]:
    """
    Calculate various metrics for a file.

    Args:
        file_path: Path to the file
        content: File content

    Returns:
        Dictionary containing file metrics
    """
    path = Path(file_path)
    lines = content.split("\n")

    return {
        "file_size": len(content),
        "line_count": len(lines),
        "non_empty_lines": len([line for line in lines if line.strip()]),
        "comment_lines": len(
            [line for line in lines if line.strip().startswith(("#", "//", "/*", "*"))]
        ),
        "extension": path.suffix,
        "directory": str(path.parent),
        "language": detect_language_from_content(content, path.suffix),
        "functionality": categorize_by_functionality(file_path, content),
        "complexity": assess_complexity_level(content),
    }


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning a default value if denominator is zero.

    Args:
        numerator: The numerator
        denominator: The denominator
        default: Default value to return if denominator is zero

    Returns:
        Result of division or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    """
    Clamp a value between min and max bounds.

    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_value, min(max_value, value))


def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
    """
    Validate and return a Path object for a file path.

    Args:
        file_path: String path to validate
        must_exist: Whether the file must exist

    Returns:
        Validated Path object

    Raises:
        FileNotFoundError: If must_exist is True and file doesn't exist
        ValueError: If path is invalid
    """
    if not file_path or not isinstance(file_path, str):
        raise ValueError("File path must be a non-empty string")

    path = Path(file_path)

    if must_exist and not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path
