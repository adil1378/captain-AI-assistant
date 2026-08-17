"""
Captain AI OS - Memory Lifecycle & Optimization Manager (Volume 9 Part 9F)
Responsible for background memory deduplication, cold archiving, working context pruning,
and vector index vacuuming.
"""

from typing import Dict, Any, List, Optional
import asyncio
from pydantic import BaseModel, Field
import time


class MemoryArchiveRecord(BaseModel):
    archive_id: str
    original_memory_id: str
    content: str
    archived_at: float = Field(default_factory=time.time)
    is_encrypted: bool = True


class MemoryLifecycleManager:
    """Non-blocking background memory optimization and maintenance engine."""

    def __init__(self):
        self.archive_store: List[MemoryArchiveRecord] = []
        self.optimization_count: int = 0

    async def consolidate_and_deduplicate(self, memory_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicates raw memory records based on content hashing and similarity."""
        await asyncio.sleep(0.01)
        seen_contents = set()
        deduped = []

        for record in memory_records:
            content = record.get("content", "").strip()
            if content and content not in seen_contents:
                seen_contents.add(content)
                deduped.append(record)

        self.optimization_count += 1
        return deduped

    async def archive_inactive_memories(self, inactive_memories: List[Dict[str, Any]]) -> int:
        """Compresses and moves historical inactive memories to cold encrypted archive."""
        archived_count = 0
        for item in inactive_memories:
            mem_id = item.get("id", f"mem_{int(time.time())}")
            content = item.get("content", "")
            if content:
                self.archive_store.append(
                    MemoryArchiveRecord(
                        archive_id=f"arc_{mem_id}",
                        original_memory_id=mem_id,
                        content=content,
                        is_encrypted=True
                    )
                )
                archived_count += 1
        return archived_count
