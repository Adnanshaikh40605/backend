# Deploying to Railway with PostgreSQL

This guide will help you deploy your Django application to Railway with a PostgreSQL database.

## Prerequisites

1. A [Railway](https://railway.app/) account
2. This Django project

## Step 1: Create a PostgreSQL database on Railway

1. Log in to your Railway account
2. Click "New Project" > "Database" > "PostgreSQL"
3. Wait for the database to be provisioned
4. Once created, go to the "Variables" tab to see your database credentials

## Step 2: Link your database to your Django project

1. Create a new empty project on Railway
2. Connect your GitHub repository to Railway
3. Under "Variables", add the necessary environment variables:

```
DEBUG=False
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=.railway.app,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
CORS_ALLOW_ALL_ORIGINS=False
CSRF_TRUSTED_ORIGINS=https://backend-production-49ec.up.railway.app,http://localhost:3000,https://your-frontend-domain.com
DJANGO_LOG_LEVEL=INFO
```

4. Link your PostgreSQL database to your Django project:
   - In your PostgreSQL service, go to "Connect" tab
   - Click "Connect" button
   - Select your Django project 
   - This will automatically add the `DATABASE_URL` variable to your Django project

## Step 3: Deploy your Django project

1. Railway should automatically deploy your project based on the configuration files:
   - `railway.toml`
   - `nixpacks.toml`
   - `Procfile`
   - `Dockerfile` (if you choose to use Docker)

2. The deployment should use the startup command: `gunicorn backend.wsgi:application --log-file -`

## Step 4: Verify the deployment

1. Once deployed, click on the domain provided by Railway
2. You should see your Django application running
3. Check the logs to ensure no errors occurred during deployment

## Troubleshooting

1. **No start command found**: Make sure your `railway.toml` file has the proper `startCommand` defined.
2. **Database connection issues**: Verify your `DATABASE_URL` environment variable is correctly set and the database is linked.
3. **Static files not loading**: Ensure the `collectstatic` command is running during the build process.
4. **Migrations not applied**: Check that migrations are applied during deployment using the `post_compile` script or in the build process.

## Useful Railway CLI Commands

If you're using the Railway CLI:

```bash
# Deploy your project
railway up

# View logs
railway logs

# View variables
railway variables

# Connect to your PostgreSQL database
railway connect
```

For more help, refer to the [Railway documentation](https://docs.railway.app/). 