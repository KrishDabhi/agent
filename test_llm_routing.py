import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests, json

# Test previously failing queries
tests = [
    ("Explain REST API", "text_generation"),  # Previously FAILED
    ("What is machine learning", "text_generation"),  # Previously FAILED
    ("Write code for making advanced RAG", "code_generation"),  # Should still work
    ("Book flight to Paris", "web_search"),  # Should still work
    ("Difference between RAM and ROM", "text_generation"),  # Previously FAILED
]

print("🧪 TESTING LLM-BASED ROUTING")
print("=" * 70)

passed = 0
failed = 0

for query, expected in tests:
    payload = {
        "jsonrpc": "2.0",
        "method": "agent.chat",
        "params": {"message": query},
        "id": 1
    }
    
    try:
        r = requests.post('http://localhost:5000/api', json=payload, timeout=30)
        result = r.json()['result']['metadata']
        tool = result['tool_used']
        conf = result['confidence']
        
        if tool == expected:
            print(f"✅ {query:45} → {tool:18} ({conf}%)")
            passed += 1
        else:
            print(f"❌ {query:45} → {tool:18} ({conf}%) [Expected: {expected}]")
            failed += 1
    except Exception as e:
        print(f"⚠️  {query:45} → ERROR: {str(e)[:40]}")
        failed += 1

print("=" * 70)
print(f"\n📊 Results: {passed}/{len(tests)} passed ({passed/len(tests)*100:.1f}% accuracy)")
if failed == 0:
    print("🎉 PERFECT SCORE! All queries routed correctly!")
else:
    print(f"⚠️  {failed} queries still failing")
print("=" * 70)
