#!/bin/sh

# The number of worker is recommended for the current CPU is  CPU number * 2 + 1 eg:2 CPU is 5
# so you have create a  a .ctfd_secret_key file or set SECRET_KEY envvar
WORKERS=5

# Check that a .ctfd_secret_key file or SECRET_KEY envvar is set
if [ ! -f .ctfd_secret_key ] && [ -z "$SECRET_KEY" ]; then
    if [ $WORKERS -gt 1 ]; then
        echo "[ WARNING ] You are configured to use more than 1 worker."
        echo "[ WARNING ] To do this, you must define the SECRET_KEY environment variable or create a .ctfd_secret_key file."
        echo "[ WARNING ] WORKERS will set to 1"
        WORKERS=1
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

if [ -z "$WORKERS" ]; then
    WORKERS=1
fi

# Start CTFd
echo "Starting CTFd"
gunicorn 'CTFd:create_app()' \
    --bind '0.0.0.0:8000' \
    --workers $WORKERS \
    --worker-class 'gevent' \
    --access-logfile "${LOG_FOLDER:-/opt/CTFd/CTFd/logs}/access.log" \
    --error-logfile "${LOG_FOLDER:-/opt/CTFd/CTFd/logs}/error.log"
