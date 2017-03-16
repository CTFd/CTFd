#!/bin/sh

# http://stackoverflow.com/questions/25503412/how-do-i-know-when-my-docker-mysql-container-is-up-and-mysql-is-ready-for-taking#29793382
echo "Waiting on MySQL"
while ! mysqladmin ping -h db --silent; do
    # Show some progress
    echo -n '.';
    sleep 1;
done
echo "Ready"
# Give it another second.
sleep 1;

echo "Starting CTFd"
gunicorn --bind 0.0.0.0:8000 -w 4 'CTFd:create_app()' --access-logfile '/opt/CTFd/CTFd/logs/access.log' --error-logfile '/opt/CTFd/CTFd/logs/error.log'