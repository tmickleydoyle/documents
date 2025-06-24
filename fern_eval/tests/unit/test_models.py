"""
Unit tests for the data models in the Universal Code Evaluation Framework.

These tests verify the core data structures and their behavior
with simple, isolated test cases.
"""

from pathlib import Path

import pytest
from src.models import (
    ApplicationStructure,
    BatchEvaluationResult,
    CodeSample,
    EvaluationResult,
    FileInfo,
    FunctionalSignature,
)


class TestFileInfo:
    """Test suite for FileInfo class."""

    def test_init_with_path_object(self):
        """Test FileInfo initialization with Path object."""
        file_path = Path("test.py")
        metadata = {"language": "python"}

        file_info = FileInfo(file_path=file_path, metadata=metadata)

        assert file_info.file_path == file_path
        assert file_info.metadata == metadata

    def test_init_with_string_path(self):
        """Test FileInfo initialization with string path."""
        file_path_str = "test.py"
        metadata = {"language": "python"}

        file_info = FileInfo(file_path=file_path_str, metadata=metadata)

        assert isinstance(file_info.file_path, Path)
        assert str(file_info.file_path) == file_path_str
        assert file_info.metadata == metadata

    def test_suffix_property(self, temp_dir):
        """Test suffix property returns file extension."""
        test_file = temp_dir / "test.py"
        test_file.write_text("print('hello')")

        file_info = FileInfo(file_path=test_file)
        assert file_info.suffix == ".py"

    def test_name_property(self, temp_dir):
        """Test name property returns filename."""
        test_file = temp_dir / "test_file.py"
        test_file.write_text("print('hello')")

        file_info = FileInfo(file_path=test_file)
        assert file_info.name == "test_file.py"

    def test_stem_property(self, temp_dir):
        """Test stem property returns filename without extension."""
        test_file = temp_dir / "test_file.py"
        test_file.write_text("print('hello')")

        file_info = FileInfo(file_path=test_file)
        assert file_info.stem == "test_file"

    def test_parent_property(self, temp_dir):
        """Test parent property returns parent directory."""
        test_file = temp_dir / "subdir" / "test.py"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text("print('hello')")

        file_info = FileInfo(file_path=test_file)
        assert file_info.parent == test_file.parent

    def test_read_text(self, temp_dir):
        """Test read_text method."""
        test_file = temp_dir / "test.py"
        content = "print('Hello, World!')"
        test_file.write_text(content)

        file_info = FileInfo(file_path=test_file)
        assert file_info.read_text() == content

    def test_exists(self, temp_dir):
        """Test exists method."""
        existing_file = temp_dir / "existing.py"
        existing_file.write_text("content")

        non_existing_file = temp_dir / "non_existing.py"

        existing_info = FileInfo(file_path=existing_file)
        non_existing_info = FileInfo(file_path=non_existing_file)

        assert existing_info.exists() is True
        assert non_existing_info.exists() is False

    def test_str_representation(self, temp_dir):
        """Test string representation."""
        test_file = temp_dir / "test.py"
        test_file.write_text("content")

        file_info = FileInfo(file_path=test_file)
        assert str(file_info) == str(test_file)

    def test_fspath(self, temp_dir):
        """Test __fspath__ method for os.fspath() compatibility."""
        test_file = temp_dir / "test.py"
        test_file.write_text("content")

        file_info = FileInfo(file_path=test_file)
        assert file_info.__fspath__() == str(test_file)


class TestCodeSample:
    """Test suite for CodeSample class."""

    def test_init_valid(self):
        """Test CodeSample initialization with valid data."""
        sample = CodeSample(
            id="test_id",
            content="print('hello')",
            file_path="/path/to/file.py",
            language="python",
            functionality="general",
            complexity="simple",
        )

        assert sample.id == "test_id"
        assert sample.content == "print('hello')"
        assert sample.file_path == "/path/to/file.py"
        assert sample.language == "python"
        assert sample.functionality == "general"
        assert sample.complexity == "simple"
        assert sample.metadata == {}

    def test_init_with_metadata(self):
        """Test CodeSample initialization with metadata."""
        metadata = {"line_count": 10, "author": "test"}

        sample = CodeSample(
            id="test_id",
            content="print('hello')",
            file_path="/path/to/file.py",
            language="python",
            functionality="general",
            complexity="simple",
            metadata=metadata,
        )

        assert sample.metadata == metadata

    def test_empty_content_validation(self):
        """Test validation fails for empty content."""
        with pytest.raises(ValueError, match="Code content cannot be empty"):
            CodeSample(
                id="test_id",
                content="   ",  # Only whitespace
                file_path="/path/to/file.py",
                language="python",
                functionality="general",
                complexity="simple",
            )

    def test_empty_string_content_validation(self):
        """Test validation fails for empty string content."""
        with pytest.raises(ValueError, match="Code content cannot be empty"):
            CodeSample(
                id="test_id",
                content="",  # Empty string
                file_path="/path/to/file.py",
                language="python",
                functionality="general",
                complexity="simple",
            )


class TestApplicationStructure:
    """Test suite for ApplicationStructure class."""

    def test_init_default(self, temp_dir):
        """Test ApplicationStructure initialization with defaults."""
        structure = ApplicationStructure(root_path=temp_dir)

        assert structure.root_path == temp_dir
        assert structure.all_files == []
        assert structure.language_distribution == {}
        assert structure.functionality_groups == {}
        assert structure.detected_frameworks == []
        assert structure.directory_structure == {}

    def test_total_files_empty(self, temp_dir):
        """Test total_files method with no files."""
        structure = ApplicationStructure(root_path=temp_dir)
        assert structure.total_files() == 0

    def test_total_files_with_files(self, temp_dir):
        """Test total_files method with files."""
        structure = ApplicationStructure(root_path=temp_dir)

        # Add some FileInfo objects
        file1 = FileInfo(file_path=temp_dir / "file1.py")
        file2 = FileInfo(file_path=temp_dir / "file2.py")
        structure.all_files = [file1, file2]

        assert structure.total_files() == 2

    def test_detected_languages_property(self, temp_dir):
        """Test detected_languages property."""
        structure = ApplicationStructure(root_path=temp_dir)
        structure.language_distribution = {
            "python": 5,
            "javascript": 3,
            "typescript": 2,
        }

        languages = structure.detected_languages
        assert languages == {"python", "javascript", "typescript"}

    def test_get_primary_language_empty(self, temp_dir):
        """Test get_primary_language with no languages."""
        structure = ApplicationStructure(root_path=temp_dir)
        assert structure.get_primary_language() == "unknown"

    def test_get_primary_language_single(self, temp_dir):
        """Test get_primary_language with single language."""
        structure = ApplicationStructure(root_path=temp_dir)
        structure.language_distribution = {"python": 10}

        assert structure.get_primary_language() == "python"

    def test_get_primary_language_multiple(self, temp_dir):
        """Test get_primary_language with multiple languages."""
        structure = ApplicationStructure(root_path=temp_dir)
        structure.language_distribution = {
            "python": 5,
            "javascript": 10,  # Most common
            "typescript": 3,
        }

        assert structure.get_primary_language() == "javascript"

    def test_get_functionality_coverage_empty(self, temp_dir):
        """Test get_functionality_coverage with no files."""
        structure = ApplicationStructure(root_path=temp_dir)
        assert structure.get_functionality_coverage() == {}

    def test_get_functionality_coverage_with_files(self, temp_dir):
        """Test get_functionality_coverage with files."""
        structure = ApplicationStructure(root_path=temp_dir)

        # Create FileInfo objects
        file1 = FileInfo(file_path=temp_dir / "file1.py")
        file2 = FileInfo(file_path=temp_dir / "file2.py")
        file3 = FileInfo(file_path=temp_dir / "file3.py")
        structure.all_files = [file1, file2, file3]

        # Set functionality groups
        structure.functionality_groups = {
            "ui_components": [file1, file2],  # 2 files = 66.67%
            "api_routes": [file3],  # 1 file = 33.33%
        }

        coverage = structure.get_functionality_coverage()

        assert abs(coverage["ui_components"] - 66.67) < 0.01
        assert abs(coverage["api_routes"] - 33.33) < 0.01


class TestFunctionalSignature:
    """Test suite for FunctionalSignature class."""

    def test_init_minimal(self):
        """Test FunctionalSignature initialization with minimal data."""
        signature = FunctionalSignature(
            language="python", functionality_category="general"
        )

        assert signature.language == "python"
        assert signature.functionality_category == "general"
        assert signature.exports == []
        assert signature.imports == []
        assert signature.functions == []
        assert signature.classes == []
        assert signature.keywords == []
        assert signature.api_endpoints == []
        assert signature.ui_elements == []

    def test_init_complete(self):
        """Test FunctionalSignature initialization with all data."""
        signature = FunctionalSignature(
            language="javascript",
            functionality_category="ui_components",
            exports=["Button", "Input"],
            imports=["react", "lodash"],
            functions=["handleClick", "validateInput"],
            classes=["Component"],
            keywords=["component", "button"],
            api_endpoints=["/api/users"],
            ui_elements=["button", "input"],
        )

        assert signature.language == "javascript"
        assert signature.functionality_category == "ui_components"
        assert signature.exports == ["Button", "Input"]
        assert signature.imports == ["react", "lodash"]
        assert signature.functions == ["handleClick", "validateInput"]
        assert signature.classes == ["Component"]
        assert signature.keywords == ["component", "button"]
        assert signature.api_endpoints == ["/api/users"]
        assert signature.ui_elements == ["button", "input"]


class TestEvaluationResult:
    """Test suite for EvaluationResult class."""

    def test_init(self):
        """Test EvaluationResult initialization."""
        result = EvaluationResult(
            overall_similarity=0.85,
            functional_equivalence=0.90,
            structural_similarity=0.80,
            details={"test": "data"},
            metadata={"file": "test.py"},
        )

        assert result.overall_similarity == 0.85
        assert result.functional_equivalence == 0.90
        assert result.structural_similarity == 0.80
        assert result.details == {"test": "data"}
        assert result.metadata == {"file": "test.py"}


class TestBatchEvaluationResult:
    """Test suite for BatchEvaluationResult class."""

    def test_init(self):
        """Test BatchEvaluationResult initialization."""
        model_scores = {"model1": 0.85, "model2": 0.75}
        summary_stats = {"mean": 0.80, "std": 0.05}

        result = BatchEvaluationResult(
            model_scores=model_scores,
            summary_statistics=summary_stats,
            best_model="model1",
            worst_model="model2",
        )

        assert result.model_scores == model_scores
        assert result.summary_statistics == summary_stats
        assert result.best_model == "model1"
        assert result.worst_model == "model2"
        assert result.detailed_results == []

    def test_init_with_detailed_results(self):
        """Test BatchEvaluationResult initialization with detailed results."""
        model_scores = {"model1": 0.85}
        summary_stats = {"mean": 0.85}
        detailed_results = [{"model": "model1", "score": 0.85}]

        result = BatchEvaluationResult(
            model_scores=model_scores,
            summary_statistics=summary_stats,
            best_model="model1",
            worst_model="model1",
            detailed_results=detailed_results,
        )

        assert result.detailed_results == detailed_results


class TestModelValidation:
    """Test suite for model validation and edge cases."""

    def test_file_info_with_special_characters(self, temp_dir):
        """Test FileInfo with special characters in path."""
        special_file = temp_dir / "test-file_name.special.py"
        special_file.write_text("content")

        file_info = FileInfo(file_path=special_file)
        assert file_info.name == "test-file_name.special.py"
        assert file_info.suffix == ".py"
        assert file_info.stem == "test-file_name.special"

    def test_application_structure_edge_cases(self, temp_dir):
        """Test ApplicationStructure edge cases."""
        structure = ApplicationStructure(root_path=temp_dir)

        # Test with None values
        structure.language_distribution = None
        assert structure.get_primary_language() == "unknown"

        # Test with empty dict
        structure.language_distribution = {}
        assert structure.get_primary_language() == "unknown"

    def test_code_sample_whitespace_validation(self):
        """Test CodeSample validation with different whitespace scenarios."""
        # Test with only newlines
        with pytest.raises(ValueError):
            CodeSample(
                id="test",
                content="\n\n\n",
                file_path="test.py",
                language="python",
                functionality="general",
                complexity="simple",
            )

        # Test with tabs and spaces
        with pytest.raises(ValueError):
            CodeSample(
                id="test",
                content="\t  \t  ",
                file_path="test.py",
                language="python",
                functionality="general",
                complexity="simple",
            )

    def test_functional_signature_empty_lists(self):
        """Test FunctionalSignature with explicitly empty lists."""
        signature = FunctionalSignature(
            language="python",
            functionality_category="general",
            exports=[],
            imports=[],
            functions=[],
            classes=[],
            keywords=[],
            api_endpoints=[],
            ui_elements=[],
        )

        # All lists should remain empty
        assert len(signature.exports) == 0
        assert len(signature.imports) == 0
        assert len(signature.functions) == 0
        assert len(signature.classes) == 0
        assert len(signature.keywords) == 0
        assert len(signature.api_endpoints) == 0
        assert len(signature.ui_elements) == 0
