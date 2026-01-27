import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import time

# Worst case test scenarios
test_cases = [
    # Ambiguous queries
    ("book", "Should detect booking intent → web_search"),
    ("code", "Vague, could be code_generation but unclear"),
    ("python", "Just a word, no clear intent"),
    
    # Mixed intents
    ("explain how to book a flight and write code for it", "Mixed: explain + book + code"),
    ("find latest python tutorial", "Mixed: find + latest + tutorial"),
    
    # Misspellings
    ("bok flite from mumbai to delli", "Misspelled booking query"),
    ("explin REST API", "Misspelled explain"),
    
    # No keywords
    ("hi", "Greeting, no clear tool"),
    ("thanks", "Gratitude, no clear tool"),
    ("help me", "Generic help request"),
    
    # Complex real queries
    ("I need to travel from Oakland to Sharjah tomorrow, what are my options and prices", "Clear travel query"),
    ("Show me how to implement a REST API in Python with authentication", "Mixed: show + implement + code"),
    ("What happened in tech news yesterday", "Clear news query"),
    
    # Edge cases
    ("", "Empty query"),
    ("a", "Single character"),
    ("1234567890", "Just numbers"),
]

print("🧪 WORST CASE SCENARIO TESTING")
print("=" * 80)

results = {
    "passed": 0,
    "failed": 0,
    "errors": 0
}

for query, description in test_cases:
    if not query:  # Skip empty
        continue
        
    print(f"\n📝 Query: '{query}'")
    print(f"   Description: {description}")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "agent.chat",
        "params": {"message": query},
        "id": 1
    }
    
    try:
        r = requests.post("http://localhost:5000/api", json=payload, timeout=30)
        result = r.json()
        
        if "result" in result:
            metadata = result["result"]["metadata"]
            tool = metadata.get("tool_used", "unknown")
            conf = metadata.get("confidence", 0)
            response = result["result"]["response"][:100]
            
            print(f"   ✓ Tool: {tool} | Confidence: {conf}%")
            print(f"   Response: {response}...")
            results["passed"] += 1
        else:
            print(f"   ✗ Error in response: {result.get('error')}")
            results["failed"] += 1
            
    except Exception as e:
        print(f"   ✗ Exception: {str(e)[:100]}")
        results["errors"] += 1
    
    time.sleep(0.5)  # Rate limit

print("\n" + "=" * 80)
print("📊 RESULTS:")
print(f"   ✅ Passed: {results['passed']}")
print(f"   ❌ Failed: {results['failed']}")
print(f"   ⚠️  Errors: {results['errors']}")
print("=" * 80)
