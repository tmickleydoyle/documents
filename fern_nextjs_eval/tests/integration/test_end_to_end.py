"""
Integration tests for the Universal Code Evaluation Framework.

These tests verify that all components work together correctly
using real file operations and end-to-end evaluation scenarios.
"""

import tempfile
from pathlib import Path

import pytest
from src.universal_evaluator import UniversalCodeEvaluator
from src.universal_parser import UniversalParser


class TestEndToEndEvaluation:
    """Integration tests for complete evaluation workflows."""

    def test_evaluate_python_applications(self):
        """Test end-to-end evaluation of Python applications."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create golden standard Python app
            golden_app = temp_path / "golden_python"
            golden_app.mkdir()

            (golden_app / "app.py").write_text(
                """
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Hello World'})

@app.route('/api/users')
def get_users():
    return jsonify({'users': ['alice', 'bob']})

if __name__ == '__main__':
    app.run(debug=True)
"""
            )

            (golden_app / "requirements.txt").write_text("flask==2.0.1\n")

            (golden_app / "test_app.py").write_text(
                """
import pytest
from app import app

def test_home():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200

def test_users():
    client = app.test_client()
    response = client.get('/api/users')
    assert response.status_code == 200
"""
            )

            # Create generated Python app (similar but different)
            generated_app = temp_path / "generated_python"
            generated_app.mkdir()

            (generated_app / "main.py").write_text(
                """
from flask import Flask, jsonify

application = Flask(__name__)

@application.route('/')
def index():
    return jsonify({'msg': 'Hello World'})

@application.route('/api/users')
def users():
    return jsonify({'users': ['alice', 'bob', 'charlie']})

if __name__ == '__main__':
    application.run()
"""
            )

            (generated_app / "requirements.txt").write_text("flask==2.0.1\n")

            # Run evaluation
            evaluator = UniversalCodeEvaluator()
            result = evaluator.evaluate(
                str(golden_app), str(generated_app), evaluation_type="app"
            )

            # Verify results
            assert result.metadata["evaluation_type"] == "application"
            assert "python" in result.detailed_analysis.get("golden_languages", [])
            assert "python" in result.detailed_analysis.get("generated_languages", [])
            assert result.overall_similarity > 0.0
            assert len(result.detailed_analysis.get("file_matches", [])) > 0

    def test_evaluate_typescript_applications(self):
        """Test end-to-end evaluation of TypeScript React applications."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create golden standard TypeScript app
            golden_app = temp_path / "golden_ts"
            golden_app.mkdir()

            (golden_app / "package.json").write_text(
                """
{
  "name": "golden-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.0.0",
    "typescript": "^4.0.0"
  }
}
"""
            )

            components_dir = golden_app / "components"
            components_dir.mkdir()

            (components_dir / "Button.tsx").write_text(
                """
import React from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
}

export const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
  return (
    <button onClick={onClick} className="btn">
      {label}
    </button>
  );
};
"""
            )

            pages_dir = golden_app / "pages"
            pages_dir.mkdir()

            (pages_dir / "index.tsx").write_text(
                """
import React from 'react';
import { Button } from '../components/Button';

const HomePage: React.FC = () => {
  const handleClick = () => {
    console.log('Button clicked');
  };

  return (
    <div>
      <h1>Welcome to My App</h1>
      <Button label="Click Me" onClick={handleClick} />
    </div>
  );
};

export default HomePage;
"""
            )

            # Create generated TypeScript app
            generated_app = temp_path / "generated_ts"
            generated_app.mkdir()

            (generated_app / "package.json").write_text(
                """
{
  "name": "generated-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.0.0",
    "typescript": "^4.0.0"
  }
}
"""
            )

            components_dir = generated_app / "components"
            components_dir.mkdir()

            (components_dir / "Button.tsx").write_text(
                """
import React from 'react';

type ButtonProps = {
  text: string;
  onPress: () => void;
}

export const Button: React.FC<ButtonProps> = ({ text, onPress }) => {
  return (
    <button onClick={onPress} className="button">
      {text}
    </button>
  );
};
"""
            )

            pages_dir = generated_app / "pages"
            pages_dir.mkdir()

            (pages_dir / "index.tsx").write_text(
                """
import React from 'react';
import { Button } from '../components/Button';

const Home: React.FC = () => {
  return (
    <div>
      <h1>My Application</h1>
      <Button text="Press Me" onPress={() => alert('clicked')} />
    </div>
  );
};

export default Home;
"""
            )

            # Run evaluation
            evaluator = UniversalCodeEvaluator()
            result = evaluator.evaluate(
                str(golden_app), str(generated_app), evaluation_type="app"
            )

            # Verify results
            assert result.metadata["evaluation_type"] == "application"
            assert "typescript" in result.detailed_analysis.get("golden_languages", [])
            assert "typescript" in result.detailed_analysis.get(
                "generated_languages", []
            )
            assert result.overall_similarity > 0.0
            assert (
                len(result.detailed_analysis.get("file_matches", [])) >= 3
            )  # package.json, Button.tsx, index.tsx

    def test_evaluate_cross_language_applications(self):
        """Test evaluation of applications in different languages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create Python app
            python_app = temp_path / "python_app"
            python_app.mkdir()

            (python_app / "api.py").write_text(
                """
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello from Python'})
"""
            )

            # Create JavaScript app with similar functionality
            js_app = temp_path / "js_app"
            js_app.mkdir()

            (js_app / "api.js").write_text(
                """
const express = require('express');
const app = express();

app.get('/api/hello', (req, res) => {
  res.json({ message: 'Hello from JavaScript' });
});

module.exports = app;
"""
            )

            # Run evaluation
            evaluator = UniversalCodeEvaluator()
            result = evaluator.evaluate(
                str(python_app), str(js_app), evaluation_type="app"
            )

            # Verify results
            assert result.metadata["evaluation_type"] == "application"
            assert "python" in result.detailed_analysis.get("golden_languages", [])
            assert "javascript" in result.detailed_analysis.get(
                "generated_languages", []
            )
            # Cross-language evaluation should still work with functionality matching
            assert result.overall_similarity >= 0.0

    def test_evaluate_single_files(self):
        """Test end-to-end evaluation of single files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create similar Python files
            golden_file = temp_path / "golden.py"
            golden_file.write_text(
                """
def calculate_area(radius):
    '''Calculate the area of a circle.'''
    import math
    return math.pi * radius * radius

def calculate_circumference(radius):
    '''Calculate the circumference of a circle.'''
    import math
    return 2 * math.pi * radius

if __name__ == '__main__':
    r = 5
    print(f'Area: {calculate_area(r)}')
    print(f'Circumference: {calculate_circumference(r)}')
"""
            )

            generated_file = temp_path / "generated.py"
            generated_file.write_text(
                """
import math

def area(r):
    \"\"\"Compute circle area.\"\"\"
    return math.pi * r ** 2

def circumference(r):
    \"\"\"Compute circle circumference.\"\"\"
    return 2 * math.pi * r

if __name__ == '__main__':
    radius = 5
    print(f'Circle area: {area(radius)}')
    print(f'Circle circumference: {circumference(radius)}')
"""
            )

            # Run evaluation
            evaluator = UniversalCodeEvaluator()
            result = evaluator.evaluate(
                str(golden_file), str(generated_file), evaluation_type="file"
            )

            # Verify results
            assert result.metadata["evaluation_type"] == "file"
            assert result.metadata["golden_file"] == str(golden_file)
            assert result.metadata["generated_file"] == str(generated_file)
            assert result.overall_similarity > 0.5  # Should be quite similar
            assert result.metadata["golden_language"] == "python"
            assert result.metadata["generated_language"] == "python"

    def test_batch_evaluation(self):
        """Test batch evaluation of multiple applications."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create golden standard
            golden_app = temp_path / "golden"
            golden_app.mkdir()

            (golden_app / "main.py").write_text(
                """
def greet(name):
    return f'Hello, {name}!'

if __name__ == '__main__':
    print(greet('World'))
"""
            )

            # Create multiple generated versions
            batch_dir = temp_path / "batch"
            batch_dir.mkdir()

            # Version 1: Very similar
            model1_dir = batch_dir / "model1"
            model1_dir.mkdir()
            (model1_dir / "main.py").write_text(
                """
def greet(name):
    return f'Hello, {name}!'

if __name__ == '__main__':
    print(greet('World'))
"""
            )

            # Version 2: Somewhat different
            model2_dir = batch_dir / "model2"
            model2_dir.mkdir()
            (model2_dir / "main.py").write_text(
                """
def say_hello(person):
    return 'Hello, ' + person + '!'

if __name__ == '__main__':
    result = say_hello('World')
    print(result)
"""
            )

            # Version 3: Very different
            model3_dir = batch_dir / "model3"
            model3_dir.mkdir()
            (model3_dir / "main.py").write_text(
                """
class Greeter:
    def __init__(self):
        self.greeting = 'Hello'

    def greet(self, name):
        return f'{self.greeting}, {name}!'

if __name__ == '__main__':
    g = Greeter()
    print(g.greet('World'))
"""
            )

            # Run batch evaluation
            evaluator = UniversalCodeEvaluator()
            batch_paths = [str(model1_dir), str(model2_dir), str(model3_dir)]

            result = evaluator.evaluate_batch(str(golden_app), batch_paths)

            # Verify results
            assert len(result.model_scores) == 3
            assert result.best_model is not None
            assert result.worst_model is not None
            assert result.summary_statistics["mean"] > 0.0

            # Model1 should score highest (most similar)
            assert (
                result.model_scores[str(model1_dir)]
                > result.model_scores[str(model3_dir)]
            )


class TestParserIntegration:
    """Integration tests for parser functionality."""

    def test_parse_mixed_language_application(self):
        """Test parsing application with multiple languages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mixed language app
            app_dir = temp_path / "mixed_app"
            app_dir.mkdir()

            # Python backend
            (app_dir / "backend.py").write_text(
                """
from flask import Flask
app = Flask(__name__)

@app.route('/api/data')
def get_data():
    return {'data': 'from python'}
"""
            )

            # JavaScript frontend
            (app_dir / "frontend.js").write_text(
                """
async function fetchData() {
    const response = await fetch('/api/data');
    return response.json();
}
"""
            )

            # CSS styles
            (app_dir / "styles.css").write_text(
                """
.container {
    max-width: 1200px;
    margin: 0 auto;
}
"""
            )

            # Configuration
            (app_dir / "config.json").write_text(
                """
{
    "debug": true,
    "port": 3000
}
"""
            )

            # Tests
            test_dir = app_dir / "tests"
            test_dir.mkdir()
            (test_dir / "test_backend.py").write_text(
                """
import pytest
from backend import app

def test_api():
    client = app.test_client()
    response = client.get('/api/data')
    assert response.status_code == 200
"""
            )

            # Parse the application
            parser = UniversalParser()
            structure = parser.parse_application(str(app_dir))

            # Verify parsing results
            assert structure.total_files() >= 5  # Should find at least the main files
            assert len(structure.detected_languages) >= 3  # Python, JavaScript, CSS
            assert "python" in structure.detected_languages
            assert "javascript" in structure.detected_languages
            assert "css" in structure.detected_languages

            # Check functionality categorization
            functionalities = structure.functionality_groups.keys()
            assert "api_routes" in functionalities  # backend.py
            assert "styling" in functionalities  # styles.css
            assert "tests" in functionalities  # test_backend.py

            # Check file info objects
            assert all(hasattr(f, "metadata") for f in structure.all_files)
            assert all("language" in f.metadata for f in structure.all_files)

    def test_parse_large_application_structure(self):
        """Test parsing a larger, more complex application structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create complex app structure
            app_dir = temp_path / "complex_app"
            app_dir.mkdir()

            # Create multiple directories and files
            directories = [
                "src/components",
                "src/pages",
                "src/utils",
                "src/api",
                "tests/unit",
                "tests/integration",
                "config",
                "docs",
            ]

            for dir_path in directories:
                (app_dir / dir_path).mkdir(parents=True)

            # Add files to each directory
            files_to_create = [
                ("src/components/Header.tsx", "React component"),
                ("src/components/Footer.tsx", "React component"),
                ("src/pages/home.tsx", "React page"),
                ("src/pages/about.tsx", "React page"),
                ("src/utils/helpers.ts", "Utility functions"),
                ("src/utils/constants.ts", "Constants"),
                ("src/api/users.ts", "API endpoints"),
                ("src/api/auth.ts", "Authentication API"),
                ("tests/unit/components.test.ts", "Unit tests"),
                ("tests/integration/api.test.ts", "Integration tests"),
                ("config/database.json", "Database config"),
                ("config/app.json", "App config"),
                ("docs/README.md", "Documentation"),
                ("package.json", "Package definition"),
            ]

            for file_path, content in files_to_create:
                file_obj = app_dir / file_path
                file_obj.write_text(f"// {content}\n" + "console.log('test');")

            # Parse the application
            parser = UniversalParser()
            structure = parser.parse_application(str(app_dir))

            # Verify comprehensive parsing
            assert structure.total_files() == len(files_to_create)
            assert structure.get_primary_language() == "typescript"

            # Check that all major functionality categories are detected
            functionalities = set(structure.functionality_groups.keys())
            expected_functionalities = {
                "ui_components",
                "tests",
                "configuration",
                "utilities",
                "api_routes",
            }
            assert expected_functionalities.issubset(functionalities)

            # Verify directory structure analysis
            assert structure.directory_structure is not None
            assert len(structure.directory_structure) > 0


class TestErrorHandling:
    """Integration tests for error handling scenarios."""

    def test_evaluate_nonexistent_paths(self):
        """Test evaluation with non-existent file paths."""
        evaluator = UniversalCodeEvaluator()

        result = evaluator.evaluate(
            "/nonexistent/path1", "/nonexistent/path2", evaluation_type="file"
        )

        # Should handle gracefully and return error information
        assert "error" in result.metadata
        assert result.metadata["evaluation_type"] == "file"

    def test_evaluate_empty_directory(self):
        """Test evaluation with empty directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            empty_dir1 = temp_path / "empty1"
            empty_dir1.mkdir()

            empty_dir2 = temp_path / "empty2"
            empty_dir2.mkdir()

            evaluator = UniversalCodeEvaluator()
            result = evaluator.evaluate(
                str(empty_dir1), str(empty_dir2), evaluation_type="app"
            )

            # Should handle empty directories gracefully
            assert result.metadata["evaluation_type"] == "application"
            assert len(result.detailed_analysis.get("file_matches", {})) == 0

    def test_evaluate_mixed_file_app_input(self):
        """Test evaluation with one file and one directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a single file
            single_file = temp_path / "test.py"
            single_file.write_text("print('hello')")

            # Create a directory
            app_dir = temp_path / "app"
            app_dir.mkdir()
            (app_dir / "main.py").write_text("print('world')")

            evaluator = UniversalCodeEvaluator()
            result = evaluator.evaluate(
                str(single_file), str(app_dir), evaluation_type="auto"
            )

            # Should detect as file evaluation (default when mixed)
            assert result.metadata["evaluation_type"] == "file"


@pytest.mark.slow
class TestPerformance:
    """Performance-related integration tests."""

    def test_evaluate_large_files(self):
        """Test evaluation of large files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create large Python files
            lines = []
            for i in range(1000):
                lines.extend(
                    [
                        f"def function_{i}():",
                        f"    '''Function number {i}'''",
                        f"    return {i} * 2",
                        "",
                    ]
                )
            large_content = "\n".join(lines)

            golden_file = temp_path / "large_golden.py"
            golden_file.write_text(large_content)

            # Create similar but slightly different large file
            modified_content = large_content.replace(
                "return {i} * 2", "return {i} + {i}"
            )
            generated_file = temp_path / "large_generated.py"
            generated_file.write_text(modified_content)

            # Evaluate (should complete in reasonable time)
            evaluator = UniversalCodeEvaluator()
            result = evaluator.evaluate(
                str(golden_file), str(generated_file), evaluation_type="file"
            )

            # Should complete successfully
            assert result.metadata["evaluation_type"] == "file"
            assert result.overall_similarity > 0.0
