# 🔒 Backend CORS Configuration

This document provides the CORS configuration needed for the backend to properly communicate with the frontend.

## 🌐 Frontend Domains

The frontend will be accessible from these domains:

### Development
- `http://localhost:3000` - Local development server

### Production (Render)
- `https://your-app-name.onrender.com` - Render deployment URL
- `https://your-custom-domain.com` - Custom domain (if configured)

## 🔧 CORS Configuration

### FastAPI (Python)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://your-app-name.onrender.com",  # Render production
        "https://your-custom-domain.com",  # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Alternative: Load from environment variables
import os
from typing import List

def get_allowed_origins() -> List[str]:
    origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
    origins = [origin.strip() for origin in origins if origin.strip()]
    
    # Add default development origin if none specified
    if not origins:
        origins = ["http://localhost:3000"]
    
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Express.js (Node.js)

```javascript
const express = require('express');
const cors = require('cors');

const app = express();

// CORS configuration
const corsOptions = {
  origin: [
    'http://localhost:3000',  // Development
    'https://your-app-name.onrender.com',  // Render production
    'https://your-custom-domain.com',  // Custom domain
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
};

app.use(cors(corsOptions));

// Alternative: Load from environment variables
const getAllowedOrigins = () => {
  const origins = process.env.ALLOWED_ORIGINS?.split(',') || [];
  const cleanOrigins = origins.map(origin => origin.trim()).filter(Boolean);
  
  // Add default development origin if none specified
  if (cleanOrigins.length === 0) {
    cleanOrigins.push('http://localhost:3000');
  }
  
  return cleanOrigins;
};

app.use(cors({
  origin: getAllowedOrigins(),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
}));
```

### Django (Python)

```python
# settings.py

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Development
    "https://your-app-name.onrender.com",  # Render production
    "https://your-custom-domain.com",  # Custom domain
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Set to True only for development

# Alternative: Load from environment variables
import os

CORS_ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000"
).split(",")

CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS]
```

## 🔐 Environment Variables

Set these environment variables in your backend:

```env
# Development
ALLOWED_ORIGINS=http://localhost:3000

# Production
ALLOWED_ORIGINS=https://your-app-name.onrender.com,https://your-custom-domain.com

# Multiple domains (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://staging.example.com,https://example.com
```

## 🚀 WebSocket CORS (if applicable)

If your backend uses WebSockets, ensure CORS is also configured for WebSocket connections:

### FastAPI WebSocket

```python
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Your WebSocket logic here
```

### Node.js WebSocket

```javascript
const WebSocket = require('ws');

const wss = new WebSocket.Server({ 
  port: 8080,
  verifyClient: (info) => {
    const origin = info.origin;
    const allowedOrigins = getAllowedOrigins();
    return allowedOrigins.includes(origin);
  }
});
```

## 🧪 Testing CORS

### Test with curl

```bash
# Test preflight request
curl -X OPTIONS \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v \
  http://localhost:8000/your-endpoint

# Test actual request
curl -X POST \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' \
  -v \
  http://localhost:8000/your-endpoint
```

### Test in browser console

```javascript
// Test API endpoint
fetch('http://localhost:8000/your-endpoint', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ test: 'data' })
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));

// Test WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/logs');
ws.onopen = () => console.log('WebSocket connected');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

## ⚠️ Security Considerations

1. **Never use `allow_origins=["*"]` in production**
2. **Always validate the Origin header**
3. **Use HTTPS in production**
4. **Limit allowed methods and headers to what's necessary**
5. **Regularly review and update allowed origins**

## 🔄 Updating CORS Configuration

When deploying to new domains:

1. **Add the new domain to `ALLOWED_ORIGINS`**
2. **Update environment variables**
3. **Redeploy the backend**
4. **Test the connection from the new domain**

## 📚 Additional Resources

- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [Express CORS Documentation](https://github.com/expressjs/cors)
- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

**Remember**: CORS is a security feature, not a bug. Configure it properly to ensure secure communication between your frontend and backend.
