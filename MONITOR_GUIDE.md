# JSON-RPC Communication Monitoring Guide

## Overview
Monitor all JSON-RPC requests and responses flowing through your intelligent agent system in real-time!

## Features
- 📤 **Request Tracking** - See every JSON-RPC request with method, params, and routing
- 📥 **Response Tracking** - View responses with results, errors, and metadata
- 🎨 **Color Coded** - Different colors for USER layer (Client↔Agent) and MCP layer (Agent↔MCP Server)
- ⏱️ **Timestamps** - Precise timing for each communication
- 📊 **Metadata Display** - Tool used, confidence, response times
- 💾 **Persistent Logs** - All communications saved to `logs/communications.jsonl`

## Quick Start

### Step 1: Start the Agent with Monitoring
```bash
python app.py --monitor
```

You'll see:
```
📊 Enabling JSON-RPC Communication Monitoring...
✅ Monitoring enabled
💡 Run 'python monitor_viewer.py' in another terminal to see communications
```

### Step 2: Open Monitor in Separate Terminal
```bash
# Open a new terminal window/tab
python monitor_viewer.py
```

You'll see:
```
================================================================================
🔍 JSON-RPC COMMUNICATION MONITOR
================================================================================
Monitoring all JSON-RPC requests and responses...
Press Ctrl+C to stop
================================================================================
```

### Step 3: Use the Client
```bash
# Open yet another terminal (3rd one)
python simple_client.py
```

Type your queries and watch the monitor terminal show all communications!

## What You'll See

### Example Communication Flow

**Terminal 2 (Monitor) will show:**

```
================================================================================
📤 REQUEST #1 [USER Layer]
   Time: 17:30:15.234
   Flow: Client → Agent
   Method: agent.chat
   ID: 1
   Params:
     message: What are the latest news about AI?
================================================================================

--------------------------------------------------------------------------------
✅ RESPONSE #1 [USER Layer]
   Time: 17:30:18.567
   Flow: Agent → Client
   ID: 1
   Metadata:
     tool_used: web_search
     confidence: 90
     total_time: 3.333
   Response Length: 1234 chars
--------------------------------------------------------------------------------

================================================================================
📤 REQUEST #2 [MCP Layer]
   Time: 17:30:15.456
   Flow: Agent → MCP Server
   Method: web_search
   ID: 2
   Params:
     query: What are the latest news about AI?
================================================================================

--------------------------------------------------------------------------------
✅ RESPONSE #2 [MCP Layer]
   Time: 17:30:17.890
   Flow: MCP Server → Agent
   ID: 2
   Result: 1. AI Latest News...
--------------------------------------------------------------------------------
```

## Communication Layers

### 🔵 USER Layer (Cyan)
- **Client → Agent** - User sends query via JSON-RPC
- **Agent → Client** - Agent returns response with metadata

### 🟣 MCP Layer (Magenta)
- **Agent → MCP Server** - Agent calls tool via internal JSON-RPC
- **MCP Server → Agent** - Tool result returned

## Log File Format

All communications are saved to `logs/communications.jsonl` in JSONL format (one JSON per line):

```json
{"type": "REQUEST", "timestamp": "17:30:15.234", "counter": 1, "layer": "USER", "source": "Client", "destination": "Agent", "data": {...}}
{"type": "RESPONSE", "timestamp": "17:30:18.567", "counter": 1, "layer": "USER", "source": "Agent", "destination": "Client", "data": {...}}
```

## Command Line Options

### Start Agent with Monitoring:
```bash
python app.py --monitor    # Enable monitoring
python app.py --debug      # Enable monitoring + debug mode
python app.py              # Run without monitoring
```

### View Existing Logs:
```bash
# View all communications
cat logs/communications.jsonl

# View in JSON format (pretty print)
cat logs/communications.jsonl | python -m json.tool

# Count requests
grep '"type": "REQUEST"' logs/communications.jsonl | wc -l
```

## Troubleshooting

### Monitor not showing anything
1. Make sure you started `app.py` with `--monitor` flag
2. Verify `monitor_viewer.py` is running
3. Check that `logs/` directory exists

### Colors not showing
- Windows: Install `colorama` or use Windows Terminal
- Linux/Mac: Should work out of the box

### Performance impact
Monitoring adds minimal overhead (<5ms per request). Disable for production:
```bash
python app.py  # Without --monitor flag
```

## Advanced Usage

### Custom Analysis
The log file is in JSONL format, perfect for analysis:

```python
import json

# Read all communications
with open('logs/communications.jsonl', 'r') as f:
    for line in f:
        entry = json.loads(line)
        print(f"{entry['type']}: {entry['data'].get('method', 'N/A')}")
```

### Filter by Layer
```bash
# Only USER layer
grep '"layer": "USER"' logs/communications.jsonl

# Only MCP layer
grep '"layer": "MCP"' logs/communications.jsonl
```

## Summary

**3 Terminal Setup:**
1. **Terminal 1:** `python app.py --monitor` - Agent server
2. **Terminal 2:** `python monitor_viewer.py` - Communication monitor
3. **Terminal 3:** `python simple_client.py` - Chat client

Watch the magic happen in Terminal 2! 🎭
