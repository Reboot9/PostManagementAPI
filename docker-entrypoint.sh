#!/bin/sh
set -e

./wait-for-it.sh $DB_HOST:$PGPORT -t 60

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply django migrations
until python3 manage.py migrate
do
  echo "Waiting for the database to be ready..."
  sleep 2
done

echo "Database is ready. Starting the development server..."

# Wait for Nginx to become ready
./wait-for-it.sh nginx:80 -- echo "Nginx is ready to accept connections."

# Start the development server
gunicorn PostManagementAPI.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile - --workers 4 --threads 4

exec "$@"