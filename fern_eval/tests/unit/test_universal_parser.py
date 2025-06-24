"""
Unit tests for the UniversalParser class.

These tests verify the core functionality of the universal parser
with simple, isolated test cases that a junior engineer can understand.
"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from src.exceptions import UnsupportedFileTypeError
from src.universal_parser import UniversalParser


class TestUniversalParser:
    """Test suite for UniversalParser class."""

    def test_init(self):
        """Test parser initialization."""
        parser = UniversalParser()
        assert parser.supported_extensions is not None
        assert parser.language_patterns is not None
        assert parser.functionality_patterns is not None

    def test_detect_language_python(self):
        """Test Python language detection."""
        parser = UniversalParser()
        file_path = Path("test.py")
        content = "def hello():\n    print('Hello, world!')"

        language = parser._detect_language(file_path, content)
        assert language == "python"

    def test_detect_language_javascript(self):
        """Test JavaScript language detection."""
        parser = UniversalParser()
        file_path = Path("test.js")
        content = "function hello() {\n    console.log('Hello, world!');\n}"

        language = parser._detect_language(file_path, content)
        assert language == "javascript"

    def test_detect_language_typescript(self):
        """Test TypeScript language detection."""
        parser = UniversalParser()
        file_path = Path("test.tsx")
        content = (
            "interface Props {\n  name: string;\n}\n"
            "const Component: React.FC<Props> = ({ name }) => "
            "<div>{name}</div>;"
        )

        language = parser._detect_language(file_path, content)
        assert language == "typescript"

    def test_detect_language_unknown(self):
        """Test unknown language detection fallback."""
        parser = UniversalParser()
        file_path = Path("test.unknown")
        content = "some random content"

        language = parser._detect_language(file_path, content)
        assert language == "unknown"

    def test_detect_functionality_ui_components(self):
        """Test UI components functionality detection."""
        parser = UniversalParser()
        file_path = Path("components/Button.tsx")
        content = "const Button = () => <button>Click me</button>;"

        functionality = parser._detect_functionality(file_path, content)
        assert functionality == "ui_components"

    def test_detect_functionality_api_routes(self):
        """Test API routes functionality detection."""
        parser = UniversalParser()
        file_path = Path("api/users.py")
        content = "@app.route('/api/users')\n" "def get_users():\n    return users"

        functionality = parser._detect_functionality(file_path, content)
        assert functionality == "api_routes"

    def test_detect_functionality_tests(self):
        """Test test files functionality detection."""
        parser = UniversalParser()
        file_path = Path("tests/test_auth.py")
        content = "def test_login():\n    assert True"

        functionality = parser._detect_functionality(file_path, content)
        assert functionality == "tests"

    def test_detect_functionality_styling(self):
        """Test styling functionality detection."""
        parser = UniversalParser()
        file_path = Path("styles/main.css")
        content = ".button { color: blue; }"

        functionality = parser._detect_functionality(file_path, content)
        assert functionality == "styling"

    def test_assess_complexity_simple(self):
        """Test simple complexity assessment."""
        parser = UniversalParser()
        content = "print('hello')"

        complexity = parser._assess_complexity(content)
        assert complexity == "simple"

    def test_assess_complexity_moderate(self):
        """Test moderate complexity assessment."""
        parser = UniversalParser()
        content = "\n".join([f"line_{i} = {i}" for i in range(20)])

        complexity = parser._assess_complexity(content)
        assert complexity == "moderate"

    def test_assess_complexity_complex(self):
        """Test complex complexity assessment."""
        parser = UniversalParser()
        # Create content with multiple complexity indicators
        content = "\n".join(
            [
                "class ComplexClass:",
                "    def method1(self):",
                "        if condition:",
                "            for i in range(100):",
                "                try:",
                "                    result = complex_function()",
                "                except Exception as e:",
                "                    handle_error(e)",
                "    def method2(self):",
                "        pass",
            ]
            + [f"    # line {i}" for i in range(50)]
        )

        complexity = parser._assess_complexity(content)
        assert complexity == "complex"

    def test_should_include_file_valid(self):
        """Test file inclusion for valid files."""
        parser = UniversalParser()

        # Test valid Python file
        file_path = Path("src/main.py")
        assert parser._should_include_file(file_path) is True

    def test_should_include_file_hidden(self):
        """Test file exclusion for hidden files."""
        parser = UniversalParser()

        # Test hidden file (should be excluded)
        file_path = Path(".hidden/file.py")
        assert parser._should_include_file(file_path) is False

    def test_should_include_file_build_dir(self):
        """Test file exclusion for build directories."""
        parser = UniversalParser()

        # Test file in build directory (should be excluded)
        file_path = Path("node_modules/package/file.js")
        assert parser._should_include_file(file_path) is False

    def test_calculate_file_metrics(self):
        """Test file metrics calculation."""
        parser = UniversalParser()
        file_path = Path("test.py")
        content = "# Comment\nprint('hello')\n" "# Another comment\nprint('world')"

        metrics = parser._calculate_file_metrics(file_path, content)

        assert metrics["file_size"] == len(content)
        assert metrics["line_count"] == 4
        assert metrics["non_empty_lines"] == 4
        assert metrics["comment_lines"] == 2
        assert metrics["extension"] == ".py"

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="print('hello')")
    def test_parse_file_success(self, mock_file, mock_exists):
        """Test successful file parsing."""
        mock_exists.return_value = True

        parser = UniversalParser()
        result = parser.parse_file("test.py")

        assert result is not None
        assert result.language == "python"
        assert result.content == "print('hello')"
        assert result.complexity in ["simple", "moderate", "complex"]

    @patch("pathlib.Path.exists")
    def test_parse_file_not_found(self, mock_exists):
        """Test file parsing with non-existent file."""
        mock_exists.return_value = False

        parser = UniversalParser()

        with pytest.raises(FileNotFoundError):
            parser.parse_file("nonexistent.py")

    def test_parse_file_unsupported_extension(self):
        """Test file parsing with unsupported extension."""
        parser = UniversalParser()

        # Create a temporary file with unsupported extension
        with pytest.raises(UnsupportedFileTypeError):
            parser.parse_file("test.unsupported")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch("pathlib.Path.exists")
    def test_parse_file_empty(self, mock_exists, mock_file):
        """Test parsing empty file."""
        mock_exists.return_value = True

        parser = UniversalParser()
        result = parser.parse_file("empty.py")

        assert result is None


class TestFileMetrics:
    """Test suite for file metrics calculation."""

    def test_empty_file_metrics(self):
        """Test metrics for empty file."""
        parser = UniversalParser()
        file_path = Path("empty.py")
        content = ""

        metrics = parser._calculate_file_metrics(file_path, content)

        assert metrics["file_size"] == 0
        # split() always returns at least one
        assert metrics["line_count"] == 1
        assert metrics["non_empty_lines"] == 0
        assert metrics["comment_lines"] == 0

    def test_single_line_file_metrics(self):
        """Test metrics for single line file."""
        parser = UniversalParser()
        file_path = Path("single.py")
        content = "print('hello world')"

        metrics = parser._calculate_file_metrics(file_path, content)

        assert metrics["file_size"] == len(content)
        assert metrics["line_count"] == 1
        assert metrics["non_empty_lines"] == 1
        assert metrics["comment_lines"] == 0

    def test_multiline_file_metrics(self):
        """Test metrics for multi-line file with comments."""
        parser = UniversalParser()
        file_path = Path("multi.py")
        content = """# This is a comment
print('line 1')

# Another comment
print('line 2')"""

        metrics = parser._calculate_file_metrics(file_path, content)

        assert metrics["file_size"] == len(content)
        assert metrics["line_count"] == 5
        assert metrics["non_empty_lines"] == 4  # Excluding empty line
        assert metrics["comment_lines"] == 2


class TestLanguageDetection:
    """Test suite for language detection accuracy."""

    @pytest.mark.parametrize(
        "extension,expected_language",
        [
            (".py", "python"),
            (".js", "javascript"),
            (".ts", "typescript"),
            (".tsx", "typescript"),
            (".jsx", "javascript"),
            (".java", "java"),
            (".go", "go"),
            (".rs", "rust"),
            (".cpp", "cpp"),
            (".c", "c"),
            (".cs", "csharp"),
            (".php", "php"),
            (".rb", "ruby"),
            (".swift", "swift"),
            (".kt", "kotlin"),
        ],
    )
    def test_extension_based_detection(self, extension, expected_language):
        """Test language detection based on file extensions."""
        parser = UniversalParser()
        file_path = Path(f"test{extension}")
        content = "// Generic content"

        language = parser._detect_language(file_path, content)
        assert language == expected_language

    @pytest.mark.parametrize(
        "content,expected_language",
        [
            ("def hello():\n    pass", "python"),
            ("function hello() {}", "javascript"),
            ("public class Test {}", "java"),
            ("package main\nfunc main() {}", "go"),
            ("fn main() {}", "rust"),
            ("<?php echo 'hello'; ?>", "php"),
            ("puts 'hello'", "ruby"),
        ],
    )
    def test_content_based_detection(self, content, expected_language):
        """Test language detection based on content keywords."""
        parser = UniversalParser()
        file_path = Path("test.unknown")  # Unknown extension, rely on content

        language = parser._detect_language(file_path, content)
        assert language == expected_language
