#!/bin/sh

# Exit script in case of error
set -e

# Run Django migrations
echo "Running migrations"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting server"
exec gunicorn "approval_polls.wsgi:application" "-b 0.0.0.0:8000"
