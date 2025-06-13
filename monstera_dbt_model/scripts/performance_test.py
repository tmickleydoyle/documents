#!/usr/bin/env python3
"""
Performance testing script for Monstera dbt models.
This script tests query performance, data quality, and resource utilization.
"""

import argparse
import logging
import os
import statistics
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, List

import psutil
import psycopg2
import psycopg2.extras


@dataclass
class PerformanceResult:
    """Data class for storing performance test results."""

    model_name: str
    query: str
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    row_count: int
    memory_usage_mb: float
    cpu_percent: float
    iterations: int
    success_rate: float


class PerformanceTester:
    """Main performance testing class."""

    def __init__(self, db_config: Dict[str, Any]):
        """Initialize performance tester with database configuration."""
        self.db_config = db_config
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("performance_test.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        return logging.getLogger(__name__)

    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            yield conn
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def run_query_test(
        self, model_name: str, query: str, iterations: int = 10
    ) -> PerformanceResult:
        """Run performance test for a specific query."""
        self.logger.info(f"Starting performance test for {model_name}")

        times = []
        row_counts = []
        memory_usage = []
        cpu_usage = []
        successful_runs = 0

        for i in range(iterations):
            try:
                # Monitor system resources before query
                process = psutil.Process()
                memory_before = process.memory_info().rss / 1024 / 1024  # MB
                cpu_before = process.cpu_percent()

                start_time = time.time()

                with self.get_db_connection() as conn:
                    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                        cur.execute(query)
                        results = cur.fetchall()
                        row_count = len(results)

                execution_time = time.time() - start_time

                # Monitor system resources after query
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                cpu_after = process.cpu_percent()

                times.append(execution_time)
                row_counts.append(row_count)
                memory_usage.append(memory_after - memory_before)
                cpu_usage.append(cpu_after - cpu_before)
                successful_runs += 1

                self.logger.debug(
                    f"{model_name} iteration {i+1}: {execution_time: .2f}s, "
                    f"{row_count} rows, {memory_after - memory_before: .1f}MB memory"
                )

            except Exception as e:
                self.logger.error(f"{model_name} iteration {i+1} failed: {e}")
                continue

        if not times:
            raise RuntimeError(f"All iterations failed for {model_name}")

        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        avg_memory = statistics.mean(memory_usage) if memory_usage else 0
        avg_cpu = statistics.mean(cpu_usage) if cpu_usage else 0
        avg_row_count = int(statistics.mean(row_counts)) if row_counts else 0
        success_rate = successful_runs / iterations * 100

        result = PerformanceResult(
            model_name=model_name,
            query=query,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            row_count=avg_row_count,
            memory_usage_mb=avg_memory,
            cpu_percent=avg_cpu,
            iterations=iterations,
            success_rate=success_rate,
        )

        self.logger.info(
            f"{model_name} completed: Avg {avg_time: .2f}s, "
            f"Min {min_time: .2f}s, Max {max_time: .2f}s, "
            f"Success rate {success_rate: .1f}%"
        )

        return result

    def run_data_quality_tests(self) -> Dict[str, Any]:
        """Run data quality and consistency tests."""
        self.logger.info("Running data quality tests")

        quality_tests = {
            "row_count_consistency": """
                SELECT
                    'bronze.events' as table_name,
                    COUNT(*) as row_count
                FROM bronze.events
                UNION ALL
                SELECT
                    'silver.enriched_events' as table_name,
                    COUNT(*) as row_count
                FROM silver.enriched_events
            """,
            "data_freshness": """
                SELECT
                    'bronze.events' as table_name,
                    MAX(event_date) as latest_date,
                    CURRENT_DATE - MAX(event_date) as days_stale
                FROM bronze.events
                UNION ALL
                SELECT
                    'silver.enriched_events' as table_name,
                    MAX(event_date) as latest_date,
                    CURRENT_DATE - MAX(event_date) as days_stale
                FROM silver.enriched_events
            """,
            "null_value_check": """
                SELECT
                    'bronze.events.user_id' as field,
                    COUNT(*) as total_rows,
                    COUNT(user_id) as non_null_rows,
                    (COUNT(*) - COUNT(user_id)) * 100.0 / COUNT(*) as null_percentage
                FROM bronze.events
                UNION ALL
                SELECT
                    'bronze.events.event_type' as field,
                    COUNT(*) as total_rows,
                    COUNT(event_type) as non_null_rows,
                    (COUNT(*) - COUNT(event_type)) * 100.0 / COUNT(*) as null_percentage
                FROM bronze.events
            """,
            "duplicate_check": """
                SELECT
                    'bronze.events' as table_name,
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT event_id) as unique_rows,
                    COUNT(*) - COUNT(DISTINCT event_id) as duplicates
                FROM bronze.events
            """,
        }

        results = {}

        for test_name, query in quality_tests.items():
            try:
                with self.get_db_connection() as conn:
                    with conn.cursor(
                        cursor_factory=psycopg2.extras.RealDictCursor
                    ) as cur:
                        cur.execute(query)
                        results[test_name] = cur.fetchall()

                self.logger.info(f"Data quality test '{test_name}' completed")

            except Exception as e:
                self.logger.error(f"Data quality test '{test_name}' failed: {e}")
                results[test_name] = {"error": str(e)}

        return results

    def run_concurrent_load_test(
        self,
        queries: Dict[str, str],
        concurrent_users: int = 5,
        duration_seconds: int = 60,
    ) -> Dict[str, Any]:
        """Run concurrent load test simulating multiple users."""
        import concurrent.futures
        import threading

        self.logger.info(
            f"Starting concurrent load test: {concurrent_users} users, "
            f"{duration_seconds} seconds"
        )

        results = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0,
            "max_response_time": 0,
            "min_response_time": float("inf"),
            "queries_per_second": 0,
        }

        all_times = []
        lock = threading.Lock()

        def worker():
            """Worker function for concurrent execution."""
            start_time = time.time()

            while time.time() - start_time < duration_seconds:
                for model_name, query in queries.items():
                    try:
                        query_start = time.time()

                        with self.get_db_connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute(query)
                                cur.fetchall()

                        query_time = time.time() - query_start

                        with lock:
                            all_times.append(query_time)
                            results["total_queries"] += 1
                            results["successful_queries"] += 1

                    except Exception as e:
                        with lock:
                            results["total_queries"] += 1
                            results["failed_queries"] += 1

                        self.logger.debug(f"Concurrent query failed: {e}")

        # Run concurrent workers
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrent_users
        ) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_users)]
            concurrent.futures.wait(futures)

        # Calculate final statistics
        if all_times:
            results["avg_response_time"] = statistics.mean(all_times)
            results["max_response_time"] = max(all_times)
            results["min_response_time"] = min(all_times)
            results["queries_per_second"] = len(all_times) / duration_seconds

        self.logger.info(
            f"Concurrent load test completed: "
            f"{results['successful_queries']}/{results['total_queries']} "
            f"successful queries, {results['queries_per_second']: .2f} QPS"
        )

        return results


def get_test_queries() -> Dict[str, str]:
    """Get predefined test queries for different models."""
    return {
        "bronze_events_count": """
            SELECT COUNT(*) as event_count
            FROM bronze.events
            WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
        """,
        "bronze_events_recent": """
            SELECT entity_id, event_type, timestamp
            FROM bronze.events
            WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY timestamp DESC
            LIMIT 1000
        """,
        "silver_enriched_events": """
            SELECT
                e.event_type,
                COUNT(*) as event_count,
                COUNT(DISTINCT e.entity_id) as unique_entities
            FROM public_silver.silver_events_enriched e
            WHERE e.event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY e.event_type
            ORDER BY event_count DESC
        """,
        "gold_overall_metrics": """
            SELECT *
            FROM public_gold.gold_overall_metrics
            WHERE metric_date >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY metric_date DESC
        """,
        "gold_segment_metrics": """
            SELECT
                country,
                account_type,
                SUM(monthly_active_users) as total_mau
            FROM public_gold.gold_segment_metrics
            WHERE event_month >= date_trunc('month', CURRENT_DATE - INTERVAL '7 days')
            GROUP BY country, account_type
            ORDER BY total_mau DESC
            LIMIT 100
        """,
        "gold_activity_metrics": """
            SELECT
                event_type,
                COUNT(*) as occurrences,
                AVG(event_count) as avg_events
            FROM public_gold.gold_activity_metrics
            WHERE event_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY event_type
            ORDER BY occurrences DESC
        """,
    }


def print_results_summary(results: List[PerformanceResult]):
    """Print a formatted summary of performance test results."""
    print("\n" + "=" * 80)
    print("PERFORMANCE TEST RESULTS SUMMARY")
    print("=" * 80)

    # Sort by average time (slowest first)
    sorted_results = sorted(results, key=lambda x: x.avg_time, reverse=True)

    print(
        f"{'Model': <25} | {'Avg Time': <10} | {'Min/Max': <12} | "
        f"{'Rows': <8} | {'Success%': <8}"
    )
    print("-" * 80)

    for result in sorted_results:
        print(
            f"{result.model_name: <25} | "
            f"{result.avg_time: >8.2f}s | "
            f"{result.min_time: >5.2f}/{result.max_time: <5.2f}s | "
            f"{result.row_count: >7} | "
            f"{result.success_rate: >7.1f}%"
        )

    # Performance analysis
    print("\n" + "=" * 80)
    print("PERFORMANCE ANALYSIS")
    print("=" * 80)

    total_avg_time = sum(r.avg_time for r in results)
    slowest = max(results, key=lambda x: x.avg_time)
    fastest = min(results, key=lambda x: x.avg_time)

    print(f"Total execution time: {total_avg_time: .2f}s")
    print(f"Slowest query: {slowest.model_name} ({slowest.avg_time: .2f}s)")
    print(f"Fastest query: {fastest.model_name} ({fastest.avg_time: .2f}s)")

    # Identify performance issues
    performance_threshold = 5.0  # seconds
    slow_queries = [r for r in results if r.avg_time > performance_threshold]

    if slow_queries:
        print(f"\nSlow queries (>{performance_threshold}s):")
        for query in slow_queries:
            print(f"  - {query.model_name}: {query.avg_time:.2f}s")

    # Success rate analysis
    failed_queries = [r for r in results if r.success_rate < 100]
    if failed_queries:
        print("\nQueries with failures:")
        for query in failed_queries:
            print(f"  - {query.model_name}: {query.success_rate:.1f}% success rate")


def main():
    """Main function to run performance tests."""
    parser = argparse.ArgumentParser(description="Monstera DBT Performance Testing")
    parser.add_argument(
        "--iterations", type=int, default=10, help="Number of iterations per test"
    )
    parser.add_argument(
        "--concurrent-users",
        type=int,
        default=5,
        help="Number of concurrent users for load test",
    )
    parser.add_argument(
        "--load-test-duration",
        type=int,
        default=60,
        help="Load test duration in seconds",
    )
    parser.add_argument(
        "--skip-load-test", action="store_true", help="Skip concurrent load testing"
    )
    parser.add_argument(
        "--skip-quality-test", action="store_true", help="Skip data quality testing"
    )

    args = parser.parse_args()

    # Database configuration from environment variables
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "user": os.getenv("DB_USER", "tmickleydoyle"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "monstera_demo"),
    }

    # Initialize performance tester
    tester = PerformanceTester(db_config)

    try:
        # Test database connection
        with tester.get_db_connection():
            tester.logger.info("Database connection successful")

        # Get test queries
        test_queries = get_test_queries()

        # Run individual query performance tests
        results = []
        for model_name, query in test_queries.items():
            try:
                result = tester.run_query_test(model_name, query, args.iterations)
                results.append(result)
            except Exception as e:
                tester.logger.error(f"Performance test failed for {model_name}: {e}")

        # Print results summary
        if results:
            print_results_summary(results)

        # Run data quality tests
        if not args.skip_quality_test:
            quality_results = tester.run_data_quality_tests()
            print("\n" + "=" * 80)
            print("DATA QUALITY TEST RESULTS")
            print("=" * 80)
            for test_name, test_result in quality_results.items():
                print(f"\n{test_name}:")
                if isinstance(test_result, list):
                    for row in test_result:
                        print(f"  {dict(row)}")
                else:
                    print(f"  {test_result}")

        # Run concurrent load test
        if not args.skip_load_test:
            load_test_queries = {
                k: v for k, v in list(test_queries.items())[:3]  # Use first 3 queries
            }
            load_results = tester.run_concurrent_load_test(
                load_test_queries, args.concurrent_users, args.load_test_duration
            )

            print("\n" + "=" * 80)
            print("CONCURRENT LOAD TEST RESULTS")
            print("=" * 80)
            print(f"Duration: {args.load_test_duration} seconds")
            print(f"Concurrent users: {args.concurrent_users}")
            print(f"Total queries: {load_results['total_queries']}")
            print(f"Successful queries: {load_results['successful_queries']}")
            print(f"Failed queries: {load_results['failed_queries']}")
            print(f"Queries per second: {load_results['queries_per_second']: .2f}")
            print(f"Average response time: {load_results['avg_response_time']: .2f}s")
            print(f"Max response time: {load_results['max_response_time']: .2f}s")

        tester.logger.info("Performance testing completed successfully")

    except Exception as e:
        tester.logger.error(f"Performance testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
