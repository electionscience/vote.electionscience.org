#!/bin/sh

# Exit script in case of error
set -e

# Log the start of the script
echo "Starting entrypoint script..."

# Ensure the necessary environment variables are set
if [ -z "${DJANGO_SETTINGS_MODULE}" ]; then
	echo "Error: DJANGO_SETTINGS_MODULE is not set."
	exit 1
fi

# Run Django migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn "approval_polls.wsgi:application" "-b 0.0.0.0:8000"
