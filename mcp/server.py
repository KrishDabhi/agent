from jsonrpc import JsonRpcHandler
from mcp.tools import discover_tools

class MCPServer:
    def __init__(self):
        self.rpc_handler = JsonRpcHandler()
        self.tools_metadata = {}  # Store tool metadata
        self._load_tools()
        
        # Register MCP-specific methods
        self.rpc_handler.register("mcp.list_tools", self._list_tools_handler)
        self.rpc_handler.register("mcp.reload_tools", self._reload_tools_handler)
    
    def _load_tools(self):
        """Dynamically load all available tools"""
        tools_data = discover_tools()
        for tool_name, tool_data in tools_data.items():
            self.rpc_handler.register(tool_name, tool_data["func"])
            self.tools_metadata[tool_name] = tool_data["metadata"]
            print(f"🔧 Registered MCP tool: {tool_name}")
    
    def _list_tools_handler(self, params: dict) -> dict:
        """Handler for mcp.list_tools JSON-RPC method"""
        return {"tools": list(self.tools_metadata.values())}
    
    def _reload_tools_handler(self, params: dict) -> dict:
        """Handler for mcp.reload_tools JSON-RPC method"""
        print("🔄 Reloading tools...")
        self.tools_metadata.clear()
        self._load_tools()
        return {"status": "reloaded", "tool_count": len(self.tools_metadata)}
    
    def list_tools(self) -> dict:
        """List all registered tools with metadata"""
        return self.tools_metadata
    
    def register_tool(self, name: str, func: callable):
        """Manual tool registration (for programmatic use)"""
        self.rpc_handler.register(name, func)
    
    def handle_request(self, raw_data: str) -> str:
        return self.rpc_handler.handle(raw_data)