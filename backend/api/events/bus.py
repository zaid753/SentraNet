import asyncio
import logging
from typing import Callable, Dict, List, Any
from .models import EventEnvelope

logger = logging.getLogger(__name__)

class EventBus:
    """
    In-process EventBus for Phase 4 architecture.
    Intended for a single backend instance. Avoids Redis/Kafka intentionally.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[EventEnvelope], Any]]] = {}
        self._all_subscribers: List[Callable[[EventEnvelope], Any]] = []

    def subscribe(self, event_type: str, handler: Callable[[EventEnvelope], Any]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: Callable[[EventEnvelope], Any]):
        if handler not in self._all_subscribers:
            self._all_subscribers.append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[EventEnvelope], Any]):
        if event_type in self._subscribers:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)

    def unsubscribe_all(self, handler: Callable[[EventEnvelope], Any]):
        if handler in self._all_subscribers:
            self._all_subscribers.remove(handler)
        for event_type, handlers in self._subscribers.items():
            if handler in handlers:
                handlers.remove(handler)

    def publish(self, event: EventEnvelope):
        handlers = self._subscribers.get(event.event_type, []) + self._all_subscribers
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
            
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    if loop:
                        asyncio.create_task(handler(event))
                    else:
                        # In tests without a running loop, we can use asyncio.run
                        # But wait, asyncio.run inside a synchronous context might be nested if there is a loop.
                        # Since we caught RuntimeError, there is no loop.
                        asyncio.run(handler(event))
                else:
                    if loop:
                        loop.run_in_executor(None, handler, event)
                    else:
                        handler(event)
            except Exception as e:
                logger.error(f"Error executing event handler for {event.event_type}: {e}")

# Global singleton event bus
event_bus = EventBus()
