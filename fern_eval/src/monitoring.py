"""
Monitoring and metrics collection for production deployments.

This module provides performance monitoring, metrics collection,
and alerting capabilities for the evaluation framework.
"""

import logging
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point."""

    timestamp: float
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class EvaluationMetrics:
    """Metrics for a single evaluation."""

    duration_seconds: float
    model_name: Optional[str] = None
    evaluation_type: str = "unknown"
    similarity_score: float = 0.0
    cache_hit: bool = False
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class MetricsCollector:
    """
    Collects and aggregates performance metrics.

    Provides thread-safe metric collection with automatic aggregation
    and export capabilities for monitoring systems.
    """

    def __init__(self, max_points: int = 10000):
        """
        Initialize metrics collector.

        Args:
            max_points: Maximum number of metric points to retain
        """
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.evaluations: deque = deque(maxlen=max_points)
        self.lock = threading.Lock()
        self.start_time = time.time()

    def record_metric(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for the metric
        """
        with self.lock:
            point = MetricPoint(timestamp=time.time(), value=value, tags=tags or {})
            self.metrics[name].append(point)

    def record_evaluation(self, metrics: EvaluationMetrics) -> None:
        """
        Record evaluation metrics.

        Args:
            metrics: Evaluation metrics to record
        """
        with self.lock:
            self.evaluations.append(metrics)

        # Also record as individual metrics
        self.record_metric(
            "evaluation_duration",
            metrics.duration_seconds,
            {
                "model": metrics.model_name or "unknown",
                "type": metrics.evaluation_type,
                "error": "true" if metrics.error else "false",
            },
        )

        if not metrics.error:
            self.record_metric(
                "similarity_score",
                metrics.similarity_score,
                {
                    "model": metrics.model_name or "unknown",
                    "type": metrics.evaluation_type,
                },
            )

        self.record_metric("cache_hit", 1.0 if metrics.cache_hit else 0.0)

    def get_summary_stats(
        self, metric_name: str, window_seconds: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get summary statistics for a metric.

        Args:
            metric_name: Name of the metric
            window_seconds: Time window to analyze (None for all data)

        Returns:
            Dictionary with min, max, mean, count statistics
        """
        with self.lock:
            points = list(self.metrics[metric_name])

        if not points:
            return {"min": 0.0, "max": 0.0, "mean": 0.0, "count": 0}

        # Filter by time window if specified
        if window_seconds:
            cutoff_time = time.time() - window_seconds
            points = [p for p in points if p.timestamp >= cutoff_time]

        if not points:
            return {"min": 0.0, "max": 0.0, "mean": 0.0, "count": 0}

        values = [p.value for p in points]
        return {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "count": len(values),
        }

    def get_evaluation_summary(
        self, window_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get summary of evaluation performance.

        Args:
            window_seconds: Time window to analyze

        Returns:
            Dictionary with evaluation statistics
        """
        with self.lock:
            evaluations = list(self.evaluations)

        if not evaluations:
            return {"total_evaluations": 0, "error_rate": 0.0, "avg_duration": 0.0}

        # Filter by time window if specified
        if window_seconds:
            cutoff_time = time.time() - window_seconds
            evaluations = [e for e in evaluations if e.timestamp >= cutoff_time]

        if not evaluations:
            return {"total_evaluations": 0, "error_rate": 0.0, "avg_duration": 0.0}

        total = len(evaluations)
        errors = sum(1 for e in evaluations if e.error)
        durations = [e.duration_seconds for e in evaluations]

        # Group by model
        by_model = defaultdict(list)
        for eval_metric in evaluations:
            if eval_metric.model_name:
                by_model[eval_metric.model_name].append(eval_metric)

        model_stats = {}
        for model, model_evals in by_model.items():
            model_durations = [e.duration_seconds for e in model_evals]
            model_errors = sum(1 for e in model_evals if e.error)
            model_stats[model] = {
                "count": len(model_evals),
                "avg_duration": sum(model_durations) / len(model_durations),
                "error_rate": model_errors / len(model_evals),
            }

        return {
            "total_evaluations": total,
            "error_rate": errors / total,
            "avg_duration": sum(durations) / len(durations),
            "models": model_stats,
            "cache_hit_rate": sum(1 for e in evaluations if e.cache_hit) / total,
        }

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.

        Returns:
            Metrics in Prometheus text format
        """
        lines = []

        # Add help and type information
        lines.append("# HELP fern_evaluation_duration_seconds Duration of evaluations")
        lines.append("# TYPE fern_evaluation_duration_seconds histogram")

        lines.append("# HELP fern_similarity_score Similarity scores from evaluations")
        lines.append("# TYPE fern_similarity_score gauge")

        # Export recent metrics (last 1000 points)
        with self.lock:
            for metric_name, points in self.metrics.items():
                for point in list(points)[-1000:]:  # Last 1000 points
                    tags_str = ""
                    if point.tags:
                        tag_pairs = [f'{k}="{v}"' for k, v in point.tags.items()]
                        tags_str = "{" + ",".join(tag_pairs) + "}"

                    lines.append(
                        f"fern_{metric_name}{tags_str} {point.value} {int(point.timestamp * 1000)}"
                    )

        return "\n".join(lines)

    def export_json(self) -> str:
        """
        Export metrics in JSON format.

        Returns:
            Metrics in JSON format
        """
        data = {
            "uptime_seconds": time.time() - self.start_time,
            "summary": self.get_evaluation_summary(3600),  # Last hour
            "recent_metrics": {},
        }

        # Add recent metric summaries
        for metric_name in self.metrics:
            data["recent_metrics"][metric_name] = self.get_summary_stats(
                metric_name, 3600
            )

        return json.dumps(data, indent=2)


class PerformanceMonitor:
    """
    Context manager for monitoring function performance.

    Automatically records execution time and other metrics
    when used as a context manager or decorator.
    """

    def __init__(self, collector: MetricsCollector, operation_name: str, **tags):
        """
        Initialize performance monitor.

        Args:
            collector: Metrics collector instance
            operation_name: Name of the operation being monitored
            **tags: Additional tags for the metrics
        """
        self.collector = collector
        self.operation_name = operation_name
        self.tags = tags
        self.start_time = None
        self.error = None

    def __enter__(self):
        """Start monitoring."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop monitoring and record metrics."""
        if self.start_time:
            duration = time.time() - self.start_time
            error_occurred = exc_type is not None

            tags = self.tags.copy()
            tags["operation"] = self.operation_name
            tags["error"] = "true" if error_occurred else "false"

            self.collector.record_metric("operation_duration", duration, tags)

            if error_occurred:
                tags["error_type"] = exc_type.__name__
                self.collector.record_metric("operation_error", 1.0, tags)

    def __call__(self, func: Callable) -> Callable:
        """Use as decorator."""

        def wrapper(*args, **kwargs):
            with PerformanceMonitor(self.collector, self.operation_name, **self.tags):
                return func(*args, **kwargs)

        return wrapper


class AlertManager:
    """
    Simple alerting system for monitoring evaluation performance.

    Checks metrics against thresholds and triggers alerts when
    conditions are met.
    """

    def __init__(self, collector: MetricsCollector):
        """
        Initialize alert manager.

        Args:
            collector: Metrics collector to monitor
        """
        self.collector = collector
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds = {
            "error_rate": 0.05,  # 5% error rate
            "avg_duration": 30.0,  # 30 seconds average duration
            "cache_hit_rate_min": 0.3,  # Minimum 30% cache hit rate
        }

    def check_alerts(self, window_seconds: int = 300) -> List[Dict[str, Any]]:
        """
        Check for alert conditions.

        Args:
            window_seconds: Time window to check

        Returns:
            List of active alerts
        """
        alerts = []
        summary = self.collector.get_evaluation_summary(window_seconds)

        # Check error rate
        if summary["error_rate"] > self.thresholds["error_rate"]:
            alerts.append(
                {
                    "type": "high_error_rate",
                    "severity": "warning",
                    "message": f"Error rate {summary['error_rate']:.1%} exceeds threshold {self.thresholds['error_rate']:.1%}",
                    "value": summary["error_rate"],
                    "threshold": self.thresholds["error_rate"],
                    "timestamp": time.time(),
                }
            )

        # Check average duration
        if summary["avg_duration"] > self.thresholds["avg_duration"]:
            alerts.append(
                {
                    "type": "slow_evaluations",
                    "severity": "warning",
                    "message": f"Average duration {summary['avg_duration']:.1f}s exceeds threshold {self.thresholds['avg_duration']:.1f}s",
                    "value": summary["avg_duration"],
                    "threshold": self.thresholds["avg_duration"],
                    "timestamp": time.time(),
                }
            )

        # Check cache hit rate
        if summary["cache_hit_rate"] < self.thresholds["cache_hit_rate_min"]:
            alerts.append(
                {
                    "type": "low_cache_hit_rate",
                    "severity": "info",
                    "message": f"Cache hit rate {summary['cache_hit_rate']:.1%} below threshold {self.thresholds['cache_hit_rate_min']:.1%}",
                    "value": summary["cache_hit_rate"],
                    "threshold": self.thresholds["cache_hit_rate_min"],
                    "timestamp": time.time(),
                }
            )

        return alerts


# Global monitoring instances
_metrics_collector: Optional[MetricsCollector] = None
_alert_manager: Optional[AlertManager] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_alert_manager() -> AlertManager:
    """Get or create global alert manager."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(get_metrics_collector())
    return _alert_manager


def monitor_evaluation(
    operation_name: str = "evaluation", **tags
) -> PerformanceMonitor:
    """
    Create a performance monitor for evaluations.

    Args:
        operation_name: Name of the operation
        **tags: Additional tags

    Returns:
        Performance monitor context manager
    """
    return PerformanceMonitor(get_metrics_collector(), operation_name, **tags)


def record_evaluation_metrics(
    duration: float,
    model_name: Optional[str] = None,
    evaluation_type: str = "unknown",
    similarity_score: float = 0.0,
    cache_hit: bool = False,
    error: Optional[str] = None,
) -> None:
    """
    Record evaluation metrics.

    Args:
        duration: Evaluation duration in seconds
        model_name: Name of the model being evaluated
        evaluation_type: Type of evaluation
        similarity_score: Similarity score result
        cache_hit: Whether cache was hit
        error: Error message if evaluation failed
    """
    metrics = EvaluationMetrics(
        duration_seconds=duration,
        model_name=model_name,
        evaluation_type=evaluation_type,
        similarity_score=similarity_score,
        cache_hit=cache_hit,
        error=error,
    )
    get_metrics_collector().record_evaluation(metrics)
