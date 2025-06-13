# Deploying to Railway

This Django project is configured to deploy on Railway. Here's how to set it up:

## Required Environment Variables

Set these in your Railway project settings:

- `DEBUG` - Set to `False` for production
- `SECRET_KEY` - Your Django secret key
- `ALLOWED_HOSTS` - Add `.railway.app` and your custom domain if any
- `CORS_ALLOW_ALL_ORIGINS` - Set to `True` if needed or configure specific origins
- `CORS_ALLOWED_ORIGINS` - Your frontend domain(s)
- `CSRF_TRUSTED_ORIGINS` - Your frontend domain(s)
- `DATABASE_URL` - Railway will set this automatically if you add a PostgreSQL service

## Deployment Steps

1. Push your code to GitHub
2. In Railway, create a new project from GitHub
3. Select your repository
4. Railway will automatically detect the Python project and deploy it
5. Add a PostgreSQL service if needed (recommended for production)
6. Set the environment variables mentioned above
7. Your app should deploy successfully!

## Troubleshooting

If you encounter the "No start command could be found" error:
- Make sure you have the `Procfile` in your repository
- Make sure `gunicorn` is in your requirements.txt
- Check that your `railway.toml` file is properly configured

## File Structure

The following files are important for deployment:
- `Procfile` - Tells Railway how to run your app
- `runtime.txt` - Specifies the Python version
- `requirements.txt` - Lists all Python dependencies
- `railway.toml` - Additional Railway configuration
- `package.json` - Contains start scripts 