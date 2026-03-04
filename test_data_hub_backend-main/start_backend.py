#!/usr/bin/env python3
"""
Startup Script for Test Data Environment Backend
Easy way to start the FastAPI server with proper configuration
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'websockets',
        'pydantic',
        'requests',
        'pandas',
        'openai',
        'faker',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_config():
    """Check if configuration is properly set up."""
    print("\n🔧 Checking configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("💡 Please copy .env.example to .env and configure your settings")
        return False
    
    # Check if OpenAI API key is set
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or openai_key == "your-openai-api-key-here":
        print("❌ OPENAI_API_KEY not configured in .env file")
        return False
    print("✅ OpenAI API key configured")
    
    # Check if input directories exist
    required_dirs = ['input_schemas', 'business_logic_library']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ Required directory '{dir_name}' not found")
            return False
        print(f"✅ Directory '{dir_name}' exists")
    
    # Check environment
    env = os.getenv('ENVIRONMENT', 'development')
    print(f"✅ Environment: {env}")
    
    # Check CORS configuration
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:3001')
    print(f"✅ CORS origins: {allowed_origins}")
    
    return True

def start_server():
    """Start the FastAPI server."""
    print("\n🚀 Starting FastAPI server...")
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    env = os.getenv('ENVIRONMENT', 'development')
    
    # Set environment variables
    env_vars = os.environ.copy()
    env_vars['PYTHONPATH'] = os.getcwd()
    
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--host', host, 
            '--port', str(port), 
            '--reload', str(env == 'development').lower(),
            '--log-level', 'info'
        ], env=env_vars)
        
        print("✅ Server started successfully!")
        print(f"📡 Server URL: http://{host}:{port}")
        print(f"📚 API Documentation: http://{host}:{port}/docs")
        print(f"🔌 WebSocket endpoint: ws://{host}:{port}/ws/logs")
        print(f"🌍 Environment: {env}")
        print("\n💡 Tips:")
        print("   - Press Ctrl+C to stop the server")
        print("   - Run 'python websocket_client.py' in another terminal to see real-time logs")
        print("   - Run 'python api_client.py' to test the API endpoints")
        
        # Wait for server to be ready
        print("\n⏳ Waiting for server to be ready...")
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get(f'http://{host}:{port}/health', timeout=5)
            if response.status_code == 200:
                print("✅ Server is responding!")
            else:
                print("⚠️  Server started but health check failed")
        except requests.exceptions.RequestException:
            print("⚠️  Server started but health check failed (server might still be starting)")
        
        # Keep the script running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
            process.wait()
            print("✅ Server stopped")
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("🚀 Test Data Environment Backend Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check configuration
    if not check_config():
        return False
    
    # Start server
    return start_server()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 