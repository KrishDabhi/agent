# JSON-RPC 2.0 Implementation Reference

## Complete Implementation Map of 7 Core Principles

This document shows **exactly where** each JSON-RPC 2.0 principle is implemented in your project.

---

## 1️⃣ **JSON Message Building Logic** (बनावणी/banavani)

### Where: `jsonrpc/__init__.py`

**Success Response Builder:**
```python
# Lines 186-192
def _success_response(self, request_id: Any, result: Any) -> str:
    """Create a success response"""
    return json.dumps({
        "jsonrpc": "2.0",
        "result": result,
        "id": request_id
    })
```

**Error Response Builder:**
```python
# Lines 194-204
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
```

**Request Builder (Client Side):**
```python
# mcp/client.py - Lines 74-81
payload = {
    "jsonrpc": "2.0",
    "method": tool_name,
    "params": params,
    "id": self.request_id
}
```

---

## 2️⃣ **Transport (HTTP)**

### Where: `app.py` (Server Side)

**User API Endpoint:**
```python
# Lines 120-138
@app.route("/api", methods=["POST"])
def user_endpoint():
    """User-facing JSON-RPC endpoint with logging"""
    try:
        get_agent()
        response = user_rpc.handle(request.data.decode())
        if response is None:
            return "", 204
        # ... logging code ...
        return response, 200, {"Content-Type": "application/json"}
```

**MCP Server Endpoint:**
```python
# Lines 140-151
@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    """MCP Server JSON-RPC endpoint"""
    try:
        response = mcp_server.handle_request(request.data.decode())
        if response is None:
            return "", 204
        return response, 200, {"Content-Type": "application/json"}
```

### Where: `mcp/client.py` (Client Side)

**HTTP POST Transport:**
```python
# Lines 84-111
try:
    response = requests.post(
        self.server_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
```

---

## 3️⃣ **Method Name → Function Mapping**

### Where: `jsonrpc/__init__.py`

**Method Registry:**
```python
# Lines 13-15
def __init__(self):
    self.methods: Dict[str, Callable] = {}  # The mapping dictionary
    self.request_history: List[Dict[str, Any]] = []
    self.response_history: List[Dict[str, Any]] = []
```

**Register Method:**
```python
# Lines 17-20
def register(self, method_name: str, func: Callable) -> None:
    """Register a method handler"""
    self.methods[method_name] = func
    print(f"📝 Registered JSON-RPC method: {method_name}")
```

**Method Lookup & Execution:**
```python
# Lines 151-157
request_id = request.get("id")
method = request.get("method")
params = request.get("params", {})

# Check if method exists
if method not in self.methods:
    error_response = self._error_response(request_id, -32601, f"Method not found: {method}")
    print(f"❌ Method not found: {method}")
    print(f"   Available methods: {list(self.methods.keys())}")
    return error_response
```

### Where: Method Registration Happens

**User API Methods (`app.py` - Lines 97-100):**
```python
user_rpc.register("agent.chat", lambda params: agent.handle_user_request("chat", params))
user_rpc.register("agent.execute_tool", lambda params: agent.handle_user_request("execute_tool", params))
user_rpc.register("agent.list_capabilities", lambda params: agent.handle_user_request("list_capabilities", params))
user_rpc.register("agent.refresh_capabilities", lambda params: agent.handle_user_request("refresh_capabilities", params))
```

**MCP Tool Methods (`mcp/server.py` - Lines 12-16):**
```python
def _load_tools(self):
    """Dynamically load all available tools"""
    tools_data = discover_tools()
    for tool_name, tool_data in tools_data.items():
        self.rpc_handler.register(tool_name, tool_data["func"])
        self.tools_metadata[tool_name] = tool_data["metadata"]
```

---

## 4️⃣ **Params Validation**

### Where: `jsonrpc/__init__.py`

**Request Structure Validation:**
```python
# Lines 53-85
def _validate_request(self, request: Any) -> tuple[bool, Optional[str]]:
    """Validate JSON-RPC request structure"""
    
    # Check if request is a dict
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
```

**Validation Usage:**
```python
# Lines 138-143
# Validate request structure
is_valid, error_msg = self._validate_request(request)
if not is_valid:
    error_response = self._error_response(request.get("id"), -32600, f"Invalid Request: {error_msg}")
    print(f"❌ Validation Error: {error_msg}")
    return error_response
```

### Where: Tool-Level Validation

**Example in `mcp/tools/text_generation.py`:**
```python
# Lines 21-24
prompt = params.get("prompt", "")

if not prompt:
    raise ValueError("'prompt' parameter is required")
```

**Example in `mcp/tools/web_search.py`:**
```python
# Lines 13-15
query = params.get("query", "")

if not query:
    raise ValueError("'query' parameter is required")
```

---

## 5️⃣ **Function Execution**

### Where: `jsonrpc/__init__.py`

**Safe Execution with Error Handling:**
```python
# Lines 160-183
# Execute method
try:
    print(f"🔄 Executing JSON-RPC method: {method}")
    result = self.methods[method](params)  # ← ACTUAL EXECUTION
    
    elapsed = time.time() - start_time
    print(f"✅ Method '{method}' completed in {elapsed:.3f}s")
    
    # Notification (no response expected)
    if request_id is None:
        return None
    
    response = self._success_response(request_id, result)
    self._track_response(json.loads(response))
    
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
```

---

## 6️⃣ **Error Codes Handling**

### Where: `jsonrpc/__init__.py`

All standard JSON-RPC 2.0 error codes are implemented:

**Parse Error (-32700):**
```python
# Lines 100-103
except json.JSONDecodeError as e:
    error_response = self._error_response(None, -32700, f"Parse error: {str(e)}")
    print(f"❌ JSON-RPC Parse Error: {str(e)}")
    return error_response
```

**Invalid Request (-32600):**
```python
# Lines 138-143
is_valid, error_msg = self._validate_request(request)
if not is_valid:
    error_response = self._error_response(request.get("id"), -32600, f"Invalid Request: {error_msg}")
    print(f"❌ Validation Error: {error_msg}")
    return error_response
```

**Method Not Found (-32601):**
```python
# Lines 151-157
if method not in self.methods:
    error_response = self._error_response(request_id, -32601, f"Method not found: {method}")
    print(f"❌ Method not found: {method}")
    print(f"   Available methods: {list(self.methods.keys())}")
    return error_response
```

**Invalid Params (-32602):**
```python
# Lines 173-176
except TypeError as e:
    error_response = self._error_response(request_id, -32602, f"Invalid params: {str(e)}")
    print(f"❌ Invalid params for '{method}': {str(e)}")
    return error_response
```

**Internal Error (-32603):**
```python
# Lines 177-183
except Exception as e:
    error_response = self._error_response(request_id, -32603, f"Internal error: {str(e)}")
    print(f"❌ Internal error in '{method}': {str(e)}")
    import traceback
    traceback.print_exc()
    return error_response
```

### Where: Client-Side Error Handling

**In `mcp/client.py`:**
```python
# Lines 100-112
except requests.exceptions.RequestException as e:
    error = {
        "error": {
            "code": -32603,
            "message": f"Transport error: {str(e)}"
        }
    }
    return error
except json.JSONDecodeError as e:
    error = {
        "error": {
            "code": -32700,
            "message": f"Parse error: {str(e)}"
        }
    }
    return error
```

---

## 7️⃣ **Request–Response ID Tracking**

### Where: `jsonrpc/__init__.py`

**Request History Tracking:**
```python
# Lines 32-40
def _track_request(self, request: Dict[str, Any]) -> None:
    """Track incoming request"""
    self.request_history.append({
        "timestamp": datetime.now().isoformat(),
        "request": request
    })
    # Keep only last max_history items
    if len(self.request_history) > self.max_history:
        self.request_history.pop(0)
```

**Response History Tracking:**
```python
# Lines 42-51
def _track_response(self, response: Dict[str, Any]) -> None:
    """Track outgoing response"""
    self.response_history.append({
        "timestamp": datetime.now().isoformat(),
        "response": response
    })
    # Keep only last max_history items
    if len(self.response_history) > self.max_history:
        self.response_history.pop(0)
```

**Usage in Request Handling:**
```python
# Line 135
self._track_request(request)

# Line 165
self._track_response(json.loads(response))
```

**ID Matching:**
```python
# Lines 145-147
request_id = request.get("id")
method = request.get("method")
params = request.get("params", {})

# ... later ...

# Line 163
response = self._success_response(request_id, result)  # Same ID returned
```

### Where: Client-Side ID Tracking

**In `mcp/client.py`:**
```python
# Lines 9-10
def __init__(self, server_url: str, status_callback: Optional[Callable] = None):
    self.server_url = server_url
    self.request_id = 0  # ← ID counter
    
# Lines 72-81
def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    self.request_id += 1  # ← Increment for each request
    
    payload = {
        "jsonrpc": "2.0",
        "method": tool_name,
        "params": params,
        "id": self.request_id  # ← Use unique ID
    }
```

---

## 📊 **Summary Table**

| Principle | Main File | Lines | Secondary Files |
|-----------|-----------|-------|-----------------|
| 1. JSON Building | `jsonrpc/__init__.py` | 186-204 | `mcp/client.py` (74-81) |
| 2. HTTP Transport | `app.py` | 120-151 | `mcp/client.py` (84-111) |
| 3. Method Mapping | `jsonrpc/__init__.py` | 13-20, 151-157 | `app.py` (97-100), `mcp/server.py` (12-16) |
| 4. Params Validation | `jsonrpc/__init__.py` | 53-85, 138-143 | All `mcp/tools/*.py` files |
| 5. Function Execution | `jsonrpc/__init__.py` | 160-183 | - |
| 6. Error Codes | `jsonrpc/__init__.py` | 100-183 | `mcp/client.py` (100-112) |
| 7. ID Tracking | `jsonrpc/__init__.py` | 32-51, 135, 165 | `mcp/client.py` (9-10, 72-81) |

---

## 🎯 **Key Files Breakdown**

### Core JSON-RPC Implementation
- **`jsonrpc/__init__.py`** - All 7 principles implemented here ✅

### Transport Layer
- **`app.py`** - HTTP endpoints for JSON-RPC
- **`mcp/client.py`** - HTTP client for MCP calls

### Business Logic
- **`agent/core.py`** - Uses JSON-RPC to communicate
- **`mcp/server.py`** - Uses JSON-RPC for tool registry
- **`mcp/tools/*.py`** - Individual tool implementations

All communication in your system follows JSON-RPC 2.0 specification! 🎉
