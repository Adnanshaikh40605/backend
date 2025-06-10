# Railway Deployment Guide

This guide will help you deploy the Django Blog CMS on Railway.

## Prerequisites

1. A [Railway](https://railway.app/) account
2. [Railway CLI](https://docs.railway.app/develop/cli) installed (optional but recommended)

## Steps to Deploy

### 1. Create a PostgreSQL Database on Railway

1. Log in to your Railway account
2. Click "New Project" and select "PostgreSQL" from the database options
3. Once created, go to the PostgreSQL service and click on "Connect" to view connection details
4. Note the connection URL (you'll need this later)

### 2. Deploy the Django Application

#### Using Railway Dashboard (Web UI)

1. In your Railway dashboard, click "New Project" → "Deploy from GitHub"
2. Select your repository containing this Django project
3. Once connected, go to the "Variables" tab and add the following environment variables:
   - `SECRET_KEY`: A secure random string
   - `DEBUG`: Set to `False` for production
   - `DATABASE_URL`: Use the PostgreSQL connection URL from step 1
   - `ALLOWED_HOSTS`: Include your Railway app domain (e.g., `yourapp.railway.app`)

4. Railway will automatically detect the Python project and build it

#### Using Railway CLI

1. Navigate to your project directory in the terminal
2. Login to Railway CLI:
   ```
   railway login
   ```
3. Link your project:
   ```
   railway init
   ```
4. Add your PostgreSQL database:
   ```
   railway link
   ```
   (Select your PostgreSQL service when prompted)
5. Set environment variables:
   ```
   railway variables set SECRET_KEY=your-secret-key-here
   railway variables set DEBUG=False
   ```
6. Deploy your application:
   ```
   railway up
   ```

### 3. Run Migrations

After deployment, you need to run migrations:

1. In the Railway dashboard, go to your Django service
2. Click on "Deployments" tab
3. Click on the "Shell" button
4. Run:
   ```
   python manage.py migrate
   ```

### 4. Create a Superuser (Admin)

In the same shell:

```
python manage.py createsuperuser
```

### 5. Access Your Application

Your application will be available at the domain provided by Railway (e.g., `https://yourapp.railway.app`).

The admin interface will be at `https://yourapp.railway.app/admin/`.

## Troubleshooting

- If you encounter any issues, check the logs in the Railway dashboard
- Make sure all environment variables are correctly set
- Ensure the PostgreSQL service is properly linked to your application 