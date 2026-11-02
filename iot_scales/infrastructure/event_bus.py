"""
IoT Scale Event Bus (Infrastructure Layer)
Thread-safe in-memory event streaming bus for Server-Sent Events (SSE).
"""

import queue
import threading

class ScaleEventBus:
    """Thread-safe event dispatcher for distributing live scale telemetry to SSE subscribers."""

    def __init__(self):
        self._subscribers = []
        self._lock = threading.Lock()

    def subscribe(self, device_id=None):
        q = queue.Queue(maxsize=100)
        with self._lock:
            self._subscribers.append((q, device_id))
        return q

    def unsubscribe(self, q):
        with self._lock:
            self._subscribers = [sub for sub in self._subscribers if sub[0] != q]

    def broadcast(self, payload, device_id):
        with self._lock:
            dead_subscribers = []
            for q, subscribed_device in self._subscribers:
                if subscribed_device is None or subscribed_device == device_id:
                    try:
                        q.put_nowait(payload)
                    except queue.Full:
                        dead_subscribers.append((q, subscribed_device))
            for dead in dead_subscribers:
                if dead in self._subscribers:
                    self._subscribers.remove(dead)

scale_event_bus = ScaleEventBus()
