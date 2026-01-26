"""
JSON-RPC Communication Monitor - Viewer
Run this in a separate terminal to see all communications in real-time
"""
import os
import sys
import time
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print monitor header"""
    print("=" * 80)
    print("🔍 JSON-RPC COMMUNICATION MONITOR")
    print("=" * 80)
    print("Monitoring all JSON-RPC requests and responses...")
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()

def tail_file(filename, interval=0.1):
    """
    Tail a file and yield new lines as they're added
    Similar to 'tail -f' command
    """
    # Wait for file to exist
    while not os.path.exists(filename):
        print(f"Waiting for log file: {filename}")
        time.sleep(1)
    
    with open(filename, 'r', encoding='utf-8') as f:
        # Go to end of file
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                time.sleep(interval)

def main():
    """Main monitor loop"""
    log_file = "logs/communications.jsonl"
    
    clear_screen()
    print_header()
    
    print(f"📁 Log file: {log_file}")
    print()
    
    try:
        # Read existing logs first
        if os.path.exists(log_file):
            print("📜 Reading existing logs...")
            print()
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            import json
                            entry = json.loads(line)
                            # The monitor.py already formats output
                            # Here we just confirm we can read it
                        except:
                            pass
        
        # Now tail for new entries
        print("👀 Watching for new communications... (Live monitoring active)")
        print()
        
        for line in tail_file(log_file):
            # Lines are already formatted by monitor.py
            # This script just keeps the terminal open and tailing
            pass
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("✋ Monitoring stopped by user")
        print("=" * 80)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Enable monitoring when this script runs
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from monitor import enable_monitoring
    enable_monitoring()
    
    main()
