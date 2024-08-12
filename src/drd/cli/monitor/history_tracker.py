from collections import deque
from enum import Enum
import time


class EventType(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class HistoryTracker:
    def __init__(self, max_entries=5):
        self.history = deque(maxlen=max_entries)

    def add_event(self, event_type: EventType, content: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "timestamp": timestamp,
            "role": event_type.value,
            "content": content
        })

    def get_history(self):
        return list(self.history)

    def get_history_as_chat(self):
        return [{"role": event["role"], "content": event["content"]} for event in self.history]

    def clear_history(self):
        self.history.clear()

    def __str__(self):
        return "\n".join([f"{event['timestamp']} - {event['role'].capitalize()}: {event['content']}" for event in self.history])
