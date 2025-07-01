"""
Embedding cache system for production optimization.

This module provides caching functionality for sentence transformer embeddings
to avoid recomputation and significantly speed up repeated evaluations.
"""

import hashlib
import json
import logging
import os
import pickle
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """
    Cache for storing and retrieving sentence transformer embeddings.

    Uses file content hashing to determine cache keys and stores embeddings
    in pickle format for fast serialization/deserialization.
    """

    def __init__(self, cache_dir: Optional[str] = None, max_cache_size_mb: int = 500):
        """
        Initialize the embedding cache.

        Args:
            cache_dir: Directory to store cache files (default: .cache/embeddings)
            max_cache_size_mb: Maximum cache size in MB before cleanup
        """
        self.cache_dir = Path(cache_dir or ".cache/embeddings")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.metadata_file = self.cache_dir / "metadata.json"
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load cache metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, "r") as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {"entries": {}, "total_size": 0}
        except Exception as e:
            logger.warning(f"Failed to load cache metadata: {e}")
            self.metadata = {"entries": {}, "total_size": 0}

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache metadata: {e}")

    def _compute_cache_key(self, content: str, model_name: str) -> str:
        """
        Compute cache key from content and model name.

        Args:
            content: File content
            model_name: Name of the embedding model

        Returns:
            SHA256 hash as cache key
        """
        # Create a hash from content + model name
        combined = f"{content}|{model_name}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def get(self, content: str, model_name: str) -> Optional[np.ndarray]:
        """
        Retrieve embedding from cache.

        Args:
            content: File content
            model_name: Name of the embedding model

        Returns:
            Cached embedding or None if not found
        """
        cache_key = self._compute_cache_key(content, model_name)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "rb") as f:
                embedding = pickle.load(f)

            # Update access time in metadata
            if cache_key in self.metadata["entries"]:
                self.metadata["entries"][cache_key][
                    "last_accessed"
                ] = self._get_timestamp()
                self._save_metadata()

            logger.debug(f"Cache hit for key: {cache_key[:16]}...")
            return embedding

        except Exception as e:
            logger.warning(f"Failed to load cached embedding: {e}")
            # Remove corrupted cache file
            try:
                cache_file.unlink()
            except Exception:
                pass
            return None

    def put(self, content: str, model_name: str, embedding: np.ndarray) -> None:
        """
        Store embedding in cache.

        Args:
            content: File content
            model_name: Name of the embedding model
            embedding: Embedding to cache
        """
        cache_key = self._compute_cache_key(content, model_name)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        try:
            # Check if we need to cleanup cache first
            self._cleanup_if_needed()

            # Save embedding
            with open(cache_file, "wb") as f:
                pickle.dump(embedding, f)

            # Update metadata
            file_size = cache_file.stat().st_size
            timestamp = self._get_timestamp()

            self.metadata["entries"][cache_key] = {
                "created": timestamp,
                "last_accessed": timestamp,
                "size": file_size,
                "model_name": model_name,
            }

            self.metadata["total_size"] = self._calculate_total_size()
            self._save_metadata()

            logger.debug(f"Cached embedding for key: {cache_key[:16]}...")

        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")

    def _cleanup_if_needed(self) -> None:
        """Cleanup cache if it exceeds size limit."""
        current_size = self._calculate_total_size()

        if current_size <= self.max_cache_size_bytes:
            return

        logger.info(
            f"Cache size ({current_size / 1024 / 1024:.1f}MB) exceeds limit, cleaning up..."
        )

        # Sort entries by last accessed time (oldest first)
        entries = list(self.metadata["entries"].items())
        entries.sort(key=lambda x: x[1]["last_accessed"])

        # Remove oldest entries until we're under the limit
        target_size = self.max_cache_size_bytes * 0.8  # Clean to 80% of limit

        for cache_key, entry_info in entries:
            if current_size <= target_size:
                break

            cache_file = self.cache_dir / f"{cache_key}.pkl"
            try:
                if cache_file.exists():
                    cache_file.unlink()
                    current_size -= entry_info["size"]

                del self.metadata["entries"][cache_key]

            except Exception as e:
                logger.warning(f"Failed to remove cache file {cache_key}: {e}")

        self.metadata["total_size"] = current_size
        self._save_metadata()

        logger.info(
            f"Cache cleanup completed, new size: {current_size / 1024 / 1024:.1f}MB"
        )

    def _calculate_total_size(self) -> int:
        """Calculate total cache size in bytes."""
        total_size = 0
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                total_size += cache_file.stat().st_size
            except Exception:
                pass
        return total_size

    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time

        return time.time()

    def clear(self) -> None:
        """Clear all cached embeddings."""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()

            self.metadata = {"entries": {}, "total_size": 0}
            self._save_metadata()

            logger.info("Cache cleared successfully")

        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self.metadata["entries"]),
            "total_size_mb": self.metadata["total_size"] / 1024 / 1024,
            "cache_dir": str(self.cache_dir),
            "max_size_mb": self.max_cache_size_bytes / 1024 / 1024,
        }


# Global cache instance
_global_cache: Optional[EmbeddingCache] = None


def get_embedding_cache() -> EmbeddingCache:
    """Get or create the global embedding cache instance."""
    global _global_cache
    if _global_cache is None:
        cache_dir = os.environ.get("EMBEDDING_CACHE_DIR")
        max_size = int(os.environ.get("EMBEDDING_CACHE_SIZE_MB", "500"))
        _global_cache = EmbeddingCache(cache_dir, max_size)
    return _global_cache


def clear_embedding_cache() -> None:
    """Clear the global embedding cache."""
    cache = get_embedding_cache()
    cache.clear()
