# Quick Usage Guide

## See JSON-RPC Communications

### Method 1: Simple - Just Run the Client (Recommended)

```bash
# Terminal 1: Start agent
python app.py

# Terminal 2: Use client
python simple_client.py
```

**What you'll see:**

**In Terminal 2 (Client):**
```
🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵
📤 SENDING JSON-RPC REQUEST TO AGENT:
{
  "jsonrpc": "2.0",
  "method": "agent.chat",
  "params": {
    "message": "What are the latest news?"
  },
  "id": 1
}
🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵

🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢
📥 RECEIVED JSON-RPC RESPONSE FROM AGENT:
{
  "jsonrpc": "2.0",
  "result": {
    "response": "Based on search results...",
    "status_updates": [...],
    "metadata": {
      "tool_used": "web_search",
      "confidence": 90,
      "total_time": 3.45
    }
  },
  "id": 1
}
🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢
```

**In Terminal 1 (Server):**
```
================================================================================
📤 INCOMING JSON-RPC REQUEST
================================================================================
{
  "jsonrpc": "2.0",
  "method": "agent.chat",
  "params": {
    "message": "What are the latest news?"
  },
  "id": 1
}
================================================================================

🤖 Agent: 💭 Thinking... analyzing your request
🤖 Agent: 🎯 Selected tool: web_search (confidence: 90%)
🤖 Agent: ⚙️  Executing web_search...

================================================================================
📤 INCOMING JSON-RPC REQUEST (Internal - MCP Layer)
================================================================================
{
  "jsonrpc": "2.0",
  "method": "web_search",
  "params": {
    "query": "What are the latest news?"
  },
  "id": 2
}
================================================================================

🔄 Executing JSON-RPC method: web_search
✅ Method 'web_search' completed in 2.341s

--------------------------------------------------------------------------------
📥 OUTGOING JSON-RPC RESPONSE (Internal - MCP Layer)
--------------------------------------------------------------------------------
{
  "jsonrpc": "2.0",
  "result": "1. Latest News...",
  "id": 2
}
--------------------------------------------------------------------------------

🤖 Agent: ✅ web_search completed in 2.34s
🤖 Agent: ✨ Response ready

--------------------------------------------------------------------------------
📥 OUTGOING JSON-RPC RESPONSE
--------------------------------------------------------------------------------
{
  "jsonrpc": "2.0",
  "result": {
    "response": "Based on search results...",
    "status_updates": [...]
  },
  "id": 1
}
--------------------------------------------------------------------------------
```

## That's It!

Now you can see **every JSON-RPC message** as it flows through the system:
- ✅ Client → Agent request
- ✅ Agent → Client response  
- ✅ Agent → MCP Server request (internal)
- ✅ MCP Server → Agent response (internal)

All automatically displayed in your terminal! 🎉
