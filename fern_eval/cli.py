"""
Command-line interface for the Universal Code Evaluation Framework.

This module provides a CLI for evaluating any type of application in any
programming language.
"""

import argparse
import json
import sys
from typing import Any, Dict, Optional

from src.exceptions import FernEvaluationError
from src.models import EvaluationResult
from src.universal_evaluator import UniversalCodeEvaluator
from src.utils import setup_logging


def convert_results_for_json(results: Any) -> Any:
    """Convert EvaluationResult objects to dictionaries for JSON serialization."""
    if isinstance(results, EvaluationResult):
        return results.to_dict()
    elif isinstance(results, dict):
        return {k: convert_results_for_json(v) for k, v in results.items()}
    elif isinstance(results, list):
        return [convert_results_for_json(item) for item in results]
    elif isinstance(results, set):
        return list(results)  # Convert sets to lists for JSON serialization
    else:
        return results


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Universal Code Evaluation Framework - Compare any type of "
        "application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two single files (any language)
  python cli.py evaluate --golden main.py --generated main.py

  # Compare two complete applications (any structure)
  python cli.py evaluate --golden ./original_app --generated ./generated_app --type app

  # Generate detailed report
  python cli.py evaluate --golden app.js --generated app.js --report output.txt

  # Run batch evaluation
  python cli.py batch --golden golden_app --models model1_app model2_app model3_app

  # Run performance benchmarks
  python cli.py benchmark --iterations 100
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate code samples")
    eval_parser.add_argument(
        "--golden", required=True, help="Path to golden standard (file or directory)"
    )
    eval_parser.add_argument(
        "--generated", required=True, help="Path to generated code (file or directory)"
    )
    eval_parser.add_argument(
        "--type",
        choices=["file", "app", "auto"],
        default="auto",
        help="Evaluation type (default: auto-detect)",
    )
    eval_parser.add_argument("--report", help="Path to save detailed report")
    eval_parser.add_argument("--json", help="Path to save results as JSON")
    eval_parser.add_argument(
        "--weights", help="Path to JSON file with custom evaluation weights"
    )

    # Batch evaluation command
    batch_parser = subparsers.add_parser("batch", help="Batch evaluate multiple models")
    batch_parser.add_argument("--golden", required=True, help="Path to golden standard")
    batch_parser.add_argument(
        "--models", nargs="+", required=True, help="Paths to model outputs"
    )
    batch_parser.add_argument(
        "--names", nargs="+", help="Custom names for models (optional)"
    )
    batch_parser.add_argument("--report", help="Path to save batch report")
    batch_parser.add_argument("--json", help="Path to save results as JSON")

    # Benchmark command
    benchmark_parser = subparsers.add_parser(
        "benchmark", help="Run performance benchmarks"
    )
    benchmark_parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Number of iterations for benchmarks (default: 50)",
    )
    benchmark_parser.add_argument("--report", help="Path to save benchmark report")

    # Match analysis command
    match_parser = subparsers.add_parser(
        "match-analysis", help="Analyze file matching capabilities"
    )
    match_parser.add_argument(
        "--golden", required=True, help="Path to golden standard application directory"
    )
    match_parser.add_argument(
        "--generated", required=True, help="Path to generated application directory"
    )
    match_parser.add_argument("--output", help="Output file for match analysis report")
    match_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Generate detailed match analysis with file signatures",
    )

    # Global options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--version", action="version", version="Fern Model Evaluation Framework 1.0.0"
    )

    return parser


def load_custom_weights(weights_path: str) -> Optional[Dict[str, float]]:
    """Load custom evaluation weights from JSON file."""
    try:
        with open(weights_path, "r") as f:
            weights = json.load(f)

        # Validate weights
        expected_keys = {
            "semantic",
            "functional",
            "structural",
            "style",
            "maintainability",
            "accessibility",
        }
        if not all(key in weights for key in expected_keys):
            print(f"Warning: Missing weight keys. Expected: {expected_keys}")
            return None

        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            print(f"Warning: Weights sum to {total}, not 1.0. They will be normalized.")

        return weights
    except Exception as e:
        print(f"Error loading weights from {weights_path}: {e}")
        return None


def handle_evaluate_command(args) -> int:
    """Handle the evaluate command."""
    try:
        # Load custom weights if provided
        weights = None
        if args.weights:
            weights = load_custom_weights(args.weights)

        # Initialize evaluator
        evaluator = UniversalCodeEvaluator(weights=weights, log_level=args.log_level)

        # Run evaluation
        print(f"Evaluating: {args.golden} vs {args.generated}")
        results = evaluator.evaluate(args.golden, args.generated, args.type)

        # Generate and display report
        report = evaluator.generate_report(results, args.report)
        print(report)

        # Save JSON results if requested
        if args.json:
            # Convert EvaluationResult objects to dictionaries for proper JSON
            # serialization
            try:
                json_results = convert_results_for_json(results)
                with open(args.json, "w") as f:
                    json.dump(json_results, f, indent=2, default=str)
                print(f"\\nResults saved to {args.json}")
            except Exception as e:
                print(f"Warning: Could not save JSON results: {e}")
                # Save with basic string conversion as fallback
                try:
                    with open(args.json, "w") as f:
                        json.dump(str(results), f, indent=2)
                    print(f"\\nResults saved to {args.json} (simplified format)")
                except Exception as e2:
                    print(f"Error: Could not save results in any format: {e2}")

        return 0

    except FernEvaluationError as e:
        print(f"Evaluation error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


def handle_batch_command(args) -> int:
    """Handle the batch command."""
    try:
        # Prepare model mapping
        model_names = args.names or [f"model_{i+1}" for i in range(len(args.models))]

        if len(model_names) != len(args.models):
            print("Error: Number of model names must match number of model paths")
            return 1

        model_outputs = dict(zip(model_names, args.models))

        # Initialize evaluator
        evaluator = UniversalCodeEvaluator(log_level=args.log_level)

        # Run batch evaluation
        print(f"Running batch evaluation with {len(model_outputs)} models...")
        batch_results = evaluator.evaluate_batch(args.golden, model_outputs)

        # Display results
        print("\\n" + "=" * 60)
        print("BATCH EVALUATION RESULTS")
        print("=" * 60)

        for i, (model_name, score) in enumerate(batch_results.rankings, 1):
            print(f"{i}. {model_name}: {score:.3f}")

        if batch_results.summary_statistics:
            stats = batch_results.summary_statistics
            print("\\nSummary Statistics:")
            print(f"  Mean score: {stats['mean_score']:.3f}")
            print(f"  Median score: {stats['median_score']:.3f}")
            print(f"  Standard deviation: {stats['std_dev']:.3f}")
            print(f"  Range: {stats['min_score']:.3f} - {stats['max_score']:.3f}")

        print(f"\\nBest model: {batch_results.get_best_model()}")

        # Save results if requested
        if args.json:
            # Convert to serializable format
            serializable_results = {
                "rankings": batch_results.rankings,
                "summary_statistics": batch_results.summary_statistics,
                "best_model": batch_results.get_best_model(),
                "worst_model": batch_results.get_worst_model(),
            }

            with open(args.json, "w") as f:
                json.dump(serializable_results, f, indent=2)
            print(f"\\nResults saved to {args.json}")

        return 0

    except FernEvaluationError as e:
        print(f"Batch evaluation error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


def handle_benchmark_command(args) -> int:
    """Handle the benchmark command."""
    try:
        from benchmarks import PerformanceBenchmark

        print("Running performance benchmarks...")
        benchmark = PerformanceBenchmark()

        # Run individual benchmarks with custom iterations
        results = {}
        results["single_file"] = benchmark.benchmark_single_file_evaluation(
            args.iterations
        )
        results["embeddings"] = benchmark.benchmark_embedding_computation(
            args.iterations // 2
        )
        results["batch"] = benchmark.benchmark_batch_evaluation(5, 10)

        # Calculate summary
        results["summary"] = {
            "framework_overhead": results["single_file"]["mean_time"],
            "embedding_overhead": results["embeddings"]["mean_time"],
            "throughput_files_per_second": results["batch"]["files_per_second"],
            "recommended_batch_size": min(
                100, max(10, int(1.0 / results["single_file"]["mean_time"]))
            ),
        }

        # Print report
        benchmark.print_benchmark_report(results)

        # Save report if requested
        if args.report:
            with open(args.report, "w") as f:
                f.write(
                    "Fern Model Evaluation Framework - Performance Benchmark Report\\n"
                )
                f.write("=" * 70 + "\\n\\n")

                # Single file evaluation
                sf = results["single_file"]
                f.write(f"Single File Evaluation ({sf['iterations']} iterations):\\n")
                f.write(f"  Mean time: {sf['mean_time']*1000:.2f}ms\\n")
                f.write(f"  Median time: {sf['median_time']*1000:.2f}ms\\n")
                f.write(
                    f"  Min/Max: {sf['min_time']*1000:.2f}ms / "
                    f"{sf['max_time']*1000:.2f}ms\\n"
                )
                f.write(f"  Std deviation: {sf['std_dev']*1000:.2f}ms\\n\\n")

                # Add other sections...

            print(f"\\nBenchmark report saved to {args.report}")

        return 0

    except ImportError:
        print("Error: Benchmark module not available")
        return 1
    except Exception as e:
        print(f"Benchmark error: {e}")
        return 1


def handle_match_analysis_command(args) -> int:
    """Handle the match analysis command."""
    try:
        from src.match_analysis import MatchAnalyzer

        # Initialize match analyzer
        analyzer = MatchAnalyzer(log_level=args.log_level)

        # Run match analysis
        print(f"Analyzing match: {args.golden} vs {args.generated}")
        analysis_results = analyzer.analyze(args.golden, args.generated, args.detailed)

        # Display results
        print("\\n" + "=" * 60)
        print("MATCH ANALYSIS RESULTS")
        print("=" * 60)
        print(analysis_results["summary"])

        if args.detailed and "file_signatures" in analysis_results:
            print("\\nFile Signatures:")
            for file, signature in analysis_results["file_signatures"].items():
                print(f"  {file}: {signature}")

        # Save report if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(analysis_results, f, indent=2)
            print(f"\\nMatch analysis report saved to {args.output}")

        return 0

    except Exception as e:
        print(f"Error during match analysis: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level)

    # Handle commands
    if args.command == "evaluate":
        return handle_evaluate_command(args)
    elif args.command == "batch":
        return handle_batch_command(args)
    elif args.command == "benchmark":
        return handle_benchmark_command(args)
    elif args.command == "match-analysis":
        return handle_match_analysis_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
