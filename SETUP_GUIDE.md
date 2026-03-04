# 🚀 Local Setup Guide

This guide will help you download and launch the Test Data Hub application locally on your machine.

## 📋 Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.8+** (check with `python --version`)
- **Node.js 16+** and npm (check with `node --version` and `npm --version`)
- **OpenAI API Key** (required for AI features)
- **Git** (if downloading from a repository)

## 📥 Step 1: Download the Project

You already have the project files in:
- `C:\Users\User\Desktop\Codingyay\Crayon Data\Test-Data-Hub`

If you need to download it fresh:
```bash
# If using Git
git clone <repository-url>
cd Test-Data-Hub
```

## 🔧 Step 2: Backend Setup

### 2.1 Navigate to Backend Directory
```bash
cd test_data_hub_backend-main
```

### 2.2 Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 2.3 Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2.4 Create Environment Configuration File

Create a `.env` file in the `test_data_hub_backend-main` directory:

```bash
# Windows PowerShell
cd test_data_hub_backend-main
New-Item -Path .env -ItemType File
```

Then add the following content to `.env`:

```env
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your-actual-openai-api-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Database Configuration (Optional - only if using MySQL/Oracle)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=test_data_environment
MYSQL_USERNAME=root
MYSQL_PASSWORD=your-password

ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=XEPDB1
ORACLE_USERNAME=system
ORACLE_PASSWORD=your-password
```

**⚠️ Important**: Replace `your-actual-openai-api-key-here` with your actual OpenAI API key.

### 2.5 Start the Backend Server

You have two options:

**Option A: Using the startup script (Recommended)**
```bash
python start_backend.py
```

**Option B: Direct command**
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will start on **http://localhost:8000**

You should see:
- ✅ API Documentation: http://localhost:8000/docs
- ✅ WebSocket endpoint: ws://localhost:8000/ws/logs
- ✅ Health check: http://localhost:8000/health

**Keep this terminal window open!** The backend needs to stay running.

## 🎨 Step 3: Frontend Setup

### 3.1 Open a New Terminal Window

**Important**: Keep the backend server running in the first terminal, and open a new terminal for the frontend.

### 3.2 Navigate to Frontend Directory
```bash
cd test_data_hub_frontend-main
```

### 3.3 Install Node Dependencies

The `node_modules` folder already exists, but to ensure everything is up to date:
```bash
npm install
```

This may take a few minutes the first time.

### 3.4 Create Frontend Environment File (Optional)

Create a `.env` file in the `test_data_hub_frontend-main` directory:

```bash
# Windows PowerShell
cd test_data_hub_frontend-main
New-Item -Path .env -ItemType File
```

Add the following content:
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_APP_ENVIRONMENT=development
```

**Note**: If you don't create this file, the frontend will use the default values (localhost:8000).

### 3.5 Start the Frontend Development Server
```bash
npm start
```

The frontend will start on **http://localhost:3000** and should automatically open in your browser.

## ✅ Step 4: Verify Installation

1. **Backend is running**: Visit http://localhost:8000/docs - you should see the API documentation
2. **Frontend is running**: Visit http://localhost:3000 - you should see the application interface
3. **Connection**: The frontend should be able to communicate with the backend

## 🎯 Quick Launch Commands Summary

### Terminal 1 (Backend):
```bash
cd test_data_hub_backend-main
# Activate venv if using: venv\Scripts\activate
python start_backend.py
```

### Terminal 2 (Frontend):
```bash
cd test_data_hub_frontend-main
npm start
```

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError` or missing packages
```bash
# Solution: Reinstall dependencies
cd test_data_hub_backend-main
pip install -r requirements.txt
```

**Problem**: `OPENAI_API_KEY` error
```bash
# Solution: Make sure .env file exists and has your API key
# Check that .env is in test_data_hub_backend-main directory
```

**Problem**: Port 8000 already in use
```bash
# Solution 1: Change port in .env file
PORT=8001

# Solution 2: Find and stop the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Frontend Issues

**Problem**: `npm install` fails
```bash
# Solution: Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Frontend can't connect to backend
```bash
# Solution: 
# 1. Make sure backend is running
# 2. Check .env file has correct API URL
# 3. Check CORS settings in backend .env file
```

**Problem**: Port 3000 already in use
```bash
# Solution: The app will prompt you to use a different port (e.g., 3001)
# Accept the prompt, or set PORT in .env:
PORT=3001
```

## 📚 Next Steps

Once both servers are running:

1. **Explore the API**: Visit http://localhost:8000/docs to see all available endpoints
2. **Use the Frontend**: Navigate to http://localhost:3000 to start using the application
3. **Read the Documentation**: Check the README files in both backend and frontend folders

## 🔒 Security Notes

- **Never commit `.env` files** to version control
- Keep your OpenAI API key secure
- In production, use environment variables set in your deployment platform

## 📞 Need Help?

- Check the README.md files in both backend and frontend directories
- Review the DEPLOYMENT.md files for deployment-specific information
- Check console/terminal logs for error messages

---

**You're all set! 🎉 Happy coding!**

