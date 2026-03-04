@echo off
REM Test Data Frontend Deployment Script for Windows
REM This script helps deploy the frontend to Render

echo 🚀 Starting deployment process...

REM Check if we're in the right directory
if not exist "package.json" (
    echo ❌ Error: package.json not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Using default configuration.
    echo    Please create a .env file based on env.example for production deployment.
)

REM Install dependencies
echo 📦 Installing dependencies...
call npm install

REM Run tests (if available)
echo 🧪 Running tests...
call npm run test --if-present
if %errorlevel% equ 0 (
    echo ✅ Tests passed
) else (
    echo ⚠️  Tests failed or not available, continuing with deployment...
)

REM Build the application
echo 🔨 Building application...
call npm run build

REM Check if build was successful
if not exist "build" (
    echo ❌ Error: Build failed - build directory not found
    pause
    exit /b 1
)

echo ✅ Build completed successfully!

REM Display build information
echo 📊 Build Information:
for /f "tokens=1" %%i in ('dir /s /-c build ^| find "File(s)"') do set BUILD_SIZE=%%i
echo    - Build directory: %BUILD_SIZE% bytes
for /f "tokens=1" %%i in ('dir /s /b build\*.* ^| find /c /v ""') do set BUILD_FILES=%%i
echo    - Build files: %BUILD_FILES%

REM Check for environment variables
echo 🔧 Environment Configuration:
if exist ".env" (
    echo    - .env file: ✅ Found
    for /f "tokens=2 delims==" %%a in ('findstr "REACT_APP_API_BASE_URL" .env') do set API_URL=%%a
    for /f "tokens=2 delims==" %%a in ('findstr "REACT_APP_WS_URL" .env') do set WS_URL=%%a
    echo    - API Base URL: %API_URL%
    echo    - WebSocket URL: %WS_URL%
) else (
    echo    - .env file: ❌ Not found (using defaults)
)

echo.
echo 🎉 Deployment preparation completed!
echo.
echo Next steps:
echo 1. Push your code to GitHub
echo 2. Connect your repository to Render
echo 3. Set environment variables in Render dashboard
echo 4. Deploy!
echo.
echo For Render deployment:
echo - Use the render.yaml file for automatic setup
echo - Set REACT_APP_API_BASE_URL to your backend URL
echo - Set REACT_APP_WS_URL to your backend WebSocket URL
echo.
pause
