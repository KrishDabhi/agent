import json
import os
from datetime import datetime
from threading import Lock
from typing import Dict, Any, Optional


class CommunicationMonitor:
    """Monitor and log all JSON-RPC communications"""
    
    def __init__(self, log_file: str = "logs/communications.jsonl"):
        self.log_file = log_file
        self.lock = Lock()
        self.request_counter = 0
        
        # Create logs directory
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Enable colored output
        self.colors = {
            'RESET': '\033[0m',
            'BOLD': '\033[1m',
            'RED': '\033[91m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'BLUE': '\033[94m',
            'MAGENTA': '\033[95m',
            'CYAN': '\033[96m',
            'WHITE': '\033[97m',
        }
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color to text"""
        return f"{self.colors.get(color, '')}{text}{self.colors['RESET']}"
    
    def _format_json(self, data: Dict[str, Any]) -> str:
        """Format JSON with indentation"""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def log_request(self, 
                    source: str, 
                    destination: str, 
                    request_data: Dict[str, Any],
                    layer: str = "USER"):
        """
        Log a JSON-RPC request
        
        Args:
            source: Where the request came from (e.g., "Client", "Agent")
            destination: Where it's going (e.g., "Agent", "MCP Server")
            request_data: The JSON-RPC request
            layer: Communication layer ("USER" or "MCP")
        """
        with self.lock:
            self.request_counter += 1
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Prepare log entry
            log_entry = {
                "type": "REQUEST",
                "timestamp": timestamp,
                "counter": self.request_counter,
                "layer": layer,
                "source": source,
                "destination": destination,
                "data": request_data
            }
            
            # Write to file (JSONL format - one JSON per line)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            # Print to console
            self._print_request(log_entry)
    
    def log_response(self,
                     source: str,
                     destination: str,
                     response_data: Dict[str, Any],
                     layer: str = "USER"):
        """
        Log a JSON-RPC response
        
        Args:
            source: Where the response came from
            destination: Where it's going
            response_data: The JSON-RPC response
            layer: Communication layer
        """
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Prepare log entry
            log_entry = {
                "type": "RESPONSE",
                "timestamp": timestamp,
                "counter": self.request_counter,
                "layer": layer,
                "source": source,
                "destination": destination,
                "data": response_data
            }
            
            # Write to file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            # Print to console
            self._print_response(log_entry)
    
    def _print_request(self, log_entry: Dict[str, Any]):
        """Print formatted request to console"""
        print("\n" + "=" * 80)
        
        # Header
        layer_color = 'CYAN' if log_entry['layer'] == 'USER' else 'MAGENTA'
        print(self._colorize(f"📤 REQUEST #{log_entry['counter']} [{log_entry['layer']} Layer]", 'BOLD'))
        print(self._colorize(f"   Time: {log_entry['timestamp']}", 'WHITE'))
        print(self._colorize(f"   Flow: {log_entry['source']} → {log_entry['destination']}", layer_color))
        
        # Request details
        request = log_entry['data']
        print(self._colorize(f"   Method: {request.get('method', 'N/A')}", 'YELLOW'))
        print(self._colorize(f"   ID: {request.get('id', 'N/A')}", 'WHITE'))
        
        # Params
        params = request.get('params', {})
        if params:
            print(self._colorize("   Params:", 'WHITE'))
            for key, value in params.items():
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:97] + "..."
                print(f"     {key}: {value_str}")
        
        print("=" * 80)
    
    def _print_response(self, log_entry: Dict[str, Any]):
        """Print formatted response to console"""
        print("\n" + "-" * 80)
        
        # Header
        layer_color = 'CYAN' if log_entry['layer'] == 'USER' else 'MAGENTA'
        
        response = log_entry['data']
        has_error = 'error' in response
        status_icon = "❌" if has_error else "✅"
        status_color = 'RED' if has_error else 'GREEN'
        
        print(self._colorize(f"{status_icon} RESPONSE #{log_entry['counter']} [{log_entry['layer']} Layer]", 'BOLD'))
        print(self._colorize(f"   Time: {log_entry['timestamp']}", 'WHITE'))
        print(self._colorize(f"   Flow: {log_entry['source']} → {log_entry['destination']}", layer_color))
        print(self._colorize(f"   ID: {response.get('id', 'N/A')}", 'WHITE'))
        
        # Result or Error
        if has_error:
            error = response['error']
            print(self._colorize(f"   Error Code: {error.get('code', 'N/A')}", 'RED'))
            print(self._colorize(f"   Error Message: {error.get('message', 'N/A')}", 'RED'))
        else:
            result = response.get('result', {})
            if isinstance(result, dict):
                # Show metadata if available
                if 'metadata' in result:
                    meta = result['metadata']
                    print(self._colorize("   Metadata:", 'WHITE'))
                    for key, value in meta.items():
                        print(f"     {key}: {value}")
                
                # Show response size
                response_text = result.get('response', '')
                if response_text:
                    print(self._colorize(f"   Response Length: {len(response_text)} chars", 'WHITE'))
            else:
                # Show result preview
                result_str = str(result)
                if len(result_str) > 150:
                    result_str = result_str[:147] + "..."
                print(self._colorize(f"   Result: {result_str}", 'GREEN'))
        
        print("-" * 80)


# Global monitor instance
_monitor = None
_enabled = False

def get_monitor() -> Optional[CommunicationMonitor]:
    """Get global monitor instance"""
    global _monitor
    if _monitor is None and _enabled:
        _monitor = CommunicationMonitor()
    return _monitor

def enable_monitoring():
    """Enable communication monitoring"""
    global _enabled
    _enabled = True

def disable_monitoring():
    """Disable communication monitoring"""
    global _enabled
    _enabled = False

def is_monitoring_enabled() -> bool:
    """Check if monitoring is enabled"""
    return _enabled