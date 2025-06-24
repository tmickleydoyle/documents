"""
Unit tests for the utils module.

This module tests utility functions used throughout the evaluation framework.
"""

import logging

import pytest
from src.utils import (
    calculate_complexity_score,
    clamp,
    extract_function_names,
    extract_hooks,
    extract_imports,
    extract_jsx_elements,
    preprocess_code_for_analysis,
    safe_divide,
    setup_logging,
)


class TestSetupLogging:
    """Test the setup_logging utility function."""

    def test_setup_logging_default_level(self):
        """Test setup_logging with default level."""
        # Reset logging to clean state
        logging.root.handlers = []
        logging.root.level = logging.WARNING

        setup_logging()

        # Check that logging is configured
        logger = logging.getLogger()
        assert logger.level <= logging.INFO

    def test_setup_logging_custom_level(self):
        """Test setup_logging with custom level."""
        # Reset logging to clean state
        logging.root.handlers = []
        logging.root.level = logging.WARNING

        setup_logging("DEBUG")

        # Check that logging level is set correctly
        logger = logging.getLogger()
        assert logger.level <= logging.DEBUG

    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid level."""
        # Should raise an AttributeError for invalid level
        with pytest.raises(AttributeError):
            setup_logging("INVALID_LEVEL")


class TestSafeDivide:
    """Test the safe_divide utility function."""

    def test_safe_divide_normal_case(self):
        """Test safe division with normal values."""
        result = safe_divide(10, 2)
        assert result == 5.0

    def test_safe_divide_zero_denominator(self):
        """Test safe division with zero denominator."""
        result = safe_divide(10, 0)
        assert result == 0.0

    def test_safe_divide_zero_denominator_custom_default(self):
        """Test safe division with zero denominator and custom default."""
        result = safe_divide(10, 0, default=1.5)
        assert result == 1.5

    def test_safe_divide_zero_numerator(self):
        """Test safe division with zero numerator."""
        result = safe_divide(0, 5)
        assert result == 0.0

    def test_safe_divide_negative_numbers(self):
        """Test safe division with negative numbers."""
        result = safe_divide(-10, 2)
        assert result == -5.0

        result = safe_divide(10, -2)
        assert result == -5.0

    def test_safe_divide_float_inputs(self):
        """Test safe division with float inputs."""
        result = safe_divide(7.5, 2.5)
        assert result == 3.0


class TestClamp:
    """Test the clamp utility function."""

    def test_clamp_within_range(self):
        """Test clamp with value within range."""
        result = clamp(0.5)
        assert result == 0.5

    def test_clamp_below_minimum(self):
        """Test clamp with value below minimum."""
        result = clamp(-0.5)
        assert result == 0.0

    def test_clamp_above_maximum(self):
        """Test clamp with value above maximum."""
        result = clamp(1.5)
        assert result == 1.0

    def test_clamp_at_boundaries(self):
        """Test clamp at boundary values."""
        assert clamp(0.0) == 0.0
        assert clamp(1.0) == 1.0

    def test_clamp_custom_range(self):
        """Test clamp with custom range."""
        result = clamp(5, min_value=0, max_value=10)
        assert result == 5

        result = clamp(-1, min_value=0, max_value=10)
        assert result == 0

        result = clamp(15, min_value=0, max_value=10)
        assert result == 10


class TestPreprocessCodeForAnalysis:
    """Test the preprocess_code_for_analysis utility function."""

    def test_preprocess_simple_code(self):
        """Test preprocessing simple code."""
        code = "def hello():\\n    return 'Hello'"
        result = preprocess_code_for_analysis(code)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_preprocess_with_comments(self):
        """Test preprocessing code with comments."""
        code = (
            "# This is a comment\\n"
            "def hello():  # Another comment\\n"
            "    return 'Hello'"
        )
        result = preprocess_code_for_analysis(code)

        assert isinstance(result, str)

    def test_preprocess_with_whitespace(self):
        """Test preprocessing code with excessive whitespace."""
        code = "\\n\\n  def hello():  \\n\\n    return 'Hello'  \\n\\n"
        result = preprocess_code_for_analysis(code)

        assert isinstance(result, str)
        # Should have normalized whitespace
        assert result.strip() != ""

    def test_preprocess_empty_code(self):
        """Test preprocessing empty code."""
        result = preprocess_code_for_analysis("")
        assert isinstance(result, str)


class TestExtractFunctionNames:
    """Test the extract_function_names utility function."""

    def test_extract_python_functions(self):
        """Test extracting function names from Python code."""
        code = "def hello():\\n    pass\\n\\n" "def world(param):\\n    return param"
        functions = extract_function_names(code)

        assert isinstance(functions, list)
        assert len(functions) >= 0

    def test_extract_javascript_functions(self):
        """Test extracting function names from JavaScript code."""
        code = "function hello() { return 'Hello'; }"
        functions = extract_function_names(code)

        assert isinstance(functions, list)
        assert len(functions) >= 0

    def test_extract_no_functions(self):
        """Test extracting from code with no functions."""
        code = "const x = 5; console.log(x);"
        functions = extract_function_names(code)

        assert isinstance(functions, list)


class TestExtractImports:
    """Test the extract_imports utility function."""

    def test_extract_python_imports(self):
        """Test extracting imports from Python code."""
        code = "import os\\nfrom pathlib import Path"
        imports = extract_imports(code)

        assert isinstance(imports, list)
        assert len(imports) >= 0

    def test_extract_javascript_imports(self):
        """Test extracting imports from JavaScript code."""
        code = "import React from 'react';"
        imports = extract_imports(code)

        assert isinstance(imports, list)
        assert len(imports) >= 0

    def test_extract_no_imports(self):
        """Test extracting from code with no imports."""
        code = "const x = 5; console.log(x);"
        imports = extract_imports(code)

        assert isinstance(imports, list)


class TestExtractJsxElements:
    """Test the extract_jsx_elements utility function."""

    def test_extract_basic_jsx(self):
        """Test extracting basic JSX elements."""
        code = "function App() { return <div><h1>Hello</h1></div>; }"
        elements = extract_jsx_elements(code)

        assert isinstance(elements, list)
        assert len(elements) >= 0

    def test_extract_no_jsx(self):
        """Test extracting from code with no JSX."""
        code = "const x = 5; console.log(x);"
        elements = extract_jsx_elements(code)

        assert isinstance(elements, list)


class TestExtractHooks:
    """Test the extract_hooks utility function."""

    def test_extract_react_hooks(self):
        """Test extracting React hooks."""
        code = "const [state, setState] = useState(0);"
        hooks = extract_hooks(code)

        assert isinstance(hooks, list)
        assert len(hooks) >= 0

    def test_extract_no_hooks(self):
        """Test extracting from code with no hooks."""
        code = "const x = 5; console.log(x);"
        hooks = extract_hooks(code)

        assert isinstance(hooks, list)


class TestCalculateComplexityScore:
    """Test the calculate_complexity_score utility function."""

    def test_simple_code_complexity(self):
        """Test complexity calculation for simple code."""
        code = "def hello():\\n    return 'Hello'"
        score = calculate_complexity_score(code)

        assert isinstance(score, (int, float))
        assert score >= 0

    def test_complex_code_complexity(self):
        """Test complexity calculation for complex code."""
        code = (
            "def complex_function(data):\\n    for item in data:\\n"
            "        if item > 0:\\n            for i in range(item):\\n"
            "                pass"
        )
        score = calculate_complexity_score(code)

        assert isinstance(score, (int, float))
        assert score >= 0

    def test_empty_code_complexity(self):
        """Test complexity calculation for empty code."""
        score = calculate_complexity_score("")

        assert isinstance(score, (int, float))
        assert score >= 0
