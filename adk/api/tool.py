# adk/api/tool.py
import inspect
import json
from typing import Any, Callable, Dict, List

class Tool:
    """A decorator class that wraps functions to make them callable by agents."""
    
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or ""
        
        # Extract function signature
        sig = inspect.signature(func)
        self.parameters = {}
        for name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                self.parameters[name] = str(param.annotation)
            else:
                self.parameters[name] = "Any"
    
    def execute(self, *args, **kwargs):
        """Execute the wrapped function."""
        try:
            result = self.func(*args, **kwargs)
            return result
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for LLM consumption."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

def tool(func: Callable) -> Tool:
    """Decorator to wrap functions as tools."""
    return Tool(func)
