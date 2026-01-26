# Configuration Guide

## Setup Instructions

### 1. Copy the Example File
```bash
copy .env.example .env
```

### 2. Edit .env File
Open `.env` and add your API keys:

```env
# ==================== API Keys ====================
GROK_API_KEY=xai-your-actual-grok-key-here
GROQ_API_KEY=gsk_your-actual-groq-key-here

# ==================== Model Settings ====================
# Text Generation (Grok)
TEXT_GENERATION_MODEL=grok-beta
TEXT_GENERATION_TEMPERATURE=0.7
TEXT_GENERATION_MAX_TOKENS=1000

# Code Generation (Groq)
CODE_GENERATION_MODEL=llama3-70b-8192
CODE_GENERATION_TEMPERATURE=0.2
CODE_GENERATION_MAX_TOKENS=800

# Web Search
WEB_SEARCH_MAX_RESULTS=5

# ==================== Server Configuration ====================
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG_MODE=True
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Agent
```bash
python app.py
```

## Configuration Options

### API Keys
- **GROK_API_KEY**: Get from https://console.x.ai
- **GROQ_API_KEY**: Get from https://console.groq.com

### Model Settings

#### Text Generation (Grok)
- **TEXT_GENERATION_MODEL**: Model to use (default: grok-beta)
- **TEXT_GENERATION_TEMPERATURE**: Creativity level 0.0-1.0 (default: 0.7)
- **TEXT_GENERATION_MAX_TOKENS**: Max response length (default: 1000)

#### Code Generation (Groq)
- **CODE_GENERATION_MODEL**: Model to use (default: llama3-70b-8192)
  - Options: `llama3-70b-8192`, `llama3-8b-8192`, `mixtral-8x7b-32768`
- **CODE_GENERATION_TEMPERATURE**: Precision level 0.0-1.0 (default: 0.2 - more deterministic)
- **CODE_GENERATION_MAX_TOKENS**: Max code length (default: 800)

#### Web Search
- **WEB_SEARCH_MAX_RESULTS**: Number of search results to return (default: 5)

### Server Settings
- **SERVER_HOST**: Host to bind to (default: 0.0.0.0 - all interfaces)
- **SERVER_PORT**: Port number (default: 5000)
- **DEBUG_MODE**: Enable Flask debug mode (default: True)

## Troubleshooting

### Issue: Agent can't get tool list
✅ **Fixed!** Now uses local MCP client instead of HTTP calls during initialization.

### Issue: Missing API keys
Add your keys to the `.env` file. The agent will still work with web_search if other keys are missing.

### Issue: Import errors
Run: `pip install -r requirements.txt`
