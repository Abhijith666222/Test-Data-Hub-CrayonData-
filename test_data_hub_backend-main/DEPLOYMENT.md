# 🚀 Deployment Guide for Render

This guide will help you deploy the Test Data Environment Backend to Render.

## 📋 Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Environment Variables**: Prepare your configuration values

## 🔧 Environment Variables Setup

### **Required Environment Variables**

Set these in your Render dashboard:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-actual-openai-api-key

# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# CORS Configuration
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://another-domain.com

# Database Configuration (if needed)
MYSQL_HOST=your-mysql-host
MYSQL_PORT=3306
MYSQL_DATABASE=your-database
MYSQL_USERNAME=your-username
MYSQL_PASSWORD=your-password

ORACLE_HOST=your-oracle-host
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=your-service-name
ORACLE_USERNAME=your-username
ORACLE_PASSWORD=your-password
```

### **Optional Environment Variables**

```bash
# These have sensible defaults
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
```

## 🚀 Deployment Steps

### **Step 1: Connect Repository**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository containing this backend

### **Step 2: Configure Service**

- **Name**: `test-data-backend` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start_backend.py`
- **Plan**: Choose based on your needs (Free tier available)

### **Step 3: Set Environment Variables**

1. In your service dashboard, go to "Environment"
2. Add each environment variable from the list above
3. **Important**: Never commit `.env` files to your repository

### **Step 4: Deploy**

1. Click "Create Web Service"
2. Render will automatically build and deploy your service
3. Monitor the build logs for any issues

## 🔍 Health Check

Your service includes a health check endpoint:

```
GET /health
```

Render will use this to monitor your service health.

## 📊 Monitoring

- **Logs**: View real-time logs in the Render dashboard
- **Metrics**: Monitor performance and resource usage
- **Alerts**: Set up notifications for service issues

## 🚨 Troubleshooting

### **Common Issues**

1. **Build Failures**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **Runtime Errors**
   - Check environment variables are set correctly
   - Review logs for specific error messages

3. **CORS Issues**
   - Verify `ALLOWED_ORIGINS` includes your frontend domain
   - Check for typos in domain names

### **Debug Commands**

```bash
# Check environment variables
echo $OPENAI_API_KEY

# Test the service locally
python start_backend.py

# Check dependencies
pip list
```

## 🔒 Security Considerations

1. **Never commit sensitive data** to your repository
2. **Use environment variables** for all configuration
3. **Set appropriate CORS origins** for production
4. **Monitor API usage** and set rate limits if needed

## 📈 Scaling

- **Free Tier**: Good for development and testing
- **Paid Plans**: Better performance and reliability for production
- **Auto-scaling**: Available on higher-tier plans

## 🔗 API Documentation

Once deployed, your API documentation will be available at:

```
https://your-service-name.onrender.com/docs
```

## 📞 Support

- **Render Support**: [help.render.com](https://help.render.com)
- **Documentation**: [render.com/docs](https://render.com/docs)
- **Community**: [Render Community](https://community.render.com)

## 🎯 Next Steps

After successful deployment:

1. **Test all endpoints** using the API documentation
2. **Set up monitoring** and alerts
3. **Configure your frontend** to use the new backend URL
4. **Set up CI/CD** for automatic deployments

---

**Happy Deploying! 🚀**
