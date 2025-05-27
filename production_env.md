# Production Environment Configuration for Railway

Add these environment variables to your Railway project to ensure proper connectivity between your frontend and backend.

```json
{
  "SECRET_KEY": "a!x(mhy4kdh(r(*%)tw5cb5n%y4u%l*gtwuc-j=b&!kdohs-u5",
  "DEBUG": "false",
  "ALLOWED_HOSTS": "web-production-2f30.up.railway.app,localhost,127.0.0.1",
  "CORS_ALLOWED_ORIGINS": "https://dohblog.vercel.app,http://localhost:3000,http://localhost:5173",
  "CORS_ALLOW_ALL_ORIGINS": "false",
  "CSRF_TRUSTED_ORIGINS": "https://web-production-2f30.up.railway.app,https://dohblog.vercel.app",
  "DATABASE_URL": "postgresql://postgres:pJWJRAQlayFpWLWffkTnidosfmLhOrCZ@hopper.proxy.rlwy.net:36010/railway"
}
```

## Vercel Frontend Environment Variables

Add these environment variables to your Vercel frontend project:

```
VITE_API_BASE_URL=https://web-production-2f30.up.railway.app
VITE_MEDIA_URL=https://web-production-2f30.up.railway.app/media/
VITE_USE_MOCK_API=false
VITE_DEBUG=false
```

## URL Structure Notes

The frontend expects these API endpoints to be available:

1. Comment counts: `/api/comments/counts/`
2. Posts: `/api/posts/`
3. Featured posts: `/api/posts/featured/`
4. Latest posts: `/api/posts/latest/`
5. Categories: `/api/categories/all/`

If you encounter 404 errors, ensure the above URLs are properly configured in your backend. 