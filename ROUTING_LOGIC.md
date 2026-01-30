# 🗺️ Agent Routing Logic - Complete Guide

## Overview
The agent has **two routing systems** working together:
1. **LLM-based routing** (primary, 100% accuracy)
2. **Keyword-based routing** (fallback if LLM fails)

---

## 📍 File Locations

### 1. Keyword Configuration: `config.py` (Lines 31-88)
This is where all the **rules** are defined!

```python
ROUTING_CONFIG = {
    "code_generation": {
        "keywords": [
            "write code", "implement", "python", "rag", ...
        ],
        "priority_weight": 3  # HIGHEST priority
    },
    "web_search": {
        "keywords": [
            "book", "flight", "current", "weather", "price", ...
        ],
        "priority_weight": 2  # Medium priority
    },
    "text_generation": {
        "keywords": [
            "explain", "what is", "how does", ...
        ],
        "priority_weight": 1  # Lowest priority
    }
}
```

### 2. Keyword Matching Logic: `agent/core.py`

#### Method: `_select_tool_fallback()` (Lines 318-353)

**How it works:**

```python
# Step 1: Loop through each tool
for tool_name, config in ROUTING_CONFIG.items():
    
    # Step 2: Check each keyword for this tool
    for keyword in config["keywords"]:
        
        # Step 3: Score based on match type:
        
        # Exact phrase match (highest score)
        if " keyword " in " query ":
            score += 10 * priority_weight  # e.g., 10 * 3 = 30
        
        # Starts/ends with keyword
        elif query.startswith(keyword) or query.endswith(keyword):
            score += 8 * priority_weight   # e.g., 8 * 3 = 24
        
        # Contains keyword anywhere
        elif keyword in query:
            score += 5 * priority_weight   # e.g., 5 * 3 = 15

# Step 4: Pick tool with highest score
best_tool = tool with max(score)
```

---

## 🔄 Complete Routing Flow

```
User Query: "Write code for RAG"
           |
           v
    [1. LLM Analysis First]  <-- query_analyzer.py
           |
           |-- LLM analyzes intent
           |-- Returns: tool="code_generation", confidence=95%, reasoning="..."
           |
           v
    [2. Validate Tool Available]
           |
           v
    [3. Check Confidence Threshold]
           |
           |-- If confidence >= 70% --> Use LLM's recommendation ✅
           |
           |-- If confidence < 70% --> Check if needs real-time data
           |                            |
           |                            |-- Yes --> web_search
           |                            |-- No --> Use LLM's tool anyway
           v
    [4. If LLM Fails (Exception)]
           |
           v
    [5. FALLBACK: Keyword Matching]  <-- _select_tool_fallback()
           |
           |-- Score each tool by keyword matches
           |-- Multiply by priority_weight
           |-- Pick highest score
           v
    [Execute Selected Tool]
```

---

## 📝 Example: How Keywords Trigger Tools

### Query: "Write code for making advanced RAG"

**Keyword Matching Process:**

1. **Check code_generation keywords:**
   - "write code" ✅ (exact match) → score += 10 * 3 = 30
   - "rag" ✅ (contains) → score += 5 * 3 = 15
   - **Total: 45 points**

2. **Check web_search keywords:**
   - No matches
   - **Total: 0 points**

3. **Check text_generation keywords:**
   - No matches
   - **Total: 0 points**

**Winner: code_generation** (45 points)

---

## 🎯 Adding New Keywords

To make a keyword trigger a specific tool:

```python
# In config.py, add to the tool's keywords list:

"code_generation": {
    "keywords": [
        "write code",
        "YOUR NEW KEYWORD HERE",  # <-- Add here
        "python",
        ...
    ],
    "priority_weight": 3
}
```

---

## 🔑 Key Points

1. **Higher priority_weight = more influence**
   - code_generation: 3 (wins in ties)
   - web_search: 2
   - text_generation: 1

2. **Exact phrase matches score highest** (10 points × weight)
3. **LLM routing is used by default** (keyword fallback rarely triggered)
4. **Keyword system is backup only** (for when LLM API fails)

---

## Files to Modify

| What to Change | File | Lines |
|----------------|------|-------|
| Add/remove keywords | `config.py` | 32-88 |
| Change priority weights | `config.py` | 56, 75, 85 |
| Modify matching logic | `agent/core.py` | 318-353 |
| LLM routing prompt | `query_analyzer.py` | 30-65 |
