import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== API Configuration ====================
GROK_API_KEY = os.getenv("GROK_API_KEY", "")

# ==================== Model Configuration ====================
# Text Generation Model (Grok)
TEXT_GENERATION_MODEL = os.getenv("TEXT_GENERATION_MODEL", "grok-beta")
TEXT_GENERATION_TEMPERATURE = float(os.getenv("TEXT_GENERATION_TEMPERATURE", "0.7"))
TEXT_GENERATION_MAX_TOKENS = int(os.getenv("TEXT_GENERATION_MAX_TOKENS", "1000"))

# Code Generation Model (Groq)
CODE_GENERATION_MODEL = os.getenv("CODE_GENERATION_MODEL", "llama3-70b-8192")
CODE_GENERATION_TEMPERATURE = float(os.getenv("CODE_GENERATION_TEMPERATURE", "0.2"))
CODE_GENERATION_MAX_TOKENS = int(os.getenv("CODE_GENERATION_MAX_TOKENS", "800"))

# Web Search Configuration
WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))

# ==================== Tool Configuration ====================
ENABLED_TOOLS = [
    "text_generation",
    "web_search", 
    "code_generation"
]

# ==================== Routing Keywords ====================
ROUTING_CONFIG = {
    "text_generation": {
        "keywords": ["explain", "what is", "how does", "why", "difference between", 
                     "concept", "theory", "protocol", "detail", "describe", "tell me about"],
        "model": TEXT_GENERATION_MODEL
    },
    "code_generation": {
        "keywords": ["write code", "generate code", "implement", "coding", "programming", 
                     "script", "function", "algorithm", "create a", "build a"],
        "model": CODE_GENERATION_MODEL
    },
    "web_search": {
        "keywords": ["current", "latest", "today", "now", "price", "weather", "news", 
                     "trending", "real-time", "recent", "happening", "update"],
        "engine": "duckduckgo"
    }
}

# ==================== Server Configuration ====================
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"