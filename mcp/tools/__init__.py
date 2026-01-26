import os
import importlib
from typing import Dict, Callable, Any


def discover_tools() -> Dict[str, Dict[str, Any]]:
    """
    Dynamically discover and load all tool modules
    
    Returns:
        Dictionary mapping tool names to their function and metadata
    """
    tools = {}
    tools_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(tools_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove .py
            try:
                module = importlib.import_module(f"mcp.tools.{module_name}")
                
                # Check if module has required attributes
                if hasattr(module, "TOOL_NAME") and hasattr(module, "execute"):
                    tool_name = module.TOOL_NAME
                    
                    # Extract metadata
                    metadata = {
                        "name": tool_name,
                        "description": getattr(module, "TOOL_DESCRIPTION", "No description"),
                        "parameters": getattr(module, "TOOL_PARAMETERS", {}),
                        "module": module_name
                    }
                    
                    tools[tool_name] = {
                        "func": module.execute,
                        "metadata": metadata
                    }
                    
                    print(f"✅ Loaded tool: {tool_name}")
                else:
                    print(f"⚠️  Skipping {filename}: Missing TOOL_NAME or execute function")
                    
            except Exception as e:
                print(f"❌ Failed to load tool {filename}: {e}")
                import traceback
                traceback.print_exc()
    
    return tools