# Process Monitor - Render Deployment Guide

## Overview
This guide will help you deploy the Process Monitor application to Render, a cloud platform that offers free hosting for web applications.

## Prerequisites
- A GitHub account
- A Render account (sign up at https://render.com)
- Git installed on your local machine

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit - Process Monitor app"
```

### 1.2 Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Render

### 2.1 Create a New Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" button
3. Select "Web Service"
4. Connect your GitHub account if not already connected
5. Select your repository

### 2.2 Configure the Service
- **Name**: `process-monitor` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  cd process_monitor/backend
  mkdir -p staticfiles
  python manage.py collectstatic --noinput
  python manage.py migrate
  ```
- **Start Command**: 
  ```
  cd process_monitor/backend && gunicorn process_monitor_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
  ```

### 2.3 Environment Variables
The following environment variables will be automatically set:
- `PYTHON_VERSION`: 3.11.0
- `DJANGO_SECRET_KEY`: Auto-generated
- `DJANGO_DEBUG`: false
- `ALLOWED_HOSTS`: .onrender.com
- `DJANGO_SETTINGS_MODULE`: process_monitor_backend.settings_production
- `DATABASE_URL`: Auto-configured from PostgreSQL database

### 2.4 Create Database
1. In the same project, click "New +" again
2. Select "PostgreSQL"
3. Choose "Free" plan
4. Name it `process-monitor-db`
5. The `DATABASE_URL` will be automatically linked

## Step 3: Monitor Deployment

### 3.1 Build Logs
- Watch the build logs for any errors
- Common build time: 5-10 minutes

### 3.2 Common Build Issues & Solutions

#### Issue: Module not found
**Solution**: Ensure all dependencies are in `requirements.txt`

#### Issue: Static files not found
**Solution**: The build script automatically runs `collectstatic`

#### Issue: Database connection failed
**Solution**: Check that `DATABASE_URL` is properly set

#### Issue: Port binding error
**Solution**: Ensure `$PORT` environment variable is used in gunicorn

## Step 4: Verify Deployment

### 4.1 Check Application Status
- Visit your app URL: `https://your-app-name.onrender.com`
- Check the logs in Render dashboard

### 4.2 Test API Endpoints
```bash
# Test the main endpoint
curl https://your-app-name.onrender.com/

# Test API endpoints
curl https://your-app-name.onrender.com/api/hosts/
```

## Step 5: Troubleshooting

### 5.1 Application Won't Start
1. Check the logs in Render dashboard
2. Verify all environment variables are set
3. Ensure the Procfile is correct

### 5.2 Database Issues
1. Verify PostgreSQL service is running
2. Check `DATABASE_URL` format
3. Ensure migrations ran successfully

### 5.3 Static Files Not Loading
1. Check if `collectstatic` ran during build
2. Verify whitenoise middleware is configured
3. Check static files directory structure

## Configuration Files Explained

### render.yaml
- Defines the service configuration
- Sets up environment variables
- Configures database connection

### Procfile
- Tells Render how to start the application
- Uses gunicorn with proper worker configuration

### build.sh
- Runs during the build process
- Installs dependencies
- Runs database migrations
- Collects static files

### settings_production.py
- Production-specific Django settings
- Configures database for PostgreSQL
- Sets up static file handling with whitenoise
- Configures security settings

## Maintenance

### Updating the Application
1. Make changes locally
2. Commit and push to GitHub
3. Render will automatically redeploy

### Monitoring
- Check Render dashboard regularly
- Monitor application logs
- Set up alerts for downtime

### Scaling
- Free tier has limitations
- Consider upgrading for production use
- Monitor resource usage

## Support

If you encounter issues:
1. Check the Render documentation
2. Review the build and runtime logs
3. Verify all configuration files are correct
4. Ensure all dependencies are properly specified

## Security Notes

- `DJANGO_DEBUG` is set to `false` in production
- `SECRET_KEY` is auto-generated
- HTTPS is enforced on Render
- Database credentials are automatically managed

---

**Happy Deploying! 🚀** 