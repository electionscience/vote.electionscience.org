#!/bin/sh

# Exit script in case of error
set -e

# Log the start of the script
echo "Starting entrypoint script..."

# Ensure the necessary environment variables are set
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
  echo "Error: DJANGO_SETTINGS_MODULE is not set."
  exit 1
fi

# Run Django migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Compress static files
echo "Compressing static files..."
python manage.py compress --force

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn "approval_polls.wsgi:application" "-b 0.0.0.0:8000"