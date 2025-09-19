#!/bin/sh
set -e

echo "Waiting for postgres..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL started"

# --- Django manage dir ---
cd apps

# Worker
if [ "${ROLE}" = "worker" ]; then
  echo "ROLE=worker → skipping migrate/seed, starting Celery..."
  exec celery -A project worker -l info
fi



# ROLE=web (по умолчанию)
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  python manage.py migrate --noinput
fi

python manage.py shell << 'END'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin")
END


# Seed (опционально, по флагу)
if [ "${SEED_DEMO}" = "true" ]; then
  echo "Seeding demo data..."
  python manage.py seed_initial_data
fi

# Server on
if [ "${RUNSERVER}" = "true" ]; then
  echo "Starting Django development server..."
  exec python manage.py runserver 0.0.0.0:8000
else
  echo "Collecting static..."
  # python manage.py collectstatic --noinput
  echo "Starting uvicorn..."
  exec uvicorn project.asgi:application --host 0.0.0.0 --port 8000 --workers 3
fi
