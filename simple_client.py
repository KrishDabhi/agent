"""
Enhanced Interactive Client with Status Updates
"""
import sys
import io

# Fix Windows encoding issue for colored output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
REQUEST_ID = 1

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            return True
    except:
        return False
    return False

def query_agent(message):
    """Send a query to the agent and display status updates"""
    global REQUEST_ID
    
    payload = {
        "jsonrpc": "2.0",
        "method": "agent.chat",
        "params": {"message": message},
        "id": REQUEST_ID
    }
    REQUEST_ID += 1
    
    print("\n" + "🔵" * 40)
    print("📤 SENDING JSON-RPC REQUEST TO AGENT:")
    print(json.dumps(payload, indent=2))
    print("🔵" * 40)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "🟢" * 40)
            print("📥 RECEIVED JSON-RPC RESPONSE FROM AGENT:")
            print(json.dumps(result, indent=2))
            print("🟢" * 40 + "\n")
            
            if "result" in result:
                data = result["result"]
                
                # Display status updates
                if "status_updates" in data and data["status_updates"]:
                    print("\n📊 Processing Steps:")
                    for update in data["status_updates"]:
                        print(f"  {update['status']}")
                
                # Display metadata
                if "metadata" in data and data["metadata"]:
                    meta = data["metadata"]
                    print(f"\n📈 Metrics:")
                    if "tool_used" in meta:
                        print(f"  🔧 Tool: {meta['tool_used']}")
                    if "confidence" in meta:
                        print(f"  🎯 Confidence: {meta['confidence']}%")
                    if "total_time" in meta:
                        print(f"  ⏱️  Total Time: {meta['total_time']:.2f}s")
                    if "search_time" in meta:
                        print(f"  🔍 Search Time: {meta['search_time']:.2f}s")
                    if "tool_time" in meta:
                        print(f"  ⚙️  Tool Time: {meta['tool_time']:.2f}s")
                
                return data.get("response", "")
            elif "error" in result:
                return f"Error: {result['error']['message']}"
        else:
            return f"HTTP Error: {response.status_code}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out"
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to server"
    except Exception as e:
        return f"Error: {str(e)}"

def list_capabilities():
    """List available agent capabilities"""
    payload = {
        "jsonrpc": "2.0",
        "method": "agent.list_capabilities",
        "params": {},
        "id": 999
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return result["result"]["capabilities"]
    except:
        pass
    return []

def get_session_stats():
    """Get current session statistics"""
    try:
        response = requests.get(f"{BASE_URL}/logs/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def print_capabilities():
    """Print available capabilities"""
    print("\n📋 Available Capabilities:")
    print("=" * 60)
    caps = list_capabilities()
    if caps:
        for cap in caps:
            print(f"  • {cap['name']}: {cap['description']}")
    else:
        print("  Could not fetch capabilities")
    print("=" * 60)

def print_stats():
    """Print session statistics"""
    stats = get_session_stats()
    if stats:
        print("\n📊 Session Statistics:")
        print("=" * 60)
        print(f"  Total Conversations: {stats.get('total_conversations', 0)}")
        print(f"  Average Response Time: {stats.get('average_response_time', 0):.2f}s")
        print(f"  Total Response Time: {stats.get('total_response_time', 0):.2f}s")
        
        tools_usage = stats.get('tools_usage', {})
        if tools_usage:
            print(f"\n  Tools Usage:")
            for tool, count in tools_usage.items():
                print(f"    - {tool}: {count} times")
        print("=" * 60)
    else:
        print("\n⚠️  Could not fetch statistics")

def main():
    print("\n" + "=" * 60)
    print("🤖 Intelligent Agent - Interactive Client with Status Updates")
    print("=" * 60)
    
    # Check server
    print("\n🔍 Checking server status...")
    if not check_server():
        print("❌ Error: Agent server is not running!")
        print("\n💡 Start the server first:")
        print("   python app.py")
        sys.exit(1)
    
    print("✅ Server is running!")
    
    # Show capabilities
    print_capabilities()
    
    print("\n💬 Chat Mode:")
    print("  Commands:")
    print("    /help  - Show help")
    print("    /caps  - Show capabilities")
    print("    /stats - Show session statistics")
    print("    quit   - Exit")
    print("=" * 60)
    
    while True:
        try:
            # Get user input
            query = input("\n👤 You: ").strip()
            
            if not query:
                continue
            
            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                print_stats()
                break
            
            if query.lower() in ['/help', 'help', '?']:
                print("\n📖 Help:")
                print("  • Just type your question naturally")
                print("  • /caps  - Show available capabilities")
                print("  • /stats - Show session statistics")
                print("  • /help  - Show this help")
                print("  • quit   - Exit the client")
                print("\n💡 Examples:")
                print("  • Explain how JSON-RPC works")
                print("  • What are the latest news about AI?")
                print("  • Write code to reverse a string in Python")
                continue
            
            if query.lower() == '/caps':
                print_capabilities()
                continue
            
            if query.lower() == '/stats':
                print_stats()
                continue
            
            # Send query to agent
            print()  # Empty line for spacing
            response = query_agent(query)
            print(f"\n🤖 Agent:\n{response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            print_stats()
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
