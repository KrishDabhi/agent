"""
Chat Logger - Logs all conversations in JSON format with metrics
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import threading


class ChatLogger:
    """Thread-safe chat logger that saves conversations to JSON files"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.lock = threading.Lock()
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Current session log file
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"chat_{self.session_id}.json")
        
        # Initialize log file
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Initialize the log file with session metadata"""
        initial_data = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "conversations": []
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def log_conversation(self, 
                        user_message: str,
                        agent_response: str,
                        metadata: Dict[str, Any]):
        """
        Log a conversation with metadata
        
        Args:
            user_message: User's input message
            agent_response: Agent's response
            metadata: Additional metadata (tool_used, confidence, timings, etc.)
        """
        with self.lock:
            # Read current log
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            # Create conversation entry
            conversation = {
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "agent_response": agent_response,
                "metadata": metadata
            }
            
            # Add to conversations
            log_data["conversations"].append(conversation)
            
            # Write back
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current session"""
        with self.lock:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            conversations = log_data.get("conversations", [])
            
            if not conversations:
                return {
                    "total_conversations": 0,
                    "average_response_time": 0,
                    "tools_usage": {}
                }
            
            # Calculate stats
            total_time = sum(c["metadata"].get("total_time", 0) for c in conversations)
            avg_time = total_time / len(conversations) if conversations else 0
            
            # Tool usage count
            tools_usage = {}
            for c in conversations:
                tool = c["metadata"].get("tool_used")
                if tool:
                    tools_usage[tool] = tools_usage.get(tool, 0) + 1
            
            return {
                "total_conversations": len(conversations),
                "average_response_time": round(avg_time, 3),
                "total_response_time": round(total_time, 3),
                "tools_usage": tools_usage
            }
    
    def get_all_logs(self) -> List[str]:
        """Get list of all log files"""
        log_files = [f for f in os.listdir(self.log_dir) if f.startswith("chat_") and f.endswith(".json")]
        return sorted(log_files, reverse=True)
    
    def load_log_file(self, filename: str) -> Dict[str, Any]:
        """Load a specific log file"""
        filepath = os.path.join(self.log_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)


# Global logger instance
_logger = None

def get_logger() -> ChatLogger:
    """Get or create global logger instance"""
    global _logger
    if _logger is None:
        _logger = ChatLogger()
    return _logger
