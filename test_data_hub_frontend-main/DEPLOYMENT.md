# 🚀 Deployment Guide

This guide will walk you through deploying the Test Data Frontend to GitHub and Render.

## 📋 Prerequisites

- [Node.js 16+](https://nodejs.org/) installed
- [Git](https://git-scm.com/) installed
- [GitHub](https://github.com/) account
- [Render](https://render.com/) account
- Backend API running and accessible

## 🐙 GitHub Repository Setup

### 1. Create a New Repository

1. Go to [GitHub](https://github.com/) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Name your repository (e.g., `test-data-frontend`)
5. Make it public or private as needed
6. **Don't** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### 2. Initialize Local Git Repository

```bash
# Navigate to your project directory
cd /path/to/test_data_frontend

# Initialize git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: Test Data Frontend"

# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/test-data-frontend.git

# Push to GitHub
git push -u origin main
```

### 3. Verify Repository

- Check that all files are uploaded
- Ensure `.gitignore` is working (no `node_modules` or `build` folders)
- Verify `env.example` is included but `.env` is not

## 🌐 Render Deployment

### 1. Connect Repository to Render

1. Sign in to [Render](https://render.com/)
2. Click "New +" and select "Static Site"
3. Connect your GitHub account if not already connected
4. Select your repository: `test-data-frontend`
5. Configure the deployment:

### 2. Deployment Configuration

**Basic Settings:**
- **Name**: `test-data-frontend` (or your preferred name)
- **Branch**: `main` (or your default branch)
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `build`

**Environment Variables:**
Set these in the Render dashboard:

```env
NODE_VERSION=16
REACT_APP_API_BASE_URL=https://your-backend-domain.com
REACT_APP_WS_URL=wss://your-backend-domain.com
REACT_APP_APP_ENVIRONMENT=production
REACT_APP_ENABLE_DEBUG_MODE=false
REACT_APP_ENABLE_ANALYTICS=true
```

### 3. Automatic Deployment

- Render will automatically deploy when you push to the main branch
- Each deployment creates a unique URL
- You can set up a custom domain later

## 🔧 Environment Configuration

### 1. Local Development

Create a `.env` file in your project root:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_APP_ENVIRONMENT=development
REACT_APP_ENABLE_DEBUG_MODE=true
REACT_APP_ENABLE_ANALYTICS=false
```

### 2. Production Deployment

Set these in your deployment platform (Render):

```env
REACT_APP_API_BASE_URL=https://your-backend-api.com
REACT_APP_WS_URL=wss://your-backend-api.com
REACT_APP_APP_ENVIRONMENT=production
REACT_APP_ENABLE_DEBUG_MODE=false
REACT_APP_ENABLE_ANALYTICS=true
```

## 🚀 Deployment Commands

### Using NPM Scripts

```bash
# Build for production
npm run build

# Build and check for Render
npm run deploy:render

# Full deployment check
npm run deploy:check
```

### Using Deployment Scripts

**Windows:**
```cmd
scripts\deploy.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check Node.js version (16+ required)
   - Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
   - Check for TypeScript errors: `npm run build`

2. **Environment Variables Not Working**
   - Ensure variables start with `REACT_APP_`
   - Restart development server after changing `.env`
   - Check Render dashboard for production variables

3. **API Connection Issues**
   - Verify backend is running and accessible
   - Check CORS configuration on backend
   - Ensure URLs use correct protocol (http/https, ws/wss)

4. **Deployment Fails on Render**
   - Check build logs in Render dashboard
   - Verify build command and publish directory
   - Ensure all dependencies are in `package.json`

### Debug Mode

Enable debug mode in development:

```env
REACT_APP_ENABLE_DEBUG_MODE=true
```

This will show additional console logs and error information.

## 🔄 Continuous Deployment

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Render
      uses: johnbeynon/render-deploy-action@v1.0.0
      with:
        service-id: ${{ secrets.RENDER_SERVICE_ID }}
        api-key: ${{ secrets.RENDER_API_KEY }}
```

## 📊 Monitoring & Analytics

### Render Analytics

- View deployment history in Render dashboard
- Monitor build times and success rates
- Check for failed deployments

### Application Monitoring

- Enable analytics with `REACT_APP_ENABLE_ANALYTICS=true`
- Monitor API response times
- Track user interactions (if implemented)

## 🔐 Security Considerations

1. **Environment Variables**
   - Never commit `.env` files to Git
   - Use Render's secure environment variable storage
   - Rotate API keys regularly

2. **CORS Configuration**
   - Configure backend to only allow your frontend domain
   - Use `REACT_APP_ALLOWED_ORIGINS` for reference

3. **HTTPS/WSS**
   - Always use HTTPS in production
   - Use WSS for WebSocket connections
   - Render provides SSL certificates automatically

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Create React App Deployment](https://create-react-app.dev/docs/deployment/)
- [React Environment Variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)
- [GitHub Pages Deployment](https://create-react-app.dev/docs/deployment/#github-pages)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Render deployment logs
3. Check browser console for errors
4. Verify environment variable configuration
5. Ensure backend is accessible from Render's servers

---

**Happy Deploying! 🎉**
