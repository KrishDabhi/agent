from flask import Flask, request, jsonify
from jsonrpc import JsonRpcHandler
from mcp.server import MCPServer
from agent.core import Agent
from mcp.client import MCPClient
from config import SERVER_HOST, SERVER_PORT, DEBUG_MODE
from logger import get_logger
import os
import sys

# Flask Application
app = Flask(__name__)

# Initialize MCP Server (auto-discovers tools)
print("=" * 60)
print("🚀 Initializing Intelligent Agent System")
print("=" * 60)

# Check for monitoring flag
if '--monitor' in sys.argv or '--debug' in sys.argv:
    print("📊 Enabling JSON-RPC Communication Monitoring...")
    try:
        from monitor import enable_monitoring
        enable_monitoring()
        print("✅ Monitoring enabled")
        print("💡 Run 'python monitor_viewer.py' in another terminal to see communications")
    except Exception as e:
        print(f"⚠️  Could not enable monitoring: {e}")

mcp_server = MCPServer()

# Status callback for agent
def agent_status_callback(status):
    """Callback to print agent status updates"""
    print(f"  📊 Status: {status}")

# Initialize User-facing JSON-RPC handler
user_rpc = JsonRpcHandler()

# Global agent instance (will be initialized after first request)
agent = None

def get_agent():
    """Lazy initialization of agent to avoid circular dependency"""
    global agent
    if agent is None:
        # Get tools directly from MCP server instead of HTTP call
        print("🔍 Discovering capabilities from MCP server...")
        tools_metadata = mcp_server.list_tools()
        
        # Create a mock client that doesn't need HTTP
        class LocalMCPClient:
            def __init__(self, mcp_server_instance, status_callback=None):
                self.mcp_server = mcp_server_instance
                self.status_callback = status_callback
                self._available_tools = None
            
            def _emit_status(self, status: str):
                if self.status_callback:
                    self.status_callback(status)
            
            def list_tools(self):
                """Get tools directly from MCP server"""
                tools_dict = self.mcp_server.list_tools()
                self._available_tools = tools_dict
                print(f"✅ Discovered {len(self._available_tools)} tools")
                return self._available_tools
            
            def get_available_tools(self):
                if self._available_tools is None:
                    return self.list_tools()
                return self._available_tools
            
            def reload_tools(self):
                self._emit_status("Requesting MCP server to reload tools...")
                self.mcp_server._load_tools()
                return self.list_tools()
            
            def call_tool(self, tool_name: str, params: dict):
                """Call tool via JSON-RPC internally"""
                self._emit_status(f"Calling MCP tool: {tool_name}")
                
                import json
                payload = json.dumps({
                    "jsonrpc": "2.0",
                    "method": tool_name,
                    "params": params,
                    "id": 1
                })
                
                response_str = self.mcp_server.handle_request(payload)
                if response_str:
                    response = json.loads(response_str)
                    if "error" in response:
                        return {"error": response["error"]}
                    return {"result": response.get("result")}
                return {"error": {"code": -32603, "message": "No response from MCP"}}
        
        # Initialize agent with local client
        local_client = LocalMCPClient(mcp_server, status_callback=agent_status_callback)
        agent = Agent(local_client, status_callback=agent_status_callback)
        
        # Register agent methods
        user_rpc.register("agent.chat", lambda params: agent.handle_user_request("chat", params))
        user_rpc.register("agent.execute_tool", lambda params: agent.handle_user_request("execute_tool", params))
        user_rpc.register("agent.list_capabilities", lambda params: agent.handle_user_request("list_capabilities", params))
        user_rpc.register("agent.refresh_capabilities", lambda params: agent.handle_user_request("refresh_capabilities", params))
        
        print("✅ Agent initialized successfully")
    
    return agent

@app.route("/api", methods=["POST"])
def user_endpoint():
    """User-facing JSON-RPC endpoint with logging"""
    try:
        # Ensure agent is initialized
        get_agent()
        
        response = user_rpc.handle(request.data.decode())
        if response is None:
            return "", 204
        
        # Log the conversation if it's a chat request
        try:
            import json
            request_data = json.loads(request.data.decode())
            response_data = json.loads(response)
            
            if request_data.get("method") == "agent.chat" and "result" in response_data:
                logger = get_logger()
                result = response_data["result"]
                
                logger.log_conversation(
                    user_message=request_data["params"]["message"],
                    agent_response=result.get("response", ""),
                    metadata=result.get("metadata", {})
                )
        except Exception as log_error:
            print(f"⚠️  Logging error: {log_error}")
        
        return response, 200, {"Content-Type": "application/json"}
    except Exception as e:
        print(f"❌ Error in /api: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    """MCP Server JSON-RPC endpoint"""
    try:
        response = mcp_server.handle_request(request.data.decode())
        if response is None:
            return "", 204
        return response, 200, {"Content-Type": "application/json"}
    except Exception as e:
        print(f"❌ Error in /mcp: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "agent": "intelligent",
        "mcp": "ready",
        "tools": len(mcp_server.list_tools())
    }), 200

@app.route("/tools", methods=["GET"])
def list_tools():
    """List all available tools"""
    tools = mcp_server.list_tools()
    return jsonify({"tools": list(tools.values())}), 200

@app.route("/tools/reload", methods=["POST"])
def reload_tools():
    """Reload tools from directory"""
    try:
        # Reload on MCP server
        mcp_server._load_tools()
        
        # Refresh agent capabilities if initialized
        if agent:
            agent.refresh_capabilities()
        
        return jsonify({
            "status": "reloaded",
            "tool_count": len(mcp_server.list_tools())
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logs", methods=["GET"])
def get_logs():
    """Get list of all log files"""
    try:
        logger = get_logger()
        log_files = logger.get_all_logs()
        return jsonify({
            "current_session": logger.session_id,
            "log_files": log_files
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logs/current", methods=["GET"])
def get_current_log():
    """Get current session log"""
    try:
        logger = get_logger()
        log_data = logger.load_log_file(f"chat_{logger.session_id}.json")
        return jsonify(log_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logs/stats", methods=["GET"])
def get_session_stats():
    """Get current session statistics"""
    try:
        logger = get_logger()
        stats = logger.get_session_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎯 Intelligent Agent with Dynamic Tools Started")
    print("=" * 60)
    print(f"   👤 User API (JSON-RPC): http://{SERVER_HOST}:{SERVER_PORT}/api")
    print(f"   🔧 MCP Server (JSON-RPC): http://{SERVER_HOST}:{SERVER_PORT}/mcp")
    print(f"   💊 Health Check: http://{SERVER_HOST}:{SERVER_PORT}/health")
    print(f"   📋 List Tools: http://{SERVER_HOST}:{SERVER_PORT}/tools")
    print(f"   🔄 Reload Tools: POST http://{SERVER_HOST}:{SERVER_PORT}/tools/reload")
    print("=" * 60)
    print(f"   ✨ Discovered {len(mcp_server.list_tools())} tools")
    print(f"   💡 Add new tools: Create .py files in mcp/tools/ directory")
    print(f"   ⚙️  Configure: Edit .env file for API keys and model settings")
    print("=" * 60 + "\n")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_MODE)