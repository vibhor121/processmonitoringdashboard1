# Process Monitor System

A Django-based process monitoring system with a REST API backend and monitoring agent.

## Features

- Real-time process monitoring
- REST API backend
- Monitoring agent for system metrics
- Web dashboard interface
- Database storage for historical data

## Project Structure

```
├── process_monitor/          # Main project directory
│   ├── backend/             # Django backend application
│   ├── agent/               # Monitoring agent
│   ├── docs/                # Documentation
│   ├── logs/                # Application logs
│   └── requirements.txt     # Python dependencies
├── render.yaml              # Render deployment configuration
├── requirements.txt         # Root requirements (for deployment)
├── build.sh                 # Build script for deployment
├── Procfile                 # Alternative deployment method
└── runtime.txt              # Python version specification
```

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <project-directory>
   ```

2. Create and activate virtual environment:
   ```bash
   cd process_monitor
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the system:
   ```bash
   chmod +x start_system.sh
   ./start_system.sh
   ```

The system will start:
- Django backend on http://localhost:8000/
- Monitoring agent in the background
- Logs will be written to the `logs/` directory

## Deployment to Render

### Automatic Deployment

1. Connect your GitHub repository to Render
2. Render will automatically detect the `render.yaml` configuration
3. The system will be deployed with:
   - Python 3.11.0
   - PostgreSQL database
   - Automatic migrations and static file collection

### Manual Deployment

1. Create a new Web Service on Render
2. Set the following environment variables:
   - `PYTHON_VERSION`: 3.11.0
   - `DJANGO_SECRET_KEY`: (auto-generated)
   - `DJANGO_DEBUG`: false
   - `ALLOWED_HOSTS`: .onrender.com
   - `DJANGO_SETTINGS_MODULE`: process_monitor_backend.settings_production

3. Build Command:
   ```bash
   pip install -r requirements.txt && cd process_monitor/backend && python manage.py collectstatic --noinput && python manage.py migrate
   ```

4. Start Command:
   ```bash
   cd process_monitor/backend && gunicorn process_monitor_backend.wsgi:application --bind 0.0.0.0:$PORT
   ```

## API Endpoints

- Dashboard: `/`
- API Root: `/api/`
- Hosts: `/api/hosts/`
- Processes: `/api/processes/`

## Troubleshooting

### Common Issues

1. **Requirements not found**: Ensure `requirements.txt` is in the root directory
2. **Database connection**: Check environment variables for database configuration
3. **Static files**: Ensure `collectstatic` is run during build
4. **Port binding**: Verify the `$PORT` environment variable is set

### Logs

- Django logs: `logs/django.log`
- Agent logs: `logs/agent.log`
- Render logs: Available in the Render dashboard

## Dependencies

- Django 5.2.0+
- Django REST Framework 3.16.0+
- psutil 7.0.0+
- requests 2.32.0+
- gunicorn 21.0.0+
- dj-database-url 2.0.0+

## License

This project is licensed under the MIT License. 