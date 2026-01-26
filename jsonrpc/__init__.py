"""JSON-RPC 2.0 handler implementation with request tracking and validation"""
import json
import time
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
try:
    from monitor import get_monitor, is_monitoring_enabled
except ImportError:
    get_monitor = lambda: None
    is_monitoring_enabled = lambda: False


class JsonRpcHandler:
    """Pure JSON-RPC 2.0 implementation with comprehensive tracking and validation"""
    
    def __init__(self):
        self.methods: Dict[str, Callable] = {}
        self.request_history: List[Dict[str, Any]] = []
        self.response_history: List[Dict[str, Any]] = []
        self.max_history = 100  # Keep last 100 requests/responses

    def register(self, method_name: str, func: Callable) -> None:
        """Register a method handler"""
        self.methods[method_name] = func
        print(f"📝 Registered JSON-RPC method: {method_name}")
    
    def get_request_history(self) -> List[Dict[str, Any]]:
        """Get request history for debugging"""
        return self.request_history
    
    def get_response_history(self) -> List[Dict[str, Any]]:
        """Get response history for debugging"""
        return self.response_history
    
    def _track_request(self, request: Dict[str, Any]) -> None:
        """Track incoming request"""
        self.request_history.append({
            "timestamp": datetime.now().isoformat(),
            "request": request
        })
        # Keep only last max_history items
        if len(self.request_history) > self.max_history:
            self.request_history.pop(0)
    
    def _track_response(self, response: Dict[str, Any]) -> None:
        """Track outgoing response"""
        self.response_history.append({
            "timestamp": datetime.now().isoformat(),
            "response": response
        })
        # Keep only last max_history items
        if len(self.response_history) > self.max_history:
            self.response_history.pop(0)
    
    def _validate_request(self, request: Any) -> tuple[bool, Optional[str]]:
        """
        Validate JSON-RPC request structure
        
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(request, dict):
            return False, "Request must be a JSON object"
        
        # Check required fields
        if "jsonrpc" not in request:
            return False, "Missing 'jsonrpc' field"
        
        if request.get("jsonrpc") != "2.0":
            return False, "Invalid 'jsonrpc' version, must be '2.0'"
        
        if "method" not in request:
            return False, "Missing 'method' field"
        
        if not isinstance(request.get("method"), str):
            return False, "'method' must be a string"
        
        # Params is optional but must be object or array if present
        if "params" in request:
            params = request["params"]
            if not isinstance(params, (dict, list)):
                return False, "'params' must be an object or array"
        
        return True, None
    
    def handle(self, raw_data: str) -> Optional[str]:
        """
        Handle a JSON-RPC 2.0 request with validation and tracking
        
        Args:
            raw_data: JSON string containing the request
            
        Returns:
            JSON string response or None for notifications
        """
        # Parse JSON
        try:
            request = json.loads(raw_data)
            
            # ===== PRINT RAW REQUEST =====
            print("\n" + "="*80)
            print("📤 INCOMING JSON-RPC REQUEST")
            print("="*80)
            print(json.dumps(request, indent=2, ensure_ascii=False))
            print("="*80)
            
        except json.JSONDecodeError as e:
            error_response = self._error_response(None, -32700, f"Parse error: {str(e)}")
            print(f"❌ JSON-RPC Parse Error: {str(e)}")
            return error_response
        
        # Log request if monitoring is enabled
        if is_monitoring_enabled():
            monitor = get_monitor()
            if monitor:
                # Determine layer based on method
                layer = "MCP" if isinstance(request, dict) and request.get("method", "").startswith(("web_search", "text_generation", "code_generation")) else "USER"
                source = "Client" if layer == "USER" else "Agent"
                destination = "Agent" if layer == "USER" else "MCP Server"
                monitor.log_request(source, destination, request, layer)
        
        # Handle batch requests
        if isinstance(request, list):
            return self._handle_batch(request)
        
        # Handle single request
        return self._handle_single(request)
    
    def _handle_batch(self, requests: list) -> str:
        """Handle batch JSON-RPC requests"""
        responses = []
        for req in requests:
            response = self._handle_single(req)
            if response is not None:  # Skip notifications
                responses.append(json.loads(response))
        
        return json.dumps(responses) if responses else None
    
    def _handle_single(self, request: Dict[str, Any]) -> Optional[str]:
        """Handle a single JSON-RPC request with validation and tracking"""
        start_time = time.time()
        
        # Track request
        self._track_request(request)
        
        # Validate request structure
        is_valid, error_msg = self._validate_request(request)
        if not is_valid:
            error_response = self._error_response(request.get("id"), -32600, f"Invalid Request: {error_msg}")
            print(f"❌ Validation Error: {error_msg}")
            return error_response
        
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        # Check if method exists
        if method not in self.methods:
            error_response = self._error_response(request_id, -32601, f"Method not found: {method}")
            print(f"❌ Method not found: {method}")
            print(f"   Available methods: {list(self.methods.keys())}")
            return error_response
        
        # Execute method
        try:
            print(f"🔄 Executing JSON-RPC method: {method}")
            result = self.methods[method](params)
            
            elapsed = time.time() - start_time
            print(f"✅ Method '{method}' completed in {elapsed:.3f}s")
            
            # Notification (no response expected)
            if request_id is None:
                return None
            
            response = self._success_response(request_id, result)
            self._track_response(json.loads(response))
            
            # ===== PRINT RAW RESPONSE =====
            print("\n" + "-"*80)
            print("📥 OUTGOING JSON-RPC RESPONSE")
            print("-"*80)
            print(json.dumps(json.loads(response), indent=2, ensure_ascii=False))
            print("-"*80 + "\n")
            
            return response
            
        except TypeError as e:
            error_response = self._error_response(request_id, -32602, f"Invalid params: {str(e)}")
            print(f"❌ Invalid params for '{method}': {str(e)}")
            return error_response
        except Exception as e:
            error_response = self._error_response(request_id, -32603, f"Internal error: {str(e)}")
            print(f"❌ Internal error in '{method}': {str(e)}")
            import traceback
            traceback.print_exc()
            return error_response
    
    def _success_response(self, request_id: Any, result: Any) -> str:
        """Create a success response"""
        return json.dumps({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })
    
    def _error_response(self, request_id: Any, code: int, message: str) -> str:
        """Create an error response"""
        return json.dumps({
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        })


__all__ = ['JsonRpcHandler']