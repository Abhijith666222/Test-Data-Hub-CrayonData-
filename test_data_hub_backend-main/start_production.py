#!/usr/bin/env python3
"""
Production Startup Script for Test Data Environment Backend
Optimized for production deployment without development features
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

def check_production_config():
    """Check if production configuration is properly set up."""
    print("\n🔧 Checking production configuration...")
    
    # Check environment
    env = os.getenv('ENVIRONMENT', 'development')
    if env != 'production':
        print(f"⚠️  Warning: Environment is set to '{env}', not 'production'")
        print("💡 For production deployment, set ENVIRONMENT=production")
    
    # Check if OpenAI API key is set
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or openai_key == "your-openai-api-key-here":
        print("❌ OPENAI_API_KEY not configured")
        return False
    print("✅ OpenAI API key configured")
    
    # Check CORS configuration
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '')
    if not allowed_origins or allowed_origins == "http://localhost:3000,http://localhost:3001":
        print("⚠️  Warning: CORS origins not configured for production")
        print("💡 Set ALLOWED_ORIGINS to your frontend domain(s)")
    else:
        print(f"✅ CORS origins configured: {allowed_origins}")
    
    # Check if input directories exist
    required_dirs = ['input_schemas', 'business_logic_library']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ Required directory '{dir_name}' not found")
            return False
        print(f"✅ Directory '{dir_name}' exists")
    
    return True

def start_production_server():
    """Start the FastAPI server in production mode."""
    print("\n🚀 Starting production FastAPI server...")
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    env = os.getenv('ENVIRONMENT', 'development')
    
    # Set environment variables
    env_vars = os.environ.copy()
    env_vars['PYTHONPATH'] = os.getcwd()
    
    try:
        # Start the server in production mode (no reload)
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--host', host, 
            '--port', str(port), 
            '--log-level', 'info',
            '--workers', '1'  # Single worker for stability
        ], env=env_vars)
        
        print("✅ Production server started successfully!")
        print(f"📡 Server URL: http://{host}:{port}")
        print(f"📚 API Documentation: http://{host}:{port}/docs")
        print(f"🔌 WebSocket endpoint: ws://{host}:{port}/ws/logs")
        print(f"🌍 Environment: {env}")
        print("🔒 Production mode: Reload disabled, optimized for stability")
        
        # Wait for server to be ready
        print("\n⏳ Waiting for server to be ready...")
        time.sleep(5)
        
        # Test if server is responding
        try:
            response = requests.get(f'http://{host}:{port}/health', timeout=10)
            if response.status_code == 200:
                print("✅ Server is responding!")
                print("🚀 Production server is ready to handle requests")
            else:
                print("⚠️  Server started but health check failed")
        except requests.exceptions.RequestException:
            print("⚠️  Server started but health check failed (server might still be starting)")
        
        # Keep the script running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping production server...")
            process.terminate()
            process.wait()
            print("✅ Production server stopped")
            
    except Exception as e:
        print(f"❌ Failed to start production server: {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("🚀 Test Data Environment Backend - Production Startup")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check production configuration
    if not check_production_config():
        return False
    
    # Start production server
    return start_production_server()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Production startup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
