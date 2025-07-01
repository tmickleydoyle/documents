"""
Production configuration management for the evaluation framework.

This module provides environment-specific configuration management,
allowing different settings for development, staging, and production.
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .config import DEFAULT_EVALUATION_WEIGHTS, DEFAULT_EMBEDDING_MODEL


@dataclass
class DatabaseConfig:
    """Database configuration for storing evaluation results."""

    host: str = "localhost"
    port: int = 5432
    database: str = "fern_eval"
    username: str = "fern_user"
    password: str = ""
    connection_pool_size: int = 10

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create database config from environment variables."""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "fern_eval"),
            username=os.getenv("DB_USER", "fern_user"),
            password=os.getenv("DB_PASSWORD", ""),
            connection_pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        )


@dataclass
class CacheConfig:
    """Cache configuration for embeddings and results."""

    cache_dir: Optional[str] = None
    max_size_mb: int = 500
    ttl_hours: int = 24
    cleanup_interval_hours: int = 6

    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Create cache config from environment variables."""
        return cls(
            cache_dir=os.getenv("CACHE_DIR"),
            max_size_mb=int(os.getenv("CACHE_SIZE_MB", "500")),
            ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "24")),
            cleanup_interval_hours=int(os.getenv("CACHE_CLEANUP_HOURS", "6")),
        )


@dataclass
class ModelConfig:
    """Model configuration for embeddings and evaluation."""

    embedding_model: str = DEFAULT_EMBEDDING_MODEL
    evaluation_weights: Dict[str, float] = field(
        default_factory=lambda: DEFAULT_EVALUATION_WEIGHTS.copy()
    )
    model_cache_dir: Optional[str] = None
    gpu_acceleration: bool = True
    model_timeout_seconds: int = 30

    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Create model config from environment variables."""
        # Parse custom weights if provided
        weights = DEFAULT_EVALUATION_WEIGHTS.copy()
        if os.getenv("EVALUATION_WEIGHTS"):
            try:
                import json

                custom_weights = json.loads(os.getenv("EVALUATION_WEIGHTS", "{}"))
                weights.update(custom_weights)
            except (json.JSONDecodeError, TypeError):
                pass  # Fall back to defaults

        return cls(
            embedding_model=os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
            evaluation_weights=weights,
            model_cache_dir=os.getenv("MODEL_CACHE_DIR"),
            gpu_acceleration=os.getenv("GPU_ACCELERATION", "true").lower() == "true",
            model_timeout_seconds=int(os.getenv("MODEL_TIMEOUT", "30")),
        )


@dataclass
class PerformanceConfig:
    """Performance and scaling configuration."""

    max_workers: int = 4
    batch_size: int = 100
    memory_limit_mb: int = 2048
    timeout_seconds: int = 300
    enable_profiling: bool = False

    @classmethod
    def from_env(cls) -> "PerformanceConfig":
        """Create performance config from environment variables."""
        return cls(
            max_workers=int(os.getenv("MAX_WORKERS", "4")),
            batch_size=int(os.getenv("BATCH_SIZE", "100")),
            memory_limit_mb=int(os.getenv("MEMORY_LIMIT_MB", "2048")),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "300")),
            enable_profiling=os.getenv("ENABLE_PROFILING", "false").lower() == "true",
        )


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 5

    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """Create logging config from environment variables."""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv(
                "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
            file_path=os.getenv("LOG_FILE"),
            max_file_size_mb=int(os.getenv("LOG_MAX_SIZE_MB", "100")),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5")),
        )


@dataclass
class ProductionConfig:
    """Complete production configuration."""

    environment: str = "development"
    debug: bool = False
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_env(cls) -> "ProductionConfig":
        """Create complete config from environment variables."""
        return cls(
            environment=os.getenv("ENVIRONMENT", "development"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            database=DatabaseConfig.from_env(),
            cache=CacheConfig.from_env(),
            model=ModelConfig.from_env(),
            performance=PerformanceConfig.from_env(),
            logging=LoggingConfig.from_env(),
        )

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    def setup_logging(self) -> None:
        """Setup logging based on configuration."""
        import logging
        import logging.handlers

        # Set log level
        numeric_level = getattr(logging, self.logging.level.upper(), logging.INFO)
        logging.basicConfig(level=numeric_level, format=self.logging.format)

        # Add file handler if specified
        if self.logging.file_path:
            log_path = Path(self.logging.file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=self.logging.max_file_size_mb * 1024 * 1024,
                backupCount=self.logging.backup_count,
            )
            file_handler.setFormatter(logging.Formatter(self.logging.format))
            logging.getLogger().addHandler(file_handler)


# Global configuration instance
_config: Optional[ProductionConfig] = None


def get_config() -> ProductionConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = ProductionConfig.from_env()
        _config.setup_logging()
    return _config


def reload_config() -> ProductionConfig:
    """Reload configuration from environment variables."""
    global _config
    _config = ProductionConfig.from_env()
    _config.setup_logging()
    return _config


# Convenience functions for common config access
def get_max_workers() -> int:
    """Get maximum number of workers from config."""
    return get_config().performance.max_workers


def get_cache_config() -> CacheConfig:
    """Get cache configuration."""
    return get_config().cache


def get_model_config() -> ModelConfig:
    """Get model configuration."""
    return get_config().model


def get_evaluation_weights() -> Dict[str, float]:
    """Get evaluation weights from config."""
    return get_config().model.evaluation_weights


def is_production() -> bool:
    """Check if running in production environment."""
    return get_config().is_production()


# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    "ENVIRONMENT": "development",
    "DEBUG": "true",
    "LOG_LEVEL": "DEBUG",
    "MAX_WORKERS": "2",
    "CACHE_SIZE_MB": "100",
    "GPU_ACCELERATION": "false",
}

STAGING_CONFIG = {
    "ENVIRONMENT": "staging",
    "DEBUG": "false",
    "LOG_LEVEL": "INFO",
    "MAX_WORKERS": "4",
    "CACHE_SIZE_MB": "500",
    "GPU_ACCELERATION": "true",
}

PRODUCTION_CONFIG = {
    "ENVIRONMENT": "production",
    "DEBUG": "false",
    "LOG_LEVEL": "WARNING",
    "MAX_WORKERS": "8",
    "CACHE_SIZE_MB": "1000",
    "GPU_ACCELERATION": "true",
    "ENABLE_PROFILING": "false",
}
