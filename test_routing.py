import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

# Test queries
tests = [
    ("Explain REST API", "text_generation"),
    ("Write Python code to reverse string", "code_generation"),
    ("Book train ticket Delhi to Mumbai", "web_search"),
    ("Latest AI news", "web_search"),
    ("Find cheapest flight to Paris", "web_search"),
]

print("Testing Intelligent Routing:")
print("=" * 70)

for i, (query, expected) in enumerate(tests, 1):
    payload = {
        "jsonrpc": "2.0",
        "method": "agent.chat",
        "params": {"message": query},
        "id": i
    }
    
    try:
        r = requests.post("http://localhost:5000/api", json=payload, timeout=30)
        result = r.json()["result"]["metadata"]
        tool = result["tool_used"]
        conf = result["confidence"]
        
        match = "✅" if tool == expected else "❌"
        print(f"\n{match} Query: {query}")
        print(f"   Tool: {tool} | Confidence: {conf}% | Expected: {expected}")
    except Exception as e:
        print(f"\n❌ Query: {query}")
        print(f"   Error: {e}")

print("\n" + "=" * 70)
