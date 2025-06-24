"""
Performance benchmarks for the Universal Code Evaluation Framework.

These tests measure performance characteristics and ensure the system
can handle realistic workloads efficiently.
"""

import pytest
from src.analyzers import QualityAnalyzer, SemanticSimilarityAnalyzer
from src.universal_evaluator import UniversalCodeEvaluator


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = UniversalCodeEvaluator()

    @pytest.mark.benchmark
    def test_single_file_evaluation_performance(self, benchmark, temp_dir):
        """Benchmark single file evaluation performance."""

        # Create test files
        golden_code = """
        class DataProcessor {
            constructor(options = {}) {
                this.options = {
                    timeout: 5000,
                    retries: 3,
                    ...options
                };
                this.cache = new Map();
            }

            async process(data) {
                const cacheKey = this.generateCacheKey(data);

                if (this.cache.has(cacheKey)) {
                    return this.cache.get(cacheKey);
                }

                const result = await this.performProcessing(data);
                this.cache.set(cacheKey, result);

                return result;
            }

            async performProcessing(data) {
                let attempts = 0;

                while (attempts < this.options.retries) {
                    try {
                        const processed = await this.transform(data);
                        return this.validate(processed);
                    } catch (error) {
                        attempts++;
                        if (attempts >= this.options.retries) {
                            throw error;
                        }
                        await this.delay(1000 * attempts);
                    }
                }
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
                if (!data || typeof data !== 'object') {
                    throw new Error('Invalid data format');
                }
                return data;
            }

            generateCacheKey(data) {
                return `${data.id}_${data.type}_${data.version || 'latest'}`;
            }

            delay(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }

            clearCache() {
                this.cache.clear();
            }
        }

        module.exports = DataProcessor;
        """

        generated_code = """
        const DataProcessor = function(options) {
            this.options = Object.assign({
                timeout: 5000,
                retries: 3
            }, options || {});
            this.cache = new Map();
        };

        DataProcessor.prototype.process = async function(data) {
            const cacheKey = this.generateCacheKey(data);

            if (this.cache.has(cacheKey)) {
                return this.cache.get(cacheKey);
            }

            const result = await this.performProcessing(data);
            this.cache.set(cacheKey, result);

            return result;
        };

        DataProcessor.prototype.performProcessing = async function(data) {
            let attempts = 0;

            while (attempts < this.options.retries) {
                try {
                    const processed = await this.transform(data);
                    return this.validate(processed);
                } catch (error) {
                    attempts++;
                    if (attempts >= this.options.retries) {
                        throw error;
                    }
                    await this.delay(1000 * attempts);
                }
            }
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
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid data format');
            }
            return data;
        };

        DataProcessor.prototype.generateCacheKey = function(data) {
            return data.id + '_' + data.type + '_' + (data.version || 'latest');
        };

        DataProcessor.prototype.delay = function(ms) {
            return new Promise(function(resolve) {
                setTimeout(resolve, ms);
            });
        };

        DataProcessor.prototype.clearCache = function() {
            this.cache.clear();
        };

        module.exports = DataProcessor;
        """

        golden_file = temp_dir / "golden.js"
        generated_file = temp_dir / "generated.js"

        golden_file.write_text(golden_code)
        generated_file.write_text(generated_code)

        # Benchmark the evaluation
        def evaluate_files():
            return self.evaluator.evaluate(str(golden_file), str(generated_file))

        result = benchmark(evaluate_files)

        # Verify the result is valid
        assert result.overall_similarity > 0.5

    @pytest.mark.benchmark
    def test_batch_evaluation_performance(self, benchmark, temp_dir):
        """Benchmark batch evaluation performance."""

        # Create multiple test file pairs
        file_pairs = []

        for i in range(10):  # Test with 10 file pairs
            golden_code = f"""
            function processItem{i}(item) {{
                if (!item || typeof item !== 'object') {{
                    throw new Error('Invalid item');
                }}

                return {{
                    id: item.id,
                    processed: true,
                    value: item.value * {i + 1},
                    timestamp: Date.now()
                }};
            }}

            function validateItem{i}(item) {{
                return item.id && typeof item.value === 'number';
            }}
            """

            generated_code = f"""
            const processItem{i} = (item) => {{
                if (!item || typeof item !== 'object') {{
                    throw new Error('Invalid item');
                }}

                return {{
                    id: item.id,
                    processed: true,
                    value: item.value * {i + 1},
                    timestamp: Date.now()
                }};
            }};

            const validateItem{i} = (item) => {{
                return item.id && typeof item.value === 'number';
            }};
            """

            golden_file = temp_dir / f"golden_{i}.js"
            generated_file = temp_dir / f"generated_{i}.js"

            golden_file.write_text(golden_code)
            generated_file.write_text(generated_code)

            file_pairs.append((str(golden_file), str(generated_file)))

        # Benchmark batch evaluation
        def batch_evaluate():
            results = []
            for golden, generated in file_pairs:
                result = self.evaluator.evaluate(golden, generated)
                results.append(result)
            return results

        results = benchmark(batch_evaluate)

        # Verify all results are valid
        assert len(results) == 10
        assert all(r.overall_similarity > 0.5 for r in results)

    @pytest.mark.benchmark
    def test_semantic_analysis_performance(self, benchmark):
        """Benchmark semantic analysis performance."""

        analyzer = SemanticSimilarityAnalyzer()

        code1 = """
        async function fetchUserData(userId) {
            try {
                const response = await fetch(`/api/users/${userId}`);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const userData = await response.json();

                return {
                    user: userData,
                    lastFetched: new Date().toISOString(),
                    status: 'success'
                };
            } catch (error) {
                console.error('Failed to fetch user data:', error);
                return {
                    user: null,
                    lastFetched: new Date().toISOString(),
                    status: 'error',
                    error: error.message
                };
            }
        }
        """

        code2 = """
        const fetchUserData = async (userId) => {
            try {
                const response = await fetch(`/api/users/${userId}`);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const userData = await response.json();

                return {
                    user: userData,
                    lastFetched: new Date().toISOString(),
                    status: 'success'
                };
            } catch (error) {
                console.error('Failed to fetch user data:', error);
                return {
                    user: null,
                    lastFetched: new Date().toISOString(),
                    status: 'error',
                    error: error.message
                };
            }
        };
        """

        # Benchmark semantic similarity computation
        def analyze_semantic_similarity():
            return analyzer.analyze_similarity(code1, code2)

        similarity = benchmark(analyze_semantic_similarity)

        # Verify the result is reasonable
        assert 0 <= similarity <= 1

    @pytest.mark.benchmark
    def test_structural_analysis_performance(self, benchmark):
        """Benchmark structural analysis performance."""

        analyzer = QualityAnalyzer()

        code1 = """
        class UserManager {
            constructor(database) {
                this.db = database;
                this.cache = new Map();
            }

            async getUser(id) {
                if (this.cache.has(id)) {
                    return this.cache.get(id);
                }

                const user = await this.db.findById(id);

                if (user) {
                    this.cache.set(id, user);
                }

                return user;
            }

            async createUser(userData) {
                const user = await this.db.create(userData);
                this.cache.set(user.id, user);
                return user;
            }

            async updateUser(id, updates) {
                const user = await this.db.update(id, updates);

                if (user) {
                    this.cache.set(id, user);
                }

                return user;
            }

            async deleteUser(id) {
                await this.db.delete(id);
                this.cache.delete(id);
            }

            clearCache() {
                this.cache.clear();
            }
        }
        """

        code2 = """
        function UserManager(database) {
            this.db = database;
            this.cache = new Map();
        }

        UserManager.prototype.getUser = async function(id) {
            if (this.cache.has(id)) {
                return this.cache.get(id);
            }

            const user = await this.db.findById(id);

            if (user) {
                this.cache.set(id, user);
            }

            return user;
        };

        UserManager.prototype.createUser = async function(userData) {
            const user = await this.db.create(userData);
            this.cache.set(user.id, user);
            return user;
        };

        UserManager.prototype.updateUser = async function(id, updates) {
            const user = await this.db.update(id, updates);

            if (user) {
                this.cache.set(id, user);
            }

            return user;
        };

        UserManager.prototype.deleteUser = async function(id) {
            await this.db.delete(id);
            this.cache.delete(id);
        };

        UserManager.prototype.clearCache = function() {
            this.cache.clear();
        };
        """

        # Benchmark structural similarity computation
        def analyze_structural_similarity():
            return analyzer.analyze_structure(code1, code2)

        similarity = benchmark(analyze_structural_similarity)

        # Verify the result is reasonable
        assert 0 <= similarity <= 1

    @pytest.mark.benchmark
    def test_large_application_evaluation_performance(self, benchmark, temp_dir):
        """Benchmark evaluation of larger applications."""

        # Create a larger application structure
        golden_dir = temp_dir / "golden_app"
        generated_dir = temp_dir / "generated_app"

        golden_dir.mkdir()
        generated_dir.mkdir()

        # Create multiple components
        components = [
            ("UserList", "displays a list of users"),
            ("UserCard", "displays individual user information"),
            ("UserForm", "form for creating/editing users"),
            ("Navigation", "main navigation component"),
            ("Header", "page header component"),
        ]

        for component_name, description in components:
            golden_code = f"""
            import React, {{ useState, useEffect }} from 'react';

            const {component_name} = (props) => {{
                const [state, setState] = useState(null);
                const [loading, setLoading] = useState(true);
                const [error, setError] = useState(null);

                useEffect(() => {{
                    const loadData = async () => {{
                        try {{
                            setLoading(true);
                            const data = await props.fetchData();
                            setState(data);
                        }} catch (err) {{
                            setError(err.message);
                        }} finally {{
                            setLoading(false);
                        }}
                    }};

                    loadData();
                }}, [props.fetchData]);

                const handleAction = (action, payload) => {{
                    if (props.onAction) {{
                        props.onAction(action, payload);
                    }}
                }};

                if (loading) {{
                    return <div className="loading">Loading...</div>;
                }}

                if (error) {{
                    return <div className="error">Error: {{error}}</div>;
                }}

                return (
                    <div className="{component_name.lower()}">
                        <h2>{description}</h2>
                        <div className="content">
                            {{state && <pre>{{JSON.stringify(state, null, 2)}}</pre>}}
                        </div>
                        <button onClick={{() => handleAction('refresh')}}>
                            Refresh
                        </button>
                    </div>
                );
            }};

            export default {component_name};
            """

            generated_code = f"""
            import React, {{ useState, useEffect }} from 'react';

            function {component_name}(props) {{
                const [state, setState] = useState(null);
                const [loading, setLoading] = useState(true);
                const [error, setError] = useState(null);

                useEffect(function() {{
                    async function loadData() {{
                        try {{
                            setLoading(true);
                            const data = await props.fetchData();
                            setState(data);
                        }} catch (err) {{
                            setError(err.message);
                        }} finally {{
                            setLoading(false);
                        }}
                    }}

                    loadData();
                }}, [props.fetchData]);

                function handleAction(action, payload) {{
                    if (props.onAction) {{
                        props.onAction(action, payload);
                    }}
                }}

                if (loading) {{
                    return React.createElement('div', {{className: 'loading'}},
                        'Loading...');
                }}

                if (error) {{
                    return React.createElement('div', {{className: 'error'}},
                        'Error: ' + error);
                }}

                return React.createElement('div',
                    {{className: '{component_name.lower()}'}},
                    React.createElement('h2', null, '{description}'),
                    React.createElement('div', {{className: 'content'}},
                        state && React.createElement('pre', null,
                            JSON.stringify(state, null, 2))
                    ),
                    React.createElement('button', {{onClick: function() {{
                        handleAction('refresh'); }}}}, 'Refresh')
                );
            }}

            export default {component_name};
            """

            (golden_dir / f"{component_name}.jsx").write_text(golden_code)
            (generated_dir / f"{component_name}.jsx").write_text(generated_code)

        # Benchmark application evaluation
        def evaluate_application():
            return self.evaluator.evaluate(str(golden_dir), str(generated_dir))

        result = benchmark(evaluate_application)

        # Verify the result is valid
        assert result.overall_similarity > 0.4  # Should have reasonable similarity


class TestMemoryUsage:
    """Memory usage tests."""

    def test_memory_usage_large_files(self, temp_dir):
        """Test memory usage with large files."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Create a large file
        large_code = "function test() { return 'hello'; }\n" * 1000  # 1000 lines

        golden_file = temp_dir / "large_golden.js"
        generated_file = temp_dir / "large_generated.js"

        golden_file.write_text(large_code)
        generated_file.write_text(large_code)

        evaluator = UniversalCodeEvaluator()
        result = evaluator.evaluate(str(golden_file), str(generated_file))

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before

        # Memory increase should be reasonable (less than 500MB for this test)
        assert memory_increase < 500
        assert result.overall_similarity > 0.6  # Should be reasonably similar

    def test_memory_cleanup_batch_processing(self, temp_dir):
        """Test that memory is properly cleaned up during batch processing."""
        import gc
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_start = process.memory_info().rss / 1024 / 1024  # MB

        evaluator = UniversalCodeEvaluator()

        # Process multiple files in sequence
        for i in range(20):
            code = f"function test{i}() {{ return {i}; }}"

            golden_file = temp_dir / f"golden_{i}.js"
            generated_file = temp_dir / f"generated_{i}.js"

            golden_file.write_text(code)
            generated_file.write_text(code)

            _ = evaluator.evaluate(str(golden_file), str(generated_file))

            # Force garbage collection
            gc.collect()

            # Check memory usage doesn't grow excessively
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - memory_start

            # Memory should not increase more than 400MB during batch processing
            # (Adjusted based on realistic usage patterns and ML model memory
            # requirements)
            assert memory_increase < 400
