import requests
import json

BASE_URL = "http://localhost:5000"

def make_jsonrpc_request(endpoint, method, params, request_id=1):
    """Make a JSON-RPC 2.0 request"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }
    
    print(f"\n{'='*60}")
    print(f"📤 Sending JSON-RPC Request to {endpoint}")
    print(f"   Method: {method}")
    print(f"   Params: {json.dumps(params, indent=2)}")
    print(f"{'='*60}")
    
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    print(f"\n📥 Received Response:")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"   Error: {response.text}")
        return None

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_list_tools():
    """Test listing available tools"""
    print("\n" + "="*60)
    print("TEST 2: List Available Tools (via HTTP)")
    print("="*60)
    response = requests.get(f"{BASE_URL}/tools")
    print(f"Status: {response.status_code}")
    tools = response.json()
    print(f"Found {len(tools.get('tools', []))} tools:")
    for tool in tools.get('tools', []):
        print(f"  - {tool['name']}: {tool['description']}")

def test_agent_capabilities():
    """Test agent capability discovery via JSON-RPC"""
    print("\n" + "="*60)
    print("TEST 3: Agent Capability Discovery (via JSON-RPC)")
    print("="*60)
    result = make_jsonrpc_request(
        "/api",
        "agent.list_capabilities",
        {}
    )
    
    if result and "result" in result:
        caps = result["result"]["capabilities"]
        print(f"\n✅ Agent has {len(caps)} capabilities:")
        for cap in caps:
            print(f"  - {cap['name']}: {cap['description']}")

def test_chat_basic():
    """Test basic chat request"""
    print("\n" + "="*60)
    print("TEST 4: Basic Chat (Text Generation)")
    print("="*60)
    result = make_jsonrpc_request(
        "/api",
        "agent.chat",
        {"message": "Explain what is JSON-RPC in simple terms"}
    )
    
    if result and "result" in result:
        print(f"\n✅ Agent Response:")
        print(f"{result['result']['response']}")

def test_chat_web_search():
    """Test web search request"""
    print("\n" + "="*60)
    print("TEST 5: Web Search Query")
    print("="*60)
    result = make_jsonrpc_request(
        "/api",
        "agent.chat",
        {"message": "What are the latest news about Python programming?"}
    )
    
    if result and "result" in result:
        print(f"\n✅ Agent Response:")
        print(f"{result['result']['response']}")

def test_chat_code_generation():
    """Test code generation request"""
    print("\n" + "="*60)
    print("TEST 6: Code Generation")
    print("="*60)
    result = make_jsonrpc_request(
        "/api",
        "agent.chat",
        {"message": "Write code for a Python function that calculates factorial"}
    )
    
    if result and "result" in result:
        print(f"\n✅ Agent Response:")
        print(f"{result['result']['response']}")

def test_direct_tool_execution():
    """Test direct tool execution"""
    print("\n" + "="*60)
    print("TEST 7: Direct Tool Execution via MCP")
    print("="*60)
    result = make_jsonrpc_request(
        "/mcp",
        "web_search",
        {"query": "Python 3.14 new features"}
    )
    
    if result and "result" in result:
        print(f"\n✅ Search Results:")
        print(f"{result['result']}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Intelligent Agent System Test Suite")
    print("="*60)
    print("Make sure the agent server is running on http://localhost:5000")
    input("Press Enter to start tests...")
    
    try:
        test_health_check()
        test_list_tools()
        test_agent_capabilities()
        test_chat_basic()
        test_chat_web_search()
        test_chat_code_generation()
        test_direct_tool_execution()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server.")
        print("   Make sure the agent is running: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
