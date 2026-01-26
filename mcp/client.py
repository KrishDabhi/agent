"""MCP Client for making JSON-RPC calls to MCP server"""
import requests
import json
from typing import Dict, Any, Optional, Callable
try:
    from monitor import get_monitor, is_monitoring_enabled
except ImportError:
    get_monitor = lambda: None
    is_monitoring_enabled = lambda: False


class MCPClient:
    def __init__(self, server_url: str, status_callback: Optional[Callable] = None):
        self.server_url = server_url
        self.request_id = 0
        self.status_callback = status_callback
        self._available_tools = None
    
    def _emit_status(self, status: str):
        """Emit status update if callback is provided"""
        if self.status_callback:
            self.status_callback(status)
    
    def list_tools(self) -> Dict[str, Any]:
        """
        Get list of available tools from MCP server
        
        Returns:
            Dictionary of available tools with metadata
        """
        self._emit_status("Querying MCP server for available tools...")
        result = self.call_tool("mcp.list_tools", {})
        
        if "error" in result:
            print(f"❌ Failed to list tools: {result['error']['message']}")
            return {}
        
        tools_list = result.get("result", {}).get("tools", [])
        # Convert list to dict keyed by tool name
        self._available_tools = {tool["name"]: tool for tool in tools_list}
        
        print(f"✅ Discovered {len(self._available_tools)} tools")
        return self._available_tools
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get cached list of available tools"""
        if self._available_tools is None:
            return self.list_tools()
        return self._available_tools
    
    def reload_tools(self) -> Dict[str, Any]:
        """Request MCP server to reload tools"""
        self._emit_status("Requesting MCP server to reload tools...")
        result = self.call_tool("mcp.reload_tools", {})
        
        if "error" not in result:
            # Refresh our cache
            self.list_tools()
        
        return result
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server via JSON-RPC
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters to pass to the tool
            
        Returns:
            Result from the tool or error dict
        """
        self.request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "method": tool_name,
            "params": params,
            "id": self.request_id
        }
        
        self._emit_status(f"Calling MCP tool: {tool_name}")
        
        try:
            response = requests.post(
                self.server_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"❌ MCP Error: {result['error']['message']}")
                return {"error": result["error"]}
            
            return {"result": result.get("result")}
            
        except requests.exceptions.RequestException as e:
            error = {
                "error": {
                    "code": -32603,
                    "message": f"Transport error: {str(e)}"
                }
            }
            print(f"❌ Transport Error: {str(e)}")
            return error
        except json.JSONDecodeError as e:
            error = {
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(f"❌ JSON Parse Error: {str(e)}")
            return error
