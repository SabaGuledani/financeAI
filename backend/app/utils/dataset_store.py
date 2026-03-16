from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class DatasetEntry:
    df: pd.DataFrame
    created_at_monotonic: float
    last_access_monotonic: float


class DatasetStore:
    """
    In-memory DataFrame store keyed by dataset_id.

    Notes:
    - This is per-process memory (won't work across multiple workers).
    - Data is ephemeral and removed after TTL or when capacity is exceeded.
    """

    def __init__(self, *, ttl_seconds: int = 60 * 30, max_items: int = 32) -> None:
        self._ttl_seconds = int(ttl_seconds)
        self._max_items = int(max_items)
        self._lock = threading.Lock()
        self._items: dict[str, DatasetEntry] = {}

    def put(self, df: pd.DataFrame) -> str:
        now = time.monotonic()
        dataset_id = uuid.uuid4().hex

        with self._lock:
            self._gc_locked(now)
            if len(self._items) >= self._max_items:
                self._evict_one_locked()
            self._items[dataset_id] = DatasetEntry(df=df, created_at_monotonic=now, last_access_monotonic=now)

        return dataset_id

    def get(self, dataset_id: str) -> Optional[pd.DataFrame]:
        now = time.monotonic()
        with self._lock:
            self._gc_locked(now)
            entry = self._items.get(dataset_id)
            if entry is None:
                return None
            self._items[dataset_id] = DatasetEntry(
                df=entry.df,
                created_at_monotonic=entry.created_at_monotonic,
                last_access_monotonic=now,
            )
            return entry.df

    def delete(self, dataset_id: str) -> bool:
        with self._lock:
            return self._items.pop(dataset_id, None) is not None

    def _gc_locked(self, now: float) -> None:
        expired: list[str] = []
        for dataset_id, entry in self._items.items():
            if (now - entry.last_access_monotonic) > self._ttl_seconds:
                expired.append(dataset_id)
        for dataset_id in expired:
            self._items.pop(dataset_id, None)

    def _evict_one_locked(self) -> None:
        # Evict least recently used.
        lru_id: Optional[str] = None
        lru_access: float = float("inf")
        for dataset_id, entry in self._items.items():
            if entry.last_access_monotonic < lru_access:
                lru_access = entry.last_access_monotonic
                lru_id = dataset_id
        if lru_id is not None:
            self._items.pop(lru_id, None)


dataset_store = DatasetStore()

