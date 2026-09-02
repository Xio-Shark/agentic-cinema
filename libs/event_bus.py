"""
Async Event Bus for CineOps Studio.
Broadcasts typed production events to connected SSE streams and maintains history.
"""

import asyncio
import json
from typing import List, AsyncGenerator
from libs.models import CineOpsProductionEvent


class EventBus:
    """In-memory Pub/Sub event broadcaster for real-time SSE telemetry."""

    def __init__(self) -> None:
        self._subscribers: List[asyncio.Queue] = []
        self._history: List[CineOpsProductionEvent] = []

    async def publish(self, event: CineOpsProductionEvent) -> None:
        """Record and broadcast event to all active subscriber queues."""
        self._history.append(event)
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(event)
            except Exception:
                pass

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """Subscribe to the event stream yielding SSE-formatted messages."""
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        try:
            # First send past history to sync newly joined clients
            for past_event in self._history:
                yield f"data: {past_event.model_dump_json()}\n\n"
            while True:
                event: CineOpsProductionEvent = await queue.get()
                yield f"data: {event.model_dump_json()}\n\n"
        finally:
            if queue in self._subscribers:
                self._subscribers.remove(queue)

    def get_history(self) -> List[CineOpsProductionEvent]:
        """Retrieve all recorded events in the current production session."""
        return list(self._history)

    def clear(self) -> None:
        """Reset history and active event streams."""
        self._history.clear()


# Global Singleton Event Bus instance
event_bus = EventBus()
