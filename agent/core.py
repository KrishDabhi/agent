from mcp.client import MCPClient
from config import ROUTING_CONFIG
from typing import Optional, Callable, Dict, Any, List
import time
import re


class Agent:
    def __init__(self, mcp_client: MCPClient, status_callback: Optional[Callable] = None):
        self.mcp = mcp_client
        self.status_callback = status_callback
        self.capabilities = {}
        self.status_updates = []  # Store status updates for response
        
        # Discover available tools on initialization
        self._discover_capabilities()
    
    def _emit_status(self, status: str):
        """Emit status update and store it"""
        self.status_updates.append({
            "timestamp": time.time(),
            "status": status
        })
        if self.status_callback:
            self.status_callback(status)
        print(f"🤖 Agent: {status}")
    
    def _discover_capabilities(self):
        """Discover what tools are available from MCP server"""
        self._emit_status("Discovering capabilities...")
        self.capabilities = self.mcp.list_tools()
        
        if self.capabilities:
            tool_names = list(self.capabilities.keys())
            self._emit_status(f"Capabilities loaded: {', '.join(tool_names)}")
        else:
            self._emit_status("Warning: No capabilities discovered")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return available capabilities"""
        return self.capabilities
    
    def refresh_capabilities(self):
        """Refresh capabilities from MCP server"""
        self._emit_status("Refreshing capabilities...")
        self.mcp.reload_tools()
        self._discover_capabilities()
    
    def handle_user_request(self, method: str, params: dict) -> dict:
        # Clear status updates for new request
        self.status_updates = []
        
        if method == "chat":
            result = self._handle_chat(params["message"])
            return {
                "response": result["response"],
                "status_updates": result.get("status_updates", []),
                "metadata": result.get("metadata", {})
            }
        elif method == "execute_tool":
            return self.mcp.call_tool(
                params["tool_name"],
                params["tool_params"]
            )
        elif method == "list_capabilities":
            return {"capabilities": list(self.capabilities.values())}
        elif method == "refresh_capabilities":
            self.refresh_capabilities()
            return {"capabilities": list(self.capabilities.values())}
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _handle_chat(self, message: str) -> dict:
        """
        Handle chat request and return response with metadata
        Returns:
            dict with response, status_updates, and metadata
        """
        start_time = time.time()
        
        self._emit_status("💭 Thinking... analyzing your request")
        
        # Step 1: Determine best tool
        selected_tool, confidence = self._select_tool(message)
        
        self._emit_status(f"🎯 Selected tool: {selected_tool} (confidence: {confidence}%)")
        
        # Check if tool is available
        if selected_tool not in self.capabilities:
            self._emit_status(f"⚠️  Warning: Tool {selected_tool} not available")
            response = f"I don't have access to the '{selected_tool}' capability. Available capabilities: {', '.join(self.capabilities.keys())}"
            
            return {
                "response": response,
                "status_updates": self.status_updates,
                "metadata": {
                    "tool_used": None,
                    "confidence": 0,
                    "total_time": time.time() - start_time,
                    "error": "Tool not available"
                }
            }
        
        tool_start_time = time.time()
        
        if selected_tool == "web_search":
            # Web search + structure results
            self._emit_status("🔍 Executing web search...")
            search_result = self.mcp.call_tool("web_search", {"query": message})
            
            if "error" in search_result:
                error_msg = search_result['error']['message']
                self._emit_status(f"❌ Search failed: {error_msg}")
                return {
                    "response": f"Search failed: {error_msg}",
                    "status_updates": self.status_updates,
                    "metadata": {
                        "tool_used": "web_search",
                        "confidence": confidence,
                        "total_time": time.time() - start_time,
                        "error": error_msg
                    }
                }
            
            search_time = time.time() - tool_start_time
            self._emit_status(f"✅ Search completed in {search_time:.2f}s")
            
            # Structure results using text generation
            search_data = search_result['result']
            self._emit_status("📝 Structuring search results...")
            
            structure_start_time = time.time()
            structured_prompt = f"Based on these search results:\n{search_data}\n\nProvide a concise, well-structured answer to: {message}"
            structured_result = self.mcp.call_tool("text_generation", {"prompt": structured_prompt})
            
            if "error" in structured_result:
                self._emit_status("⚠️  Failed to structure results, returning raw search data")
                response = f"Search Results:\n\n{search_data}"
            else:
                structure_time = time.time() - structure_start_time
                self._emit_status(f"✅ Results structured in {structure_time:.2f}s")
                response = structured_result["result"]
            
            self._emit_status("✨ Response ready")
            
            total_time = time.time() - start_time
            return {
                "response": response,
                "status_updates": self.status_updates,
                "metadata": {
                    "tool_used": "web_search",
                    "confidence": confidence,
                    "search_time": round(search_time, 3),
                    "structure_time": round(time.time() - structure_start_time, 3) if "error" not in structured_result else 0,
                    "total_time": round(total_time, 3)
                }
            }
        
        else:
            # Direct tool execution
            self._emit_status(f"⚙️  Executing {selected_tool}...")
            result = self.mcp.call_tool(selected_tool, {"prompt": message})
            
            if "error" in result:
                error_msg = result['error']['message']
                self._emit_status(f"❌ Tool execution failed: {error_msg}")
                return {
                    "response": f"Tool execution failed: {error_msg}",
                    "status_updates": self.status_updates,
                    "metadata": {
                        "tool_used": selected_tool,
                        "confidence": confidence,
                        "total_time": time.time() - start_time,
                        "error": error_msg
                    }
                }
            
            tool_time = time.time() - tool_start_time
            self._emit_status(f"✅ {selected_tool} completed in {tool_time:.2f}s")
            self._emit_status("✨ Response ready")
            
            total_time = time.time() - start_time
            return {
                "response": result["result"],
                "status_updates": self.status_updates,
                "metadata": {
                    "tool_used": selected_tool,
                    "confidence": confidence,
                    "tool_time": round(tool_time, 3),
                    "total_time": round(total_time, 3)
                }
            }
    
    def _select_tool(self, query: str) -> tuple[str, int]:
        """
        Intelligently select the best tool based on query content
        Returns:
            (tool_name, confidence_percentage)
        """
        query_lower = query.lower()
        
        # Score each tool based on keyword matches
        scores = {}
        for tool_name, config in ROUTING_CONFIG.items():
            # Skip if tool not available
            if tool_name not in self.capabilities:
                continue
                
            score = 0
            for keyword in config["keywords"]:
                if keyword in query_lower:
                    score += 1
                # Bonus for exact phrase matches
                if f" {keyword} " in f" {query_lower} ":
                    score += 2
            
            scores[tool_name] = score
        
        # If no tools available, return default
        if not scores:
            return "text_generation", 0
        
        # Return tool with highest score
        best_tool = max(scores, key=scores.get)
        max_score = scores[best_tool]
        
        # Calculate confidence percentage (rough heuristic)
        confidence = min(100, max_score * 20)
        
        # Default to text_generation if confidence is too low
        if confidence < 20:
            return "text_generation", 50
        
        return best_tool, confidence