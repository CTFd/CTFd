#!/bin/sh

sed "s;sqlite:///ctfd.db;mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@db/ctfd;g" CTFd/config.py -i

# wait for mysql to start
while ! nc db 3306 >/dev/null 2>&1 < /dev/null; do
    if [ $i -ge 50 ]; then
      echo "$(date) - db:3306 still not reachable, giving up"
      exit 1
    fi
    echo "$(date) - waiting for db:3306..."
    sleep 1
done

gunicorn --bind 0.0.0.0:8000 -w 4 "CTFd:create_app()"
