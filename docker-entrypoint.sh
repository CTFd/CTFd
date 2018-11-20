#!/bin/sh
set -eo pipefail

WORKERS=${WORKERS:-1}

# Check that a .ctfd_secret_key file or SECRET_KEY envvar is set
if [ ! -f .ctfd_secret_key ] && [ -z "$SECRET_KEY" ]; then
    if [ $WORKERS -gt 1 ]; then
        echo "[ ERROR ] You are configured to use more than 1 worker."
        echo "[ ERROR ] To do this, you must define the SECRET_KEY environment variable or create a .ctfd_secret_key file."
        echo "[ ERROR ] Exiting..."
        exit 1
    fi
fi

# Check that the database is available
if [ -n "$DATABASE_URL" ]
    then
    database=`echo $DATABASE_URL | awk -F[@//] '{print $4}'`
    echo "Waiting for $database to be ready"
    while ! mysqladmin ping -h $database --silent; do
        # Show some progress
        echo -n '.';
        sleep 1;
    done
    echo "$database is ready"
    # Give it another second.
    sleep 1;
fi

# Log to stdout/stderr by default
if [ -n "$LOG_FOLDER" ]; then
    ACCESS_LOG=${LOG_FOLDER}/access.log
    ERROR_LOG=${LOG_FOLDER}/error.log
else
    ACCESS_LOG=-
    ERROR_LOG=-
fi

# Initialize database
python manage.py db upgrade

# Start CTFd
echo "Starting CTFd"
exec gunicorn 'CTFd:create_app()' \
    --bind '0.0.0.0:8000' \
    --workers $WORKERS \
    --worker-class 'gevent' \
    --access-logfile "$ACCESS_LOG" \
    --error-logfile "$ERROR_LOG"
