#!/usr/bin/env python3
"""
WebSocket Client for Test Data Environment Backend
Example client to test real-time logging functionality
"""

import asyncio
import websockets
import json
from datetime import datetime

async def websocket_client():
    """WebSocket client to receive real-time logs."""
    uri = "ws://localhost:8000/ws/logs"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🔌 Connected to WebSocket server")
            print("📡 Listening for real-time logs...")
            print("=" * 60)
            
            while True:
                try:
                    message = await websocket.recv()
                    log_data = json.loads(message)
                    
                    # Format the log message
                    timestamp = log_data.get('timestamp', '')
                    level = log_data.get('level', 'INFO')
                    message = log_data.get('message', '')
                    run_id = log_data.get('run_id', '')
                    step = log_data.get('step', '')
                    
                    # Color coding for different log levels
                    level_colors = {
                        'INFO': '\033[94m',    # Blue
                        'WARNING': '\033[93m', # Yellow
                        'ERROR': '\033[91m',   # Red
                        'SUCCESS': '\033[92m', # Green
                        'DEBUG': '\033[90m'    # Gray
                    }
                    
                    color = level_colors.get(level, '\033[0m')
                    reset = '\033[0m'
                    
                    # Print formatted log
                    print(f"{color}[{timestamp}] {level}{reset}")
                    if run_id:
                        print(f"  Run ID: {run_id}")
                    if step:
                        print(f"  Step: {step}")
                    print(f"  {message}")
                    print("-" * 60)
                    
                except websockets.exceptions.ConnectionClosed:
                    print("❌ WebSocket connection closed")
                    break
                except json.JSONDecodeError:
                    print(f"⚠️  Received non-JSON message: {message}")
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    
    except websockets.exceptions.ConnectionRefused:
        print("❌ Could not connect to WebSocket server. Make sure the FastAPI server is running.")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

def main():
    """Main function to run the WebSocket client."""
    print("🚀 Test Data Environment WebSocket Client")
    print("=" * 60)
    print("This client will connect to the FastAPI backend and display")
    print("real-time logs as they are generated during data processing.")
    print("=" * 60)
    
    try:
        asyncio.run(websocket_client())
    except KeyboardInterrupt:
        print("\n👋 WebSocket client stopped by user")
    except Exception as e:
        print(f"❌ Error running WebSocket client: {e}")

if __name__ == "__main__":
    main() 