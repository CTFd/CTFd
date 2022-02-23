#!/bin/sh

# create DB URL - grab from the JAWSDB configured URL
heroku config:set DATABASE_URL=`echo ${JAWSDB_MARIA_URL} | sed 's/mysql\:\/\//mysql+pymysql\:\/\//'`

# create REDIS URL - grab from REDISTOGO
heroku config:set REDIS_URL=`echo ${REDISTOGO_URL}`