"""
In-memory variant store.
In production, replace with Cosmos DB or another persistent store.
"""

from typing import Optional
import threading


class VariantStore:
    """Thread-safe in-memory storage for generated variants."""

    def __init__(self):
        self._store: dict[str, dict] = {}
        self._lock = threading.Lock()

    def store(self, variant_id: str, variant: dict) -> None:
        """Store a variant spec."""
        with self._lock:
            self._store[variant_id] = variant

    def get(self, variant_id: str) -> Optional[dict]:
        """Retrieve a variant spec by ID."""
        with self._lock:
            return self._store.get(variant_id)

    def list_all(self) -> list[str]:
        """List all stored variant IDs."""
        with self._lock:
            return list(self._store.keys())

    def delete(self, variant_id: str) -> bool:
        """Delete a variant. Returns True if it existed."""
        with self._lock:
            if variant_id in self._store:
                del self._store[variant_id]
                return True
            return False
