# Railway Backend Configuration Guide

## Environment Variables for Railway

Add these environment variables to your Railway project:

```
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=backend-production-0150.up.railway.app,127.0.0.1,localhost

# CORS settings
CORS_ALLOWED_ORIGINS=https://dohblog.vercel.app,http://localhost:3000,http://localhost:5173
CORS_ALLOW_ALL_ORIGINS=False

# Security settings
CSRF_TRUSTED_ORIGINS=https://dohblog.vercel.app,https://backend-production-0150.up.railway.app
```

## How to Set Environment Variables on Railway

1. Go to your Railway project dashboard
2. Click on your backend service
3. Go to the "Variables" tab
4. Add each variable with its corresponding value
5. Railway will automatically redeploy your application with the new settings 