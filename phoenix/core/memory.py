from dataclasses import dataclass, field
from typing import Any

@dataclass
class Memory:
    state: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    def remember(self, event):
        self.history.append(dict(event)); self.state.update(event.get("state", {}))
    def recall(self, key, default=None): return self.state.get(key, default)
