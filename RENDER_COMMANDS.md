# Render Deployment Commands

## Required Fields for Render Web Service

### Build Command
```
chmod +x build.sh && ./build.sh
```

### Start Command
```
cd process_monitor/backend && gunicorn process_monitor_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## Copy-Paste Instructions

1. **Build Command**: Copy the single line above
2. **Start Command**: Copy the single line above

## What Each Command Does

### Build Command Breakdown:
- `chmod +x build.sh` - Makes the build script executable
- `&& ./build.sh` - Runs the build script which handles:
  - Installing Python dependencies
  - Setting up Django project
  - Creating static files directory
  - Running database migrations
  - Collecting static files

### Start Command Breakdown:
- `cd process_monitor/backend` - Changes to Django project directory
- `gunicorn` - Production WSGI server
- `process_monitor_backend.wsgi:application` - Django WSGI application
- `--bind 0.0.0.0:$PORT` - Binds to Render's assigned port
- `--workers 2` - Uses 2 worker processes
- `--timeout 120` - Sets 120 second timeout

## Important Notes

- **Don't leave these fields empty** - Render requires both commands
- **Copy exactly** - Don't modify the commands
- **$PORT is automatic** - Render sets this environment variable
- **Build runs first** - Then start command runs after successful build

## Troubleshooting

If you get errors:
1. Check that you copied the commands exactly
2. Ensure no extra spaces or characters
3. Verify the commands are in the correct fields
4. Check the build logs for specific error messages 