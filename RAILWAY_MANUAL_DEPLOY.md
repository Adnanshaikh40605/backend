# Manual Railway Deployment Guide

Since you're having issues with the CLI deployment, here's a step-by-step guide to deploy your Django project using the Railway web interface:

## Step 1: Push your code to GitHub

Make sure your code is in a GitHub repository.

## Step 2: Create a new Railway project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect your Django project

## Step 3: Configure environment variables

1. In your project dashboard, go to the "Variables" tab
2. Add the following environment variables:
   ```
   DATABASE_URL=postgresql://postgres:vufrAGspjmpKTfBEuhVjknhIxbOuxkuD@containers-us-west-59.railway.app:5432/railway
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=.railway.app,localhost,127.0.0.1
   ```

## Step 4: Link your PostgreSQL database

1. In your project dashboard, go to the "Settings" tab
2. Under "Linked Services", click "Link Service"
3. Select your PostgreSQL database service

## Step 5: Run migrations

1. In your project dashboard, go to the "Deployments" tab
2. Click on the latest deployment
3. Click "Shell" to open a terminal
4. Run:
   ```
   python manage.py migrate
   ```

## Step 6: Create a superuser

In the same shell:
```
python manage.py createsuperuser
```

## Step 7: Access your application

Your application will be available at the domain provided by Railway (visible in the "Settings" tab under "Domains").

The admin interface will be at `https://your-domain.railway.app/admin/`.

## Troubleshooting

If you encounter any issues:
1. Check the deployment logs
2. Make sure your DATABASE_URL is correctly set
3. Ensure your PostgreSQL service is running
4. Check that your Django settings are correctly configured for production 