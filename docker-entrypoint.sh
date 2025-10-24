#!/bin/bash
set -e

echo "Starting Django Photo Album Application..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z ${DB_HOST} ${DB_PORT}; do
  echo "Database unavailable - sleeping"
  sleep 1
done
echo "Database is ready!"

# Wait for Redis to be ready (for Celery services)
if [ "$1" != "migrate" ] && [ "$1" != "collectstatic" ]; then
    echo "Waiting for Redis..."
    REDIS_HOST=$(echo ${CELERY_BROKER_URL} | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    while ! nc -z ${REDIS_HOST:-redis} 6379; do
      echo "Redis unavailable - sleeping"
      sleep 1
    done
    echo "Redis is ready!"
fi

# Run migrations (only for web service)
if [ "$1" = "web" ] || [ "$1" = "migrate" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
fi

# Collect static files (only for web service)
if [ "$1" = "web" ] || [ "$1" = "collectstatic" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput --clear
fi

# Create superuser if it doesn't exist (only for web service)
if [ "$1" = "web" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "Creating superuser if needed..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')
    print('Superuser created.')
else:
    print('Superuser already exists.')
END
fi

# Execute the command based on the service type
case "$1" in
    web)
        echo "Starting Gunicorn server..."
        exec gunicorn photo_album.wsgi:application \
            --bind 0.0.0.0:8000 \
            --workers ${GUNICORN_WORKERS:-4} \
            --threads ${GUNICORN_THREADS:-2} \
            --timeout ${GUNICORN_TIMEOUT:-120} \
            --worker-class sync \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --keep-alive 5 \
            --log-level info \
            --access-logfile - \
            --error-logfile -
        ;;
    celery-worker)
        echo "Starting Celery worker..."
        exec celery -A photo_album worker \
            --loglevel=${CELERY_LOG_LEVEL:-info} \
            --concurrency=${CELERY_WORKER_CONCURRENCY:-4} \
            --max-tasks-per-child=50
        ;;
    celery-beat)
        echo "Starting Celery beat scheduler..."
        exec celery -A photo_album beat \
            --loglevel=${CELERY_LOG_LEVEL:-info}
        ;;
    migrate)
        echo "Migration completed."
        exit 0
        ;;
    collectstatic)
        echo "Static files collected."
        exit 0
        ;;
    bash)
        exec /bin/bash
        ;;
    *)
        echo "Unknown command: $1"
        echo "Available commands: web, celery-worker, celery-beat, migrate, collectstatic, bash"
        exit 1
        ;;
esac