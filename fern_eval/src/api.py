"""
FastAPI web service for production AB testing of coding models.

This module provides REST API endpoints for evaluating and comparing
multiple AI coding models in production environments.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import uvicorn

from .universal_evaluator import UniversalCodeEvaluator
from .cache import get_embedding_cache

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Fern Code Evaluation API",
    description="Production API for AB testing AI coding models",
    version="1.0.0",
)

# Global evaluator instance
evaluator = UniversalCodeEvaluator()


class ModelComparisonRequest(BaseModel):
    """Request model for comparing multiple AI models."""

    golden_standard: str = Field(..., description="Path to golden standard code")
    models: Dict[str, str] = Field(
        ..., description="Dict mapping model names to their output paths"
    )
    evaluation_type: str = Field(
        "auto", description="Type of evaluation: 'file', 'app', or 'auto'"
    )
    max_workers: Optional[int] = Field(None, description="Maximum parallel workers")


class ModelComparisonResponse(BaseModel):
    """Response model for model comparison results."""

    winner: Optional[str]
    confidence: float
    rankings: List[tuple]
    summary_statistics: Dict[str, float]
    evaluation_time_seconds: float
    total_models: int


class SingleEvaluationRequest(BaseModel):
    """Request model for single file/app evaluation."""

    golden_path: str = Field(..., description="Path to golden standard")
    generated_path: str = Field(..., description="Path to generated code")
    evaluation_type: str = Field("auto", description="Type of evaluation")


class SingleEvaluationResponse(BaseModel):
    """Response model for single evaluation."""

    overall_similarity: float
    functional_equivalence: float
    structural_similarity: float
    style_consistency: float
    evaluation_type: str
    evaluation_time_seconds: float


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics."""

    total_entries: int
    total_size_mb: float
    cache_dir: str
    max_size_mb: float


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/evaluate", response_model=SingleEvaluationResponse)
async def evaluate_single(request: SingleEvaluationRequest):
    """
    Evaluate a single pair of code files or applications.

    Args:
        request: Evaluation request parameters

    Returns:
        Evaluation results with similarity scores
    """
    try:
        start_time = time.time()

        # Validate paths exist
        if not Path(request.golden_path).exists():
            raise HTTPException(
                status_code=404, detail=f"Golden path not found: {request.golden_path}"
            )
        if not Path(request.generated_path).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Generated path not found: {request.generated_path}",
            )

        # Perform evaluation
        result = evaluator.evaluate(
            golden_path=request.golden_path,
            generated_path=request.generated_path,
            evaluation_type=request.evaluation_type,
        )

        evaluation_time = time.time() - start_time

        return SingleEvaluationResponse(
            overall_similarity=result.overall_similarity,
            functional_equivalence=result.functional_equivalence,
            structural_similarity=result.structural_similarity,
            style_consistency=result.style_consistency,
            evaluation_type=result.metadata.get("evaluation_type", "unknown"),
            evaluation_time_seconds=evaluation_time,
        )

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@app.post("/compare-models", response_model=ModelComparisonResponse)
async def compare_models(request: ModelComparisonRequest):
    """
    Compare multiple AI models against a golden standard for AB testing.

    Args:
        request: Model comparison request parameters

    Returns:
        Comparison results with winner, rankings, and statistics
    """
    try:
        start_time = time.time()

        # Validate golden standard exists
        if not Path(request.golden_standard).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Golden standard not found: {request.golden_standard}",
            )

        # Validate all model output paths exist
        for model_name, output_path in request.models.items():
            if not Path(output_path).exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Model output not found for {model_name}: {output_path}",
                )

        # Perform batch evaluation with parallel processing
        batch_result = evaluator.evaluate_batch(
            golden_path=request.golden_standard,
            model_outputs=request.models,
            evaluation_type=request.evaluation_type,
            max_workers=request.max_workers,
        )

        evaluation_time = time.time() - start_time

        # Determine winner and confidence
        winner = batch_result.best_model
        confidence = 0.0

        if len(batch_result.rankings) >= 2:
            # Calculate confidence as the score difference between top 2 models
            top_score = batch_result.rankings[0][1]
            second_score = batch_result.rankings[1][1]
            confidence = abs(top_score - second_score)
        elif len(batch_result.rankings) == 1:
            confidence = batch_result.rankings[0][1]  # Single model score

        return ModelComparisonResponse(
            winner=winner,
            confidence=confidence,
            rankings=batch_result.rankings,
            summary_statistics=batch_result.summary_statistics,
            evaluation_time_seconds=evaluation_time,
            total_models=len(request.models),
        )

    except Exception as e:
        logger.error(f"Model comparison failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Model comparison failed: {str(e)}"
        )


@app.get("/batch-evaluate")
async def batch_evaluate_async(
    golden_path: str,
    model_paths: List[str],
    evaluation_type: str = "auto",
    background_tasks: BackgroundTasks = None,
):
    """
    Start an asynchronous batch evaluation job.

    Args:
        golden_path: Path to golden standard
        model_paths: List of model output paths
        evaluation_type: Type of evaluation
        background_tasks: FastAPI background tasks

    Returns:
        Job ID for tracking the evaluation
    """
    # This would integrate with a task queue like Celery in production
    job_id = f"job_{int(time.time())}"

    def run_evaluation():
        try:
            model_dict = {f"model_{i}": path for i, path in enumerate(model_paths)}
            evaluator.evaluate_batch(golden_path, model_dict, evaluation_type)
            # Store result somewhere (Redis, database, etc.)
            logger.info(f"Batch evaluation {job_id} completed")
        except Exception as e:
            logger.error(f"Batch evaluation {job_id} failed: {e}")

    if background_tasks:
        background_tasks.add_task(run_evaluation)

    return {"job_id": job_id, "status": "started"}


@app.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """Get embedding cache statistics."""
    try:
        cache = get_embedding_cache()
        stats = cache.get_stats()

        return CacheStatsResponse(
            total_entries=stats["total_entries"],
            total_size_mb=stats["total_size_mb"],
            cache_dir=stats["cache_dir"],
            max_size_mb=stats["max_size_mb"],
        )

    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache stats: {str(e)}"
        )


@app.post("/cache/clear")
async def clear_cache():
    """Clear the embedding cache."""
    try:
        cache = get_embedding_cache()
        cache.clear()
        return {"message": "Cache cleared successfully"}

    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Get system metrics for monitoring."""
    import psutil

    try:
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage("/").percent,
            "cache_stats": get_embedding_cache().get_stats(),
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return {"error": str(e), "timestamp": time.time()}


def create_app() -> FastAPI:
    """Factory function to create the FastAPI app."""
    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, workers: int = 1):
    """
    Run the API server.

    Args:
        host: Host to bind to
        port: Port to listen on
        workers: Number of worker processes
    """
    uvicorn.run(
        "src.api:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
