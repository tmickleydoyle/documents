# Universal Code Evaluation Framework

A framework for evaluating AI-generated code using semantic similarity analysis and multi-dimensional quality metrics. This is a demo project showcasing automated code evaluation capabilities.

## 🎯 What This Does

Automatically evaluates how well AI-generated code matches reference code across multiple quality dimensions:
- **Semantic Similarity**: Understanding code meaning using specialized code models (UniXcoder)
- **Functional Equivalence**: Does the code produce the same output?
- **Structural Similarity**: Code organization and patterns  
- **Style Consistency**: Formatting and conventions
- **Maintainability**: Code quality and readability
- **Accessibility**: UI/UX considerations

## 🚀 Quick Start

### Installation

```bash
cd fern_eval

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### Command Line Interface

```bash
# Evaluate two applications (basic mode)
python cli.py evaluate --golden sample_data/golden_standard --generated sample_data/generated_code

# Use quality-focused evaluation (rewards architectural improvements)
python cli.py evaluate --golden sample_data/golden_standard --generated sample_data/complex_quality_generated --quality-focused

# Save results to JSON
python cli.py evaluate --golden sample_data/golden_standard --generated sample_data/generated_code --json results.json
```

#### Python API

```python
from src.universal_evaluator import UniversalCodeEvaluator

# Traditional similarity-focused evaluation
evaluator = UniversalCodeEvaluator()
result = evaluator.evaluate("sample_data/golden_standard", "sample_data/generated_code")

# Quality-focused evaluation (rewards sophisticated implementations)
evaluator = UniversalCodeEvaluator(quality_focused=True)
result = evaluator.evaluate("sample_data/golden_standard", "sample_data/complex_quality_generated")

print(f"Overall Similarity: {result.overall_similarity:.3f}")
print(f"Maintainability: {result.maintainability_score:.3f}")
print(f"Accessibility: {result.accessibility_score:.3f}")
```

## 📊 Evaluation Modes

### Traditional Mode (Similarity-Focused)
- Emphasizes semantic and functional similarity to reference code
- Good for basic correctness evaluation
- May penalize sophisticated architectural improvements

### Quality-Focused Mode
- Rewards architectural enhancements like error handling, performance optimizations
- Recognizes comprehensive testing, accessibility improvements, type safety
- Better for evaluating complex-quality, production-ready code

**Example Results:**
```
Traditional Mode:
  Basic Code:       0.785
  Complex Quality Code: 0.553  ❌ Quality penalized

Quality-Focused Mode:  
  Basic Code:       0.777
  Complex Quality Code: 0.695  ✅ Quality rewarded
```

## 📋 Example Output

### Console Output
```
======================================================================
UNIVERSAL CODE EVALUATION REPORT
======================================================================
Evaluation Type: application
Golden Application: sample_data/golden_standard
Generated Application: sample_data/complex_quality_generated

OVERALL SCORE: 0.695
```

### JSON Output
```json
{
  "overall_similarity": 0.695,
  "functional_equivalence": 0.333,
  "structural_similarity": 0.456,
  "style_consistency": 0.823,
  "maintainability_score": 1.000,
  "accessibility_score": 0.889,
  "architectural_enhancement_score": 0.000,
  "detailed_analysis": {
    "semantic_similarity": 0.234,
    "weights_used": {
      "semantic": 0.15,
      "functional": 0.20,
      "structural": 0.15,
      "style": 0.15,
      "maintainability": 0.20,
      "accessibility": 0.10,
      "architectural_enhancement": 0.05
    }
  }
}
```

## 🏗️ Core Components

1. **Universal Parser**: Language-agnostic code analysis
2. **Semantic Similarity Engine**: ML-powered code understanding  
3. **Quality Analyzer**: Multi-dimensional quality assessment
4. **Matching System**: Intelligent file pairing for applications
5. **Evaluation Engine**: Orchestrates the complete evaluation pipeline

## 🎯 Advanced Usage

### Custom Evaluation Weights

```python
# Define custom weights for specific use cases
custom_weights = {
    'semantic': 0.30,
    'functional': 0.30, 
    'structural': 0.15,
    'style': 0.10,
    'maintainability': 0.10,
    'accessibility': 0.05
}

evaluator = UniversalCodeEvaluator(weights=custom_weights)
```

### Batch Evaluation

```bash
python cli.py batch --golden sample_data/golden_standard \
  --models sample_data/generated_code sample_data/complex_quality_generated \
  --names "basic" "complex_quality" \
  --report batch_results.txt
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test files
python -m pytest tests/test_analyzers.py -v
```

## 📊 Performance

- **Processing Speed**: ~15ms per file evaluation (may be slightly slower with UniXcoder)
- **Memory Usage**: <500MB for application evaluation (increased due to larger model)
- **Model Size**: ~500MB (UniXcoder) with ~90MB fallback (sentence-transformers)
- **Accuracy**: Significantly improved semantic similarity for code evaluation
- **Supported Languages**: JavaScript, TypeScript, Python, Java, C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin

## 🔧 Configuration

The framework supports various configuration options through `src/config.py`:

```python
# Quality-focused weights (reward architectural improvements)
QUALITY_FOCUSED_WEIGHTS = {
    "semantic": 0.15,
    "functional": 0.20,
    "structural": 0.15, 
    "style": 0.15,
    "maintainability": 0.20,
    "accessibility": 0.10,
    "architectural_enhancement": 0.05,
}

# Model configuration - Uses UniXcoder for superior code understanding
DEFAULT_EMBEDDING_MODEL = "microsoft/unixcoder-base"
FALLBACK_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

### Model Details

The framework now uses **Microsoft UniXcoder** as the default semantic similarity model:
- **Superior Code Understanding**: Pre-trained on code, comments, and AST data
- **Multi-modal Training**: Understands both code structure and natural language
- **Better Similarity Detection**: Specialized for programming language semantics
- **Fallback Support**: Automatically falls back to sentence-transformers if needed

## 📁 Project Structure

```
fern_eval/
├── src/                      # Core framework code
│   ├── analyzers.py         # Semantic similarity and quality analysis
│   ├── universal_evaluator.py  # Main evaluation orchestrator
│   ├── config.py            # Configuration and weights
│   └── models.py            # Data models and result structures
├── sample_data/             # Example datasets
│   ├── golden_standard/     # Reference implementations
│   ├── generated_code/      # Basic AI-generated code
│   └── complex_quality_generated/  # Enhanced implementations
├── tests/                   # Test suite
├── cli.py                   # Command-line interface
└── README.md               # This file
```

This is a demonstration project showing how to build comprehensive code evaluation systems for AI-generated code.