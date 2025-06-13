# Environment Configuration

This document provides an overview of the environment configuration for both the frontend and backend.

## Backend Configuration

### Local Development (.env)

```
# Django settings
DATABASE_URL=postgresql://postgres:tjivRKybjCRWGgWiVAxNpASgEmhzASyi@switchyard.proxy.rlwy.net:57528/railway
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://dohblog.vercel.app
CORS_ALLOW_ALL_ORIGINS=False
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:5173,https://dohblog.vercel.app
```

### Production (Railway Variables)

```json
{
  "DEBUG": "False",
  "SECRET_KEY": "rpsp6hme2+g^wsh@h2fzn)1*9bo$sz!_-)kxzf6@5th&i8a1@w",
  "ALLOWED_HOSTS": "backend-production-92ae.up.railway.app,localhost,127.0.0.1",
  "BACKEND_URL": "https://backend-production-92ae.up.railway.app",
  "CORS_ALLOW_ALL_ORIGINS": "True",
  "CORS_ALLOWED_ORIGINS": "http://localhost:3000,http://localhost:5173,https://backend-production-92ae.up.railway.app,https://blog-cms-frontend-ten.vercel.app,https://dohblog.vercel.app",
  "CSRF_TRUSTED_ORIGINS": "http://localhost:3000,http://localhost:5173,https://backend-production-92ae.up.railway.app,https://blog-cms-frontend-ten.vercel.app,https://dohblog.vercel.app",
  "DATABASE_URL": "postgresql://postgres:tjivRKybjCRWGgWiVAxNpASgEmhzASyi@postgres.railway.internal:5432/railway",
  "PORT": "8000",
  "PYTHONUNBUFFERED": "1",
  "DJANGO_LOG_LEVEL": "INFO"
}
```

## Frontend Configuration

### Main Environment (.env)

```
VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app
VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/
VITE_USE_MOCK_API=false
VITE_DEBUG=false
```

### Development Environment (.env.development)

```
VITE_API_BASE_URL=http://localhost:8000
VITE_MEDIA_URL=http://localhost:8000/media/
VITE_USE_MOCK_API=false
VITE_DEBUG=true
```

### Production Environment (.env.production)

```
VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app
VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/
VITE_USE_MOCK_API=false
VITE_DEBUG=false
```

### Dohblog Environment (.env.dohblog)

```
VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app
VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/
VITE_USE_MOCK_API=false
VITE_DEBUG=false
```

## Vercel Configuration

### Main Vercel Configuration (vercel.json)

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://backend-production-92ae.up.railway.app/api/:path*" },
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "framework": "vite",
  "installCommand": "npm install",
  "buildCommand": "chmod +x build.sh && ./build.sh"
}
```

### Dohblog Vercel Configuration (vercel.dohblog.json)

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://backend-production-92ae.up.railway.app/api/:path*" },
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "framework": "vite",
  "installCommand": "npm install",
  "buildCommand": "chmod +x build.sh && ./build.sh"
}
```

## Environment Update Scripts

### Windows (update_frontend_env.bat)

```batch
@echo off
echo Updating frontend environment files...

cd frontend

echo Creating .env file...
echo VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app > .env
echo VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/ >> .env
echo VITE_USE_MOCK_API=false >> .env
echo VITE_DEBUG=false >> .env

echo Creating .env.development file...
echo VITE_API_BASE_URL=http://localhost:8000 > .env.development
echo VITE_MEDIA_URL=http://localhost:8000/media/ >> .env.development
echo VITE_USE_MOCK_API=false >> .env.development
echo VITE_DEBUG=true >> .env.development

echo Creating .env.production file...
echo VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app > .env.production
echo VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/ >> .env.production
echo VITE_USE_MOCK_API=false >> .env.production
echo VITE_DEBUG=false >> .env.production

echo Creating .env.dohblog file...
echo VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app > .env.dohblog
echo VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/ >> .env.dohblog
echo VITE_USE_MOCK_API=false >> .env.dohblog
echo VITE_DEBUG=false >> .env.dohblog

echo Environment files updated successfully!
cd ..
```

## Environment Check Script (check_env_config.py)

A Python script that checks the environment configuration for both frontend and backend.

Run it with:
```
python check_env_config.py
``` 