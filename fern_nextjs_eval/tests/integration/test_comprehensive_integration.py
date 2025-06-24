"""
Comprehensive integration tests for the Universal Code Evaluation Framework.

These tests verify that different components work together correctly and
that the system can handle realistic evaluation scenarios.
"""

import json

from src.models import EvaluationResult
from src.universal_evaluator import UniversalCodeEvaluator


class TestUniversalEvaluatorIntegration:
    """Integration tests for the complete evaluation pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = UniversalCodeEvaluator()

    def test_evaluate_simple_functions_integration(self, temp_dir):
        """Test evaluation of simple function implementations."""
        # Create golden standard
        golden_code = """
        function calculateTotal(items) {
            return items.reduce((sum, item) => sum + item.price, 0);
        }
        """

        # Create generated code (functionally equivalent)
        generated_code = """
        function calculateTotal(items) {
            let total = 0;
            for (const item of items) {
                total += item.price;
            }
            return total;
        }
        """

        golden_file = temp_dir / "golden.js"
        generated_file = temp_dir / "generated.js"

        golden_file.write_text(golden_code)
        generated_file.write_text(generated_code)

        # Evaluate
        result = self.evaluator.evaluate(str(golden_file), str(generated_file))

        assert isinstance(result, EvaluationResult)
        assert 0 <= result.overall_similarity <= 1
        assert result.functional_equivalence > 0.5  # Should be functionally similar

    def test_evaluate_react_components_integration(self, temp_dir):
        """Test evaluation of React component implementations."""
        # Golden standard React component
        golden_code = """
        import React, { useState } from 'react';

        const LoginForm = ({ onSubmit }) => {
            const [email, setEmail] = useState('');
            const [password, setPassword] = useState('');

            const handleSubmit = (e) => {
                e.preventDefault();
                onSubmit({ email, password });
            };

            return (
                <form onSubmit={handleSubmit}>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit">Login</button>
                </form>
            );
        };

        export default LoginForm;
        """

        # Generated React component (different style, same functionality)
        generated_code = """
        import React, { useState } from 'react';

        function LoginForm(props) {
            const [formData, setFormData] = useState({
                email: '',
                password: ''
            });

            function handleChange(field, value) {
                setFormData(prev => ({
                    ...prev,
                    [field]: value
                }));
            }

            function handleSubmit(event) {
                event.preventDefault();
                props.onSubmit(formData);
            }

            return (
                <form onSubmit={handleSubmit}>
                    <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleChange('email', e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        value={formData.password}
                        onChange={(e) => handleChange('password', e.target.value)}
                        required
                    />
                    <button type="submit">Login</button>
                </form>
            );
        }

        export default LoginForm;
        """

        golden_file = temp_dir / "golden.jsx"
        generated_file = temp_dir / "generated.jsx"

        golden_file.write_text(golden_code)
        generated_file.write_text(generated_code)

        # Evaluate
        result = self.evaluator.evaluate(str(golden_file), str(generated_file))

        assert isinstance(result, EvaluationResult)
        assert result.overall_similarity > 0.6  # Should be quite similar
        assert result.structural_similarity > 0.5  # Similar structure

    def test_evaluate_applications_integration(self, temp_dir):
        """Test evaluation of complete applications."""
        # Create golden standard application structure
        golden_dir = temp_dir / "golden_app"
        golden_dir.mkdir()

        # Golden app structure
        (golden_dir / "package.json").write_text(
            json.dumps(
                {
                    "name": "todo-app",
                    "version": "1.0.0",
                    "dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"},
                }
            )
        )

        components_dir = golden_dir / "components"
        components_dir.mkdir()

        (components_dir / "TodoList.jsx").write_text(
            """
        import React from 'react';
        import TodoItem from './TodoItem';

        const TodoList = ({ todos, onToggle, onDelete }) => {
            return (
                <ul className="todo-list">
                    {todos.map(todo => (
                        <TodoItem
                            key={todo.id}
                            todo={todo}
                            onToggle={onToggle}
                            onDelete={onDelete}
                        />
                    ))}
                </ul>
            );
        };

        export default TodoList;
        """
        )

        # Create generated application
        generated_dir = temp_dir / "generated_app"
        generated_dir.mkdir()

        (generated_dir / "package.json").write_text(
            json.dumps(
                {
                    "name": "todo-application",
                    "version": "1.0.0",
                    "dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"},
                }
            )
        )

        components_dir_gen = generated_dir / "components"
        components_dir_gen.mkdir()

        (components_dir_gen / "TodoList.jsx").write_text(
            """
        import React from 'react';
        import TodoItem from './TodoItem';

        function TodoList(props) {
            const { todos, onToggle, onDelete } = props;

            return (
                <div className="todo-container">
                    {todos.map(todo => (
                        <TodoItem
                            key={todo.id}
                            todo={todo}
                            onToggle={onToggle}
                            onDelete={onDelete}
                        />
                    ))}
                </div>
            );
        }

        export default TodoList;
        """
        )

        # Evaluate applications
        result = self.evaluator.evaluate(str(golden_dir), str(generated_dir))

        assert isinstance(result, EvaluationResult)
        assert result.overall_similarity > 0.5
        assert "package.json" in str(result.detailed_analysis["file_results"].keys())

    def test_batch_evaluation_integration(self, temp_dir):
        """Test batch evaluation of multiple code samples."""
        # Create test samples
        samples = []

        for i in range(3):
            golden_file = temp_dir / f"golden_{i}.js"
            generated_file = temp_dir / f"generated_{i}.js"

            golden_code = f"""
            function process{i}(data) {{
                return data.map(item => item * {i + 1});
            }}
            """

            generated_code = f"""
            function process{i}(data) {{
                const result = [];
                for (let item of data) {{
                    result.push(item * {i + 1});
                }}
                return result;
            }}
            """

            golden_file.write_text(golden_code)
            generated_file.write_text(generated_code)

            samples.append((str(golden_file), str(generated_file)))

        # Batch evaluate
        results = []
        for golden, generated in samples:
            result = self.evaluator.evaluate(golden, generated)
            results.append(result)

        assert len(results) == 3
        assert all(isinstance(r, EvaluationResult) for r in results)
        assert all(r.overall_similarity > 0.4 for r in results)

    def test_evaluation_with_errors_integration(self, temp_dir):
        """Test evaluation handling of various error conditions."""
        # Test with syntax error in generated code
        golden_file = temp_dir / "golden.js"
        broken_file = temp_dir / "broken.js"

        golden_file.write_text("function test() { return 42; }")
        broken_file.write_text("function test( { invalid syntax")

        # Should handle gracefully
        result = self.evaluator.evaluate(str(golden_file), str(broken_file))

        assert isinstance(result, EvaluationResult)
        assert result.overall_similarity < 0.6  # Should be lower due to syntax issues

    def test_evaluation_custom_weights_integration(self, temp_dir):
        """Test evaluation with custom weight configuration."""
        custom_weights = {
            "semantic": 0.6,
            "structural": 0.2,
            "style": 0.1,
            "functional": 0.1,
        }

        evaluator = UniversalCodeEvaluator(weights=custom_weights)

        # Create test files
        golden_file = temp_dir / "golden.js"
        generated_file = temp_dir / "generated.js"

        golden_file.write_text("function add(a, b) { return a + b; }")
        generated_file.write_text("const add = (a, b) => a + b;")

        result = evaluator.evaluate(str(golden_file), str(generated_file))

        assert isinstance(result, EvaluationResult)
        assert result.overall_similarity > 0.5  # Semantically similar

    def test_large_file_evaluation_integration(self, temp_dir):
        """Test evaluation of larger code files."""
        # Create a larger golden standard file
        golden_code = """
        class DataProcessor {
            constructor(config) {
                this.config = config;
                this.cache = new Map();
            }

            async processData(data) {
                if (this.cache.has(data.id)) {
                    return this.cache.get(data.id);
                }

                const processed = await this.transform(data);
                const validated = this.validate(processed);

                if (validated) {
                    this.cache.set(data.id, processed);
                    return processed;
                }

                throw new Error('Validation failed');
            }

            transform(data) {
                return new Promise((resolve) => {
                    setTimeout(() => {
                        resolve({
                            ...data,
                            processed: true,
                            timestamp: Date.now()
                        });
                    }, 100);
                });
            }

            validate(data) {
                return data &&
                       typeof data.id === 'string' &&
                       data.processed === true;
            }

            clearCache() {
                this.cache.clear();
            }

            getCacheSize() {
                return this.cache.size;
            }
        }

        module.exports = DataProcessor;
        """

        # Create a generated version with different style
        generated_code = """
        const DataProcessor = function(config) {
            this.config = config;
            this.cache = new Map();
        };

        DataProcessor.prototype.processData = async function(data) {
            if (this.cache.has(data.id)) {
                return this.cache.get(data.id);
            }

            const processed = await this.transform(data);
            const isValid = this.validate(processed);

            if (isValid) {
                this.cache.set(data.id, processed);
                return processed;
            }

            throw new Error('Validation failed');
        };

        DataProcessor.prototype.transform = function(data) {
            return new Promise(function(resolve) {
                setTimeout(function() {
                    resolve(Object.assign({}, data, {
                        processed: true,
                        timestamp: Date.now()
                    }));
                }, 100);
            });
        };

        DataProcessor.prototype.validate = function(data) {
            return data &&
                   typeof data.id === 'string' &&
                   data.processed === true;
        };

        DataProcessor.prototype.clearCache = function() {
            this.cache.clear();
        };

        DataProcessor.prototype.getCacheSize = function() {
            return this.cache.size;
        };

        module.exports = DataProcessor;
        """

        golden_file = temp_dir / "golden.js"
        generated_file = temp_dir / "generated.js"

        golden_file.write_text(golden_code)
        generated_file.write_text(generated_code)

        # Evaluate
        result = self.evaluator.evaluate(str(golden_file), str(generated_file))

        assert isinstance(result, EvaluationResult)
        assert result.overall_similarity > 0.5  # Should be similar functionally
        assert result.functional_equivalence > 0.7  # Very similar functionality


class TestEvaluationResultIntegration:
    """Integration tests for evaluation result handling."""

    def test_evaluation_result_serialization(self, temp_dir):
        """Test that evaluation results can be serialized and deserialized."""
        evaluator = UniversalCodeEvaluator()

        golden_file = temp_dir / "golden.js"
        generated_file = temp_dir / "generated.js"

        golden_file.write_text("function test() { return 'hello'; }")
        generated_file.write_text("const test = () => 'hello';")

        result = evaluator.evaluate(str(golden_file), str(generated_file))

        # Convert to dictionary
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "overall_similarity" in result_dict
        assert "detailed_analysis" in result_dict

        # Should be JSON serializable
        json_str = json.dumps(result_dict)
        assert isinstance(json_str, str)

        # Should be able to recreate from dict
        recreated_dict = json.loads(json_str)
        assert recreated_dict == result_dict

    def test_evaluation_result_comparison_different_structures(self, temp_dir):
        """Test evaluation between significantly different code structures."""
        # Test that the framework can handle structurally different but functionally equivalent code

        # Imperative style
        golden_code = """
        function processUsers(users) {
            const results = [];
            for (let i = 0; i < users.length; i++) {
                const user = users[i];
                if (user.age >= 18) {
                    results.push({
                        id: user.id,
                        name: user.name.toUpperCase(),
                        category: 'adult'
                    });
                }
            }
            return results;
        }
        """

        # Functional style
        generated_code = """
        const processUsers = users =>
            users
                .filter(user => user.age >= 18)
                .map(user => ({
                    id: user.id,
                    name: user.name.toUpperCase(),
                    category: 'adult'
                }));
        """

        evaluator = UniversalCodeEvaluator()

        golden_file = temp_dir / "golden.js"
        generated_file = temp_dir / "generated.js"

        golden_file.write_text(golden_code)
        generated_file.write_text(generated_code)

        result = evaluator.evaluate(str(golden_file), str(generated_file))

        # Despite different structure, we should get valid results
        assert result.functional_equivalence >= 0.0  # Valid functional score
        # But structural similarity might be lower
        assert result.structural_similarity < 0.5  # Very different structures
