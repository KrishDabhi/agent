from flask import Flask, request
from jsonrpc import JsonRpcHandler

def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> str:
    return f"Hello, {name}!"

def get_time() -> str:
    from datetime import datetime
    return datetime.now().isoformat()

rpc = JsonRpcHandler()
rpc.register("math.add", add)
rpc.register("user.greet", greet)
rpc.register("system.time", get_time)

app = Flask(__name__)

@app.route("/api", methods=["POST"])
def jsonrpc_endpoint():
    response = rpc.handle(request.data.decode())
    
    if response is None:
        return "", 204    
    
    return response, 200, {"Content-Type": "application/json"}

if __name__ == "__main__":
    print("JSON-RPC server running on http://localhost:5000/api")
    app.run(host="0.0.0.0", port=5000, debug=True)