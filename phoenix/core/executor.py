from dataclasses import dataclass
from typing import Any, Callable
@dataclass
class Tool:
    name: str
    fn: Callable[..., Any]
    side_effect: bool = False
    permission: str = "safe"
class Executor:
    def __init__(self): self.tools = {}
    def register(self, tool): self.tools[tool.name] = tool
    def execute(self, name, args, permissions):
        tool = self.tools[name]
        if tool.side_effect and tool.permission not in permissions: raise PermissionError(f"Permission required: {tool.permission}")
        return tool.fn(**args)
