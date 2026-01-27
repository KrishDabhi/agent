# Intelligent Agent - README

## Overview
An intelligent agent that can handle multiple types of queries using different tools based on content analysis.

## Capabilities

### ✅ Code Generation (Priority: HIGHEST)
**When to use:** Writing code, implementing features, building applications

**Triggers:** "write code", "implement", "create", "build", "rag", "api", "python", etc.

**Examples:**
- ✅ "Write code for RAG" → `code_generation` (100%)
- ✅ "Implement REST API in Python" → `code_generation` (100%)
- ✅ "Create a function to sort array" → `code_generation` (80%)

### ✅ Web Search (Priority: MEDIUM)
**When to use:** Real-time info, bookings, prices, news

**Triggers:** "book", "flight", "train", "ticket", "hotel", "price", "news", "weather", "latest"

**Examples:**
- ✅ "Book flight to Paris" → `web_search` (70%)
- ✅ "Find train tickets Delhi Mumbai" → `web_search` (100%)
- ✅ "Latest tech news" → `web_search` (70%)
- ✅ "Weather tomorrow" → `web_search` (100%)

### ⚠️ Text Generation (Priority: LOW)
**When to use:** Explanations, definitions, concepts

**Triggers:** "explain", "what is", "how does", "why", "difference"

**Current Limitations:**
- ❌ "Explain REST API" → incorrectly routes to `web_search`
- ❌ "What is machine learning" → incorrectly routes to `web_search`
- ⚠️ Educational queries need improvement

### ✅ Conversational
**When to use:** Greetings, simple conversation

**Examples:**
- ✅ "hi", "hello" → Friendly welcome
- ✅ "thanks" → Acknowledgment
- ✅ Single characters → Asks for clarification

## Accuracy
**Overall: 78.6% Success Rate**

| Category | Accuracy |
|----------|----------|
| Code Generation | 100% ✅ |
| Travel/Bookings | 85-100% ✅ |
| Conversational | 100% ✅ |
| Explanations | ~30% ❌ |

## Known Issues

### 1. Educational Queries
"Explain" and "What is" queries often incorrectly route to web_search instead of text_generation.

**Workaround:** Be more specific:
- Instead of: "Explain REST API"
- Try: "Tell me about REST API" or "What does REST API mean"

### 2. Ambiguous Queries
Very short or vague queries may not route correctly.

**Solution:** Provide more context in your query.

### 3. Web Search Limitations
DuckDuckGo sometimes returns 0 results. This is an external API limitation.

## Configuration

### Priority Weights
- **Code Generation:** 3 (HIGHEST)
- **Web Search:** 2 (MEDIUM)
- **Text Generation:** 1 (LOW/FALLBACK)

### Confidence Threshold
**70%** - Agent will use alternative tool if confidence is below this for non-realtime queries.

## Usage

**Start Server:**
```bash
python app.py
```

**Start Client:**
```bash
python simple_client.py
```

## Files
- `agent/core.py` - Main agent logic
- `config.py` - Routing keywords and priorities
- `formatter.py` - Response formatting
- `logger.py` - Conversation logging

## Future Improvements
1. Fix text_generation routing for educational queries
2. Improve ambiguous query handling
3. Add more specific keyword patterns
4. Consider ML-based intent classification

---

**Honest Assessment:** The agent works well for code generation and travel/booking queries (85-100%), but needs improvement for educational queries (30%). Not perfect, but functional for most use cases.
