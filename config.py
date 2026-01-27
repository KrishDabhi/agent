import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== API Configuration ====================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ==================== Model Configuration ====================
# Text Generation Model (Grok)
TEXT_GENERATION_MODEL = os.getenv("TEXT_GENERATION_MODEL", "groq-beta")
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
    "web_search": {
        "keywords": [
            # Booking-related
            "book", "booking", "reserve", "reservation", "ticket", "tickets",
            # Travel-related
            "flight", "flights", "airline", "airlines", "fly", "flying",
            "train", "trains", "railway", "metro", "bus", "buses",
            "hotel", "hotels", "accommodation", "stay",
            "travel", "trip", "journey", "destination",
            # Real-time & current info
            "current", "latest", "today", "now", "real-time", "recent", "update", "updates",
            "news", "trending", "happening", "live",
            # Prices & shopping
            "price", "prices", "cost", "costs", "buy", "purchase", "shop", "shopping",
            "deal", "deals", "offer", "offers", "discount",
            # Location & time-sensitive
            "weather", "forecast", "temperature",
            "tomorrow", "next week", "schedule", "timing", "when",
            # Queries requiring fresh data
            "find", "search for", "look for", "locate", "where can i",
            "best", "top", "compare", "comparison"
        ],
        "priority_weight": 3,  # High priority for these keywords
        "engine": "duckduckgo"
    },
    "code_generation": {
        "keywords": [
            "write code", "generate code", "implement", "coding", "programming",
            "script", "function", "class", "method", "algorithm",
            "create a", "build a", "develop", "code for",
            "python", "javascript", "java", "c++", "sql",
            "debug", "fix code", "refactor",
            "api", "endpoint", "database query"
        ],
        "priority_weight": 2,  # Medium-high priority
        "model": CODE_GENERATION_MODEL
    },
    "text_generation": {
        "keywords": [
            "explain", "what is", "how does", "why", "difference between",
            "concept", "theory", "protocol", "detail", "describe",
            "tell me about", "define", "meaning", "understand",
            "tutorial", "learn", "teach me", "guide"
        ],
        "priority_weight": 1,  # Lower priority - fallback option
        "model": TEXT_GENERATION_MODEL
    }
}

# Confidence threshold - don't use tool if confidence below this
CONFIDENCE_THRESHOLD = 70

# ==================== Server Configuration ====================
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"