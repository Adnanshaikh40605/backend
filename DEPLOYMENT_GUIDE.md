# Deployment Guide: Blog CMS

This guide will help you deploy the Blog CMS application with the backend on Railway and the frontend on Vercel.

## Backend Deployment (Railway)

### Prerequisites
- A [Railway](https://railway.app/) account
- Git installed on your local machine

### Steps

1. **Prepare your repository**
   - Ensure your code is in a Git repository
   - Make sure you have the following files:
     - `Procfile`
     - `railway.json`
     - `requirements.txt` (with all dependencies)

2. **Create a new project on Railway**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account if not already connected
   - Select the repository containing your Django project

3. **Configure environment variables**
   - In your Railway project, go to the "Variables" tab
   - Add the following variables (refer to `backend_env.example`):
     ```
     DEBUG=False
     SECRET_KEY=<generate-a-secure-key>
     ALLOWED_HOSTS=.railway.app,your-custom-domain-if-any
     CORS_ALLOWED_ORIGINS=https://your-frontend-vercel-app.vercel.app
     CORS_ALLOW_ALL_ORIGINS=False
     FRONTEND_URL=https://your-frontend-vercel-app.vercel.app
     CSRF_TRUSTED_ORIGINS=https://your-frontend-vercel-app.vercel.app
     ```

4. **Add a PostgreSQL database**
   - In your Railway project, click "New"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically add the `DATABASE_URL` variable to your project

5. **Deploy**
   - Railway will automatically deploy your application
   - You can monitor the deployment in the "Deployments" tab

6. **Get your backend URL**
   - Once deployed, Railway will provide a URL for your application
   - This URL will be used in your frontend configuration

## Frontend Deployment (Vercel)

### Prerequisites
- A [Vercel](https://vercel.com/) account
- Git installed on your local machine

### Steps

1. **Prepare your repository**
   - Ensure your frontend code is in a Git repository
   - Make sure you have the following files:
     - `vercel.json`
     - `package.json` (with build scripts)

2. **Create a new project on Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New" → "Project"
   - Import your Git repository
   - Configure the project:
     - Framework Preset: Vite
     - Build Command: `npm run build`
     - Output Directory: `dist`

3. **Configure environment variables**
   - In your Vercel project, go to "Settings" → "Environment Variables"
   - Add the following variables:
   ```
   VITE_API_BASE_URL=https://your-railway-app-url.railway.app
   VITE_MEDIA_URL=https://your-railway-app-url.railway.app/media/
   VITE_USE_MOCK_API=false
   VITE_DEBUG=false
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your frontend application

## Connecting Frontend and Backend

1. **Update CORS settings on backend**
   - In your Railway environment variables, add your Vercel frontend URL to:
     - `CORS_ALLOWED_ORIGINS`
     - `CSRF_TRUSTED_ORIGINS`

2. **Test the connection**
   - Visit your Vercel frontend URL
   - Verify that API requests to the backend are working correctly
   - Check the browser console for any CORS errors

## Troubleshooting

### Backend Issues
- Check Railway logs for any errors
- Verify environment variables are set correctly
- Ensure the database connection is working

### Frontend Issues
- Check Vercel build logs for any errors
- Verify API URLs are correctly configured
- Check browser console for CORS errors
- Make sure environment variables are properly set in Vercel

### CORS Issues
- Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Verify `CSRF_TRUSTED_ORIGINS` is properly configured
- Check that your frontend is sending the correct headers

### Environment Variable Issues
- Make sure you've set the environment variables in the Vercel dashboard
- If using a custom domain, include it in the CORS settings
- Don't use placeholders in your code; rely on the environment variables

## Maintenance

- Monitor your Railway and Vercel dashboards for any issues
- Set up automatic deployments for future code changes
- Consider setting up a custom domain for both services 