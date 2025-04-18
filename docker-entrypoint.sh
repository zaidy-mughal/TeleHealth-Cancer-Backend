#!/bin/bash

# Function to check if database is ready
wait_for_db() {
    echo "Waiting for database..."
    while ! nc -z db 5432; do
        sleep 1
    done
    echo "Database is ready!"
}

# Wait for the database
wait_for_db

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120 