from mcp.client import MCPClient
from config import ROUTING_CONFIG, CONFIDENCE_THRESHOLD
from typing import Optional, Callable, Dict, Any, List
import time
import re
from formatter import format_text
from query_analyzer import QueryAnalyzer


class Agent:
    def __init__(self, mcp_client: MCPClient, status_callback: Optional[Callable] = None):
        self.mcp = mcp_client
        self.status_callback = status_callback
        self.capabilities = {}
        self.status_updates = []  # Store status updates for response
        
        # Initialize LLM-based query analyzer
        self.query_analyzer = QueryAnalyzer()
        
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
    
    def _extract_content(self, response: str) -> str:
        """
        Extract actual content from structured responses.
        If response is JSON with 'content' field, extract it.
        Otherwise return the response as-is.
        """
        import json
        try:
            # Try to parse as JSON
            data = json.loads(response)
            
            # If it's structured output with 'content', extract it
            if isinstance(data, dict) and 'content' in data:
                return data['content']
            
            # Otherwise return as-is
            return response
        except (json.JSONDecodeError, ValueError):
            # Not JSON, return as-is
            return response
    
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
    
    def _handle_conversational(self, message: str) -> Optional[str]:
        """
        Handle conversational queries like greetings, gratitude, very short queries
        Returns response string if conversational, None if needs tool
        """
        msg_lower = message.lower().strip()
        
        # Greetings
        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "howdy"]
        if msg_lower in greetings:
            return "Hello! I'm an intelligent agent that can help you with:\n\n- **Web searches** for flights, trains, bookings, news, and real-time information\n- **Code generation** for programming tasks\n- **Explanations** of concepts and topics\n\nWhat can I help you with today?"
        
        # Gratitude
        thanks = ["thanks", "thank you", "thx", "ty", "appreciate it", "thank you so much"]
        if msg_lower in thanks:
            return "You're welcome! Let me know if you need anything else!"
        
        # Very short or unclear queries - ask for clarification
        if len(message.strip()) <= 2:
            return "I need a bit more information. Could you please provide more details about what you're looking for?"
        
        # Single words that are too vague
        vague_words = ["help", "please", "ok", "okay", "yes", "no"]
        if msg_lower in vague_words:
            return "I'm here to help! Could you please tell me what you need assistance with?"
        
        return None
    
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
        
        # Check for conversational queries first (greetings, thanks, etc.)
        conv_response = self._handle_conversational(message)
        if conv_response:
            return {
                "response": format_text(conv_response),
                "status_updates": self.status_updates,
                "metadata": {
                    "tool_used": "conversational",
                    "confidence": 100,
                    "total_time": time.time() - start_time
                }
            }
        
        # Step 1: Determine best tool
        selected_tool, confidence = self._select_tool(message)
        
        self._emit_status(f"🎯 Selected tool: {selected_tool} (confidence: {confidence}%)")
        
        # Check if tool is available
        if selected_tool not in self.capabilities:
            self._emit_status(f"⚠️  Warning: Tool {selected_tool} not available")
            response = f"I don't have access to the '{selected_tool}' capability. Available capabilities: {', '.join(self.capabilities.keys())}"
            
            return {
                "response": format_text(response),
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
                    "response": format_text(f"Search failed: {error_msg}"),
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
                response = format_text(f"Search Results:\n\n{search_data}")
            else:
                structure_time = time.time() - structure_start_time
                self._emit_status(f"✅ Results structured in {structure_time:.2f}s")
                content = self._extract_content(structured_result["result"])
                response = format_text(content)
            
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
                    "response": format_text(f"Tool execution failed: {error_msg}"),
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
            
            # Extract content from structured response
            content = self._extract_content(result["result"])
            
            return {
                "response": format_text(content),
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
        Intelligently select the best tool using LLM-based query analysis
        Returns:
            (tool_name, confidence_percentage)
        """
        try:
            # Use LLM to analyze query and recommend tool
            available_tools = list(self.capabilities.keys())
            
            if not available_tools:
                return "text_generation", 0
            
            # Get LLM recommendation
            tool, confidence, reasoning = self.query_analyzer.get_tool_with_confidence(
                query, available_tools
            )
            
            # Show reasoning in status
            self._emit_status(f"💡 LLM Analysis: {reasoning[:80]}...")
            
            # Validate tool is available
            if tool not in self.capabilities:
                self._emit_status(f"⚠️  LLM recommended unavailable tool {tool}, using fallback")
                tool = available_tools[0] if available_tools else "text_generation"
                confidence = 50
            
            # Check confidence threshold
            if confidence < CONFIDENCE_THRESHOLD:
                self._emit_status(f"⚠️  Confidence {confidence}% below threshold {CONFIDENCE_THRESHOLD}%")
                
                # Intelligent fallback based on query content
                needs_realtime = any(word in query.lower() for word in [
                    "latest", "current", "now", "today", "recent", "news",
                    "book", "booking", "buy", "price", "find", "search", 
                    "flight", "train", "hotel", "ticket", "weather"
                ])
                
                if needs_realtime and "web_search" in self.capabilities:
                    self._emit_status(f"🔄 Query needs real-time data, using web_search")
                    return "web_search", confidence
                else:
                    self._emit_status(f"✓ Using {tool} despite low confidence")
                    return tool, max(confidence, 60)
            
            return tool, confidence
            
        except Exception as e:
            # Fallback to keyword-based routing if LLM fails
            self._emit_status(f"⚠️  LLM routing failed: {str(e)[:50]}, using keyword fallback")
            return self._select_tool_fallback(query)
    
    def _select_tool_fallback(self, query: str) -> tuple[str, int]:
        """
        Fallback keyword-based tool selection (used if LLM fails)
        """
        query_lower = query.lower()
        tool_scores = {}
        
        for tool_name, config in ROUTING_CONFIG.items():
            if tool_name not in self.capabilities:
                continue
            
            score = 0
            keyword_matches = 0
            priority_weight = config.get("priority_weight", 1)
            
            for keyword in config["keywords"]:
                keyword_lower = keyword.lower()
                if f" {keyword_lower} " in f" {query_lower} ":
                    score += 10 * priority_weight
                    keyword_matches += 1
                elif query_lower.startswith(keyword_lower) or query_lower.endswith(keyword_lower):
                    score += 8 * priority_weight
                    keyword_matches += 1
                elif keyword_lower in query_lower:
                    score += 5 * priority_weight
                    keyword_matches += 1
            
            tool_scores[tool_name] = {"score": score, "matches": keyword_matches}
        
        if not tool_scores or all(s["score"] == 0 for s in tool_scores.values()):
            return "text_generation", 50
        
        best_tool = max(tool_scores, key=lambda t: tool_scores[t]["score"])
        confidence = min(100, tool_scores[best_tool]["matches"] * 25)
        
        return best_tool, confidence
    
    def _select_tool_fallback(self, query: str) -> tuple[str, int]:
        """
        Fallback keyword-based tool selection (used if LLM fails)
        """
        query_lower = query.lower()
        tool_scores = {}
        
        for tool_name, config in ROUTING_CONFIG.items():
            if tool_name not in self.capabilities:
                continue
            
            score = 0
            keyword_matches = 0
            priority_weight = config.get("priority_weight", 1)
            
            for keyword in config["keywords"]:
                keyword_lower = keyword.lower()
                if f" {keyword_lower} " in f" {query_lower} ":
                    score += 10 * priority_weight
                    keyword_matches += 1
                elif query_lower.startswith(keyword_lower) or query_lower.endswith(keyword_lower):
                    score += 8 * priority_weight
                    keyword_matches += 1
                elif keyword_lower in query_lower:
                    score += 5 * priority_weight
                    keyword_matches += 1
            
            tool_scores[tool_name] = {"score": score, "matches": keyword_matches}
        
        if not tool_scores or all(s["score"] == 0 for s in tool_scores.values()):
            return "text_generation", 50
        
        best_tool = max(tool_scores, key=lambda t: tool_scores[t]["score"])
        confidence = min(100, tool_scores[best_tool]["matches"] * 25)
        
        return best_tool, confidence
