#!/bin/sh

# roughly the same as ../docker-entrypoint.sh

echo "Checking DB is available"

while ! mysqladmin ping -h ${DATABASE_CHECK} --silent; do
    echo -n '.';
    sleep 1;
done

cd /opt/ctfd

echo "Starting CTFd"

BUCKET=${BUCKET} DATABASE_URL=${DATABASE_URL} /usr/local/bin/gunicorn --workers 4 --bind 0.0.0.0:8080 \
'CTFd:create_app()' --access-logfile '/opt/ctfd/CTFd/logs/access.log' --error-logfile '/opt/ctfd/CTFd/logs/error.log'
