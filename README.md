# Intelligent Agent with JSON-RPC & MCP

An intelligent AI agent system with JSON-RPC 2.0 protocol, dynamic tool discovery via MCP (Model Context Protocol), and real-time status updates.

## 🌟 Features

- ✅ **JSON-RPC 2.0** - Full implementation with request tracking and validation
- ✅ **Dynamic Tool Discovery** - Auto-discover and load tools from `mcp/tools/`
- ✅ **Intelligent Routing** - Keyword-based tool selection with confidence scoring
- ✅ **Status Updates** - Real-time processing status ("Thinking", "Calling MCP", etc.)
- ✅ **Chat Logging** - All conversations logged to JSON with metrics
- ✅ **Environment Config** - API keys and settings via `.env` file
- ✅ **Hot Reload** - Add/remove tools without restarting

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example file
copy .env.example .env

# Edit .env and add your API keys
GROK_API_KEY=your_grok_key_here
GROQ_API_KEY=your_groq_key_here
```

### 3. Run the Agent

```bash
# Terminal 1: Start the agent server
python app.py

# Terminal 2: Use the interactive client
python simple_client.py
```

## 📋 Available Tools

- **text_generation** - Detailed explanations using Grok AI
- **code_generation** - Code snippets using Groq AI  
- **web_search** - Current information via DuckDuckGo

## 💬 Example Queries

```
What are the latest news about AI?
Explain how neural networks work
Write code for a binary search algorithm
```

## 📂 Project Structure

```
agent/
├── jsonrpc/           # JSON-RPC 2.0 protocol implementation
├── mcp/
│   ├── server.py      # MCP server with tool registry
│   ├── client.py      # MCP client
│   └── tools/         # Tool modules (add new tools here!)
├── agent/             
│   └── core.py        # Intelligent agent with routing
├── app.py             # Flask application entry point
├── logger.py          # Chat conversation logging
├── config.py          # Configuration from .env
└── simple_client.py   # Interactive client

logs/                  # Chat logs (auto-generated)
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api` | POST | User-facing JSON-RPC (agent methods) |
| `/mcp` | POST | MCP server JSON-RPC (tool methods) |
| `/health` | GET | Health check + tool count |
| `/tools` | GET | List all available tools |
| `/logs/stats` | GET | Session statistics |

## 📖 Documentation

- [Configuration Guide](CONFIGURATION.md) - API keys and model settings
- [Logging Guide](LOGGING_GUIDE.md) - Chat logging and metrics
- [JSON-RPC Map](JSONRPC_IMPLEMENTATION_MAP.md) - Implementation details
- [Quick Start](QUICK_START.md) - See JSON-RPC messages in action

## 🎯 Adding New Tools

1. Create `mcp/tools/your_tool.py`:

```python
TOOL_NAME = "your_tool"
TOOL_DESCRIPTION = "What this tool does"
TOOL_PARAMETERS = {"param": "description"}

def execute(params: dict) -> str:
    # Your implementation
    return "result"
```

2. Reload tools:
```bash
curl -X POST http://localhost:5000/tools/reload
```

Agent automatically discovers the new tool!

## 🔒 Environment Variables

See `.env.example` for all configuration options:

- `GROK_API_KEY` - Grok AI API key
- `GROQ_API_KEY` - Groq AI API key  
- `TEXT_GENERATION_MODEL` - Model for text generation
- `CODE_GENERATION_MODEL` - Model for code generation
- `SERVER_PORT` - Server port (default: 5000)

## 📊 Features in Detail

### Intelligent Routing
Agent analyzes queries and selects the best tool based on keywords with confidence scoring.

### Status Updates
Real-time feedback during processing:
- 💭 Thinking... analyzing request
- 🎯 Selected tool: web_search (90%)
- 🔍 Executing web search...
- ✨ Response ready

### Chat Logging
All conversations automatically logged to `logs/` with:
- Request/response content
- Tool used and confidence
- Response times
- Timestamps

## 🛠️ Development

Run with JSON-RPC monitoring:
```bash
python app.py --monitor
```

View all JSON-RPC communications in console with formatted output.

## 📜 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Add new tools in `mcp/tools/`
4. Test with `python simple_client.py`
5. Submit a pull request

## ⚙️ Requirements

- Python 3.14.2+
- Flask 3.0.3+
- See `requirements.txt` for full list

## 🎉 Acknowledgments

Built with JSON-RPC 2.0 specification and Model Context Protocol (MCP) for extensible AI agent architecture.
