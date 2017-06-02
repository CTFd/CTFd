#!/bin/sh

# TODO: Should not hack it this way, but probably will be irrelevant once using AWS
echo "Waiting on postgres..."
sleep 5;

echo "Starting CTFd"
gunicorn --bind 0.0.0.0:8000 -w 4 'CTFd:create_app()' --access-logfile '/opt/CTFd/CTFd/logs/access.log' --error-logfile '/opt/CTFd/CTFd/logs/error.log'
