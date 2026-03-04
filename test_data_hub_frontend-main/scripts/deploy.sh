#!/bin/bash

# Test Data Frontend Deployment Script
# This script helps deploy the frontend to Render

set -e

echo "🚀 Starting deployment process..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Using default configuration."
    echo "   Please create a .env file based on env.example for production deployment."
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Run tests (if available)
if npm run test --if-present; then
    echo "✅ Tests passed"
else
    echo "⚠️  Tests failed or not available, continuing with deployment..."
fi

# Build the application
echo "🔨 Building application..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Error: Build failed - build directory not found"
    exit 1
fi

echo "✅ Build completed successfully!"

# Display build information
echo "📊 Build Information:"
echo "   - Build directory: $(du -sh build | cut -f1)"
echo "   - Build files: $(find build -type f | wc -l)"

# Check for environment variables
echo "🔧 Environment Configuration:"
if [ -f ".env" ]; then
    echo "   - .env file: ✅ Found"
    echo "   - API Base URL: ${REACT_APP_API_BASE_URL:-'Not set'}"
    echo "   - WebSocket URL: ${REACT_APP_WS_URL:-'Not set'}"
else
    echo "   - .env file: ❌ Not found (using defaults)"
fi

echo ""
echo "🎉 Deployment preparation completed!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your repository to Render"
echo "3. Set environment variables in Render dashboard"
echo "4. Deploy!"
echo ""
echo "For Render deployment:"
echo "- Use the render.yaml file for automatic setup"
echo "- Set REACT_APP_API_BASE_URL to your backend URL"
echo "- Set REACT_APP_WS_URL to your backend WebSocket URL"
