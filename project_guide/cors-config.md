# CORS Configuration for Blog CMS

This document explains how Cross-Origin Resource Sharing (CORS) is configured between the frontend and backend of the Blog CMS application.

## What is CORS?

Cross-Origin Resource Sharing (CORS) is a security feature implemented by browsers that restricts web pages from making requests to a different domain than the one that served the original page. This is a security measure to prevent malicious websites from making unauthorized requests to other domains on behalf of the user.

## CORS Configuration in the Backend

The backend API is configured to allow requests from specific origins. This is done in the Django settings file (`settings.py`):

```python
# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'
CORS_ALLOW_CREDENTIALS = True  # Allow credentials

# Get CORS allowed origins from environment or use a default list
cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
# If env variable is empty, add some sensible defaults
if not cors_origins or cors_origins == [""]:
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://backend-production-92ae.up.railway.app",
        "https://blog-cms-frontend-ten.vercel.app",
        "https://dohblog.vercel.app",
        "https://blog-website-sigma-one.vercel.app",
        "https://vacation-bna.vercel.app"
    ]
CORS_ALLOWED_ORIGINS = cors_origins

# CSRF Trusted Origins
csrf_trusted_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
if not csrf_trusted_origins or csrf_trusted_origins == [""]:
    csrf_trusted_origins = cors_origins
CSRF_TRUSTED_ORIGINS = csrf_trusted_origins
```

## CORS Configuration in the Frontend

The frontend is configured to include credentials in cross-origin requests. This is done in the API client configuration:

```javascript
// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Enable CORS credentials
  withCredentials: true,
  timeout: API_CONFIG.TIMEOUT,
});
```

## Adding New Origins

If you need to add a new origin to the allowed list, you have two options:

### 1. Update the Backend Settings

Add the new origin to the `cors_origins` list in the `settings.py` file:

```python
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://backend-production-92ae.up.railway.app",
    "https://blog-cms-frontend-ten.vercel.app",
    "https://dohblog.vercel.app",
    "https://blog-website-sigma-one.vercel.app",
    "https://vacation-bna.vercel.app",
    "https://your-new-origin.com"  # Add your new origin here
]
```

### 2. Set Environment Variables

Set the `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` environment variables with a comma-separated list of allowed origins:

```
CORS_ALLOWED_ORIGINS=https://blog-website-sigma-one.vercel.app,https://dohblog.vercel.app,https://your-new-origin.com
CSRF_TRUSTED_ORIGINS=https://blog-website-sigma-one.vercel.app,https://dohblog.vercel.app,https://your-new-origin.com
```

## Testing CORS Configuration

To test if CORS is properly configured, you can:

1. Open your browser's developer tools (F12)
2. Go to the Network tab
3. Make a request to the API from your frontend
4. Check if the request includes the `Origin` header and if the response includes the `Access-Control-Allow-Origin` header

If CORS is properly configured, the API request should succeed without any CORS errors in the console.

## Common CORS Errors

If you encounter CORS errors, they will typically appear in the browser console as:

```
Access to XMLHttpRequest at 'https://backend-production-92ae.up.railway.app/api/posts/' from origin 'https://your-frontend.com' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

This indicates that the backend is not configured to allow requests from your frontend's origin.

## Troubleshooting

1. Verify that your frontend's origin is included in the `CORS_ALLOWED_ORIGINS` list in the backend settings
2. Check if the backend is properly configured to send the `Access-Control-Allow-Origin` header
3. Ensure that the `withCredentials` option in the frontend API client matches the CORS configuration in the backend
4. If using cookies for authentication, ensure that `CORS_ALLOW_CREDENTIALS` is set to `True` in the backend settings 