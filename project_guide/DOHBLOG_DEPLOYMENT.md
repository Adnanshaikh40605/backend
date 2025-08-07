# Deploying to dohblog.vercel.app

This guide provides instructions for deploying the frontend to dohblog.vercel.app.

## Prerequisites

1. Vercel CLI installed: `npm install -g vercel`
2. Access to the dohblog.vercel.app project on Vercel

## Deployment Steps

### Option 1: Using the deployment script

1. Run the dohblog deployment script:
   ```
   chmod +x deploy-dohblog.sh
   ./deploy-dohblog.sh
   ```

2. Deploy to Vercel:
   ```
   vercel --prod
   ```

### Option 2: Manual deployment

1. Create the production environment file:
   ```
   echo "VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app" > .env.production
   echo "VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/" >> .env.production
   echo "VITE_USE_MOCK_API=false" >> .env.production
   echo "VITE_DEBUG=false" >> .env.production
   ```

2. Copy the dohblog Vercel configuration:
   ```
   cp vercel.dohblog.json vercel.json
   ```

3. Build the project:
   ```
   npm run build
   ```

4. Deploy to Vercel:
   ```
   vercel --prod
   ```

## Vercel Environment Variables

Make sure the following environment variables are set in your Vercel project settings:

- `VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app`
- `VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/`
- `VITE_USE_MOCK_API=false`
- `VITE_DEBUG=false`

## Checking the Deployment

After deployment, verify that:

1. The frontend is accessible at https://dohblog.vercel.app
2. API requests are correctly routed to the backend at https://backend-production-92ae.up.railway.app
3. Media files are correctly loaded from https://backend-production-92ae.up.railway.app/media/

## Troubleshooting

If you encounter CORS issues:

1. Verify that `https://dohblog.vercel.app` is included in the backend's CORS allowed origins
2. Check the browser console for any CORS-related errors
3. Ensure the backend is properly configured to accept requests from dohblog.vercel.app 