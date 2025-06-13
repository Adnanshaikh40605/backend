# dohblog.vercel.app Connection Summary

## Changes Made

1. **Backend CORS Configuration**:
   - Added `https://dohblog.vercel.app` to the CORS allowed origins in `backend/settings.py`
   - Added `https://dohblog.vercel.app` to the CSRF trusted origins in `backend/settings.py`

2. **Railway Variables**:
   - Updated `railway_variables.json` to include `https://dohblog.vercel.app` in CORS and CSRF settings

3. **Frontend Deployment Configuration**:
   - Created `frontend/vercel.dohblog.json` with proper API routing configuration
   - Created `frontend/deploy-dohblog.sh` deployment script
   - Created `frontend/DOHBLOG_DEPLOYMENT.md` with deployment instructions

## Deployment Instructions

### Backend Deployment

1. Push the updated code to GitHub
2. Railway will automatically redeploy with the new CORS settings

### Frontend Deployment

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Use the deployment script (on Linux/Mac):
   ```
   chmod +x deploy-dohblog.sh
   ./deploy-dohblog.sh
   ```

   Or manually on Windows:
   ```
   copy vercel.dohblog.json vercel.json
   
   echo VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app > .env.production
   echo VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/ >> .env.production
   echo VITE_USE_MOCK_API=false >> .env.production
   echo VITE_DEBUG=false >> .env.production
   
   npm run build
   ```

3. Deploy to Vercel:
   ```
   npx vercel --prod
   ```

## Vercel Environment Variables

Make sure the following environment variables are set in your Vercel project settings:

- `VITE_API_BASE_URL=https://backend-production-92ae.up.railway.app`
- `VITE_MEDIA_URL=https://backend-production-92ae.up.railway.app/media/`
- `VITE_USE_MOCK_API=false`
- `VITE_DEBUG=false`

## Verification

After deployment, verify that:

1. The frontend is accessible at https://dohblog.vercel.app
2. API requests are correctly routed to the backend at https://backend-production-92ae.up.railway.app
3. Media files are correctly loaded from https://backend-production-92ae.up.railway.app/media/

## Troubleshooting

If you encounter CORS issues:

1. Check the browser console for any CORS-related errors
2. Verify that the backend is properly configured with the correct CORS settings
3. Ensure that the frontend is making requests to the correct backend URL 