#!/bin/sh

if [ -n "$DATABASE_URL" ]
    then
    # https://stackoverflow.com/a/29793382
    echo "Waiting on MySQL"
    while ! mysqladmin ping -h db --silent; do
        # Show some progress
        echo -n '.';
        sleep 1;
    done
    echo "Ready"
    # Give it another second.
    sleep 1;
fi

echo "Starting CTFd"
gunicorn 'CTFd:create_app()' \
    --bind '0.0.0.0:8000' \
    --workers 1 \
    --worker-class 'gevent' \
    --access-logfile "${LOG_FOLDER:-/opt/CTFd/CTFd/logs}/access.log" \
    --error-logfile "${LOG_FOLDER:-/opt/CTFd/CTFd/logs}/error.log"
