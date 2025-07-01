"""
Configuration and constants for the Universal Code Evaluation Framework.
Supports any programming language and application structure.
"""

from typing import Dict, Set

# Model configuration
DEFAULT_EMBEDDING_MODEL = "microsoft/unixcoder-base"
FALLBACK_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Universal file extensions - organized by language families
SUPPORTED_CODE_EXTENSIONS: Dict[str, Set[str]] = {
    "web_frontend": {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".html", ".htm"},
    "web_backend": {".js", ".ts", ".php", ".rb", ".py", ".go", ".java", ".cs", ".fs"},
    "mobile": {".swift", ".kt", ".java", ".dart", ".m", ".mm"},
    "desktop": {
        ".cpp",
        ".cc",
        ".cxx",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".java",
        ".py",
        ".rs",
    },
    "data_science": {".py", ".r", ".R", ".ipynb", ".sql", ".scala", ".jl"},
    "markup": {".html", ".htm", ".xml", ".md", ".rst", ".tex"},
    "styles": {".css", ".scss", ".sass", ".less", ".styl", ".module.css"},
    "config": {".json", ".yml", ".yaml", ".toml", ".ini", ".env", ".config", ".conf"},
    "build": {".gradle", ".maven", ".cmake", ".make", ".dockerfile", ".build"},
    "shell": {".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd"},
}

# Flatten all supported extensions
ALL_SUPPORTED_EXTENSIONS = set()
for extensions in SUPPORTED_CODE_EXTENSIONS.values():
    ALL_SUPPORTED_EXTENSIONS.update(extensions)

# Evaluation weights
DEFAULT_EVALUATION_WEIGHTS: Dict[str, float] = {
    "semantic": 0.80,
    "functional": 0.08,
    "structural": 0.05,
    "style": 0.03,
    "maintainability": 0.025,
    "accessibility": 0.015,
}

# Quality-focused weights that reward architectural improvements
QUALITY_FOCUSED_WEIGHTS: Dict[str, float] = {
    "semantic": 0.50,
    "functional": 0.125,
    "structural": 0.085,
    "style": 0.105,
    "maintainability": 0.125,
    "accessibility": 0.06,
}

# Complexity thresholds
COMPLEXITY_THRESHOLDS = {
    "simple": {"lines": 50, "complexity_score": 5},
    "moderate": {"lines": 200, "complexity_score": 15},
}

# Performance and quality thresholds
QUALITY_THRESHOLDS = {
    "min_similarity_score": 0.0,
    "max_similarity_score": 1.0,
    "performance_penalty_per_antipattern": 0.2,
    "security_penalty_per_issue": 0.3,
}

# Language detection patterns
LANGUAGE_PATTERNS: Dict[str, Dict[str, str]] = {
    "python": {
        "extensions": {".py"},
        "keywords": ["def ", "class ", "import ", "from "],
    },
    "javascript": {
        "extensions": {".js", ".jsx"},
        "keywords": ["function", "const ", "let ", "var "],
    },
    "typescript": {
        "extensions": {".ts", ".tsx"},
        "keywords": ["interface", "type ", "enum ", "export "],
    },
    "java": {
        "extensions": {".java"},
        "keywords": ["public class", "private ", "public ", "static "],
    },
    "csharp": {
        "extensions": {".cs"},
        "keywords": ["using ", "namespace ", "public class", "private "],
    },
    "go": {
        "extensions": {".go"},
        "keywords": ["package ", "func ", "import ", "type "],
    },
    "rust": {"extensions": {".rs"}, "keywords": ["fn ", "pub ", "struct ", "impl "]},
    "swift": {
        "extensions": {".swift"},
        "keywords": ["func ", "class ", "struct ", "import "],
    },
    "kotlin": {"extensions": {".kt"}, "keywords": ["fun ", "class ", "val ", "var "]},
    "php": {"extensions": {".php"}, "keywords": ["<?php", "function ", "class ", "$"]},
    "ruby": {
        "extensions": {".rb"},
        "keywords": ["def ", "class ", "module ", "require ", "puts "],
    },
    "cpp": {
        "extensions": {".cpp", ".cc", ".cxx"},
        "keywords": ["#include", "class ", "namespace ", "using "],
    },
    "c": {
        "extensions": {".c", ".h"},
        "keywords": ["#include", "int main", "void ", "struct "],
    },
    "sql": {"extensions": {".sql"}, "keywords": ["SELECT", "FROM", "WHERE", "INSERT"]},
    "html": {
        "extensions": {".html", ".htm"},
        "keywords": ["<html", "<div", "<body", "<head"],
    },
    "css": {
        "extensions": {".css"},
        "keywords": [
            "@media",
            "font-family",
            "background",
            "border",
            "margin",
            "padding",
        ],
    },
}

# Functionality-based file categorization patterns
FUNCTIONALITY_PATTERNS: Dict[str, Dict[str, list]] = {
    "authentication": {
        "keywords": [
            "login",
            "auth",
            "signin",
            "signup",
            "password",
            "token",
            "jwt",
            "session",
        ],
        "patterns": ["login.*", "auth.*", "signin.*", "signup.*", ".*auth.*"],
    },
    "api_routes": {
        "keywords": ["api", "route", "endpoint", "handler", "controller", "service"],
        "patterns": [".*api.*", ".*route.*", ".*controller.*", ".*service.*"],
    },
    "database": {
        "keywords": ["model", "schema", "migration", "query", "database", "db", "sql"],
        "patterns": [".*model.*", ".*schema.*", ".*migration.*", ".*db.*"],
    },
    "ui_components": {
        "keywords": [
            "component",
            "widget",
            "view",
            "page",
            "screen",
            "layout",
            "button",
        ],
        "patterns": [
            ".*component.*",
            ".*widget.*",
            ".*view.*",
            ".*page.*",
            ".*screen.*",
        ],
    },
    "utilities": {
        "keywords": ["util", "helper", "lib", "common", "shared", "config"],
        "patterns": [".*util.*", ".*helper.*", ".*lib.*", ".*common.*", ".*shared.*"],
    },
    "tests": {
        "keywords": ["test", "spec", "mock", "fixture", "unit", "integration"],
        "patterns": [".*test.*", ".*spec.*", ".*mock.*", "test_.*", ".*_test.*"],
    },
    "configuration": {
        "keywords": ["config", "setting", "env", "environment", "setup"],
        "patterns": [".*config.*", ".*setting.*", ".*env.*", ".*setup.*"],
    },
    "styling": {
        "keywords": ["style", "css", "theme", "design", "ui"],
        "patterns": [".*style.*", ".*css.*", ".*theme.*", ".*design.*"],
    },
}

# Universal project structure patterns
COMMON_DIRECTORY_PATTERNS: Dict[str, list] = {
    "source_code": ["src", "lib", "app", "source", "code"],
    "tests": ["test", "tests", "__tests__", "spec", "specs"],
    "documentation": ["docs", "doc", "documentation", "readme"],
    "configuration": ["config", "configs", "settings", "env"],
    "assets": ["assets", "static", "public", "resources", "media"],
    "build": ["build", "dist", "out", "target", "bin"],
    "dependencies": ["node_modules", "vendor", "packages", "deps"],
    "scripts": ["scripts", "tools", "bin", "utils"],
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "fern_evaluator": {"handlers": ["default"], "level": "INFO", "propagate": False}
    },
}
